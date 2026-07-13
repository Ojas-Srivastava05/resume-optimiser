"""Blocklist + outreach eligibility — LinkedIn-verified contacts only."""

from __future__ import annotations

import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

from cold_email.config import (
	BLOCKLIST_PATH,
	BLOCKED_LOCAL_PARTS,
	LINKEDIN_ONLY_MODE,
	LINKEDIN_VERIFIED_SOURCE_IDS,
	MAX_CONTACT_AGE_DAYS,
	STALE_SOURCE_IDS,
)
from cold_email.exclusions import is_outreach_excluded
from cold_email.mx_check import has_mx_record

EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
LINKEDIN_PROFILE_RE = re.compile(r"linkedin\.com/in/", re.I)


def _now() -> datetime:
	return datetime.now(timezone.utc)


def load_blocklist() -> dict:
	if not BLOCKLIST_PATH.exists():
		return {"blocked": {}, "replacements": {}}
	return json.loads(BLOCKLIST_PATH.read_text(encoding="utf-8"))


def save_blocklist(data: dict) -> None:
	BLOCKLIST_PATH.parent.mkdir(parents=True, exist_ok=True)
	BLOCKLIST_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")


def blocked_emails() -> set[str]:
	data = load_blocklist()
	return {e.lower() for e in data.get("blocked", {})}


def is_blocked(email: str) -> bool:
	return email.strip().lower() in blocked_emails()


def record_bounce(email: str, *, reason: str = "", replacement_emails: list[str] | None = None) -> None:
	key = email.strip().lower()
	if not key:
		return
	data = load_blocklist()
	blocked = data.setdefault("blocked", {})
	blocked[key] = {
		"reason": reason,
		"recorded_at": _now().isoformat(),
	}
	if replacement_emails:
		replacements = data.setdefault("replacements", {})
		replacements[key] = [e.lower() for e in replacement_emails if e]
	save_blocklist(data)


def extract_emails_from_text(text: str) -> list[str]:
	return [m.group(0).lower() for m in EMAIL_RE.finditer(text or "")]


def record_bounce_from_message(email: str, message: str) -> list[str]:
	replacements = extract_emails_from_text(message)
	replacements = [e for e in replacements if e != email.lower()]
	record_bounce(email, reason=message[:500], replacement_emails=replacements or None)
	return replacements


def _local_part_blocked(email: str) -> bool:
	local = email.split("@", 1)[0].lower()
	if any(part in local for part in BLOCKED_LOCAL_PARTS):
		return True
	if re.search(r"\.(webp|png|jpg|jpeg|gif|svg|pdf)$", local):
		return True
	if "grievance" in local or "redressal" in local:
		return True
	return False


def _parse_fetched_at(value: str) -> datetime | None:
	if not value:
		return None
	try:
		return datetime.fromisoformat(value)
	except ValueError:
		return None


def _has_linkedin_proof(row: dict) -> bool:
	source_url = row.get("source_url") or ""
	notes = row.get("notes") or ""
	if LINKEDIN_PROFILE_RE.search(source_url):
		return True
	if "linkedin_profile=" in notes:
		return True
	return False


def is_outreach_eligible(row: dict) -> tuple[bool, str]:
	email = (row.get("email") or "").strip().lower()
	if not email:
		return False, "missing_email"
	company = row.get("company") or row.get("company_normalized") or ""
	if is_outreach_excluded(company=company, email=email):
		return False, "excluded_company"
	if is_blocked(email):
		return False, "blocklist"
	if _local_part_blocked(email):
		return False, "blocked_local_part"

	source_id = (row.get("source_id") or "").strip()
	notes = row.get("notes") or ""

	if LINKEDIN_ONLY_MODE:
		if source_id not in LINKEDIN_VERIFIED_SOURCE_IDS:
			return False, "non_linkedin_source"
		if not _has_linkedin_proof(row):
			return False, "missing_linkedin_profile"
		if "confidence=" not in notes and "hunter_score=" not in notes and "explorium_email_status=" not in notes:
			return False, "missing_verification_score"
		if "mx_ok" not in notes and not has_mx_record(email.split("@", 1)[1]):
			return False, "mx_fail"
		name = (row.get("name") or "").strip()
		if not name:
			return False, "missing_name"
		return True, source_id

	if source_id in STALE_SOURCE_IDS:
		return False, "stale_source"

	if source_id in {
		"manual:verified",
		"web:devblogger_verified",
		"web:substack_verified",
	}:
		return True, source_id

	confidence = row.get("confidence") or ""
	if confidence not in {"scraped_personal", "public_listed", "verified"}:
		return False, "low_confidence"

	fetched = _parse_fetched_at(row.get("fetched_at") or "")
	if fetched and _now() - fetched > timedelta(days=MAX_CONTACT_AGE_DAYS):
		if source_id not in {"manual:verified", "web:devblogger_verified", "web:substack_verified"}:
			return False, "stale_age"

	local = email.split("@", 1)[0]
	domain = email.split("@", 1)[1] if "@" in email else ""
	if local in {"careers", "jobs", "recruiting"} and domain in {
		"palantir.com",
		"google.com",
		"meta.com",
		"apple.com",
		"microsoft.com",
		"amazon.com",
	}:
		return False, "mega_corp_careers"

	return True, "ok"
