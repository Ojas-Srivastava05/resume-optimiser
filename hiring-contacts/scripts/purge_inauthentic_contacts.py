#!/usr/bin/env python3
"""
Remove all unverified / scraped / inferred contacts from the database.

Keeps ONLY linkedin:hunter_verified rows that pass cold_email.authenticity.is_authentic_contact.

Usage:
  python3 scripts/purge_inauthentic_contacts.py
  python3 scripts/purge_inauthentic_contacts.py --dry-run
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from cold_email.authenticity import is_authentic_contact  # noqa: E402
from scripts.merge_master import FIELDS, INCREMENTAL_CSV, MASTER_CSV, MERGED, _write_tiers  # noqa: E402

ARCHIVE = ROOT / "data" / "archive" / "purged_contacts.csv"


def _read_csv(path: Path) -> list[dict]:
	if not path.exists():
		return []
	with path.open(encoding="utf-8") as f:
		return list(csv.DictReader(f))


def _write_csv(path: Path, rows: list[dict]) -> None:
	path.parent.mkdir(parents=True, exist_ok=True)
	with path.open("w", encoding="utf-8", newline="") as f:
		w = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="ignore")
		w.writeheader()
		w.writerows(rows)


def purge_rows(rows: list[dict]) -> tuple[list[dict], list[dict], Counter]:
	kept: list[dict] = []
	removed: list[dict] = []
	reasons: Counter = Counter()
	for row in rows:
		ok, reason = is_authentic_contact(row)
		if ok:
			kept.append(row)
		else:
			removed.append(row)
			reasons[reason] += 1
	return kept, removed, reasons


def main() -> int:
	parser = argparse.ArgumentParser(description="Purge fake/unverified contacts")
	parser.add_argument("--dry-run", action="store_true")
	args = parser.parse_args()

	master_rows = _read_csv(MASTER_CSV)
	inc_rows = _read_csv(INCREMENTAL_CSV)

	kept_master, removed_master, reasons = purge_rows(master_rows)
	kept_inc, removed_inc, inc_reasons = purge_rows(inc_rows)
	reasons.update(inc_reasons)

	report = {
		"purged_at": datetime.now(timezone.utc).isoformat(),
		"master_before": len(master_rows),
		"master_after": len(kept_master),
		"master_removed": len(removed_master),
		"incremental_before": len(inc_rows),
		"incremental_after": len(kept_inc),
		"incremental_removed": len(removed_inc),
		"removal_reasons": dict(reasons.most_common()),
		"kept_emails": [r.get("email") for r in kept_master],
	}

	print(json.dumps(report, indent=2))

	if args.dry_run:
		print("\nDry-run — no files modified.")
		return 0

	# Archive removed rows (audit trail)
	all_removed = removed_master + [r for r in removed_inc if r.get("email") not in {x.get("email") for x in removed_master}]
	if all_removed:
		ARCHIVE.parent.mkdir(parents=True, exist_ok=True)
		exists = ARCHIVE.exists()
		with ARCHIVE.open("a", encoding="utf-8", newline="") as f:
			w = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="ignore")
			if not exists:
				w.writeheader()
			w.writerows(all_removed)

	kept_master.sort(key=lambda r: (r.get("company", ""), r.get("email", "")))
	_write_csv(MASTER_CSV, kept_master)
	_write_csv(INCREMENTAL_CSV, kept_inc)
	_write_tiers(kept_master)

	stats_path = MERGED / "hq_stats.json"
	stats_path.write_text(
		json.dumps(
			{
				"high_quality_contacts": len(kept_master),
				"total_contacts": len(kept_master),
				"authentic_only": True,
				"purged_at": report["purged_at"],
			},
			indent=2,
		)
		+ "\n",
		encoding="utf-8",
	)

	print(f"\nPurged {len(removed_master)} from master, {len(removed_inc)} from incremental.")
	print(f"Authentic contacts remaining: {len(kept_master)}")
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
