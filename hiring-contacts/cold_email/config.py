"""Cold outreach configuration — Summer 2027 internship focus."""

from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = ROOT.parent
INTERNSHIP_SCOUT_ENV = REPO_ROOT / "internship-scout" / ".env"

# Load SMTP from internship-scout .env when present (local dev)
try:
	from dotenv import load_dotenv

	load_dotenv(INTERNSHIP_SCOUT_ENV)
except ImportError:
	pass

DATA = ROOT / "data"
MERGED = DATA / "merged"
STATE_PATH = DATA / "outreach_state.json"
DRAFTS_DIR = DATA / "drafts"

MASTER_CSV = MERGED / "master_contacts.csv"
SCOUT_CSV = REPO_ROOT / "internship-scout" / "data" / "all_companies.csv"

TARGET_INTERNSHIP_YEAR = 2027
TARGET_SEASON = "Summer 2027"

# SMTP (same as Internship Scout)
SMTP_EMAIL = os.getenv("SMTP_EMAIL", os.getenv("RECIPIENT_EMAIL", "srivastavaojas454@gmail.com"))
SMTP_APP_PASSWORD = os.getenv("SMTP_APP_PASSWORD", "").replace(" ", "")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL", SMTP_EMAIL)  # dry-run preview recipient

# Sending guardrails (research-backed: quality > volume)
DEFAULT_DAILY_CAP = int(os.getenv("COLD_EMAIL_DAILY_CAP", "10"))
MIN_SECONDS_BETWEEN_SENDS = int(os.getenv("COLD_EMAIL_MIN_INTERVAL_SEC", "45"))
FOLLOWUP_DAYS = int(os.getenv("COLD_EMAIL_FOLLOWUP_DAYS", "5"))
MAX_FOLLOWUPS = 1
# Never email the same address or company twice in one IST day
MAX_PER_COMPANY_PER_DAY = int(os.getenv("COLD_EMAIL_MAX_PER_COMPANY_PER_DAY", "1"))

# Confidence tiers to contact (best first). generic_inferred off by default.
DEFAULT_TIERS = (
	"scraped_personal",
	"public_listed",
	"scraped",
	"inferred_pattern",
)

RESUME_ATTACHMENT_NAME = os.getenv("COLD_EMAIL_RESUME_FILENAME", "ojas_srivastava_resume.pdf")
RESUME_SOURCE = REPO_ROOT / "Resume Collection" / "ojas_srivastava_google_swe_intern_2027.pdf"
RESUME_PATH = Path(
	os.getenv(
		"COLD_EMAIL_RESUME_PATH",
		str(REPO_ROOT / "Resume Collection" / "ojas_srivastava_resume.pdf"),
	)
)
