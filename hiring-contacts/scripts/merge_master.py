"""Merge incremental discoveries into master_contacts.csv + tier splits."""

from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MERGED = ROOT / "data" / "merged"
MASTER_CSV = MERGED / "master_contacts.csv"
INCREMENTAL_CSV = ROOT / "data" / "raw" / "incremental_hq_contacts.csv"

FIELDS = [
	"email",
	"name",
	"company",
	"company_normalized",
	"role_title",
	"contact_type",
	"confidence",
	"in_scout_list",
	"source_id",
	"source_url",
	"country",
	"target_internship_year",
	"target_season",
	"notes",
	"fetched_at",
]

CONF_RANK = {
	"verified": 5,
	"public_listed": 4,
	"google_sheet": 4,
	"scraped_personal": 4,
	"scraped": 3,
	"inferred_pattern": 2,
	"generic": 1,
	"generic_inferred": 0,
}

HQ_CONFIDENCE = frozenset(
	{"scraped_personal", "public_listed", "scraped", "inferred_pattern", "verified", "google_sheet"}
)


def _read_csv(path: Path) -> list[dict]:
	if not path.exists():
		return []
	with path.open(encoding="utf-8") as f:
		return list(csv.DictReader(f))


def merge_master(*, extra_rows: list[dict] | None = None) -> tuple[int, int]:
	"""Returns (total_rows, newly_added)."""
	by_email: dict[str, dict] = {}
	for row in _read_csv(MASTER_CSV):
		email = (row.get("email") or "").strip().lower()
		if email:
			by_email[email] = row

	before = len(by_email)
	incoming = list(extra_rows or [])
	incoming.extend(_read_csv(INCREMENTAL_CSV))

	for row in incoming:
		email = (row.get("email") or "").strip().lower()
		if not email:
			continue
		if email not in by_email:
			by_email[email] = row
			continue
		old = by_email[email]
		if CONF_RANK.get(row.get("confidence", ""), 0) > CONF_RANK.get(old.get("confidence", ""), 0):
			by_email[email] = row
		elif CONF_RANK.get(row.get("confidence", ""), 0) == CONF_RANK.get(old.get("confidence", ""), 0):
			if not old.get("company") and row.get("company"):
				by_email[email] = row

	rows = sorted(by_email.values(), key=lambda r: (r.get("confidence", ""), r.get("company", ""), r.get("email", "")))
	MERGED.mkdir(parents=True, exist_ok=True)
	with MASTER_CSV.open("w", encoding="utf-8", newline="") as f:
		w = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="ignore")
		w.writeheader()
		w.writerows(rows)

	_write_tiers(rows)
	return len(rows), len(by_email) - before


def _write_tiers(rows: list[dict]) -> None:
	tiers = {
		"verified_and_public": [r for r in rows if r.get("confidence") in {"verified", "public_listed", "google_sheet"}],
		"named_recruiters": [r for r in rows if r.get("contact_type") == "recruiter" and r.get("name")],
		"personal_scraped": [r for r in rows if r.get("confidence") == "scraped_personal"],
		"inferred_patterns": [r for r in rows if r.get("confidence") == "inferred_pattern"],
		"generic_inboxes": [r for r in rows if r.get("confidence") == "generic_inferred"],
		"scout_overlap": [r for r in rows if str(r.get("in_scout_list")).lower() == "true"],
		"high_quality": [r for r in rows if r.get("confidence") in HQ_CONFIDENCE],
	}
	for name, subset in tiers.items():
		p = MERGED / f"tier_{name}.csv"
		with p.open("w", encoding="utf-8", newline="") as f:
			w = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="ignore")
			w.writeheader()
			w.writerows(subset)

	hq_count = len(tiers["high_quality"])
	(MERGED / "hq_stats.json").write_text(
		json.dumps({"high_quality_contacts": hq_count, "total_contacts": len(rows)}, indent=2) + "\n",
		encoding="utf-8",
	)
