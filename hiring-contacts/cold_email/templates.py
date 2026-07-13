"""Email templates — outcome-focused plain text (referral / OA / careers page)."""

from __future__ import annotations

import hashlib
import re

from cold_email.config import TARGET_SEASON
from cold_email.profile import (
	CGPA,
	CODEFORCES,
	CODEFORCES_STAT,
	COMMUNITY_HERO_HOOK,
	DEGREE,
	EMAIL,
	FULL_NAME,
	GITHUB,
	GRAD_MONTH_YEAR,
	INTERN_HOOK,
	LEETCODE,
	LEETCODE_STAT,
	LINKEDIN,
	LOGIFLOW_HOOK,
	LOGIFLOW_LIVE,
	LOGIFLOW_NAME,
	PHONE,
	PORTFOLIO,
	SCHOOL,
	STACK_LINE,
)


def _first_name(contact_name: str, email: str) -> str:
	if contact_name and "@" not in contact_name:
		return contact_name.split()[0]
	local = email.split("@", 1)[0]
	if "." in local:
		a, b = local.split(".", 1)
		if len(a) <= 2 and b:
			name_part = re.sub(r"\d+", "", b)
			if len(name_part) > 2:
				return name_part.title()
		if len(a) > 2:
			return a.title()
	return local.split("+", 1)[0].title()


def _project_hook(company: str, email: str) -> str:
	"""Rotate standout project line so copy stays fresh across sends."""
	choices = [LOGIFLOW_HOOK, COMMUNITY_HERO_HOOK, INTERN_HOOK]
	idx = int(hashlib.sha256(f"{company}:{email}".encode()).hexdigest()[:4], 16) % len(choices)
	return choices[idx]


def _credentials_bullets(company: str, email: str) -> str:
	return f"""• {SCHOOL} — {DEGREE}, CGPA {CGPA}, {GRAD_MONTH_YEAR}
• {_project_hook(company, email)}
• CP: {LEETCODE_STAT} · {CODEFORCES_STAT}
• {STACK_LINE}"""


def _links_bullets() -> str:
	return f"""• Portfolio: {PORTFOLIO}
• GitHub: {GITHUB}
• LinkedIn: {LINKEDIN}
• LeetCode: {LEETCODE}
• Codeforces: {CODEFORCES}
• {LOGIFLOW_NAME} (live): {LOGIFLOW_LIVE}"""


def _ask_line(company: str, contact_type: str, career_portal: str) -> str:
	company = company.strip() or "your company"
	portal = (career_portal or "").strip()

	if portal:
		portal_hint = (
			f"I found {portal} — if that's the right place for {TARGET_SEASON} SWE interns, "
			f"could you confirm or share the direct application / OA link?"
		)
	else:
		portal_hint = (
			f"Could you point me to the {TARGET_SEASON} SWE intern posting, careers page, "
			f"or campus/university recruiting contact?"
		)

	if contact_type in ("careers_inbox", "hr_inbox"):
		return (
			f"{portal_hint}\n"
			f"If employee referral is the better path at {company}, I'd appreciate guidance on that process."
		)

	return (
		f"{portal_hint}\n"
		f"If you're not the right person, a referral or intro to campus recruiting would help a lot."
	)


def subject_line(company: str, *, is_followup: bool = False) -> str:
	company = company.strip() or "your team"
	base = f"{TARGET_SEASON} SWE intern — {company}"
	if is_followup:
		return f"Re: {base}"[:72]
	return base[:72]


def _signature() -> str:
	return f"""{FULL_NAME}
{PHONE} · {EMAIL}
{LINKEDIN}"""


def body_initial(
	*,
	company: str,
	contact_name: str,
	email: str,
	career_portal: str = "",
	contact_type: str = "recruiter",
) -> str:
	greet = _first_name(contact_name, email)
	company = company.strip() or "your company"

	return f"""Hi {greet},

I'm applying for {TARGET_SEASON} software engineering internships and exploring {company}.

Quick background:
{_credentials_bullets(company, email)}

{_ask_line(company, contact_type, career_portal)}

Links:
{_links_bullets()}

Resume attached.

{_signature()}
"""


def body_followup(*, company: str, contact_name: str, email: str, career_portal: str = "") -> str:
	greet = _first_name(contact_name, email)
	company = company.strip() or "your company"
	portal = (career_portal or "").strip()
	portal_line = f"\nCareers page I found: {portal}" if portal else ""
	return f"""Hi {greet},

Quick bump on {TARGET_SEASON} SWE internships at {company}.{portal_line}

Still hoping for a pointer to the intern application, OA link, or the right campus recruiting contact — or a referral if that's how {company} prefers inbound candidates.

Links:
{_links_bullets()}

Resume attached.

{_signature()}
"""
