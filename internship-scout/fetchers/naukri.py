"""Naukri.com — major Indian job board, public listing scraper."""

import re
from urllib.parse import urljoin, quote

import requests
from bs4 import BeautifulSoup

from companies import match_priority_company
from config import COMPANY_BATCH_SIZE
from fetchers.parallel import map_parallel
from filters import Job, make_job
from logger import log
from rotation import rotated_names

BASE = "https://www.naukri.com"
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

# Naukri search URLs for intern positions
BROAD_SEARCH_URLS = [
    "/software-intern-jobs",
    "/sde-intern-jobs",
    "/software-engineering-intern-jobs",
    "/machine-learning-intern-jobs",
    "/data-science-intern-jobs",
    "/backend-developer-intern-jobs",
    "/full-stack-intern-jobs",
    "/python-developer-intern-jobs",
    "/software-developer-intern-jobs",
    "/java-developer-intern-jobs",
]

NAUKRI_INTERN_HINT = re.compile(
    r"\b(intern|trainee|campus|graduate|fresher)\b", re.I,
)


def _scrape_listing(path: str) -> list[dict]:
    """Scrape a Naukri listing page for job cards."""
    url = urljoin(BASE, path)
    items: list[dict] = []
    try:
        resp = SESSION.get(url, timeout=15)
        if resp.status_code != 200:
            return items
        soup = BeautifulSoup(resp.text, "html.parser")
    except requests.RequestException:
        return items

    # Naukri uses various card selectors
    for card in soup.select(".srp-jobtuple-wrapper, .jobTuple, article.jobTuple"):
        try:
            title_el = card.select_one(
                "a.title, .title .row1 a, .info h2 a, a.title-href"
            )
            company_el = card.select_one(
                "a.subTitle, .comp-name, .comp-dtls-wrap .companyInfo a, span.comp-name"
            )
            loc_el = card.select_one(
                ".locWdth, .loc-wrap .locWdth, span.loc, .location .locWdth"
            )
            exp_el = card.select_one(".exp-wrap .expwdth, span.expwdth, .exp")

            title = title_el.get_text(strip=True) if title_el else ""
            company = company_el.get_text(strip=True) if company_el else ""
            location = loc_el.get_text(strip=True) if loc_el else "India"
            href = ""
            if title_el and title_el.get("href"):
                href = title_el["href"]
                if not href.startswith("http"):
                    href = urljoin(BASE, href)

            # Filter for entry-level / intern
            exp_text = exp_el.get_text(strip=True) if exp_el else ""
            is_entry = bool(
                NAUKRI_INTERN_HINT.search(title)
                or "0-" in exp_text
                or "fresher" in exp_text.lower()
            )

            if title and company and href and is_entry:
                items.append({
                    "title": title,
                    "company": company,
                    "location": location,
                    "url": href,
                })
        except (AttributeError, TypeError):
            continue
    return items


def _fetch_broad(path: str) -> list[Job]:
    """Fetch from a broad search path, filtering to priority companies."""
    jobs: list[Job] = []
    items = _scrape_listing(path)
    for item in items:
        if not match_priority_company(item["company"]):
            continue
        job = make_job(
            item["title"],
            item["company"],
            item["location"],
            item["url"],
            "Naukri",
            india_platform=True,
            assume_intern=True,
        )
        if job:
            jobs.append(job)
    return jobs


def _fetch_company(name: str) -> list[Job]:
    """Search Naukri for intern roles at a specific company."""
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    path = f"/{slug}-intern-jobs"
    return _fetch_broad(path)


def fetch_naukri_jobs() -> list[Job]:
    """Scrape Naukri for tech internships at priority companies."""
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
        log(f"Naukri {label}: +{n} priority matches")

    log(f"Naukri broad scan: {len(BROAD_SEARCH_URLS)} search pages")
    add(map_parallel(BROAD_SEARCH_URLS, _fetch_broad, label="naukri-broad"), "broad")

    # Company-specific rotation
    limit = min(40, COMPANY_BATCH_SIZE)
    names = rotated_names(limit)
    log(f"Naukri company rotation: {len(names)} firms")
    add(map_parallel(names, _fetch_company, label="naukri-co"), "rotation")

    log(f"Naukri total unique: {len(out)}")
    return out
