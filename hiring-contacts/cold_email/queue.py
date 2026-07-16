"""Outreach queue + send-state persistence."""

from __future__ import annotations

import csv
import json
import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from cold_email.blocklist import is_outreach_eligible
from cold_email.config import (
	COMPANY_COOLDOWN_DAYS,
	DEFAULT_DAILY_CAP,
	DEFAULT_TIERS,
	ENABLE_FOLLOWUPS,
	FOLLOWUP_DAYS,
	MASTER_CSV,
	MAX_FOLLOWUPS,
	MAX_PER_COMPANY_PER_DAY,
	MIN_SECONDS_BETWEEN_SENDS,
	SCOUT_CSV,
	STATE_PATH,
)
from cold_email.exclusions import is_outreach_excluded
from cold_email.json_state import load_json, save_json
from cold_email.selection import (
	company_on_cooldown,
	contact_quality_score,
	passes_quality_gate,
	pick_rotated_batch,
	sync_company_registry,
)


def _now() -> datetime:
	return datetime.now(timezone.utc)


def _today_ist() -> str:
	return datetime.now(ZoneInfo("Asia/Kolkata")).strftime("%Y-%m-%d")


def norm_company(name: str) -> str:
	return re.sub(r"[^a-z0-9]", "", (name or "").lower())


@dataclass
class ContactTarget:
	email: str
	company: str
	name: str
	role_title: str
	contact_type: str
	confidence: str
	in_scout_list: bool
	source_id: str
	career_portal: str = ""
	is_followup: bool = False
	prior_sent_at: str = ""
	quality_score: int = 0


def load_scout_portals() -> dict[str, str]:
	out: dict[str, str] = {}
	if not SCOUT_CSV.exists():
		return out
	with SCOUT_CSV.open(encoding="utf-8") as f:
		for row in csv.DictReader(f):
			name = (row.get("Company") or "").strip()
			portal = (row.get("Career Portal") or "").strip()
			if name and portal:
				out[norm_company(name)] = portal
	return out


def load_state() -> dict:
	if STATE_PATH.exists():
		state = load_json(STATE_PATH)
	else:
		state = {"sent": {}, "stats": {"total_sent": 0, "total_followups": 0}}
	state.setdefault("daily_log", {})
	state.setdefault("sent", {})
	state.setdefault("stats", {})
	state.setdefault("companies", {})
	state.setdefault("rotation_index", 0)
	sync_company_registry(state)
	return state


def save_state(state: dict) -> None:
	# Prune daily_log older than 14 days
	cutoff = (datetime.now(ZoneInfo("Asia/Kolkata")).date() - timedelta(days=14)).isoformat()
	daily = state.get("daily_log", {})
	state["daily_log"] = {k: v for k, v in daily.items() if k >= cutoff}
	sync_company_registry(state)
	save_json(STATE_PATH, state)


def _daily_usage(state: dict) -> tuple[set[str], set[str]]:
	"""Return (emails_sent_today, companies_contacted_today) in IST."""
	today = _today_ist()
	bucket = state.get("daily_log", {}).get(today, {})
	emails = set((bucket.get("emails") or []))
	companies = set((bucket.get("companies") or []))
	return emails, companies


def daily_sent_count(state: dict | None = None) -> int:
	state = state or load_state()
	emails_today, _ = _daily_usage(state)
	return len(emails_today)


def daily_remaining_quota(state: dict | None = None) -> int:
	state = state or load_state()
	return max(0, DEFAULT_DAILY_CAP - daily_sent_count(state))


def seconds_until_next_send_allowed(state: dict | None = None) -> int:
	"""Seconds to wait before another SMTP send (0 = OK now)."""
	state = state or load_state()
	last = state.get("last_live_send_at")
	if not last:
		return 0
	try:
		last_dt = datetime.fromisoformat(last)
	except ValueError:
		return 0
	elapsed = (_now() - last_dt).total_seconds()
	return max(0, int(MIN_SECONDS_BETWEEN_SENDS - elapsed))


