#!/usr/bin/env python3
"""Merge referral-sheet companies + curated similar companies → JSON + CSV."""

import csv
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from data.curated_bulk import CURATED_BULK
from data.curated_similar import CURATED_ADDITIONS

ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "data" / "priority_companies.json"
CSV_PATH = ROOT / "data" / "all_companies.csv"


def _norm(name: str) -> str:
    return re.sub(r"[^a-z0-9]", "", (name or "").lower())


def _fuzzy_exists(name: str, keys: set[str]) -> bool:
    n = _norm(name)
    if n in keys:
        return True
    for k in keys:
        if n == k:
            return True
        if (n.startswith(k) or k.startswith(n)) and abs(len(n) - len(k)) <= 8:
            return True
    return False


def expand() -> dict:
    existing: list[dict] = []
    if JSON_PATH.exists():
        existing = json.loads(JSON_PATH.read_text()).get("companies", [])

    keys = {_norm(c["name"]) for c in existing}
    added = 0
    merged = []
    for c in existing:
        row = dict(c)
        row.setdefault("source", "referral_sheet")
        merged.append(row)

    all_curated = list(CURATED_ADDITIONS) + list(CURATED_BULK)
    for name, sector, portal in all_curated:
        if _fuzzy_exists(name, keys):
            continue
        entry = {
            "name": name,
            "portal": portal,
            "sector": sector,
            "gh_slug": None,
            "lever_slug": None,
            "ashby_slug": None,
            "source": "curated_expansion",
            "added_at": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        }
        merged.append(entry)
        keys.add(_norm(name))
        added += 1

    merged.sort(key=lambda c: c["name"].lower())
    payload = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "source_sheet": "https://docs.google.com/spreadsheets/d/1L-PwvyVyYnMQZfoFU4nKpUFQoiW02SC6_APS_HuWeQo/edit",
        "count": len(merged),
        "original_count": len(existing),
        "curated_added": added,
        "companies": merged,
    }

    JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
    JSON_PATH.write_text(json.dumps(payload, indent=2))

    with CSV_PATH.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "Company",
                "Career Portal",
                "Sector",
                "Source",
                "GH Slug",
                "Lever Slug",
                "Ashby Slug",
                "Added At",
            ],
        )
        writer.writeheader()
        for c in merged:
            writer.writerow(
                {
                    "Company": c["name"],
                    "Career Portal": c.get("portal", ""),
                    "Sector": c.get("sector", ""),
                    "Source": c.get("source", "referral_sheet"),
                    "GH Slug": c.get("gh_slug") or "",
                    "Lever Slug": c.get("lever_slug") or "",
                    "Ashby Slug": c.get("ashby_slug") or "",
                    "Added At": c.get("added_at", ""),
                }
            )

    print(f"Total companies: {len(merged)} ({added} curated additions appended)")
    print(f"JSON → {JSON_PATH}")
    print(f"CSV  → {CSV_PATH}")
    return payload


if __name__ == "__main__":
    expand()
