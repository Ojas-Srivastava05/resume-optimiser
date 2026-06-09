"""Fetch jobs from Ashby public job board API."""

import json
from pathlib import Path

import requests

from companies import load_companies, match_priority_company
from config import ROOT
from filters import Job, make_job

API = "https://api.ashbyhq.com/posting-api/job-board/{slug}"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; InternshipScout/1.0)"}
CACHE = ROOT / "data" / "ats_cache.json"


def _slugs() -> dict[str, str]:
    slugs: dict[str, str] = {}
    for c in load_companies():
        if c.get("ashby_slug"):
            slugs[c["ashby_slug"]] = c["name"]
    if CACHE.exists():
        data = json.loads(CACHE.read_text())
        for key, info in data.get("ashby", {}).items():
            slugs[info["slug"]] = info["company"]
    return slugs


def fetch_ashby_jobs() -> list[Job]:
    jobs: list[Job] = []
    for slug, company in _slugs().items():
        try:
            resp = requests.get(API.format(slug=slug), headers=HEADERS, timeout=25)
            if resp.status_code != 200:
                continue
            payload = resp.json()
        except (requests.RequestException, json.JSONDecodeError):
            continue

        for item in payload.get("jobs", []):
            title = item.get("title", "")
            loc = (item.get("location") or "")
            if isinstance(loc, dict):
                loc = loc.get("name", "")
            url = item.get("jobUrl") or item.get("applyUrl") or ""
            if not match_priority_company(company):
                continue
            job = make_job(title, company, str(loc), url, "Ashby", board_company=company)
            if job:
                jobs.append(job)

    return jobs