def load_contacts() -> list[dict]:
	if not MASTER_CSV.exists():
		raise FileNotFoundError(f"Missing {MASTER_CSV} — run scripts/refresh_all.py first")
	with MASTER_CSV.open(encoding="utf-8") as f:
		return list(csv.DictReader(f))


def _followup_candidates(
	state: dict,
	*,
	effective_limit: int,
	emails_today: set[str],
	company_blocked,
	company_filter: str,
) -> list[ContactTarget]:
	if not ENABLE_FOLLOWUPS or MAX_FOLLOWUPS <= 0:
		return []

	now = _now()
	targets: list[ContactTarget] = []

	for email, meta in state.get("sent", {}).items():
		if len(targets) >= effective_limit:
			break
		if meta.get("followup_sent") or meta.get("followup_count", 0) >= MAX_FOLLOWUPS:
			continue
		if meta.get("reply_status") == "replied":
			continue
		sent_at = meta.get("sent_at")
		if not sent_at:
			continue
		try:
			sent_dt = datetime.fromisoformat(sent_at)
		except ValueError:
			continue
		if now - sent_dt < timedelta(days=FOLLOWUP_DAYS):
			continue
		if company_filter and norm_company(meta.get("company", "")) != norm_company(company_filter):
			continue
		if is_outreach_excluded(company=meta.get("company", ""), email=email):
			continue
		if email.lower() in emails_today:
			continue
		if company_blocked(meta.get("company", "")):
			continue
		targets.append(
			ContactTarget(
				email=email,
				company=meta.get("company", ""),
				name=meta.get("name", ""),
				role_title=meta.get("role_title", ""),
				contact_type=meta.get("contact_type", ""),
				confidence=meta.get("confidence", ""),
				in_scout_list=bool(meta.get("in_scout_list")),
				source_id=meta.get("source_id", ""),
				career_portal=meta.get("career_portal", ""),
				is_followup=True,
				prior_sent_at=meta.get("sent_at", ""),
			)
		)
	return targets


def pick_batch(
	*,
	limit: int,
	include_generic: bool = False,
	followups_only: bool = False,
	company_filter: str = "",
	enforce_interval: bool = True,
	persist_rotation: bool = True,
) -> list[ContactTarget]:
	state = load_state()
	remaining_today = daily_remaining_quota(state)
	if remaining_today <= 0:
		return []
	if enforce_interval and seconds_until_next_send_allowed(state) > 0:
		return []

	effective_limit = min(limit, remaining_today)
	portals = load_scout_portals()
	rows = load_contacts()
	allowed = set(DEFAULT_TIERS)
	if include_generic:
		allowed.add("generic_inferred")

	emails_today, companies_today = _daily_usage(state)
	targets: list[ContactTarget] = []
	companies_in_batch: set[str] = set()

	def company_blocked(company: str) -> bool:
		if is_outreach_excluded(company=company):
			return True
		cn = norm_company(company)
		if not cn:
			return False
		if company_on_cooldown(company, state, cooldown_days=COMPANY_COOLDOWN_DAYS):
			return True
		if MAX_PER_COMPANY_PER_DAY and cn in companies_today:
			return True
		if MAX_PER_COMPANY_PER_DAY and cn in companies_in_batch:
			return True
		return False

	if ENABLE_FOLLOWUPS and MAX_FOLLOWUPS > 0:
		for t in _followup_candidates(
			state,
			effective_limit=effective_limit,
			emails_today=emails_today,
			company_blocked=company_blocked,
			company_filter=company_filter,
		):
			targets.append(t)
			companies_in_batch.add(norm_company(t.company))

	if followups_only:
		return targets[:effective_limit]

	sent_emails = set(state.get("sent", {}).keys())
	candidates: list[dict] = []
	for row in rows:
		conf = row.get("confidence") or ""
		if conf not in allowed:
			continue
		email = (row.get("email") or "").strip().lower()
		if not email or email in sent_emails:
			continue
		ok, _reason = is_outreach_eligible(row)
		if not ok:
			continue
		ok_q, _qreason = passes_quality_gate(row)
		if not ok_q:
			continue
		if email in emails_today:
			continue
		if company_blocked(row.get("company") or ""):
			continue
		if company_filter and norm_company(row.get("company", "")) != norm_company(company_filter):
			continue
		candidates.append(row)

	today = _today_ist()
	picked_rows = pick_rotated_batch(
		candidates,
		limit=max(0, effective_limit - len(targets)),
		state=state,
		today_ist=today,
	)

	for row in picked_rows:
		if len(targets) >= effective_limit:
			break
		company = row.get("company") or ""
		if company_blocked(company):
			continue
		cn = norm_company(company)
		score = contact_quality_score(row)
		targets.append(
			ContactTarget(
				email=row["email"].strip().lower(),
				company=company,
				name=row.get("name") or "",
				role_title=row.get("role_title") or "",
				contact_type=row.get("contact_type") or "",
				confidence=row.get("confidence") or "",
				in_scout_list=str(row.get("in_scout_list")).lower() == "true",
				source_id=row.get("source_id") or "",
				career_portal=portals.get(cn, ""),
				quality_score=score,
			)
		)
		companies_in_batch.add(cn)

	if picked_rows and not followups_only and persist_rotation:
		state["rotation_index"] = int(state.get("rotation_index") or 0) + 1
		save_state(state)

	return targets[:effective_limit]


