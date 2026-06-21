"""Unstop — broad sector searches (every run) + parallel rotated company batch."""

from urllib.parse import urljoin

import requests

from companies import match_priority_company
from config import COMPANY_BATCH_SIZE, UNSTOP_MAX_COMPANIES
from fetchers.parallel import map_parallel
from filters import Job, make_job
from logger import log
from rotation import rotated_names

BASE = "https://unstop.com"
API = f"{BASE}/api/public/opportunity/search-result"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; InternshipScout/1.0)"}
SESSION = requests.Session()
SESSION.headers.update(HEADERS)

# Full-scan every run — catches new postings regardless of company rotation
BROAD_QUERIES = [
    "software engineering intern",
    "SDE intern",
    "machine learning intern",
    "fintech intern",
    "backend intern",
    "full stack intern",
    "data science intern",
    "AI intern",
    "python developer intern",
    "java developer intern",
    "cloud computing intern",
    "devops intern",
    "quant intern",
    "software developer intern",
]


def _search(query: str) -> list[dict]:
    params = {
        "opportunity": "internships",
        "page": 1,
        "per_page": 20,
        "searchTerm": query,
    }
    resp = SESSION.get(API, params=params, timeout=12)
    resp.raise_for_status()
    return (resp.json().get("data") or {}).get("data") or []


def _parse_item(item: dict) -> Job | None:
    title = item.get("title") or item.get("name") or ""
    org = item.get("organisation") or item.get("organization") or {}
    company = org.get("name", "") if isinstance(org, dict) else str(org)
    if not match_priority_company(company):
        return None

    locs = item.get("locations") or []
    if locs and isinstance(locs, list):
        region = ", ".join(
            str(x.get("city") or x.get("name") or x) if isinstance(x, dict) else str(x)
            for x in locs[:3]
        )
    else:
        region = item.get("region") or "India"
    if str(region).lower() in {"online", "remote"}:
        region = "India (remote)"

    path = item.get("public_url") or ""
    url = urljoin(BASE + "/", path.lstrip("/")) if path and not path.startswith("http") else path
    return make_job(title, company, str(region), url, "Unstop", india_platform=True)


def _fetch_query(query: str) -> list[Job]:
    try:
        items = _search(query)
    except requests.RequestException as exc:
        log(f"Unstop broad query failed '{query}': {exc}")
        return []
    jobs = [_parse_item(i) for i in items]
    return [j for j in jobs if j]


def _fetch_company(name: str) -> list[Job]:
    return _fetch_query(f"{name} software intern")


def fetch_unstop_jobs() -> list[Job]:
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
        log(f"Unstop {label}: +{n} matches ({len(jobs)} raw)")

    log(f"Unstop broad scan: {len(BROAD_QUERIES)} sector queries (full coverage)")
    add(map_parallel(BROAD_QUERIES, _fetch_query, label="unstop-broad"), "broad-total")

    limit = min(UNSTOP_MAX_COMPANIES, COMPANY_BATCH_SIZE)
    names = rotated_names(limit)
    log(f"Unstop company rotation: {len(names)} firms today")
    add(map_parallel(names, _fetch_company, label="unstop-co"), "rotation-total")

    log(f"Unstop total unique: {len(out)}")
    return out
