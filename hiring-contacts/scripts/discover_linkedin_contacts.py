#!/usr/bin/env python3
"""
LinkedIn-first contact discovery — find recruiters on LinkedIn, verify email locally.

Pipeline per scout company:
  1. Public web search → LinkedIn /in/ recruiter profiles
  2. Web cross-check + SMTP RCPT verification (no API keys)
  3. MX check → incremental_hq_contacts.csv → merge_master()

Usage:
  python scripts/discover_linkedin_contacts.py
  python scripts/discover_linkedin_contacts.py --batch-size 8
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from cold_email.company_domain import norm_company, resolve_company_domain  # noqa: E402
from cold_email.email_enrichment import enrich_from_linkedin  # noqa: E402
from cold_email.exclusions import is_company_excluded  # noqa: E402
from cold_email.explorium import explorium_configured, find_company_recruiters as find_explorium_recruiters  # noqa: E402
from cold_email.hunter import find_company_recruiters, hunter_configured  # noqa: E402
from cold_email.linkedin_search import find_recruiter_profiles  # noqa: E402
from config import SCOUT_COMPANIES_CSV, TARGET_INTERNSHIP_YEAR, TARGET_SEASON  # noqa: E402
from scripts.merge_master import INCREMENTAL_CSV, MASTER_CSV, _read_csv, merge_master  # noqa: E402

DATA = ROOT / "data"
STATE_PATH = DATA / "linkedin_discovery_state.json"

DEFAULT_BATCH = 20
PROBE_COOLDOWN_DAYS = 14
PROFILE_DELAY_SEC = 1.5
LINKEDIN_SOURCE_VERIFIED = "linkedin:verified"


def now_iso() -> str:
	return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load_state() -> dict:
	if STATE_PATH.exists():
		return json.loads(STATE_PATH.read_text(encoding="utf-8"))
	return {
		"rotation_index": 0,
		"probed": {},
		"stats": {"total_runs": 0, "total_profiles_found": 0, "total_emails_verified": 0},
	}


def save_state(state: dict) -> None:
	STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
	STATE_PATH.write_text(json.dumps(state, indent=2), encoding="utf-8")


def load_scout_companies() -> list[dict]:
	rows: list[dict] = []
	if not SCOUT_COMPANIES_CSV.exists():
		return rows
	with SCOUT_COMPANIES_CSV.open(encoding="utf-8") as f:
		for row in csv.DictReader(f):
			name = (row.get("Company") or "").strip()
			portal = (row.get("Career Portal") or "").strip()
			if name:
				rows.append({"name": name, "portal": portal, "key": norm_company(name)})
	return rows


def linkedin_contacts_by_company() -> dict[str, set[str]]:
	by_co: dict[str, set[str]] = {}
	if not MASTER_CSV.exists():
		return by_co
	with MASTER_CSV.open(encoding="utf-8") as f:
		for row in csv.DictReader(f):
			if not (row.get("source_id") or "").startswith("linkedin:"):
				continue
			co = norm_company(row.get("company") or "")
			email = (row.get("email") or "").strip().lower()
			if co and email:
				by_co.setdefault(co, set()).add(email)
	return by_co


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


def _row_from_explorium_recruiter(
	recruiter,
	*,
	company: str,
	company_key: str,
	fetched_at: str,
) -> dict:
	name = f"{recruiter.first_name} {recruiter.last_name}".strip()
	return {
		"email": recruiter.email,
		"name": name,
		"company": company,
		"company_normalized": company_key,
		"role_title": recruiter.position or "Recruiter",
		"contact_type": "recruiter",
		"confidence": "verified",
		"in_scout_list": "True",
		"source_id": "linkedin:explorium_verified",
		"source_url": recruiter.linkedin_url,
		"country": "India",
		"target_internship_year": str(TARGET_INTERNSHIP_YEAR),
		"target_season": TARGET_SEASON,
		"notes": (
			f"linkedin_profile={recruiter.linkedin_url};explorium_email_status={recruiter.email_status};"
			f"explorium_prospect_id={recruiter.prospect_id};explorium_fetch;mx_ok"
		),
		"fetched_at": fetched_at,
	}


def _row_from_hunter_recruiter(
	recruiter,
	*,
	company: str,
	company_key: str,
	fetched_at: str,
) -> dict:
	name = f"{recruiter.first_name} {recruiter.last_name}".strip()
	return {
		"email": recruiter.email,
		"name": name,
		"company": company,
		"company_normalized": company_key,
		"role_title": recruiter.position or "Recruiter",
		"contact_type": "recruiter",
		"confidence": "verified",
		"in_scout_list": "True",
		"source_id": "linkedin:hunter_verified",
		"source_url": recruiter.linkedin_url,
		"country": "India",
		"target_internship_year": str(TARGET_INTERNSHIP_YEAR),
		"target_season": TARGET_SEASON,
		"notes": (
			f"linkedin_profile={recruiter.linkedin_url};hunter_score={recruiter.score};"
			f"hunter_status={recruiter.status};hunter_domain_search;mx_ok"
		),
		"fetched_at": fetched_at,
	}


def enrich_profile(
	profile,
	*,
	company: str,
	company_key: str,
	domain: str,
	fetched_at: str,
) -> dict | None:
	enriched = enrich_from_linkedin(
		linkedin_url=profile.url,
		full_name=profile.name,
		company=company,
		domain=domain,
	)
	if not enriched:
		print(f"    no verified email for {profile.name}")
		return None

	display_name = f"{enriched.first_name} {enriched.last_name}".strip()
	if enriched.verification == "hunter":
		notes = (
			f"linkedin_profile={profile.url};hunter_score={enriched.confidence};"
			f"hunter_status=valid;mx_ok"
		)
	else:
		notes = (
			f"linkedin_profile={profile.url};verification={enriched.verification};"
			f"confidence={enriched.confidence};mx_ok"
		)
	return {
		"email": enriched.email,
		"name": display_name,
		"company": company,
		"company_normalized": company_key,
		"role_title": profile.title or "Recruiter",
		"contact_type": "recruiter",
		"confidence": "verified",
		"in_scout_list": "True",
		"source_id": enriched.source_id,
		"source_url": profile.url,
		"country": "India",
		"target_internship_year": str(TARGET_INTERNSHIP_YEAR),
		"target_season": TARGET_SEASON,
		"notes": notes,
		"fetched_at": fetched_at,
	}


def discover_company_row(company: str, portal: str, *, fetched_at: str) -> list[dict]:
	key = norm_company(company)
	domain = resolve_company_domain(company, portal)
	print(f"    domain={domain or '(unresolved — skipping)'}")
	if not domain:
		return []
	rows: list[dict] = []
	seen_emails: set[str] = set()
	max_per_company = 3

	if explorium_configured():
		try:
			explorium_rows = find_explorium_recruiters(
				company=company,
				domain=domain,
				limit=max_per_company,
			)
			print(f"    explorium HR: {len(explorium_rows)} recruiter(s)")
			for rec in explorium_rows:
				if rec.email in seen_emails:
					continue
				seen_emails.add(rec.email)
				row = _row_from_explorium_recruiter(
					rec, company=company, company_key=key, fetched_at=fetched_at
				)
				rows.append(row)
				print(f"      ✓ {rec.email} | {rec.linkedin_url} (explorium {rec.email_status})")
		except Exception as exc:
			print(f"    explorium warn: {exc}")

	if len(rows) < max_per_company and hunter_configured():
		try:
			hunter_rows = find_company_recruiters(domain, company=company, limit=10)
			print(f"    hunter domain HR: {len(hunter_rows)} recruiter(s)")
			for rec in hunter_rows[: max_per_company - len(rows)]:
				if rec.email in seen_emails:
					continue
				seen_emails.add(rec.email)
				row = _row_from_hunter_recruiter(rec, company=company, company_key=key, fetched_at=fetched_at)
				rows.append(row)
				print(f"      ✓ {rec.email} | {rec.linkedin_url} (hunter q={rec.score})")
		except Exception as exc:
			print(f"    hunter domain search warn: {exc}")

	if len(rows) >= max_per_company:
		return rows

	# Slow web+SMTP fallback only when no enrichment APIs are configured
	if explorium_configured() or hunter_configured():
		return rows

	profiles = find_recruiter_profiles(company, max_profiles=2)
	print(f"    linkedin web profiles: {len(profiles)}")
	for profile in profiles:
		if len(rows) >= 2:
			break
		print(f"    → {profile.name} | {profile.url}")
		row = enrich_profile(
			profile,
			company=company,
			company_key=key,
			domain=domain,
			fetched_at=fetched_at,
		)
		if row and row["email"] not in seen_emails:
			seen_emails.add(row["email"])
			rows.append(row)
			print(f"      ✓ {row['email']} ({row['notes']})")
		time.sleep(PROFILE_DELAY_SEC)
	return rows


def main() -> int:
	parser = argparse.ArgumentParser(description="LinkedIn recruiter discovery (no API keys)")
	parser.add_argument("--batch-size", type=int, default=DEFAULT_BATCH)
	parser.add_argument("--company", default="", help="Probe one company by name")
	args = parser.parse_args()

	fetched_at = now_iso()
	state = load_state()
	companies = load_scout_companies()
	li_map = linkedin_contacts_by_company()
	probed = state.get("probed", {})

	if not companies:
		print("No scout companies found.")
		return 0

	cooldown_before = datetime.now(timezone.utc) - timedelta(days=PROBE_COOLDOWN_DAYS)
	idx = int(state.get("rotation_index", 0)) % len(companies)
	probed_this_run = 0
	attempts = 0
	max_attempts = len(companies) * 2
	discovered_rows: list[dict] = []

	target_filter = norm_company(args.company) if args.company else ""

	while probed_this_run < args.batch_size and attempts < max_attempts:
		co = companies[idx % len(companies)]
		idx += 1
		attempts += 1
		key = co["key"]
		name = co["name"]

		if target_filter and key != target_filter:
			continue

		if is_company_excluded(name):
			probed[key] = fetched_at
			continue

		last = probed.get(key)
		if last and not target_filter:
			try:
				if datetime.fromisoformat(last) > cooldown_before:
					continue
			except ValueError:
				pass

		if len(li_map.get(key, set())) >= 2 and not target_filter:
			probed[key] = fetched_at
			continue

		probed_this_run += 1
		print(f"  linkedin [{probed_this_run}/{args.batch_size}] {name}")
		try:
			rows = discover_company_row(name, co["portal"], fetched_at=fetched_at)
		except Exception as exc:
			print(f"  warn: failed for {name}: {exc}")
			rows = []
		probed[key] = fetched_at
		if rows:
			discovered_rows.extend(rows)
			for r in rows:
				li_map.setdefault(key, set()).add(r["email"])

	state["rotation_index"] = idx % len(companies)
	state["probed"] = probed
	state["stats"]["total_runs"] = state["stats"].get("total_runs", 0) + 1
	state["stats"]["last_run_at"] = fetched_at
	state["stats"]["last_batch_profiles"] = len(discovered_rows)
	state["stats"]["total_emails_verified"] = state["stats"].get("total_emails_verified", 0) + len(
		discovered_rows
	)
	save_state(state)

	append_incremental(discovered_rows)
	merge_master()
	import subprocess

	subprocess.run([sys.executable, str(ROOT / "scripts" / "purge_inauthentic_contacts.py")], check=False)
	total = len(_read_csv(MASTER_CSV))
	newly_merged = len(discovered_rows)
	print(
		f"\nLinkedIn discover done: probed={probed_this_run}, verified={len(discovered_rows)}, "
		f"newly_merged={newly_merged}, total={total}"
	)
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
