"""Email templates — 2026 cold-email format: short, soft ask, full links."""

from __future__ import annotations

import re

from cold_email.config import RESUME_ATTACHMENT_NAME, TARGET_SEASON
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
	SCHOOL,
	STACK_LINE,
)


def _first_name(contact_name: str, email: str) -> str:
	if contact_name and "@" not in contact_name:
		return contact_name.split()[0]
	local = email.split("@", 1)[0]
	if "." in local:
		a, b = local.split(".", 1)
		# r.chandrasi1996@... → Chandrasi
		if len(a) <= 2 and b:
			name_part = re.sub(r"\d+", "", b)
			if len(name_part) > 2:
				return name_part.title()
		if len(a) > 2:
			return a.title()
	return local.split("+", 1)[0].title()


def _links_block() -> str:
	return f"""Quick links:
Portfolio: {PORTFOLIO}
GitHub: {GITHUB}
LinkedIn: {LINKEDIN}
LeetCode ({LEETCODE_STAT}): {LEETCODE}
Codeforces ({CODEFORCES_STAT}): {CODEFORCES}
{LOGIFLOW_NAME} (demo): {LOGIFLOW_LIVE}
{LOGIFLOW_NAME} (code): {LOGIFLOW_GITHUB}"""


def _soft_ask(company: str, contact_type: str) -> str:
	company = company.strip() or "your company"
	if contact_type in ("careers_inbox", "hr_inbox"):
		return (
			f"If you have a moment, I'd really appreciate any guidance on how students "
			f"typically apply for {TARGET_SEASON} software intern roles at {company} — "
			f"or a pointer to whoever owns campus / university recruiting. "
			f"No pressure at all; even the right portal or timing would help."
		)
	return (
		f"If you have 10–15 minutes in the coming weeks, I'd love your perspective on "
		f"internship opportunities at {company} — what you look for in candidates, or "
		f"the best way to apply. If you're not the right person, a referral or intro "
		f"to campus recruiting would mean a lot."
	)


def subject_line(company: str, *, is_followup: bool = False) -> str:
	company = company.strip() or "your team"
	if is_followup:
		return f"Re: SVNIT student — {company} intern question"[:60]
	# Specific, human, under ~60 chars (Whali / FirstSales 2026)
	return f"SVNIT AI student — {company} intern question"[:60]


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

	opening = (
		f"I'm exploring {TARGET_SEASON} software engineering internships at {company} "
		f"and wanted to reach out respectfully — I hope you're the right person to ask, "
		f"or can point me to whoever handles campus hiring."
	)
	if career_portal and career_portal.startswith("http"):
		opening = (
			f"I'm exploring {TARGET_SEASON} software engineering internships at {company}. "
			f"I've seen the careers site and wanted to reach out to a real person rather "
			f"than send a generic application into the void."
		)

	credibility = (
		f"I'm {FIRST_NAME}, penultimate-year {DEGREE} at {SCHOOL} "
		f"(CGPA {CGPA}, graduating {GRAD_MONTH_YEAR}). "
		f"{LOGIFLOW_HOOK}. {INTERN_HOOK}. "
		f"{ACHIEVEMENTS}. "
		f"Competitive programming: {LEETCODE_STAT}; {CODEFORCES_STAT}. "
		f"Stack: {STACK_LINE}."
	)

	return f"""Hi {greet},

{opening}

{credibility}

{_soft_ask(company, contact_type)}

{_links_block()}

I've attached my resume ({RESUME_ATTACHMENT_NAME}) for convenience.

Thank you for your time,
{FULL_NAME}
{PHONE} · {EMAIL}
{LINKEDIN}
"""


def body_followup(*, company: str, contact_name: str, email: str) -> str:
	greet = _first_name(contact_name, email)
	company = company.strip() or "your company"
	return f"""Hi {greet},

Just bumping my note from last week about {TARGET_SEASON} internships at {company} — totally understand if you're busy.

If a quick 10-minute chat isn't feasible, I'd still be grateful for any steer on how to apply, who owns campus recruiting, or whether a referral might be appropriate.

{_links_block()}

Resume attached ({RESUME_ATTACHMENT_NAME}).

Best,
{FULL_NAME}
{PHONE} · {EMAIL}
{LINKEDIN}
"""
