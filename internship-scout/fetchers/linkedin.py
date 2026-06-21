"""LinkedIn guest search — broad queries + parallel rotated company batch."""

import re
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from companies import match_priority_company
from config import COMPANY_BATCH_SIZE, LINKEDIN_MAX_COMPANIES
from fetchers.parallel import map_parallel
from filters import Job, make_job
from logger import log
from rotation import rotated_names

BASE = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}
SESSION = requests.Session()
SESSION.headers.update(HEADERS)

LINKEDIN_INTERN_HINT = re.compile(
    r"\b(intern|university|campus|co-?op|trainee|apprentice|graduate)\b",
    re.I,
)

BROAD_QUERIES = [
    # Core SWE intern searches
    "software engineer intern 2028 India",
    "SDE intern India",
    "software developer intern India",
    "software engineering internship India 2028",
    # ML / AI / Data
    "machine learning intern India",
    "data science intern India",
    "AI intern India",
    "deep learning intern India",
    # Domain-specific
    "fintech intern India",
    "quant developer intern India",
    "backend developer intern India",
    "frontend developer intern India",
    "full stack developer intern India",
    "cloud engineer intern India",
    "devops intern India",
    "platform engineer intern India",
    # Campus / graduate
    "campus intern software India",
    "graduate engineer trainee software India",
    # Additional phrasing variants
    "software intern Bangalore",
    "software intern Hyderabad",
    "software intern Pune",
    "software intern Gurgaon",
]


def _search(query: str, start: int = 0) -> str:
    params = {"keywords": query, "location": "India", "start": start, "f_E": 1}
    resp = SESSION.get(BASE, params=params, timeout=12)
    resp.raise_for_status()
    return resp.text


def _parse_cards(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    jobs: list[dict] = []
    for card in soup.select(".base-search-card"):
        link_el = card.select_one("a.base-card__full-link")
        if not link_el:
            continue
        title_el = (
            card.select_one(".base-search-card__title")
            or card.select_one("h3")
            or card.select_one(".sr-only")
        )
        company_el = card.select_one(".base-search-card__subtitle") or card.select_one("h4")
        loc_el = card.select_one(".job-search-card__location")
        title = title_el.get_text(strip=True) if title_el else ""
        company = company_el.get_text(strip=True) if company_el else ""
        location = loc_el.get_text(strip=True) if loc_el else "India"
        url = link_el.get("href", "")
        if url and not url.startswith("http"):
            url = urljoin("https://www.linkedin.com", url)
        if title and company:
            jobs.append({"title": title, "company": company, "location": location, "url": url})
    return jobs


def _card_to_job(card: dict) -> Job | None:
    return make_job(
        card["title"],
        card["company"],
        card["location"],
        card["url"],
        "LinkedIn",
        india_platform=True,
        assume_intern=bool(LINKEDIN_INTERN_HINT.search(card["title"])),
    )


def _fetch_query(query: str) -> list[Job]:
    jobs: list[Job] = []
    for start in (0, 25):
        try:
            cards = _parse_cards(_search(query, start=start))
        except requests.RequestException:
            break
        if not cards:
            break
        for card in cards:
            if not match_priority_company(card["company"]):
                continue
            job = _card_to_job(card)
            if job:
                jobs.append(job)
    return jobs


def _fetch_company(name: str) -> list[Job]:
    return _fetch_query(f"{name} software intern")


def fetch_linkedin_jobs() -> list[Job]:
    seen: set[str] = set()
    out: list[Job] = []

    def add(jobs: list[Job], label: str) -> None:
        n = 0
        for job in jobs:
            if job.url in seen:
                continue
            seen.add(job.url)
            out.append(job)
            n += 1
        log(f"LinkedIn {label}: +{n} priority matches")

    log(f"LinkedIn broad scan: {len(BROAD_QUERIES)} queries (full coverage)")
    add(map_parallel(BROAD_QUERIES, _fetch_query, label="linkedin-broad"), "broad")

    limit = min(LINKEDIN_MAX_COMPANIES, COMPANY_BATCH_SIZE)
    names = rotated_names(limit)
    log(f"LinkedIn company rotation: {len(names)} firms")
    add(map_parallel(names, _fetch_company, label="linkedin-co"), "rotation")

    log(f"LinkedIn total unique: {len(out)}")
    return out
