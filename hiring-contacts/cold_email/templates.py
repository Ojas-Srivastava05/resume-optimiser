"""Email templates — direct, scannable plain text (best deliverability for 1:1 Gmail)."""

from __future__ import annotations

import re

from cold_email.config import TARGET_SEASON
from cold_email.profile import (
	CGPA,
	CODEFORCES,
	CODEFORCES_STAT,
	DEGREE,
	EMAIL,
	FIRST_NAME,
	FULL_NAME,
	GITHUB,
	GRAD_MONTH_YEAR,
	INTERN_HOOK,
	LEETCODE,
	LEETCODE_STAT,
	LINKEDIN,
	LOGIFLOW_GITHUB,
	LOGIFLOW_HOOK,
	LOGIFLOW_LIVE,
	LOGIFLOW_NAME,
	OUTREACH_AUTOMATION_NOTE,
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


def _credentials_bullets() -> str:
	return f"""• {SCHOOL} — {DEGREE}, CGPA {CGPA}, {GRAD_MONTH_YEAR}
• {LOGIFLOW_HOOK}
• {INTERN_HOOK}
• CP: {LEETCODE_STAT} · {CODEFORCES_STAT}
• {STACK_LINE}"""


def _links_bullets() -> str:
	return f"""• Portfolio: {PORTFOLIO}
• GitHub: {GITHUB}
• LinkedIn: {LINKEDIN}
• LeetCode: {LEETCODE}
• Codeforces: {CODEFORCES}
• {LOGIFLOW_NAME}: {LOGIFLOW_LIVE}
• {LOGIFLOW_NAME} (code): {LOGIFLOW_GITHUB}"""


def _ask_line(company: str, contact_type: str) -> str:
	company = company.strip() or "your company"
	if contact_type in ("careers_inbox", "hr_inbox"):
		return (
			f"Open to a brief note on how {TARGET_SEASON} SWE intern hiring works at {company} "
			f"— or a pointer to campus / university recruiting."
		)
	return (
		f"Open to a 10-minute call on {TARGET_SEASON} intern hiring at {company}, "
		f"or a referral / intro to campus recruiting if you're not the right contact."
	)


def subject_line(company: str, *, is_followup: bool = False) -> str:
	company = company.strip() or "your team"
	base = f"Summer 2027 Intern SWE — {company}"
	if is_followup:
		return f"Re: {base}"[:72]
	return base[:72]


def _signature() -> str:
	return f"""{FULL_NAME}
{PHONE} · {EMAIL}
{LINKEDIN}"""


def _footer() -> str:
	return f"""—
{OUTREACH_AUTOMATION_NOTE}"""


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

I'm targeting {TARGET_SEASON} software engineering internships at {company}.

Background:
{_credentials_bullets()}

{_ask_line(company, contact_type)}

Links:
{_links_bullets()}

I've attached my resume.

{_signature()}

{_footer()}
"""


def body_followup(*, company: str, contact_name: str, email: str) -> str:
	greet = _first_name(contact_name, email)
	company = company.strip() or "your company"
	return f"""Hi {greet},

Following up on my note about {TARGET_SEASON} SWE internships at {company}.

Still interested in a short call, or a pointer to campus recruiting / referral if that fits better.

Links:
{_links_bullets()}

I've attached my resume.

{_signature()}

{_footer()}
"""
