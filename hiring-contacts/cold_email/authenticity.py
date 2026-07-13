"""Strict authenticity gate — only verified LinkedIn recruiters pass."""

from __future__ import annotations

import re

from cold_email.selection import is_garbage_email

LINKEDIN_IN_RE = re.compile(r"linkedin\.com/in/", re.I)
HUNTER_SCORE_RE = re.compile(r"hunter_score=(\d+)")
HUNTER_STATUS_RE = re.compile(r"hunter_status=([^;]+)")
EXPLORIUM_STATUS_RE = re.compile(r"explorium_email_status=([^;]+)")

ALLOWED_SOURCE_IDS = frozenset({"linkedin:hunter_verified", "linkedin:explorium_verified"})
BLOCKED_HUNTER_STATUSES = frozenset({"invalid", "disposable", "webmail"})
BLOCKED_EXPLORIUM_STATUSES = frozenset({"invalid"})
MIN_HUNTER_SCORE = 85


def _linkedin_proof(row: dict) -> bool:
	source_url = row.get("source_url") or ""
	notes = row.get("notes") or ""
	if LINKEDIN_IN_RE.search(source_url):
		return True
	if "linkedin_profile=" in notes and LINKEDIN_IN_RE.search(notes):
		return True
	return False


def _hunter_score(notes: str) -> int | None:
	match = HUNTER_SCORE_RE.search(notes or "")
	if not match:
		return None
	try:
		return int(match.group(1))
	except ValueError:
		return None


def _hunter_status(notes: str) -> str:
	match = HUNTER_STATUS_RE.search(notes or "")
	return (match.group(1) if match else "").strip().lower()


def _explorium_status(notes: str) -> str:
	match = EXPLORIUM_STATUS_RE.search(notes or "")
	return (match.group(1) if match else "").strip().lower()


def _has_real_name(row: dict) -> bool:
	name = (row.get("name") or "").strip()
	if not name or "@" in name:
		return False
	parts = name.split()
	if len(parts) < 2:
		return False
	source_id = (row.get("source_id") or "").strip()
	if source_id == "linkedin:explorium_verified":
		return len(parts[0]) >= 2 and parts[0].replace("-", "").isalpha()
	return all(len(p) >= 2 and p.replace("-", "").isalpha() for p in parts[:2])


def _check_hunter(row: dict, notes: str) -> tuple[bool, str]:
	score = _hunter_score(notes)
	if score is None:
		return False, "no_hunter_score"
	if score < MIN_HUNTER_SCORE:
		return False, f"low_hunter_score:{score}"

	status = _hunter_status(notes)
	if status in BLOCKED_HUNTER_STATUSES:
		return False, f"bad_hunter_status:{status}"
	return True, "authentic"


def _check_explorium(notes: str) -> tuple[bool, str]:
	status = _explorium_status(notes)
	if not status:
		return False, "no_explorium_status"
	if status in BLOCKED_EXPLORIUM_STATUSES:
		return False, f"bad_explorium_status:{status}"
	if status not in {"valid", "accept_all"}:
		return False, f"low_explorium_status:{status}"
	return True, "authentic"


def is_authentic_contact(row: dict) -> tuple[bool, str]:
	"""Return (True, reason) only for verified LinkedIn recruiters."""
	email = (row.get("email") or "").strip().lower()
	if not email or "@" not in email:
		return False, "missing_email"
	if is_garbage_email(email):
		return False, "garbage_email"

	source_id = (row.get("source_id") or "").strip()
	if source_id not in ALLOWED_SOURCE_IDS:
		return False, "not_verified_source"

	if not _linkedin_proof(row):
		return False, "no_linkedin_profile"

	notes = row.get("notes") or ""
	if source_id == "linkedin:hunter_verified":
		ok, reason = _check_hunter(row, notes)
		if not ok:
			return False, reason
	elif source_id == "linkedin:explorium_verified":
		ok, reason = _check_explorium(notes)
		if not ok:
			return False, reason
		company_key = (row.get("company_normalized") or "").strip()
		email_base = email.split("@", 1)[1].split(".", 1)[0]
		if company_key and email_base and company_key not in email_base and email_base not in company_key:
			if len(company_key) >= 4 and len(email_base) >= 4:
				return False, "email_company_mismatch"

	if not _has_real_name(row):
		return False, "no_real_name"

	role = (row.get("role_title") or "").lower()
	if not role and row.get("contact_type") not in {"recruiter", "hr", "talent"}:
		return False, "not_recruiter"

	return True, "authentic"
