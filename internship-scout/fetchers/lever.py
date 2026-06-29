"""Fetch intern roles from Lever for priority companies."""

import json

import requests

from companies import load_companies
from config import ROOT
from filters import Job, make_job

API = "https://api.lever.co/v0/postings/{slug}?mode=json"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; InternshipScout/1.0)"}
CACHE = ROOT / "data" / "ats_cache.json"


def _slugs() -> dict[str, str]:
    slugs: dict[str, str] = {}
    for c in load_companies():
        if c.get("lever_slug"):
            slugs[c["lever_slug"]] = c["name"]
    if CACHE.exists():
        data = json.loads(CACHE.read_text())
        for info in data.get("lever", {}).values():
            slugs[info["slug"]] = info["company"]
    slugs.setdefault("cred", "CRED")
    return slugs


def fetch_lever_jobs() -> list[Job]:
    jobs: list[Job] = []
    for slug, company in _slugs().items():
        try:
            resp = requests.get(API.format(slug=slug), headers=HEADERS, timeout=25)
            if resp.status_code != 200:
                continue
            postings = resp.json()
        except requests.RequestException:
            continue

        if not isinstance(postings, list):
            continue

        for item in postings:
            title = item.get("text", "")
            loc = item.get("categories", {}).get("location", "")
            url = item.get("hostedUrl", "")
            job = make_job(
                title,
                company,
                loc,
                url,
                "Lever",
                board_company=company,
            )
            if job:
                jobs.append(job)

    return jobs
