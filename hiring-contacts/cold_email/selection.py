"""Contact quality scoring, company rotation, and diverse batch selection."""

from __future__ import annotations

import hashlib
import random
import re
from datetime import datetime, timedelta, timezone

from cold_email.config import (
	COMPANY_COOLDOWN_DAYS,
	MIN_CONTACT_QUALITY,
	REQUIRE_NAMED_CONTACT,
)


def norm_company(name: str) -> str:
	return re.sub(r"[^a-z0-9]", "", (name or "").lower())

RECRUITER_ROLE_RE = re.compile(
	r"\b(recruit|talent|hr|hiring|people|campus|university|staffing|sourcer)\b",
	re.I,
)
RECRUITER_TYPES = frozenset({"recruiter", "hr", "talent", "hiring_manager", "campus_recruiter"})
GENERIC_LOCALS = frozenset(
	{
		"careers",
		"jobs",
		"recruiting",
		"recruitment",
		"hr",
		"talent",
		"hiring",
		"campus",
		"university",
		"info",
		"hello",
		"contact",
		"support",
	}
)
GARBAGE_EMAIL_RE = re.compile(
	r"\.(webp|png|jpg|jpeg|gif|svg|pdf)(@|$)|@(2x|3x)\.|grievance|redressal|noreply",
	re.I,
)


def _parse_dt(value: str) -> datetime | None:
	if not value:
		return None
	try:
		return datetime.fromisoformat(value)
	except ValueError:
		return None


def _now() -> datetime:
	return datetime.now(timezone.utc)


def is_garbage_email(email: str) -> bool:
	email = (email or "").strip().lower()
	if not email or "@" not in email:
		return True
	return bool(GARBAGE_EMAIL_RE.search(email))


def has_real_name(row: dict) -> bool:
	name = (row.get("name") or "").strip()
	if not name or "@" in name:
		return False
	email = (row.get("email") or "").strip().lower()
	local = email.split("@", 1)[0] if email else ""
	if name.lower().replace(" ", ".") == local:
		return False
	if len(name.split()) < 1 or len(name) < 3:
		return False
	return True


def looks_like_recruiter(row: dict) -> bool:
	role = (row.get("role_title") or "").strip()
	ctype = (row.get("contact_type") or "").strip().lower()
	if ctype in RECRUITER_TYPES:
		return True
	return bool(RECRUITER_ROLE_RE.search(role))


def contact_quality_score(row: dict) -> int:
	"""0–100; higher = better cold-outreach target."""
	if is_garbage_email(row.get("email") or ""):
		return 0

	score = 0
	source_id = (row.get("source_id") or "").strip()
	confidence = (row.get("confidence") or "").strip()
	notes = row.get("notes") or ""
	email = (row.get("email") or "").strip().lower()
	local = email.split("@", 1)[0] if "@" in email else ""

	if source_id in {"linkedin:verified", "linkedin:hunter_verified", "linkedin:explorium_verified"}:
		score += 50
	elif source_id == "discover:career_portal":
		score += 35
	elif source_id == "manual:verified":
		score += 40
	elif source_id in {"web:devblogger_verified", "web:substack_verified", "local:hr_email_csv"}:
		score += 30
	elif confidence == "scraped_personal":
		score += 20
	elif confidence == "verified":
		score += 25
	elif confidence == "public_listed":
		score += 10
	else:
		score += 5

	if has_real_name(row):
		score += 25
	elif looks_like_recruiter(row):
		score += 10
	else:
		score -= 15

	if looks_like_recruiter(row):
		score += 15

	if str(row.get("in_scout_list")).lower() == "true":
		score += 5

	if notes == "career_portal_scrape":
		score += 10

	if "domain_fallback" in notes:
		score -= 20

	if local in GENERIC_LOCALS:
		score -= 25

	fetched = _parse_dt(row.get("fetched_at") or "")
	if fetched:
		age_days = (_now() - fetched).days
		if age_days <= 14:
			score += 10
		elif age_days > 45 and source_id not in {"manual:verified", "discover:career_portal"}:
			score -= 20

	return max(0, min(100, score))


