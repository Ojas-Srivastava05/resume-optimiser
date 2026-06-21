#!/usr/bin/env python3
"""Quick health-check for every job + hackathon source (< 120 seconds in fast mode)."""

import os
import sys
from datetime import datetime

os.environ.setdefault("FAST_MODE", "1")
os.environ.setdefault("COMPANY_BATCH_SIZE", "5")
os.environ.setdefault("UNSTOP_MAX_COMPANIES", "5")
os.environ.setdefault("LINKEDIN_MAX_COMPANIES", "5")
os.environ.setdefault("CAREERS_MAX_SCRAPES", "3")
os.environ.setdefault("ATS_PROBE_PER_RUN", "0")

from expand_companies import expand as expand_companies
from fetchers.adzuna import fetch_adzuna_jobs
from fetchers.ashby import fetch_ashby_jobs
from fetchers.careers import fetch_careers_jobs
from fetchers.greenhouse import fetch_greenhouse_jobs
from fetchers.hackathons import fetch_hackathons
from fetchers.indeed import fetch_indeed_jobs
from fetchers.internshala import fetch_internshala_jobs
from fetchers.lever import fetch_lever_jobs
from fetchers.linkedin import _parse_cards, _search, fetch_linkedin_jobs
from fetchers.naukri import fetch_naukri_jobs
from fetchers.unstop import fetch_unstop_jobs


def _ok(name: str, detail: str) -> dict:
    return {"source": name, "status": "OK", "detail": detail}


def _fail(name: str, detail: str) -> dict:
    return {"source": name, "status": "FAIL", "detail": detail}


def main() -> int:
    print(f"Fast source health check @ {datetime.now().isoformat()}\n")
    results = []

    try:
        p = expand_companies()
        results.append(_ok("Company List", f"{p['count']} companies"))
    except Exception as exc:
        results.append(_fail("Company List", str(exc)))

    # --- Internship Sources ---
    for name, fn in [
        ("Greenhouse API", fetch_greenhouse_jobs),
        ("Lever API", fetch_lever_jobs),
        ("Ashby API", fetch_ashby_jobs),
        ("Unstop API", fetch_unstop_jobs),
        ("Careers Scraper", fetch_careers_jobs),
        ("Adzuna API", fetch_adzuna_jobs),
        ("Internshala", fetch_internshala_jobs),
        ("Naukri", fetch_naukri_jobs),
        ("Indeed India", fetch_indeed_jobs),
    ]:
        try:
            n = len(fn())
            results.append(_ok(name, f"{n} matches"))
        except Exception as exc:
            results.append(_fail(name, str(exc)))

    # LinkedIn (special — test search + full fetch)
    try:
        html = _search("SDE intern India")
        cards = _parse_cards(html)
        if not cards:
            results.append(_fail("LinkedIn Guest API", "0 cards parsed"))
        else:
            n = len(fetch_linkedin_jobs())
            results.append(_ok("LinkedIn Guest API", f"parsed {len(cards)} cards, {n} matches"))
    except Exception as exc:
        results.append(_fail("LinkedIn Guest API", str(exc)))

    # --- Hackathon Sources ---
    try:
        hacks = fetch_hackathons()
        results.append(_ok("Hackathon Scout", f"{len(hacks)} elite hackathons"))
    except Exception as exc:
        results.append(_fail("Hackathon Scout", str(exc)))

    failed = sum(1 for r in results if r["status"] == "FAIL")
    print("\n" + "=" * 60)
    for r in results:
        icon = "✓" if r["status"] == "OK" else "✗"
        print(f"{icon} {r['source']}: {r['detail']}")
    print(f"\n{len(results) - failed}/{len(results)} sources healthy")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
