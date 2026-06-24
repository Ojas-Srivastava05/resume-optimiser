"""Email templates — specific ask + standout links block."""

from __future__ import annotations

from cold_email.config import TARGET_SEASON
from cold_email.profile import (
	ACHIEVEMENTS,
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
	PHONE,
	PORTFOLIO,
	RESUME_NOTE,
	SCHOOL,
	STACK_LINE,
)


def _first_name(contact_name: str, email: str) -> str:
	if contact_name and "@" not in contact_name:
		return contact_name.split()[0]
	local = email.split("@", 1)[0]
	if "." in local:
		return local.split(".", 1)[0].title()
	return local.split("+", 1)[0].title()


def _links_block() -> str:
	return f"""Links:
· Portfolio: {PORTFOLIO}
· GitHub: {GITHUB}
· LinkedIn: {LINKEDIN}
· LeetCode ({LEETCODE_STAT}): {LEETCODE}
· Codeforces ({CODEFORCES_STAT}): {CODEFORCES}
· {LOGIFLOW_NAME} (live): {LOGIFLOW_LIVE}
· {LOGIFLOW_NAME} (code): {LOGIFLOW_GITHUB}"""


def subject_line(company: str, *, is_followup: bool = False) -> str:
	company = company.strip() or "your team"
	if is_followup:
		return f"Re: {TARGET_SEASON} intern — {company} · SVNIT SWE"
	return f"{TARGET_SEASON} intern — SVNIT SWE · {company}"[:60]


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

	portal_line = ""
	if career_portal and career_portal.startswith("http"):
		portal_line = (
			f"\nI checked your careers portal ({career_portal}) and wanted to reach the right campus contact."
		)

	if contact_type in ("careers_inbox", "hr_inbox"):
		ask = (
			"Could you share the Summer 2027 software engineering intern application link "
			"or OA process for India, or point me to the campus recruiting contact?"
		)
	else:
		ask = (
			"Would you be open to sharing the Summer 2027 intern application/OA link "
			"or pointing me to the right campus recruiter for software roles?"
		)

	return f"""Hi {greet},

I'm {FIRST_NAME}, penultimate-year {DEGREE} at {SCHOOL} (CGPA {CGPA}, graduating {GRAD_MONTH_YEAR}). Stack: {STACK_LINE}.

Highlights:
· {LOGIFLOW_HOOK}
· {INTERN_HOOK}
· {ACHIEVEMENTS}
· {LEETCODE_STAT} | {CODEFORCES_STAT}{portal_line}

I'm targeting {TARGET_SEASON} software internships at {company}. {ask}

{_links_block()}

{RESUME_NOTE}

Thank you,
{FULL_NAME}
{PHONE} · {EMAIL}
"""


def body_followup(*, company: str, contact_name: str, email: str) -> str:
	greet = _first_name(contact_name, email)
	company = company.strip() or "your company"
	return f"""Hi {greet},

Quick follow-up on my note about {TARGET_SEASON} software internships at {company}.

Happy to hop on a 15-minute call this week — otherwise even the intern portal, OA timeline, or the right campus recruiter would help a lot.

{_links_block()}
{RESUME_NOTE}

Best,
{FULL_NAME}
{PHONE} · {EMAIL}
{LINKEDIN}
"""
