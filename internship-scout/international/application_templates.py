"""Application / coordinator email drafts — DISTINCT from domestic cold outreach.

Domestic (hiring-contacts): "Summer 2027 SWE intern — {Company}" + referral ask.
International: visa-aware, program-specific, research/SWE framing for first-world hosts.
"""

from __future__ import annotations

from international.config import (
	CANDIDATE_CGPA,
	CANDIDATE_DEGREE,
	CANDIDATE_FOCUS,
	CANDIDATE_GRAD,
	CANDIDATE_NAME,
	CANDIDATE_SCHOOL,
	TARGET_SEASON,
)
from international.models import Opportunity


def subject_for_program(opp: Opportunity) -> str:
	# Must NOT look like domestic "Summer 2027 SWE intern — X"
	return f"{TARGET_SEASON} — interest in {opp.name} ({opp.country})"


def body_for_program(opp: Opportunity, *, coordinator_name: str = "") -> str:
	greet = f"Dear {coordinator_name}," if coordinator_name.strip() else "Dear Selection Committee,"
	visa = opp.visa_note or "I can follow the host-country internship / research visa process if selected."
	return f"""{greet}

I am {CANDIDATE_NAME}, a {CANDIDATE_DEGREE} student at {CANDIDATE_SCHOOL} (CGPA {CANDIDATE_CGPA}, graduating {CANDIDATE_GRAD}). I am writing to express interest in the {opp.name} for {TARGET_SEASON}.

Why this programme fits my profile:
• Focus: {CANDIDATE_FOCUS}
• Production experience: Software Engineering Intern at IFFCO — Node.js/Express/MySQL APIs, Docker/CI
• Systems projects: LogiFlow (Google Solution Challenge 2026 Global Top 106) — FastAPI, Redis, SQL, GCP Cloud Run
• Problem-solving: LeetCode Knight (peak 2048) · Codeforces Specialist

I understand this is an international placement in {opp.country}. {visa}

Could you confirm the {TARGET_SEASON} application window and any materials required from Indian universities (transcript, enrollment letter, or professor recommendation)?

Portfolio: https://ojas-srivastava.vercel.app
GitHub: https://github.com/Ojas-Srivastava05
LinkedIn: https://linkedin.com/in/ojas-srivastava05

Thank you for your time.
{CANDIDATE_NAME}
+91-7424978046 · srivastavaojas454@gmail.com
"""


def subject_for_company_intl(company: str, location: str) -> str:
	# Distinct from domestic subject pattern
	return f"{TARGET_SEASON} SWE intern ({location}) — {company} [international]"


def body_for_company_intl(company: str, location: str, role_hint: str = "software engineering intern") -> str:
	return f"""Hi,

I'm {CANDIDATE_NAME} ({CANDIDATE_SCHOOL}, {CANDIDATE_DEGREE}, CGPA {CANDIDATE_CGPA}, {CANDIDATE_GRAD}). I'm targeting a {TARGET_SEASON} {role_hint} role in {location} (first-world office), not an India-only placement.

Relevant signal:
• IFFCO SWE intern — production REST APIs (Node/Express/MySQL)
• LogiFlow — GSC 2026 Top 106 (FastAPI, Redis, Cloud Run)
• LeetCode Knight 2048 · Codeforces Specialist

Could you share whether {company}'s {location} office sponsors interns from Indian universities for {TARGET_SEASON}, and the right careers / OA link?

https://ojas-srivastava.vercel.app · https://github.com/Ojas-Srivastava05

Thanks,
{CANDIDATE_NAME}
+91-7424978046
"""
