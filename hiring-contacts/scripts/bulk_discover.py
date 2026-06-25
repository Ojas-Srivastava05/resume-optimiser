#!/usr/bin/env python3
"""
Bulk internet contact harvest — probe every scout company career portal.

Uses multi-page scraping + MX-validated domain fallbacks (only when scrape is empty).

Usage:
  python scripts/bulk_discover.py                  # all companies, no cooldown
  python scripts/bulk_discover.py --limit 200      # first 200 not yet fully probed
  python scripts/bulk_discover.py --delay 1.0
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from cold_email.discovery import discover_company  # noqa: E402
from config import SCOUT_COMPANIES_CSV  # noqa: E402
from scripts.extract import norm_company  # noqa: E402
from scripts.merge_master import INCREMENTAL_CSV, merge_master  # noqa: E402

DATA = ROOT / "data"
STATE_PATH = DATA / "bulk_discover_state.json"
MASTER_CSV = DATA / "merged" / "master_contacts.csv"


def now_iso() -> str:
	return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load_companies() -> list[dict]:
	rows: list[dict] = []
	with SCOUT_COMPANIES_CSV.open(encoding="utf-8") as f:
		for row in csv.DictReader(f):
			name = (row.get("Company") or "").strip()
			portal = (row.get("Career Portal") or "").strip()
			if name:
				rows.append({"name": name, "portal": portal, "key": norm_company(name)})
	return rows


def load_state() -> dict:
	if STATE_PATH.exists():
		return json.loads(STATE_PATH.read_text(encoding="utf-8"))
	return {"completed": {}, "stats": {}}


def save_state(state: dict) -> None:
	STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
	STATE_PATH.write_text(json.dumps(state, indent=2), encoding="utf-8")


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
	parser.add_argument("--limit", type=int, default=0, help="Max companies (0 = all)")
	parser.add_argument("--delay", type=float, default=0.25, help="Seconds between companies")
	parser.add_argument("--resume", action="store_true", help="Skip companies completed in prior bulk run")
	args = parser.parse_args()

	companies = load_companies()
	state = load_state()
	completed = state.get("completed", {})
	fetched_at = now_iso()
	all_rows: list[dict] = []
	probed = 0
	scraped_live = 0
	fallback_only = 0

	for co in companies:
		if args.limit and probed >= args.limit:
			break
		key = co["key"]
		if args.resume and completed.get(key):
			continue

		probed += 1
		name = co["name"]
		portal = co["portal"]
		print(f"  [{probed}] {name}", flush=True)
		rows = discover_company(name, portal, fetched_at)
		live = sum(1 for r in rows if r.get("notes") == "career_portal_scrape")
		scraped_live += live
		if rows and live == 0:
			fallback_only += 1
		if rows:
			all_rows.extend(rows)
		completed[key] = {"at": fetched_at, "found": len(rows), "live": live}
		state["completed"] = completed
		if probed % 25 == 0:
			append_incremental(all_rows)
			merge_master()
			all_rows = []
			save_state(state)
		time.sleep(args.delay)

	append_incremental(all_rows)
	total, newly_merged = merge_master()

	state["completed"] = completed
	state["stats"] = {
		"last_run_at": fetched_at,
		"companies_probed": probed,
		"emails_found": len(all_rows) + sum(
			int(v.get("found", 0)) for v in completed.values() if isinstance(v, dict)
		),
		"live_scraped_emails": scraped_live,
		"fallback_only_companies": fallback_only,
		"newly_merged": newly_merged,
		"total_contacts": total,
	}
	save_state(state)

	print(
		f"\nBulk discover done: companies={probed}, live_scrape_emails={scraped_live}, "
		f"mx_fallback_only_cos={fallback_only}, newly_merged={newly_merged}, total={total}"
	)
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