def mark_sent(target: ContactTarget, *, subject: str, dry_run: bool) -> None:
	state = load_state()
	if not dry_run and daily_remaining_quota(state) <= 0:
		raise RuntimeError(
			f"Daily cap reached ({daily_sent_count(state)}/{DEFAULT_DAILY_CAP} sent today IST)"
		)
	key = target.email.lower()
	today = _today_ist()
	daily = state.setdefault("daily_log", {})
	day = daily.setdefault(today, {"emails": [], "companies": []})

	if key not in day["emails"]:
		day["emails"].append(key)
	cn = norm_company(target.company)
	if cn and cn not in day["companies"]:
		day["companies"].append(cn)

	entry = {
		"email": target.email,
		"company": target.company,
		"name": target.name,
		"role_title": target.role_title,
		"contact_type": target.contact_type,
		"confidence": target.confidence,
		"in_scout_list": target.in_scout_list,
		"source_id": target.source_id,
		"career_portal": target.career_portal,
		"quality_score": target.quality_score,
		"subject": subject,
		"dry_run": dry_run,
	}
	if not dry_run:
		state["last_live_send_at"] = _now().isoformat()
	if target.is_followup:
		prev = state["sent"].get(key, {})
		prev["followup_sent"] = True
		prev["followup_count"] = prev.get("followup_count", 0) + 1
		prev["followup_at"] = _now().isoformat()
		state["sent"][key] = prev
		state["stats"]["total_followups"] = state["stats"].get("total_followups", 0) + 1
	else:
		entry["sent_at"] = _now().isoformat()
		entry["followup_sent"] = False
		entry["followup_count"] = 0
		entry["reply_status"] = "no_reply"
		state["sent"][key] = entry
		state["stats"]["total_sent"] = state["stats"].get("total_sent", 0) + 1

	if cn:
		registry = sync_company_registry(state)
		prev_co = registry.get(cn, {})
		registry[cn] = {
			"company": target.company,
			"last_contacted_at": _now().isoformat(),
			"last_email": target.email,
			"status": prev_co.get("status") or "no_reply",
			"touch_count": prev_co.get("touch_count", 0) + 1,
		}
		state["companies"] = registry

	save_state(state)
