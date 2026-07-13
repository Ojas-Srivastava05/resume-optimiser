"""Companies/domains opted out of cold outreach."""

from __future__ import annotations

from cold_email.config import EXCLUDED_COMPANY_KEYS, EXCLUDED_EMAIL_DOMAINS


def norm_company(name: str) -> str:
	import re

	return re.sub(r"[^a-z0-9]", "", (name or "").lower())


def is_company_excluded(company: str) -> bool:
	key = norm_company(company)
	return bool(key and key in EXCLUDED_COMPANY_KEYS)


def is_email_domain_excluded(email: str) -> bool:
	addr = (email or "").strip().lower()
	if "@" not in addr:
		return False
	domain = addr.rsplit("@", 1)[1]
	return domain in EXCLUDED_EMAIL_DOMAINS


def is_outreach_excluded(*, company: str = "", email: str = "") -> bool:
	if is_company_excluded(company):
		return True
	if is_email_domain_excluded(email):
		return True
	return False
