"""Configuration — SAP job scout (separate from internship scout)."""

import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")


def _getenv(key: str, default: str = "") -> str:
    """Read env var; treat unset or blank as default (CI secrets may be empty)."""
    raw = os.getenv(key)
    if raw is None:
        return default
    raw = raw.strip()
    return raw if raw else default


# Primary: Ananya's email from resume
SAP_RECIPIENT_EMAIL = _getenv("SAP_RECIPIENT_EMAIL", "ananyasrivas34@gmail.com")
# Monitor copy: Ojas gets the same digest to confirm sends
SAP_MONITOR_EMAIL = _getenv("SAP_MONITOR_EMAIL", _getenv("RECIPIENT_EMAIL", "srivastavaojas454@gmail.com"))
# Extra inboxes that always get the same digest (comma-separated override via env)
_DEFAULT_EXTRA = "anshmali1964@gmail.com"
SAP_EXTRA_RECIPIENTS = [
    addr.strip()
    for addr in _getenv("SAP_EXTRA_RECIPIENTS", _DEFAULT_EXTRA).split(",")
    if addr.strip()
]

SMTP_EMAIL = _getenv("SMTP_EMAIL", SAP_MONITOR_EMAIL)
SMTP_APP_PASSWORD = _getenv("SMTP_APP_PASSWORD", "").replace(" ", "")

ADZUNA_APP_ID = _getenv("ADZUNA_APP_ID", "")
ADZUNA_APP_KEY = _getenv("ADZUNA_APP_KEY", "")

DATA = ROOT / "data"
COMPANIES_CSV = DATA / "sap_companies.csv"
SEEN_PATH = DATA / "sap_job_scout_seen.json"

MAX_EMAIL_SENDS = int(_getenv("SAP_MAX_EMAIL_SENDS", "2") or "2")
COMPANY_BATCH_SIZE = int(_getenv("SAP_COMPANY_BATCH_SIZE", "50") or "50")
FETCH_WORKERS = int(_getenv("SAP_FETCH_WORKERS", "12") or "12")
