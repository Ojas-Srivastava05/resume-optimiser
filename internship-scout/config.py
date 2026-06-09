"""Configuration for internship scout."""

import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env")

RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL", "srivastavaojas454@gmail.com")
SMTP_EMAIL = os.getenv("SMTP_EMAIL", RECIPIENT_EMAIL)
SMTP_APP_PASSWORD = os.getenv("SMTP_APP_PASSWORD", "").replace(" ", "")
ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID", "")
ADZUNA_APP_KEY = os.getenv("ADZUNA_APP_KEY", "")

SEEN_JOBS_PATH = ROOT / "seen_jobs.json"
GRAD_BATCH_YEAR = os.getenv("GRAD_BATCH_YEAR", "2028")

# Google Sheet — refreshed via sync_companies.py
PRIORITY_SHEET_ID = os.getenv(
    "PRIORITY_SHEET_ID",
    "1L-PwvyVyYnMQZfoFU4nKpUFQoiW02SC6_APS_HuWeQo",
)

MAX_EMAIL_SENDS = int(os.getenv("MAX_EMAIL_SENDS", "2"))

# Rotated sources: 120 companies/day × 8 days ≈ full 964-company coverage
# Full-scan sources (every run): Greenhouse, Lever, Ashby, LinkedIn broad, Unstop broad
COMPANY_BATCH_SIZE = int(os.getenv("COMPANY_BATCH_SIZE", "120"))
FETCH_WORKERS = int(os.getenv("FETCH_WORKERS", "16"))
UNSTOP_MAX_COMPANIES = int(os.getenv("UNSTOP_MAX_COMPANIES", "80"))
LINKEDIN_MAX_COMPANIES = int(os.getenv("LINKEDIN_MAX_COMPANIES", "80"))
CAREERS_MAX_SCRAPES = int(os.getenv("CAREERS_MAX_SCRAPES", "30"))
ATS_PROBE_PER_RUN = int(os.getenv("ATS_PROBE_PER_RUN", "20"))
FAST_MODE = os.getenv("FAST_MODE", "").lower() in {"1", "true", "yes"}

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
