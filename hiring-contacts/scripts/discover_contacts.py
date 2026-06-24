#!/usr/bin/env python3
"""
Incremental discovery — grow high-quality contacts over time without re-probing everything.

Each run:
  1. Rotates through Internship Scout companies missing HQ contacts
  2. Fetches career portal HTML and extracts hiring-related emails
  3. Appends to data/raw/incremental_hq_contacts.csv
  4. Merges into master_contacts.csv

Usage:
  python scripts/discover_contacts.py
  python scripts/discover_contacts.py --batch-size 60
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import time
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from config import COMPANY_DOMAIN_OVERRIDES, SCOUT_COMPANIES_CSV, TARGET_INTERNSHIP_YEAR, TARGET_SEASON  # noqa: E402
from scripts.extract import (  # noqa: E402
	classify_contact,
	clean_email,
	domain_from_url,
	extract_emails_from_text,
	norm_company,
)
from scripts.merge_master import HQ_CONFIDENCE, INCREMENTAL_CSV, merge_master  # noqa: E402

DATA = ROOT / "data"
STATE_PATH = DATA / "discovery_state.json"
MASTER_CSV = DATA / "merged" / "master_contacts.csv"

USER_AGENT = "HiringContactsDiscover/1.0 (+resume-optimiser)"
DEFAULT_BATCH = 50
PROBE_COOLDOWN_DAYS = 21
FETCH_DELAY_SEC = 2.0
MAX_HTML_BYTES = 500_000

HIRING_LOCAL_RE = re.compile(
	r"(recruit|talent|career|campus|university|hr|hiring|intern|people|jobs|acquisition)",
	re.I,
)


def now_iso() -> str:
	return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load_state() -> dict:
	if STATE_PATH.exists():
		return json.loads(STATE_PATH.read_text(encoding="utf-8"))
	return {
		"rotation_index": 0,
		"probed": {},  # company_key -> iso timestamp
		"stats": {"total_runs": 0, "total_discovered": 0},
	}


def save_state(state: dict) -> None:
	STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
	STATE_PATH.write_text(json.dumps(state, indent=2), encoding="utf-8")


def load_scout_companies() -> list[dict]:
	rows: list[dict] = []
	with SCOUT_COMPANIES_CSV.open(encoding="utf-8") as f:
		for row in csv.DictReader(f):
			name = (row.get("Company") or "").strip()
			portal = (row.get("Career Portal") or "").strip()
			if name:
				rows.append({"name": name, "portal": portal, "key": norm_company(name)})
	return rows


def hq_emails_by_company() -> dict[str, set[str]]:
	by_co: dict[str, set[str]] = {}
	if not MASTER_CSV.exists():
		return by_co
	with MASTER_CSV.open(encoding="utf-8") as f:
		for row in csv.DictReader(f):
			if row.get("confidence") not in HQ_CONFIDENCE:
				continue
			co = norm_company(row.get("company") or "")
			email = (row.get("email") or "").strip().lower()
			if co and email:
				by_co.setdefault(co, set()).add(email)
	return by_co


def _is_hiring_email(email: str) -> bool:
	local = email.split("@", 1)[0]
	if HIRING_LOCAL_RE.search(local):
		return True
	# named person at company domain (not freemail)
	domain = email.split("@", 1)[1]
	if domain in {"gmail.com", "yahoo.com", "hotmail.com", "outlook.com"}:
		return False
	return "." in local and len(local) > 3


def fetch_portal_text(url: str) -> str:
	if not url or not url.startswith("http"):
		return ""
	req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
	try:
		with urllib.request.urlopen(req, timeout=25) as resp:
			data = resp.read(MAX_HTML_BYTES)
		return data.decode("utf-8", errors="replace")
	except OSError as exc:
		print(f"    skip fetch: {exc}")
		return ""


def discover_from_portal(company: str, portal: str, fetched_at: str) -> list[dict]:
	rows: list[dict] = []
	text = fetch_portal_text(portal)
	if not text:
		# Fallback: official hiring inboxes from known domain
		key = norm_company(company)
		domain = COMPANY_DOMAIN_OVERRIDES.get(key) or domain_from_url(portal)
		if domain:
			for prefix in ("careers", "talent", "campus", "university"):
				email = clean_email(f"{prefix}@{domain}")
				if email:
					ctype, conf = classify_contact(email)
					rows.append(_row(email, company, conf, ctype, portal, fetched_at, f"domain_fallback:{prefix}"))
		return rows

	seen: set[str] = set()
	for email in extract_emails_from_text(text):
		if email in seen or not _is_hiring_email(email):
			continue
		seen.add(email)
		ctype, conf = classify_contact(email)
		if conf == "generic":
			conf = "public_listed"
		rows.append(_row(email, company, conf, ctype, portal, fetched_at, "career_portal_scrape"))
	return rows


def _row(
	email: str,
	company: str,
	confidence: str,
	contact_type: str,
	portal: str,
	fetched_at: str,
	notes: str,
) -> dict:
	return {
		"email": email,
		"name": "",
		"company": company,
		"company_normalized": norm_company(company),
		"role_title": "",
		"contact_type": contact_type,
		"confidence": confidence,
		"in_scout_list": "True",
		"source_id": "discover:career_portal",
		"source_url": portal,
		"country": "India",
		"target_internship_year": str(TARGET_INTERNSHIP_YEAR),
		"target_season": TARGET_SEASON,
		"notes": notes,
		"fetched_at": fetched_at,
	}


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
	parser.add_argument("--batch-size", type=int, default=DEFAULT_BATCH)
	args = parser.parse_args()

	fetched_at = now_iso()
	state = load_state()
	companies = load_scout_companies()
	hq_map = hq_emails_by_company()
	probed = state.get("probed", {})

	if not companies:
		print("No scout companies found.")
		return 1

	cooldown_before = datetime.now(timezone.utc) - timedelta(days=PROBE_COOLDOWN_DAYS)
	idx = int(state.get("rotation_index", 0)) % len(companies)
	probed_this_run = 0
	attempts = 0
	max_attempts = len(companies) * 2
	discovered_rows: list[dict] = []

	while probed_this_run < args.batch_size and attempts < max_attempts:
		co = companies[idx % len(companies)]
		idx += 1
		attempts += 1
		key = co["key"]
		name = co["name"]

		last = probed.get(key)
		if last:
			try:
				if datetime.fromisoformat(last) > cooldown_before:
					continue
			except ValueError:
				pass

		if len(hq_map.get(key, set())) >= 2:
			probed[key] = fetched_at
			continue

		probed_this_run += 1
		print(f"  probe [{probed_this_run}/{args.batch_size}] {name}")
		rows = discover_from_portal(name, co["portal"], fetched_at)
		probed[key] = fetched_at
		if rows:
			discovered_rows.extend(rows)
			for r in rows:
				hq_map.setdefault(key, set()).add(r["email"])
		time.sleep(FETCH_DELAY_SEC)

	state["rotation_index"] = idx % len(companies)
	state["probed"] = probed
	state["stats"]["total_runs"] = state["stats"].get("total_runs", 0) + 1
	state["stats"]["last_run_at"] = fetched_at
	state["stats"]["last_batch_discovered"] = len(discovered_rows)

	append_incremental(discovered_rows)
	total, newly_merged = merge_master()

	from scripts.merge_master import _read_csv

	all_rows = _read_csv(MASTER_CSV)
	hq_count = sum(1 for r in all_rows if r.get("confidence") in HQ_CONFIDENCE)
	state["stats"]["total_discovered"] = state["stats"].get("total_discovered", 0) + newly_merged
	state["stats"]["hq_total"] = hq_count
	state["stats"]["total_contacts"] = total
	save_state(state)

	print(
		f"\nDiscover done: probed={probed_this_run}, raw_found={len(discovered_rows)}, "
		f"newly_merged={newly_merged}, total={total}, hq={hq_count}"
	)
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
