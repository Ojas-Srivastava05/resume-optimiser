"""Fetch SAP-relevant jobs from public India job boards."""

from __future__ import annotations

import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import quote, urlencode, urljoin

import requests
from bs4 import BeautifulSoup

from sap_job_scout.companies import company_names, rotated_names
from sap_job_scout.config import ADZUNA_APP_ID, ADZUNA_APP_KEY, COMPANY_BATCH_SIZE, FETCH_WORKERS
from sap_job_scout.filters import dedupe_jobs, make_job
from sap_job_scout.models import SapJob

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}
SESSION = requests.Session()
SESSION.headers.update(HEADERS)

LINKEDIN_BASE = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
NAUKRI_BASE = "https://www.naukri.com"
INDEED_BASE = "https://in.indeed.com"

SAP_QUERIES = [
    "SAP UI5 developer",
    "SAP Fiori developer",
    "SAP UI5 consultant",
    "SAP Fiori consultant",
    "SAP frontend developer",
    "SAP BTP developer",
    "SAP CAP developer",
    "SAP ABAP developer",
    "SAP UI5 Fiori India",
    "SAP OData developer",
    "SAP application developer",
    "SAP technical consultant",
    "SAP UI developer",
    "SAP Fiori application",
    "Packaged application developer SAP",
]

NAUKRI_PATHS = [
    "/sap-ui5-developer-jobs",
    "/sap-fiori-developer-jobs",
    "/sap-abap-developer-jobs",
    "/sap-consultant-jobs",
    "/sap-developer-jobs",
    "/sap-btp-developer-jobs",
    "/sap-technical-consultant-jobs",
    "/sap-fresher-jobs",
    "/sap-jobs-in-bangalore",
    "/sap-jobs-in-hyderabad",
    "/sap-jobs-in-pune",
    "/sap-jobs-in-chennai",
    "/sap-jobs-in-noida",
    "/sap-jobs-in-mumbai",
]

INDEED_QUERIES = [
    "SAP UI5 developer",
    "SAP Fiori developer",
    "SAP ABAP developer",
    "SAP consultant",
    "SAP BTP developer",
    "SAP frontend developer",
    "SAP technical consultant",
    "SAP OData developer",
]


def _parallel(items: list, fn, label: str = "") -> list:
    if not items:
        return []
    out = []
    with ThreadPoolExecutor(max_workers=FETCH_WORKERS) as pool:
        futures = {pool.submit(fn, item): item for item in items}
        for fut in as_completed(futures):
            try:
                result = fut.result()
                if isinstance(result, list):
                    out.extend(result)
            except Exception as exc:
                if label:
                    print(f"[sap-fetch:{label}] skip: {exc}")
    return out


def _linkedin_search(query: str, start: int = 0) -> str:
    params = {"keywords": query, "location": "India", "start": start}
    resp = SESSION.get(LINKEDIN_BASE, params=params, timeout=12)
    resp.raise_for_status()
    return resp.text


