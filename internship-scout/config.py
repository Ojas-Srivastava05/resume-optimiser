"""Configuration for internship scout."""

import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env")

def _getenv(key: str, default: str = "") -> str:
    """Treat unset or blank env (e.g. empty CI secret) as default."""
    raw = os.getenv(key)
    if raw is None:
        return default
    raw = raw.strip()
    return raw if raw else default


RECIPIENT_EMAIL = _getenv("RECIPIENT_EMAIL", "srivastavaojas454@gmail.com")
SMTP_EMAIL = _getenv("SMTP_EMAIL", RECIPIENT_EMAIL)
SMTP_APP_PASSWORD = _getenv("SMTP_APP_PASSWORD", "").replace(" ", "")
# Extra digests every run (comma-separated). Default: Vansh + Jatin.
_DEFAULT_EXTRA = "rawatvans94@gmail.com,jatinnigam2118@gmail.com"
EXTRA_RECIPIENTS = [
    addr.strip()
    for addr in _getenv("EXTRA_RECIPIENTS", _DEFAULT_EXTRA).split(",")
    if addr.strip()
]
ADZUNA_APP_ID = _getenv("ADZUNA_APP_ID", "")
ADZUNA_APP_KEY = _getenv("ADZUNA_APP_KEY", "")

SEEN_JOBS_PATH = ROOT / "seen_jobs.json"
GRAD_BATCH_YEAR = os.getenv("GRAD_BATCH_YEAR", "2028")

# Google Sheet — refreshed via sync_companies.py
PRIORITY_SHEET_ID = os.getenv(
    "PRIORITY_SHEET_ID",
    "1L-PwvyVyYnMQZfoFU4nKpUFQoiW02SC6_APS_HuWeQo",
)

MAX_EMAIL_SENDS = int(os.getenv("MAX_EMAIL_SENDS", "2"))

# Rotated sources: LinkedIn/Unstop/Naukri use COMPANY_BATCH_SIZE.
# Career portals: CAREERS_MAX_SCRAPES<=0 queues the full roster and stops on CAREERS_TIME_BUDGET_SEC.
# Full-scan sources (every run): Greenhouse, Lever, Ashby, Workday, SmartRecruiters, Oracle CX, LinkedIn broad, Unstop broad
COMPANY_BATCH_SIZE = int(os.getenv("COMPANY_BATCH_SIZE", "120"))
FETCH_WORKERS = int(os.getenv("FETCH_WORKERS", "16"))
UNSTOP_MAX_COMPANIES = int(os.getenv("UNSTOP_MAX_COMPANIES", "80"))
LINKEDIN_MAX_COMPANIES = int(os.getenv("LINKEDIN_MAX_COMPANIES", "80"))
# 0 = queue every company; time budget decides how many finish this run
CAREERS_MAX_SCRAPES = int(os.getenv("CAREERS_MAX_SCRAPES", "0"))
# Wall-clock cap for portal scraping (required when CAREERS_MAX_SCRAPES=0)
CAREERS_TIME_BUDGET_SEC = int(os.getenv("CAREERS_TIME_BUDGET_SEC", "0"))
CAREERS_MAX_URLS_PER_COMPANY = int(os.getenv("CAREERS_MAX_URLS_PER_COMPANY", "0"))
CAREERS_HTTP_TIMEOUT = int(os.getenv("CAREERS_HTTP_TIMEOUT", "12"))
CAREERS_INFER_PLACEHOLDERS = os.getenv("CAREERS_INFER_PLACEHOLDERS", "1").lower() in {
    "1",
    "true",
    "yes",
}
ORACLE_PROBE_PER_RUN = int(os.getenv("ORACLE_PROBE_PER_RUN", "40"))
ATS_PROBE_PER_RUN = int(os.getenv("ATS_PROBE_PER_RUN", "20"))
FAST_MODE = os.getenv("FAST_MODE", "").lower() in {"1", "true", "yes"}

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
