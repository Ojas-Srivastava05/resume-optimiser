"""Fetch intern roles from Workday career portals (CX public API)."""

from __future__ import annotations

import re

import requests

from companies import load_companies
from filters import Job, make_job
from logger import log
from portal_resolver import WorkdayBoard, collect_workday_boards, parse_workday

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; InternshipScout/1.0)",
    "Content-Type": "application/json",
    "Accept": "application/json",
}
SESSION = requests.Session()
SESSION.headers.update(HEADERS)

INTERN_QUERIES = ("intern india", "internship india", "software intern india", "campus india")


def _fetch_board(company: str, board: WorkdayBoard) -> list[Job]:
    jobs: list[Job] = []
    seen_urls: set[str] = set()
    for query in INTERN_QUERIES:
        offset = 0
        limit = 50
        pages = 0
        while pages < 2:
            try:
                resp = SESSION.post(
                    board.jobs_api,
                    json={
                        "appliedFacets": {},
                        "limit": limit,
                        "offset": offset,
                        "searchText": query,
                    },
                    timeout=20,
                )
                if resp.status_code != 200:
                    break
                payload = resp.json()
            except requests.RequestException:
                break

            postings = payload.get("jobPostings") or []
            if not postings:
                break

            for item in postings:
                title = item.get("title", "")
                loc = item.get("locationsText", "")
                path = item.get("externalPath", "")
                url = f"{board.public_root}{path}" if path else board.public_root
                if url in seen_urls:
                    continue
                seen_urls.add(url)
                job = make_job(
                    title,
                    company,
                    loc,
                    url,
                    "Workday",
                    board_company=company,
                )
                if job:
                    jobs.append(job)

            offset += limit
            pages += 1
            total = int(payload.get("total") or 0)
            if offset >= total:
                break

    return jobs


def fetch_workday_jobs() -> list[Job]:
    companies = load_companies()
    boards = collect_workday_boards(companies)
    log(f"Workday: polling {len(boards)} boards (full scan)")
    jobs: list[Job] = []
    for company, board in boards:
        found = _fetch_board(company, board)
        if found:
            log(f"  Workday/{board.tenant}/{board.site}: {len(found)} intern matches")
        jobs.extend(found)
    return jobs


def fetch_workday_from_html(company: str, html: str) -> list[Job]:
    """Discover embedded Workday boards while scraping generic portals."""
    jobs: list[Job] = []
    seen: set[str] = set()
    for m in re.finditer(
        r"https?://([^.]+)\.wd(\d+)\.myworkdayjobs\.com/([^/\"'\s<>]+)",
        html,
        re.I,
    ):
        url = m.group(0)
        board = parse_workday(url)
        if not board or board.key in seen:
            continue
        seen.add(board.key)
        jobs.extend(_fetch_board(company, board))
    return jobs
