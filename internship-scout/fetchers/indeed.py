"""Indeed India — public job listing scraper for internships."""

import re
from urllib.parse import urlencode, urljoin

import requests
from bs4 import BeautifulSoup

from companies import match_priority_company
from fetchers.parallel import map_parallel
from filters import Job, make_job
from logger import log

BASE = "https://in.indeed.com"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}
SESSION = requests.Session()
SESSION.headers.update(HEADERS)

BROAD_QUERIES = [
    "software engineer intern",
    "SDE intern",
    "software developer intern",
    "machine learning intern",
    "data science intern",
    "full stack developer intern",
    "backend developer intern",
    "python developer intern",
]


def _search(query: str, start: int = 0) -> list[dict]:
    """Scrape one Indeed search results page."""
    params = {"q": query, "l": "India", "start": start, "fromage": 14}
    url = f"{BASE}/jobs?{urlencode(params)}"
    items: list[dict] = []
    try:
        resp = SESSION.get(url, timeout=15)
        if resp.status_code != 200:
            return items
        soup = BeautifulSoup(resp.text, "html.parser")
    except requests.RequestException:
        return items

    # Indeed cards use various selectors
    for card in soup.select(".job_seen_beacon, .resultContent, .jobsearch-ResultsList > li"):
        try:
            title_el = card.select_one(
                "h2.jobTitle a, a.jcs-JobTitle, .jobTitle > a, h2 a span[title]"
            )
            company_el = card.select_one(
                "span.css-1x7wu6e, span[data-testid='company-name'], .companyName, .company"
            )
            loc_el = card.select_one(
                "div[data-testid='text-location'], .companyLocation, .location"
            )

            # Handle Indeed's nested title spans
            title = ""
            if title_el:
                title_span = title_el.select_one("span[title]")
                if title_span:
                    title = title_span.get("title", "") or title_span.get_text(strip=True)
                else:
                    title = title_el.get_text(strip=True)

            company = company_el.get_text(strip=True) if company_el else ""
            location = loc_el.get_text(strip=True) if loc_el else "India"

            # Build URL
            href = ""
            if title_el:
                href_raw = title_el.get("href", "")
                if href_raw:
                    href = urljoin(BASE, href_raw) if not href_raw.startswith("http") else href_raw
                # Sometimes Indeed uses data-jk attribute
                jk = title_el.get("data-jk", "") or card.get("data-jk", "")
                if not href and jk:
                    href = f"{BASE}/viewjob?jk={jk}"

            if title and company and href:
                items.append({
                    "title": title,
                    "company": company,
                    "location": location,
                    "url": href,
                })
        except (AttributeError, TypeError):
            continue
    return items


def _fetch_query(query: str) -> list[Job]:
    """Search one query across first 2 pages, filter to priority companies."""
    jobs: list[Job] = []
    for start in (0, 10):
        items = _search(query, start=start)
        if not items:
            break
        for item in items:
            if not match_priority_company(item["company"]):
                continue
            job = make_job(
                item["title"],
                item["company"],
                item["location"],
                item["url"],
                "Indeed",
                india_platform=True,
                assume_intern=True,
            )
            if job:
                jobs.append(job)
    return jobs


def fetch_indeed_jobs() -> list[Job]:
    """Scrape Indeed India for tech internships at priority companies."""
    seen: set[str] = set()
    out: list[Job] = []

    log(f"Indeed broad scan: {len(BROAD_QUERIES)} queries")
    results = map_parallel(BROAD_QUERIES, _fetch_query, label="indeed-broad")
    for job in results:
        if job.url in seen:
            continue
        seen.add(job.url)
        out.append(job)

    log(f"Indeed total unique: {len(out)}")
    return out