def _parse_linkedin(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    cards = []
    for card in soup.select(".base-search-card"):
        link_el = card.select_one("a.base-card__full-link")
        if not link_el:
            continue
        title_el = card.select_one(".base-search-card__title") or card.select_one("h3")
        company_el = card.select_one(".base-search-card__subtitle") or card.select_one("h4")
        loc_el = card.select_one(".job-search-card__location")
        title = title_el.get_text(strip=True) if title_el else ""
        company = company_el.get_text(strip=True) if company_el else ""
        location = loc_el.get_text(strip=True) if loc_el else "India"
        url = link_el.get("href", "")
        if url and not url.startswith("http"):
            url = urljoin("https://www.linkedin.com", url)
        if title and company and url:
            cards.append({"title": title, "company": company, "location": location, "url": url})
    return cards


def _fetch_linkedin_query(query: str) -> list[SapJob]:
    jobs: list[SapJob] = []
    for start in (0, 25):
        try:
            cards = _parse_linkedin(_linkedin_search(query, start))
        except requests.RequestException:
            break
        if not cards:
            break
        for card in cards:
            job = make_job(
                card["title"], card["company"], card["location"], card["url"],
                "LinkedIn", india_platform=True,
            )
            if job:
                jobs.append(job)
    return jobs


def _fetch_linkedin_company(company: str) -> list[SapJob]:
    return _fetch_linkedin_query(f"{company} SAP UI5 Fiori developer")


def fetch_linkedin_jobs() -> list[SapJob]:
    seen: set[str] = set()
    out: list[SapJob] = []
    for job in _parallel(SAP_QUERIES, _fetch_linkedin_query, "linkedin-query"):
        if job.url in seen:
            continue
        seen.add(job.url)
        out.append(job)
    names = rotated_names(COMPANY_BATCH_SIZE)
    for job in _parallel(names, _fetch_linkedin_company, "linkedin-co"):
        if job.url in seen:
            continue
        seen.add(job.url)
        out.append(job)
    print(f"LinkedIn SAP: {len(out)} matches")
    return out


def _scrape_naukri(path: str) -> list[dict]:
    url = urljoin(NAUKRI_BASE, path)
    items: list[dict] = []
    try:
        resp = SESSION.get(url, timeout=15)
        if resp.status_code != 200:
            return items
        soup = BeautifulSoup(resp.text, "html.parser")
    except requests.RequestException:
        return items

    for card in soup.select(".srp-jobtuple-wrapper, .jobTuple, article.jobTuple"):
        title_el = card.select_one("a.title, .title .row1 a, a.title-href")
        company_el = card.select_one("a.subTitle, .comp-name, span.comp-name")
        loc_el = card.select_one(".locWdth, span.loc, .location .locWdth")
        title = title_el.get_text(strip=True) if title_el else ""
        company = company_el.get_text(strip=True) if company_el else ""
        location = loc_el.get_text(strip=True) if loc_el else "India"
        href = title_el.get("href", "") if title_el else ""
        if href and not href.startswith("http"):
            href = urljoin(NAUKRI_BASE, href)
        if title and href:
            items.append({"title": title, "company": company or "Unknown", "location": location, "url": href})
    return items


def _fetch_naukri_path(path: str) -> list[SapJob]:
    jobs: list[SapJob] = []
    for card in _scrape_naukri(path):
        job = make_job(
            card["title"], card["company"], card["location"], card["url"],
            "Naukri", india_platform=True,
        )
        if job:
            jobs.append(job)
    return jobs


def _fetch_naukri_company(company: str) -> list[SapJob]:
    slug = re.sub(r"[^a-z0-9]+", "-", company.lower()).strip("-")
    path = f"/sap-jobs-in-{slug}" if slug else "/sap-developer-jobs"
    jobs = _fetch_naukri_path(path)
    if not jobs:
        # fallback keyword search URL
        q = quote(f"{company} SAP UI5")
        jobs = _fetch_naukri_path(f"/sap-ui5-developer-jobs-in-india?k={q}")
    return jobs


def fetch_naukri_jobs() -> list[SapJob]:
    seen: set[str] = set()
    out: list[SapJob] = []
    for job in _parallel(NAUKRI_PATHS, _fetch_naukri_path, "naukri-path"):
        if job.url in seen:
            continue
        seen.add(job.url)
        out.append(job)
    for job in _parallel(rotated_names(COMPANY_BATCH_SIZE), _fetch_naukri_company, "naukri-co"):
        if job.url in seen:
            continue
        seen.add(job.url)
        out.append(job)
    print(f"Naukri SAP: {len(out)} matches")
    return out


def _indeed_search(query: str, start: int = 0) -> list[dict]:
    params = {"q": query, "l": "India", "start": start, "fromage": 14}
    url = f"{INDEED_BASE}/jobs?{urlencode(params)}"
    items: list[dict] = []
    try:
        resp = SESSION.get(url, timeout=15)
        if resp.status_code != 200:
            return items
        soup = BeautifulSoup(resp.text, "html.parser")
    except requests.RequestException:
        return items

    for card in soup.select(".job_seen_beacon, .resultContent, .jobsearch-ResultsList > li"):
        title_el = card.select_one("h2.jobTitle a, a.jcs-JobTitle, .jobTitle > a")
        company_el = card.select_one("span[data-testid='company-name'], .companyName")
        loc_el = card.select_one("div[data-testid='text-location'], .companyLocation")
        title = title_el.get_text(strip=True) if title_el else ""
        company = company_el.get_text(strip=True) if company_el else ""
        location = loc_el.get_text(strip=True) if loc_el else "India"
        href = title_el.get("href", "") if title_el else ""
        if href and not href.startswith("http"):
            href = urljoin(INDEED_BASE, href)
        if title and href:
            items.append({"title": title, "company": company or "Unknown", "location": location, "url": href})
    return items


def _fetch_indeed_query(query: str) -> list[SapJob]:
    jobs: list[SapJob] = []
    for start in (0, 10):
        cards = _indeed_search(query, start)
        if not cards:
            break
        for card in cards:
            job = make_job(
                card["title"], card["company"], card["location"], card["url"],
                "Indeed", india_platform=True,
            )
            if job:
                jobs.append(job)
    return jobs


def fetch_indeed_jobs() -> list[SapJob]:
    seen: set[str] = set()
    out: list[SapJob] = []
    for job in _parallel(INDEED_QUERIES, _fetch_indeed_query, "indeed"):
        if job.url in seen:
            continue
        seen.add(job.url)
        out.append(job)
    print(f"Indeed SAP: {len(out)} matches")
    return out


def fetch_adzuna_jobs() -> list[SapJob]:
    if not ADZUNA_APP_ID or not ADZUNA_APP_KEY:
        return []
    jobs: list[SapJob] = []
    queries = ["SAP UI5", "SAP Fiori", "SAP ABAP", "SAP consultant"]
    for what in queries:
        params = {
            "app_id": ADZUNA_APP_ID,
            "app_key": ADZUNA_APP_KEY,
            "results_per_page": 50,
            "what": what,
            "where": "india",
        }
        try:
            resp = SESSION.get(
                "https://api.adzuna.com/v1/api/jobs/in/search/1",
                params=params,
                timeout=25,
            )
            if resp.status_code != 200:
                continue
            for item in resp.json().get("results", []):
                job = make_job(
                    item.get("title", ""),
                    (item.get("company") or {}).get("display_name", ""),
                    (item.get("location") or {}).get("display_name", "India"),
                    item.get("redirect_url", ""),
                    "Adzuna",
                    india_platform=True,
                )
                if job:
                    jobs.append(job)
        except requests.RequestException:
            continue
    print(f"Adzuna SAP: {len(jobs)} matches")
    return jobs


def collect_all_jobs() -> list[SapJob]:
    all_jobs: list[SapJob] = []
    for name, fn in (
        ("LinkedIn", fetch_linkedin_jobs),
        ("Naukri", fetch_naukri_jobs),
        ("Indeed", fetch_indeed_jobs),
        ("Adzuna", fetch_adzuna_jobs),
    ):
        try:
            found = fn()
            all_jobs.extend(found)
            print(f"{name}: collected {len(found)}")
        except Exception as exc:
            print(f"{name} FAILED: {exc}")
    return dedupe_jobs(all_jobs)
