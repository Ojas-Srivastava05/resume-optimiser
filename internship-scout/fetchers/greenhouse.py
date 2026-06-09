"""Fetch intern roles from ALL Greenhouse boards — full scan every run."""

import requests

from companies import greenhouse_slugs
from filters import Job, make_job
from logger import log

API = "https://boards-api.greenhouse.io/v1/boards/{slug}/jobs"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; InternshipScout/1.0)"}


def fetch_greenhouse_jobs() -> list[Job]:
    slugs = greenhouse_slugs()
    log(f"Greenhouse: polling {len(slugs)} boards (full scan)")
    jobs: list[Job] = []
    ok_boards = 0

    for slug, board_name in slugs.items():
        try:
            resp = requests.get(API.format(slug=slug), headers=HEADERS, timeout=20)
            if resp.status_code != 200:
                continue
            ok_boards += 1
            payload = resp.json()
        except requests.RequestException:
            continue

        board_hits = 0
        for item in payload.get("jobs", []):
            job = make_job(
                item.get("title", ""),
                board_name,
                (item.get("location") or {}).get("name", ""),
                item.get("absolute_url", ""),
                "Greenhouse",
                board_company=board_name,
            )
            if job:
                jobs.append(job)
                board_hits += 1
        if board_hits:
            log(f"  Greenhouse/{slug}: {board_hits} intern matches")

    log(f"Greenhouse: {ok_boards}/{len(slugs)} boards responded, {len(jobs)} total matches")
    return jobs
