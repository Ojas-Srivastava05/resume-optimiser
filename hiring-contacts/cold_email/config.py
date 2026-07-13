"""Cold outreach configuration — Summer 2027 internship focus."""

from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = ROOT.parent
INTERNSHIP_SCOUT_ENV = REPO_ROOT / "internship-scout" / ".env"
HIRING_CONTACTS_ENV = ROOT / ".env"


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
	load_dotenv(HIRING_CONTACTS_ENV)
except ImportError:
	_load_env_file(INTERNSHIP_SCOUT_ENV)
	_load_env_file(HIRING_CONTACTS_ENV)

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
# Follow-ups to silent contacts are off by default — user opts in explicitly.
ENABLE_FOLLOWUPS = os.getenv("COLD_EMAIL_ENABLE_FOLLOWUPS", "false").lower() in ("1", "true", "yes")
FOLLOWUP_DAYS = int(os.getenv("COLD_EMAIL_FOLLOWUP_DAYS", "5"))
MAX_FOLLOWUPS = int(os.getenv("COLD_EMAIL_MAX_FOLLOWUPS", "0" if not ENABLE_FOLLOWUPS else "1"))
# Never re-contact a company for this many days after any outreach (initial or follow-up).
COMPANY_COOLDOWN_DAYS = int(os.getenv("COLD_EMAIL_COMPANY_COOLDOWN_DAYS", "180"))
# Minimum quality score (0–100) from cold_email.selection.contact_quality_score
MIN_CONTACT_QUALITY = int(os.getenv("COLD_EMAIL_MIN_QUALITY", "55"))
REQUIRE_NAMED_CONTACT = os.getenv("COLD_EMAIL_REQUIRE_NAMED", "true").lower() in ("1", "true", "yes")
# Never email the same address or company twice in one IST day
MAX_PER_COMPANY_PER_DAY = int(os.getenv("COLD_EMAIL_MAX_PER_COMPANY_PER_DAY", "1"))

# Contacts older than this are skipped unless source is discover:career_portal.
MAX_CONTACT_AGE_DAYS = int(os.getenv("COLD_EMAIL_MAX_CONTACT_AGE_DAYS", "45"))

# LinkedIn-only outreach — reject all career-portal scrapes, HR dumps, inferred patterns.
LINKEDIN_ONLY_MODE = os.getenv("COLD_EMAIL_LINKEDIN_ONLY", "true").lower() in ("1", "true", "yes")
LINKEDIN_VERIFIED_SOURCE_IDS = frozenset(
	{
		"linkedin:verified",
		"linkedin:hunter_verified",
		"linkedin:explorium_verified",
	}
)

# SMTP RCPT verification timeout (seconds) for local email enrichment fallback
SMTP_VERIFY_TIMEOUT_SEC = int(os.getenv("SMTP_VERIFY_TIMEOUT_SEC", "5"))

# Hunter.io — LinkedIn email enrichment (https://hunter.io/api)
HUNTER_API_KEY = os.getenv("HUNTER_API_KEY", "").strip()
HUNTER_MIN_SCORE = int(os.getenv("HUNTER_MIN_SCORE", "85"))

# Explorium AgentSource — recruiter search + contact enrichment (https://developers.explorium.ai)
EXPLORIUM_API_KEY = os.getenv("EXPLORIUM_API_KEY", "").strip()

# Confidence tiers — LinkedIn-only mode accepts verified Hunter enrichments only.
DEFAULT_TIERS = (
	("verified",)
	if LINKEDIN_ONLY_MODE
	else (
		"verified",
		"scraped_personal",
		"public_listed",
	)
)

# Bulk lists with high bounce/stale rates — never cold-email.
STALE_SOURCE_IDS = frozenset(
	{
		"github:careerLauncher",
		"web:substack_atoz_50_hr",
		"web:devblogger_hr_500",
		"inferred:recruiter-emailing-script",
		"discover:career_portal",
		"generated:scout_domain",
		"local:hr_email_csv",
	}
)

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

# Companies opted out of discovery + cold email (normalized keys, e.g. angelone).
EXCLUDED_COMPANY_KEYS = frozenset(
	{
		"angelone",
	}
)
EXCLUDED_EMAIL_DOMAINS = frozenset(
	{
		"angelone.in",
	}
)

RESUME_ATTACHMENT_NAME = os.getenv("COLD_EMAIL_RESUME_FILENAME", "ojas_srivastava_resume.pdf")
RESUME_SOURCE = REPO_ROOT / "Resume Collection" / "ojas_srivastava_google_swe_intern_2027.pdf"
RESUME_PATH = Path(
	os.getenv(
		"COLD_EMAIL_RESUME_PATH",
		str(REPO_ROOT / "Resume Collection" / "ojas_srivastava_resume.pdf"),
	)
)
