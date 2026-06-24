"""Sender profile for outreach — override via env if needed."""

from __future__ import annotations

import os

FULL_NAME = os.getenv("OUTREACH_FULL_NAME", "Ojas Srivastava")
FIRST_NAME = FULL_NAME.split()[0]
SCHOOL = os.getenv("OUTREACH_SCHOOL", "SVNIT Surat")
DEGREE = os.getenv("OUTREACH_DEGREE", "B.Tech Artificial Intelligence")
CGPA = os.getenv("OUTREACH_CGPA", "9.20/10")
GRAD_MONTH_YEAR = os.getenv("OUTREACH_GRAD", "May 2028")
PHONE = os.getenv("OUTREACH_PHONE", "+91-7424978046")
EMAIL = os.getenv("OUTREACH_EMAIL", "srivastavaojas454@gmail.com")

# Profiles & portfolio
LINKEDIN = os.getenv("OUTREACH_LINKEDIN", "https://linkedin.com/in/ojas-srivastava05")
GITHUB = os.getenv("OUTREACH_GITHUB", "https://github.com/Ojas-Srivastava05")
PORTFOLIO = os.getenv("OUTREACH_PORTFOLIO", "https://ojas-srivastava.vercel.app")

# Coding platforms
LEETCODE = os.getenv("OUTREACH_LEETCODE", "https://leetcode.com/Oju_Srivastava")
CODEFORCES = os.getenv("OUTREACH_CODEFORCES", "https://codeforces.com/profile/Oju")
LEETCODE_STAT = os.getenv("OUTREACH_LEETCODE_STAT", "Knight · Rating 2048 · 637+ solved · 32 contests")
CODEFORCES_STAT = os.getenv("OUTREACH_CODEFORCES_STAT", "Specialist · Rating 1457 · 207+ solved")

# Standout work (with live links where possible)
LOGIFLOW_NAME = os.getenv("OUTREACH_LOGIFLOW_NAME", "LogiFlow")
LOGIFLOW_HOOK = os.getenv(
	"OUTREACH_LOGIFLOW_HOOK",
	"LogiFlow — Google Solution Challenge 2026 Global Top 100 (Technical Co-Lead); GCP Cloud Run backend, 100–400 ms latency",
)
LOGIFLOW_GITHUB = os.getenv(
	"OUTREACH_LOGIFLOW_GITHUB",
	"https://github.com/Ojas-Srivastava05/LogiFlow-Solution-Challenge-2026",
)
LOGIFLOW_LIVE = os.getenv(
	"OUTREACH_LOGIFLOW_LIVE",
	"https://logi-flow-solution-challenge-2026.vercel.app/",
)

INTERN_HOOK = os.getenv(
	"OUTREACH_INTERN_HOOK",
	"Software Engineering Intern at IFFCO — shipped 10+ production REST APIs (Node.js, Express, MySQL, Docker/CI/CD)",
)

ACHIEVEMENTS = os.getenv(
	"OUTREACH_ACHIEVEMENTS",
	"McKinsey.org Forward Fellow 2026 · "
	"Executive Member, ACM SVNIT & Mentor, Nexus SVNIT (DSA workshops & contests)",
)

STACK_LINE = os.getenv(
	"OUTREACH_STACK",
	"C++ · Python · TypeScript · Node.js · SQL · system design & DSA",
)
