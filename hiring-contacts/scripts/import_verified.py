#!/usr/bin/env python3
"""Append manually verified contacts (e.g. from bounce auto-replies) into the discovery pipeline."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scripts.extract import norm_company  # noqa: E402
from scripts.merge_master import INCREMENTAL_CSV, merge_master  # noqa: E402

BLOCKLIST = ROOT / "data" / "blocklist.json"


def now_iso() -> str:
	return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def rows_from_blocklist_replacements() -> list[dict]:
	if not BLOCKLIST.exists():
		return []
	data = json.loads(BLOCKLIST.read_text(encoding="utf-8"))
	fetched_at = now_iso()
	rows: list[dict] = []
	for _old, emails in (data.get("replacements") or {}).items():
		for email in emails:
			domain = email.split("@", 1)[1]
			company = domain.split(".", 1)[0].title()
			if "cerebras" in domain:
				company = "Cerebras"
			rows.append(
				{
					"email": email.lower(),
					"name": "",
					"company": company,
					"company_normalized": norm_company(company),
					"role_title": "Recruiting (bounce redirect)",
					"contact_type": "recruiter",
					"confidence": "verified",
					"in_scout_list": "True",
					"source_id": "manual:verified",
					"source_url": "bounce_auto_reply",
					"country": "India",
					"target_internship_year": "2027",
					"target_season": "Summer 2027",
					"notes": "replacement_from_bounce",
					"fetched_at": fetched_at,
				}
			)
	return rows


def append_rows(rows: list[dict]) -> int:
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
	parser.add_argument("--from-blocklist", action="store_true", help="Import replacement emails from blocklist.json")
	args = parser.parse_args()

	rows: list[dict] = []
	if args.from_blocklist:
		rows.extend(rows_from_blocklist_replacements())

	if not rows:
		print("No rows to import.")
		return 0

	added = append_rows(rows)
	total, newly_merged = merge_master()
	print(f"Imported {added} row(s); newly_merged={newly_merged}, total={total}")
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
