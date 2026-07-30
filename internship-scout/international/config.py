"""Config for First-World Internship Radar (Summer 2027)."""

from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]  # internship-scout/
INTL_ROOT = Path(__file__).resolve().parent

try:
	from dotenv import load_dotenv

	load_dotenv(ROOT / ".env")
except ImportError:
	pass

RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL", "srivastavaojas454@gmail.com")
SMTP_EMAIL = os.getenv("SMTP_EMAIL", RECIPIENT_EMAIL)
SMTP_APP_PASSWORD = os.getenv("SMTP_APP_PASSWORD", "").replace(" ", "")

# Separate state so India scout dedupe never collides
SEEN_PATH = INTL_ROOT / "seen_international.json"
PREVIEW_DIR = INTL_ROOT / "previews"

TARGET_SEASON = "Summer 2027"
GRAD_BATCH_YEAR = "2028"

# Profile fit (Ojas) — used in digest framing + application draft tone
CANDIDATE_NAME = "Ojas Srivastava"
CANDIDATE_SCHOOL = "SVNIT Surat"
CANDIDATE_DEGREE = "B.Tech Artificial Intelligence"
CANDIDATE_CGPA = "9.20/10"
CANDIDATE_GRAD = "May 2028"
CANDIDATE_FOCUS = "SWE / Systems / Backend · DSA · FastAPI · Cloud · CP (LeetCode Knight)"

# How often we re-email the same curated program (not ATS jobs)
MAX_PROGRAM_EMAILS = int(os.getenv("INTL_MAX_PROGRAM_EMAILS", "2"))

# Distinct branding — never reuse "Scout:" / "Summer 2027 SWE intern —"
DIGEST_BRAND = "First-World Internship Radar"
DIGEST_SUBJECT_PREFIX = "🌍 Radar"
