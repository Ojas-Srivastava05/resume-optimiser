"""Scrape career portals — parallel, rotated batch."""

import re
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from companies import load_companies, match_priority_company
from config import CAREERS_MAX_SCRAPES
from fetchers.parallel import map_parallel
from filters import Job, make_job
from rotation import rotated_names

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
}
INTERN_HINT = re.compile(r"intern|internship|campus|university|graduate", re.I)
TECH_HINT = re.compile(
    r"software|sde|swe|developer|engineer|ml|machine.?learning|\bai\b|data|backend|"
    r"frontend|full.?stack|platform",
    re.I,
)
SKIP_PORTAL = re.compile(r"google\.com/search|careers\.google\.com", re.I)
SESSION = requests.Session()
SESSION.headers.update(HEADERS)


def _valid_portal(url: str) -> bool:
    return bool(url and url.startswith("http") and not SKIP_PORTAL.search(url))


def _from_greenhouse_embed(company: str, slug: str) -> list[Job]:
    jobs: list[Job] = []
    try:
        r = SESSION.get(
            f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs",
            timeout=10,
        )
        if r.status_code != 200:
            return jobs
        for item in r.json().get("jobs", []):
            job = make_job(
                item.get("title", ""),
                company,
                (item.get("location") or {}).get("name", ""),
                item.get("absolute_url", ""),
                "Careers→GH",
                board_company=company,
            )
            if job:
                jobs.append(job)
    except requests.RequestException:
        pass
    return jobs


def _scrape_portal(company: str, portal: str) -> list[Job]:
    jobs: list[Job] = []
    try:
        resp = SESSION.get(portal, timeout=10, allow_redirects=True)
        if resp.status_code != 200:
            return jobs
        soup = BeautifulSoup(resp.text, "html.parser")
    except requests.RequestException:
        return jobs

    seen: set[str] = set()
    for a in soup.find_all("a", href=True):
        text = a.get_text(" ", strip=True)
        href = urljoin(resp.url, a["href"])
        if href in seen:
            continue
        blob = f"{text} {href}"
        if not INTERN_HINT.search(blob) or not TECH_HINT.search(blob):
            continue
        seen.add(href)
        job = make_job(
            text[:120] if text else "Internship opening",
            company,
            "India",
            href,
            "Careers Web",
            india_platform=True,
        )
        if job:
            jobs.append(job)

    for m in re.finditer(
        r"https?://(?:boards\.greenhouse\.io|job-boards\.greenhouse\.io)/([^/\"'\s]+)",
        resp.text,
    ):
        jobs.extend(_from_greenhouse_embed(company, m.group(1)))
    return jobs


def _scrape_company(name: str) -> list[Job]:
    entry = match_priority_company(name)
    if not entry or not _valid_portal(entry.get("portal", "")):
        return []
    return _scrape_portal(entry["name"], entry["portal"])


def fetch_careers_jobs() -> list[Job]:
    names = rotated_names(CAREERS_MAX_SCRAPES)
    return map_parallel(names, _scrape_company, label="careers")