def passes_quality_gate(row: dict) -> tuple[bool, str]:
	if is_garbage_email(row.get("email") or ""):
		return False, "garbage_email"
	source_id = (row.get("source_id") or "").strip()
	if source_id in {"linkedin:verified", "linkedin:hunter_verified", "linkedin:explorium_verified"}:
		name = (row.get("name") or "").strip()
		if len(name.split()) < 2:
			return False, "linkedin_missing_name"
		notes = row.get("notes") or ""
		conf = 0
		for part in notes.split(";"):
			if part.startswith("confidence="):
				try:
					conf = int(part.split("=", 1)[1])
				except ValueError:
					conf = 0
			elif part.startswith("hunter_score="):
				try:
					conf = int(part.split("=", 1)[1])
				except ValueError:
					conf = 0
			elif part.startswith("explorium_email_status="):
				status = part.split("=", 1)[1].strip().lower()
				conf = 95 if status == "valid" else 85 if status == "accept_all" else 0
		if conf and conf < 85:
			return False, f"low_confidence:{conf}"
		if "mx_ok" not in notes and "mx_ok_public" not in notes:
			if not any(
				x in notes
				for x in (
					"verification=web_public",
					"verification=web_smtp",
					"verification=smtp",
				)
			):
				return False, "missing_mx_proof"
		return True, "linkedin_verified"
	score = contact_quality_score(row)
	if score < MIN_CONTACT_QUALITY:
		return False, f"low_quality:{score}"
	if REQUIRE_NAMED_CONTACT and not has_real_name(row) and not looks_like_recruiter(row):
		return False, "unnamed_non_recruiter"
	return True, f"ok:{score}"


def sync_company_registry(state: dict) -> dict[str, dict]:
	"""Ensure state['companies'] reflects all prior sends."""
	registry: dict[str, dict] = dict(state.get("companies") or {})
	for meta in state.get("sent", {}).values():
		company = meta.get("company") or ""
		cn = norm_company(company)
		if not cn:
			continue
		touch_at = meta.get("followup_at") or meta.get("sent_at") or ""
		touch_dt = _parse_dt(touch_at)
		prev = registry.get(cn, {})
		prev_dt = _parse_dt(prev.get("last_contacted_at") or "")
		if touch_dt and (not prev_dt or touch_dt > prev_dt):
			registry[cn] = {
				"company": company,
				"last_contacted_at": touch_at,
				"last_email": meta.get("email", ""),
				"status": meta.get("reply_status") or prev.get("status") or "no_reply",
				"touch_count": prev.get("touch_count", 0) + (1 if meta.get("sent_at") else 0),
			}
		elif cn not in registry:
			registry[cn] = {
				"company": company,
				"last_contacted_at": touch_at,
				"last_email": meta.get("email", ""),
				"status": "no_reply",
				"touch_count": 1,
			}
	state["companies"] = registry
	return registry


def company_on_cooldown(company: str, state: dict, *, cooldown_days: int | None = None) -> bool:
	cooldown_days = cooldown_days if cooldown_days is not None else COMPANY_COOLDOWN_DAYS
	cn = norm_company(company)
	if not cn:
		return False
	registry = sync_company_registry(state)
	entry = registry.get(cn)
	if not entry:
		return False
	last = _parse_dt(entry.get("last_contacted_at") or "")
	if not last:
		return False
	return _now() - last < timedelta(days=cooldown_days)


def daily_rotation_seed(state: dict, today_ist: str) -> int:
	rotation = int(state.get("rotation_index") or 0)
	raw = f"{today_ist}:{rotation}".encode()
	return int(hashlib.sha256(raw).hexdigest()[:8], 16)


def pick_rotated_batch(
	candidates: list[dict],
	*,
	limit: int,
	state: dict,
	today_ist: str,
) -> list[dict]:
	"""One high-quality contact per company; shuffle companies daily for fresh rotation."""
	by_company: dict[str, dict] = {}
	for row in candidates:
		company = row.get("company") or ""
		cn = norm_company(company)
		if not cn:
			continue
		score = contact_quality_score(row)
		prev = by_company.get(cn)
		if not prev or score > contact_quality_score(prev):
			by_company[cn] = row

	pool = list(by_company.values())
	rng = random.Random(daily_rotation_seed(state, today_ist))
	rng.shuffle(pool)
	return pool[:limit]
