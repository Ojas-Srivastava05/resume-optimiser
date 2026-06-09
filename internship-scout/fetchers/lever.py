"""Fetch intern roles from Lever for priority companies."""

import requests

from companies import load_companies, match_priority_company
from filters import Job, make_job

API = "https://api.lever.co/v0/postings/{slug}?mode=json"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; InternshipScout/1.0)"}


def fetch_lever_jobs() -> list[Job]:
    jobs: list[Job] = []
    slugs: dict[str, str] = {}
    for c in load_companies():
        if c.get("lever_slug"):
            slugs[c["lever_slug"]] = c["name"]
    slugs.setdefault("cred", "CRED")

    for slug, company in slugs.items():
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
            if not match_priority_company(company):
                continue
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
