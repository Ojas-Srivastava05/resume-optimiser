#!/usr/bin/env python3
"""
Import HR email lists (HREmailData.csv, HREmails.csv) into master_contacts.

Only keeps emails that:
  - Match an Internship Scout company by email domain
  - Look hiring-related (HR inbox or named person at company domain)
  - Pass MX validation on the email domain

Usage:
  python scripts/import_hr_csv.py
  python scripts/import_hr_csv.py --dry-run
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from cold_email.config import BLOCKED_LOCAL_PARTS  # noqa: E402
from cold_email.discovery import company_domain, contact_row  # noqa: E402
from cold_email.mx_check import has_mx_record, warm_mx_cache  # noqa: E402
from config import SCOUT_COMPANIES_CSV  # noqa: E402
from scripts.extract import clean_email, norm_company  # noqa: E402
from scripts.merge_master import INCREMENTAL_CSV, merge_master  # noqa: E402

DATA = ROOT / "data"
HR_CSV_FILES = (DATA / "HREmailData.csv", DATA / "HREmails.csv")

HIRING_LOCAL_RE = re.compile(
	r"(recruit|talent|career|campus|university|hr|hiring|intern|people|jobs|"
	r"freshers|resume|resumes|emerging|graduate|staffing|acquisition)",
	re.I,
)

SKIP_DOMAIN_RE = re.compile(
	r"(\.edu$|\.ac\.|uaeu\.ac\.|student\.|school\.|k12\.)",
	re.I,
)

FREEMAIL = frozenset(
	{
		"gmail.com",
		"yahoo.com",
		"hotmail.com",
		"outlook.com",
		"icloud.com",
		"qq.com",
		"comcast.net",
		"mail.com",
		"rediffmail.com",
		"ymail.com",
	}
)


def now_iso() -> str:
	return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def build_scout_domain_map() -> dict[str, str]:
	"""email domain (or parent) -> scout company display name."""
	domain_to_name: dict[str, str] = {}
	with SCOUT_COMPANIES_CSV.open(encoding="utf-8") as f:
		for row in csv.DictReader(f):
			name = (row.get("Company") or "").strip()
			portal = (row.get("Career Portal") or "").strip()
			if not name:
				continue
			domain = company_domain(name, portal)
			if not domain:
				continue
			domain = domain.lower()
			domain_to_name[domain] = name
			parts = domain.split(".")
			if len(parts) >= 2:
				domain_to_name[".".join(parts[-2:])] = name
	return domain_to_name


def load_raw_emails() -> set[str]:
	emails: set[str] = set()
	for path in HR_CSV_FILES:
		if not path.exists():
			print(f"  skip missing {path.name}")
			continue
		with path.open(encoding="utf-8-sig") as f:
			reader = csv.DictReader(f)
			field = reader.fieldnames[0] if reader.fieldnames else "Email"
			for row in reader:
				raw = row.get(field) or row.get("Email") or ""
				email = clean_email(raw.strip())
				if email:
					emails.add(email)
		print(f"  loaded {path.name}")
	return emails


def match_company(email: str, domain_to_name: dict[str, str]) -> str:
	domain = email.split("@", 1)[1].lower()
	if domain in domain_to_name:
		return domain_to_name[domain]
	for d, name in domain_to_name.items():
		if domain == d or domain.endswith("." + d):
			return name
	return ""


def is_hiring_email(email: str) -> bool:
	local = email.split("@", 1)[0].lower()
	domain = email.split("@", 1)[1].lower()
	if SKIP_DOMAIN_RE.search(domain):
		return False
	if any(part in local for part in BLOCKED_LOCAL_PARTS):
		return False
	if domain in FREEMAIL:
		return bool(HIRING_LOCAL_RE.search(local))
	if HIRING_LOCAL_RE.search(local):
		return True
	return "." in local and len(local) > 3


def classify(email: str) -> tuple[str, str]:
	local = email.split("@", 1)[0].lower()
	domain = email.split("@", 1)[1].lower()
	if domain in FREEMAIL:
		return "recruiter", "scraped_personal"
	if HIRING_LOCAL_RE.search(local) and local not in {"info", "office", "contact"}:
		if "." in local or "_" in local:
			return "hr_inbox", "public_listed"
		return "hr_inbox", "public_listed"
	return "recruiter", "scraped_personal"


def collect_rows(emails: set[str], domain_to_name: dict[str, str], fetched_at: str) -> list[dict]:
	candidates: list[tuple[str, str]] = []
	for email in sorted(emails):
		company = match_company(email, domain_to_name)
		if not company or not is_hiring_email(email):
			continue
		candidates.append((email, company))

	warm_mx_cache({e.split("@", 1)[1] for e, _ in candidates})

	rows: list[dict] = []
	for email, company in candidates:
		if not has_mx_record(email.split("@", 1)[1]):
			continue
		ctype, conf = classify(email)
		rows.append(
			contact_row(
				email,
				company,
				conf,
				ctype,
				"local:hr_email_csv",
				fetched_at,
				"hr_csv_scout_domain_match",
				source_id="local:hr_email_csv",
			)
		)
	return rows


def append_incremental(rows: list[dict]) -> int:
	if not rows:
		return 0
	INCREMENTAL_CSV.parent.mkdir(parents=True, exist_ok=True)
	exists = INCREMENTAL_CSV.exists()
	fieldnames = list(rows[0].keys())
	with INCREMENTAL_CSV.open("a", encoding="utf-8", newline="") as f:
		w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
		if not exists:
			w.writeheader()
		w.writerows(rows)
	return len(rows)


def main() -> int:
	parser = argparse.ArgumentParser()
	parser.add_argument("--dry-run", action="store_true")
	args = parser.parse_args()

	fetched_at = now_iso()
	domain_to_name = build_scout_domain_map()
	raw = load_raw_emails()
	print(f"Raw unique emails: {len(raw)}")

	rows = collect_rows(raw, domain_to_name, fetched_at)
	named = sum(1 for r in rows if r.get("confidence") == "scraped_personal")
	inboxes = len(rows) - named
	print(f"Scout-matched + MX-valid: {len(rows)} ({named} named, {inboxes} inboxes)")

	if args.dry_run:
		for r in rows[:15]:
			print(f"  {r['email']} @ {r['company']} ({r['confidence']})")
		return 0

	added = append_incremental(rows)
	total, newly_merged = merge_master()
	print(f"Import done: appended={added}, newly_merged={newly_merged}, total={total}")
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
