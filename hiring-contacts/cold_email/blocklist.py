"""Blocklist + outreach eligibility — skip stale/bounced/bad inboxes."""

from __future__ import annotations

import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

from cold_email.config import BLOCKLIST_PATH, BLOCKED_LOCAL_PARTS, MAX_CONTACT_AGE_DAYS, STALE_SOURCE_IDS
from cold_email.mx_check import has_mx_record

EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")


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
	return any(part in local for part in BLOCKED_LOCAL_PARTS)


def _parse_fetched_at(value: str) -> datetime | None:
	if not value:
		return None
	try:
		return datetime.fromisoformat(value)
	except ValueError:
		return None


def is_outreach_eligible(row: dict) -> tuple[bool, str]:
	email = (row.get("email") or "").strip().lower()
	if not email:
		return False, "missing_email"
	# Always enforce blocklist + local-part rules (even for discover:career_portal).
	if is_blocked(email):
		return False, "blocklist"
	if _local_part_blocked(email):
		return False, "blocked_local_part"

	source_id = (row.get("source_id") or "").strip()
	if source_id in STALE_SOURCE_IDS:
		return False, "stale_source"

	local = email.split("@", 1)[0]
	domain = email.split("@", 1)[1] if "@" in email else ""

	# Trusted fresh sources.
	if source_id in {
		"discover:career_portal",
		"manual:verified",
		"web:devblogger_verified",
		"web:substack_verified",
		"local:hr_email_csv",
	}:
		notes = row.get("notes") or ""
		if "domain_fallback" in notes:
			if "mx_ok" not in notes and not has_mx_record(domain):
				return False, "unverified_fallback"
		return True, source_id

	confidence = row.get("confidence") or ""
	if confidence not in {"scraped_personal", "public_listed", "verified"}:
		return False, "low_confidence"

	fetched = _parse_fetched_at(row.get("fetched_at") or "")
	if fetched and _now() - fetched > timedelta(days=MAX_CONTACT_AGE_DAYS):
		if source_id not in {"manual:verified", "web:devblogger_verified", "web:substack_verified"}:
			return False, "stale_age"

	# Reject mega-corp careers@ that commonly 550 external mail.
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
