#!/usr/bin/env python3
"""Build priority_companies.json from the referral Google Sheet."""

import csv
import io
import json
import re
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT_PATH = ROOT / "data" / "priority_companies.json"
CACHE_GLOB = "sheet_*.csv"

SHEET_ID = "1L-PwvyVyYnMQZfoFU4nKpUFQoiW02SC6_APS_HuWeQo"
TAB_GIDS = [1037508969, 1280391286, 1384053570, 1863495069, 429470176, 773987803, 885057618]
MAIN_GID = 285269648

SKIP_RE = re.compile(r"^sample\s*-|^company$", re.I)
GH_RE = re.compile(r"greenhouse\.io/([^/?\s]+)", re.I)
LEVER_RE = re.compile(r"jobs\.lever\.co/([^/?\s]+)", re.I)
ASHBY_RE = re.compile(r"ashbyhq\.com/([^/?\s]+)", re.I)


def _norm_key(name: str) -> str:
    return re.sub(r"[^a-z0-9]", "", name.lower())


def _merge_row(merged: dict, row: dict) -> None:
    name = (row.get("Company") or "").strip()
    if not name or SKIP_RE.search(name):
        return

    key = _norm_key(name)
    portal = (row.get("Career Portal") or "").strip()
    sector = (row.get("Sector") or "").strip()
    entry = merged.setdefault(
        key,
        {
            "name": name,
            "portal": portal,
            "sector": sector,
            "gh_slug": None,
            "lever_slug": None,
            "ashby_slug": None,
        },
    )
    if portal and len(portal) > len(entry.get("portal") or ""):
        entry["portal"] = portal
    if sector and not entry.get("sector"):
        entry["sector"] = sector

    gh = GH_RE.search(portal)
    if gh:
        entry["gh_slug"] = gh.group(1)
    lev = LEVER_RE.search(portal)
    if lev:
        entry["lever_slug"] = lev.group(1)
    ash = ASHBY_RE.search(portal)
    if ash:
        entry["ashby_slug"] = ash.group(1)


def _from_cached_csvs() -> dict[str, dict]:
    merged: dict[str, dict] = {}
    for path in sorted(ROOT.glob(CACHE_GLOB)):
        if str(MAIN_GID) in path.name:
            continue
        with path.open(encoding="utf-8") as f:
            for row in csv.DictReader(f):
                _merge_row(merged, row)
    return merged


def _from_remote() -> dict[str, dict]:
    merged: dict[str, dict] = {}
    for gid in TAB_GIDS:
        url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={gid}"
        req = urllib.request.Request(url, headers={"User-Agent": "InternshipScout/1.0"})
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                text = resp.read().decode("utf-8", errors="replace")
        except OSError as exc:
            print(f"Warning: could not fetch gid {gid}: {exc}")
            continue
        for row in csv.DictReader(io.StringIO(text)):
            _merge_row(merged, row)
        # refresh local cache
        (ROOT / f"sheet_{gid}.csv").write_text(text)
    return merged


def sync() -> dict:
    merged = _from_remote()
    if not merged:
        print("Remote sync failed — using cached sheet_*.csv files")
        merged = _from_cached_csvs()

    if not merged:
        raise RuntimeError(
            "No priority companies found. Open the Google Sheet once or add sheet_*.csv caches."
        )

    companies = sorted(merged.values(), key=lambda c: c["name"].lower())
    payload = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "source_sheet": f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit",
        "count": len(companies),
        "companies": companies,
    }
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(payload, indent=2))
    print(f"Saved {len(companies)} priority companies → {OUT_PATH}")
    return payload


if __name__ == "__main__":
    sync()
