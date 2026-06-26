"""Cold outreach configuration — Summer 2027 internship focus."""

from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = ROOT.parent
INTERNSHIP_SCOUT_ENV = REPO_ROOT / "internship-scout" / ".env"


def _load_env_file(path: Path) -> None:
	"""Minimal .env loader when python-dotenv is unavailable."""
	if not path.exists():
		return
	for line in path.read_text(encoding="utf-8").splitlines():
		line = line.strip()
		if not line or line.startswith("#") or "=" not in line:
			continue
		key, _, value = line.partition("=")
		key = key.strip()
		value = value.strip().strip('"').strip("'")
		if key and key not in os.environ:
			os.environ[key] = value


# Load SMTP from internship-scout .env when present (local dev)
try:
	from dotenv import load_dotenv

	load_dotenv(INTERNSHIP_SCOUT_ENV)
except ImportError:
	_load_env_file(INTERNSHIP_SCOUT_ENV)

DATA = ROOT / "data"
MERGED = DATA / "merged"
STATE_PATH = DATA / "outreach_state.json"
BLOCKLIST_PATH = DATA / "blocklist.json"
DRAFTS_DIR = DATA / "drafts"

MASTER_CSV = MERGED / "master_contacts.csv"
SCOUT_CSV = REPO_ROOT / "internship-scout" / "data" / "all_companies.csv"

TARGET_INTERNSHIP_YEAR = 2027
TARGET_SEASON = "Summer 2027"

# SMTP (same as Internship Scout)
SMTP_EMAIL = os.getenv("SMTP_EMAIL", os.getenv("RECIPIENT_EMAIL", "srivastavaojas454@gmail.com"))
SMTP_APP_PASSWORD = os.getenv("SMTP_APP_PASSWORD", "").replace(" ", "")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL", SMTP_EMAIL)  # dry-run preview recipient

# Sending guardrails — Gmail abuse detection is strict on burst SMTP from personal accounts.
# Default: max 3 cold emails per IST day, 1 per scheduled run, ≥1 hour apart.
DEFAULT_DAILY_CAP = int(os.getenv("COLD_EMAIL_DAILY_CAP", "3"))
MAX_PER_RUN = int(os.getenv("COLD_EMAIL_MAX_PER_RUN", "1"))
MIN_SECONDS_BETWEEN_SENDS = int(os.getenv("COLD_EMAIL_MIN_INTERVAL_SEC", "3600"))
FOLLOWUP_DAYS = int(os.getenv("COLD_EMAIL_FOLLOWUP_DAYS", "5"))
MAX_FOLLOWUPS = 1
# Never email the same address or company twice in one IST day
MAX_PER_COMPANY_PER_DAY = int(os.getenv("COLD_EMAIL_MAX_PER_COMPANY_PER_DAY", "1"))

# Confidence tiers to contact (best first). Stale bulk scrapes excluded in queue.
DEFAULT_TIERS = (
	"verified",
	"scraped_personal",
	"public_listed",
)

# Bulk lists with high bounce/stale rates — never cold-email without live re-discovery.
STALE_SOURCE_IDS = frozenset(
	{
		"github:careerLauncher",
		"web:substack_atoz_50_hr",
		"web:devblogger_hr_500",
		"inferred:recruiter-emailing-script",
	}
)

# Local-parts that are not recruiting inboxes (accessibility, vendor support, etc.).
BLOCKED_LOCAL_PARTS = frozenset(
	{
		"accessibility",
		"accessiblecareers",
		"yourresourcingsupport",
		"info",
		"support",
		"help",
		"noreply",
		"no-reply",
		"hrwebrequest",
	}
)

# Contacts older than this are skipped unless source is discover:career_portal.
MAX_CONTACT_AGE_DAYS = int(os.getenv("COLD_EMAIL_MAX_CONTACT_AGE_DAYS", "45"))

RESUME_ATTACHMENT_NAME = os.getenv("COLD_EMAIL_RESUME_FILENAME", "ojas_srivastava_resume.pdf")
RESUME_SOURCE = REPO_ROOT / "Resume Collection" / "ojas_srivastava_google_swe_intern_2027.pdf"
RESUME_PATH = Path(
	os.getenv(
		"COLD_EMAIL_RESUME_PATH",
		str(REPO_ROOT / "Resume Collection" / "ojas_srivastava_resume.pdf"),
	)
)
