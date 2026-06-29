"""Fetch intern roles from SmartRecruiters public API."""

from __future__ import annotations

import re

import requests

from companies import load_companies
from filters import Job, make_job
from logger import log
from portal_resolver import collect_smartrecruiters_slugs

API = "https://api.smartrecruiters.com/v1/companies/{slug}/postings"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; InternshipScout/1.0)"}
SESSION = requests.Session()
SESSION.headers.update(HEADERS)


def _location_text(location: dict) -> str:
    if not isinstance(location, dict):
        return ""
    parts = [
        location.get("fullLocation"),
        location.get("city"),
        location.get("region"),
        location.get("country"),
    ]
    return ", ".join(p for p in parts if p)


def _india_posting(location: dict) -> bool:
    if not isinstance(location, dict):
        return False
    country = str(location.get("country") or "").lower()
    if country in {"in", "ind", "india"}:
        return True
    blob = _location_text(location)
    return bool(re.search(r"\bindia\b|bangalore|bengaluru|hyderabad|mumbai|pune|gurgaon|noida|chennai", blob, re.I))


def _fetch_slug(company: str, slug: str) -> list[Job]:
    jobs: list[Job] = []
    seen_urls: set[str] = set()
    for query in ("intern", "internship", "campus"):
        offset = 0
        limit = 100
        pages = 0
        while pages < 2:
            try:
                resp = SESSION.get(
                    API.format(slug=slug),
                    params={"limit": limit, "offset": offset, "q": query},
                    timeout=20,
                )
                if resp.status_code != 200:
                    break
                payload = resp.json()
            except requests.RequestException:
                break

            content = payload.get("content") or []
            if not content:
                break

            for item in content:
                title = item.get("name", "")
                location = item.get("location") or {}
                if not _india_posting(location):
                    continue
                loc = _location_text(location)
                ref = item.get("refNumber") or item.get("id") or ""
                url = item.get("postingUrl") or item.get("applyUrl") or ""
                if not url and ref:
                    url = f"https://careers.smartrecruiters.com/{slug}/{ref}"
                if url in seen_urls:
                    continue
                seen_urls.add(url)
                job = make_job(
                    title,
                    company,
                    loc,
                    url,
                    "SmartRecruiters",
                    board_company=company,
                )
                if job:
                    jobs.append(job)

            offset += limit
            pages += 1
            total = int(payload.get("totalFound") or 0)
            if offset >= total:
                break

    return jobs


def fetch_smartrecruiters_jobs() -> list[Job]:
    companies = load_companies()
    boards = collect_smartrecruiters_slugs(companies)
    log(f"SmartRecruiters: polling {len(boards)} companies (full scan)")
    jobs: list[Job] = []
    for company, slug in boards:
        found = _fetch_slug(company, slug)
        if found:
            log(f"  SmartRecruiters/{slug}: {len(found)} intern matches")
        jobs.extend(found)
    return jobs


def fetch_smartrecruiters_from_html(company: str, html: str) -> list[Job]:
    jobs: list[Job] = []
    seen: set[str] = set()
    for m in re.finditer(r"careers\.smartrecruiters\.com/([^/\"'\s<>]+)", html, re.I):
        slug = m.group(1)
        if slug in seen:
            continue
        seen.add(slug)
        jobs.extend(_fetch_slug(company, slug))
    return jobs
