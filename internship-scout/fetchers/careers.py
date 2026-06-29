"""Scrape career portals — ATS routing, JSON-LD, rotated full-company coverage."""

from __future__ import annotations

import json
import re
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from companies import match_priority_company
from config import CAREERS_INFER_PLACEHOLDERS, CAREERS_MAX_SCRAPES
from fetchers.ashby import fetch_ashby_jobs_for_slug
from fetchers.oracle_cx import fetch_oracle_from_html
from fetchers.parallel import map_parallel
from fetchers.smartrecruiters import fetch_smartrecruiters_from_html
from fetchers.workday import fetch_workday_from_html
from filters import Job, make_job
from portal_resolver import (
    PortalKind,
    best_portal_url,
    classify_portal,
    parse_ashby_slug,
    parse_greenhouse_slug,
    parse_lever_slug,
    portal_candidates,
    skip_portal,
)
from rotation import rotated_names

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
}
INTERN_HINT = re.compile(r"intern|internship|campus|university|graduate|co-?op", re.I)
TECH_HINT = re.compile(
    r"software|sde|swe|developer|engineer|ml|machine.?learning|\bai\b|data|backend|"
    r"frontend|full.?stack|platform|technology|tech",
    re.I,
)
SESSION = requests.Session()
SESSION.headers.update(HEADERS)


def _flatten_json_ld(data) -> list[dict]:
    out: list[dict] = []
    stack = list(data) if isinstance(data, list) else [data]
    while stack:
        node = stack.pop()
        if isinstance(node, list):
            stack.extend(node)
            continue
        if not isinstance(node, dict):
            continue
        graph = node.get("@graph")
        if isinstance(graph, list):
            stack.extend(graph)
        elif isinstance(graph, dict):
            stack.append(graph)
        node_type = node.get("@type")
        if node_type == "JobPosting" or (
            isinstance(node_type, list) and "JobPosting" in node_type
        ):
            out.append(node)
    return out


def _from_greenhouse_slug(company: str, slug: str) -> list[Job]:
    jobs: list[Job] = []
    try:
        r = SESSION.get(
            f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs",
            timeout=12,
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


def _from_lever_slug(company: str, slug: str) -> list[Job]:
    jobs: list[Job] = []
    try:
        r = SESSION.get(
            f"https://api.lever.co/v0/postings/{slug}?mode=json",
            timeout=12,
        )
        if r.status_code != 200:
            return jobs
        postings = r.json()
        if not isinstance(postings, list):
            return jobs
        for item in postings:
            job = make_job(
                item.get("text", ""),
                company,
                (item.get("categories") or {}).get("location", ""),
                item.get("hostedUrl", ""),
                "Careers→Lever",
                board_company=company,
            )
            if job:
                jobs.append(job)
    except requests.RequestException:
        pass
    return jobs


def _from_json_ld(company: str, soup: BeautifulSoup, page_url: str) -> list[Job]:
    jobs: list[Job] = []
    for script in soup.find_all("script", type="application/ld+json"):
        raw = script.string or script.get_text()
        if not raw:
            continue
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            continue
        for item in _flatten_json_ld(data):
            title = item.get("title") or item.get("name") or ""
            loc = ""
            place = item.get("jobLocation")
            if isinstance(place, dict):
                addr = place.get("address") or {}
                if isinstance(addr, dict):
                    loc = ", ".join(
                        p
                        for p in (
                            addr.get("addressLocality"),
                            addr.get("addressRegion"),
                            addr.get("addressCountry"),
                        )
                        if p
                    )
            url = item.get("url") or item.get("hiringOrganization", {}).get("sameAs") or page_url
            blob = f"{title} {loc} {url}"
            if not INTERN_HINT.search(blob) and not INTERN_HINT.search(title):
                continue
            if not TECH_HINT.search(blob) and not TECH_HINT.search(title):
                continue
            job = make_job(
                title,
                company,
                loc or "India",
                url,
                "Careers Web",
                india_platform=True,
            )
            if job:
                jobs.append(job)
    return jobs


def _generic_link_scrape(company: str, soup: BeautifulSoup, base_url: str) -> list[Job]:
    jobs: list[Job] = []
    seen: set[str] = set()
    for a in soup.find_all("a", href=True):
        text = a.get_text(" ", strip=True)
        href = urljoin(base_url, a["href"])
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
    return jobs


def _scrape_html_portal(company: str, portal: str) -> list[Job]:
    jobs: list[Job] = []
    try:
        resp = SESSION.get(portal, timeout=12, allow_redirects=True)
        if resp.status_code != 200:
            return jobs
        html = resp.text
        soup = BeautifulSoup(html, "html.parser")
    except requests.RequestException:
        return jobs

    jobs.extend(fetch_oracle_from_html(company, resp.url, html))
    jobs.extend(_from_json_ld(company, soup, resp.url))
    jobs.extend(_generic_link_scrape(company, soup, resp.url))
    jobs.extend(fetch_workday_from_html(company, html))
    jobs.extend(fetch_smartrecruiters_from_html(company, html))

    for m in re.finditer(
        r"https?://(?:boards\.greenhouse\.io|job-boards\.greenhouse\.io)/([^/\"'\s]+)",
        html,
    ):
        jobs.extend(_from_greenhouse_slug(company, m.group(1)))

    for m in re.finditer(r"jobs\.lever\.co/([^/\"'\s]+)", html):
        jobs.extend(_from_lever_slug(company, m.group(1)))

    for m in re.finditer(r"jobs\.ashbyhq\.com/([^/\"'\s]+)", html):
        jobs.extend(fetch_ashby_jobs_for_slug(company, m.group(1)))

    return jobs


def _route_portal(company: str, portal: str) -> list[Job]:
    kind = classify_portal(portal)
    if kind == PortalKind.SKIP:
        return []
    if kind == PortalKind.GREENHOUSE:
        slug = parse_greenhouse_slug(portal)
        return _from_greenhouse_slug(company, slug) if slug else []
    if kind == PortalKind.LEVER:
        slug = parse_lever_slug(portal)
        return _from_lever_slug(company, slug) if slug else []
    if kind == PortalKind.ASHBY:
        slug = parse_ashby_slug(portal)
        return fetch_ashby_jobs_for_slug(company, slug) if slug else []
    if kind == PortalKind.ORACLE_CX:
        return _scrape_html_portal(company, portal)
    return _scrape_html_portal(company, portal)


def _scrape_company_entry(entry: dict) -> list[Job]:
    company = entry["name"]
    jobs: list[Job] = []
    for url in portal_candidates(entry, infer_placeholders=CAREERS_INFER_PLACEHOLDERS):
        if skip_portal(url):
            continue
        jobs.extend(_route_portal(company, url))
        if jobs:
            break
    return jobs


def _scrape_company(name: str) -> list[Job]:
    entry = match_priority_company(name)
    if not entry:
        return []
    portal = best_portal_url(entry, infer_placeholders=CAREERS_INFER_PLACEHOLDERS)
    if not portal and not entry.get("gh_slug"):
        return []
    return _scrape_company_entry(entry)


def fetch_careers_jobs() -> list[Job]:
    """Scrape career portals for every company in the priority list."""
    names = rotated_names(CAREERS_MAX_SCRAPES)
    return map_parallel(names, _scrape_company, label="careers")
