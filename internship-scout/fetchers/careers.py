"""Scrape career portals — ATS routing, JSON-LD, rotated full-company coverage."""

from __future__ import annotations

import json
import re
import threading
from dataclasses import dataclass
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from companies import company_names_for_search, match_priority_company
from config import (
    CAREERS_HTTP_TIMEOUT,
    CAREERS_INFER_PLACEHOLDERS,
    CAREERS_MAX_SCRAPES,
    CAREERS_MAX_URLS_PER_COMPANY,
    CAREERS_TIME_BUDGET_SEC,
    FAST_MODE,
)
from fetchers.ashby import fetch_ashby_jobs_for_slug
from fetchers.oracle_cx import fetch_oracle_from_html
from fetchers.parallel import map_parallel
from fetchers.smartrecruiters import fetch_smartrecruiters_from_html, fetch_smartrecruiters_for_slug
from fetchers.workday import fetch_workday_from_html, fetch_workday_for_url
from filters import Job, make_job
from logger import log
from portal_resolver import (
    PortalKind,
    best_portal_url,
    classify_portal,
    parse_ashby_slug,
    parse_greenhouse_slug,
    parse_lever_slug,
    parse_smartrecruiters_slug,
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
INTERN_HINT = re.compile(
    r"intern|internship|campus|university|graduate|co-?op|trainee|fellow|"
    r"summer\s+analyst|early\s+career",
    re.I,
)
TECH_HINT = re.compile(
    r"software|sde|swe|sdet|developer|programmer|engineer|engineering|"
    r"ml|machine.?learning|\bai\b|applied\s+science|data|backend|"
    r"frontend|full.?stack|platform|technology|tech|computing|computer|"
    r"quant|research|scientist|analytics|product|embedded|firmware|"
    r"chipset|wireless|multimedia|connectivity|\bit\b",
    re.I,
)
SESSION = requests.Session()
SESSION.headers.update(HEADERS)

# Filled by the latest fetch_careers_jobs() call — consumed by scout/emailer
LAST_PORTAL_COVERAGE: "PortalCoverage | None" = None
_STATS_LOCK = threading.Lock()


@dataclass
class PortalCoverage:
    companies_checked: int = 0
    urls_probed: int = 0
    matches: int = 0
    companies_with_hits: int = 0
    workday_hits: int = 0
    oracle_hits: int = 0
    skipped_budget: int = 0

    def line(self) -> str:
        return (
            f"Checked {self.companies_checked} portals today · "
            f"{self.matches} match{'es' if self.matches != 1 else ''} "
            f"({self.urls_probed} URLs probed"
            f"{f', {self.skipped_budget} skipped on time budget' if self.skipped_budget else ''})"
        )


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
            timeout=max(12, _careers_http_timeout()),
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
            timeout=max(12, _careers_http_timeout()),
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
            elif isinstance(place, list) and place:
                first = place[0]
                if isinstance(first, dict):
                    addr = first.get("address") or {}
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


def _careers_http_timeout() -> int:
    if CAREERS_HTTP_TIMEOUT:
        return CAREERS_HTTP_TIMEOUT
    # Fast mode still needs enough headroom for Workday/Oracle HTML + API hops
    return 15 if FAST_MODE else 20


def _max_urls_per_company() -> int:
    if CAREERS_MAX_URLS_PER_COMPANY > 0:
        return CAREERS_MAX_URLS_PER_COMPANY
    # Breadth-first when queuing the full roster
    if CAREERS_MAX_SCRAPES <= 0:
        return 2
    return 3 if FAST_MODE else 6


def _scrape_html_portal(company: str, portal: str) -> list[Job]:
    jobs: list[Job] = []
    try:
        resp = SESSION.get(portal, timeout=_careers_http_timeout(), allow_redirects=True)
        if resp.status_code != 200:
            return jobs
        html = resp.text
        soup = BeautifulSoup(html, "html.parser")
    except requests.RequestException:
        return jobs

    oracle_jobs = fetch_oracle_from_html(company, resp.url, html)
    jobs.extend(oracle_jobs)

    jobs.extend(_from_json_ld(company, soup, resp.url))
    jobs.extend(_generic_link_scrape(company, soup, resp.url))

    # Always try Workday / SmartRecruiters when markers appear (including FAST_MODE)
    if "myworkdayjobs.com" in html.lower() or "workday" in html.lower():
        jobs.extend(fetch_workday_from_html(company, html))
    if "smartrecruiters.com" in html.lower():
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
    if kind == PortalKind.WORKDAY:
        return fetch_workday_for_url(company, portal) or _scrape_html_portal(company, portal)
    if kind == PortalKind.SMARTRECRUITERS:
        slug = parse_smartrecruiters_slug(portal)
        if slug:
            return fetch_smartrecruiters_for_slug(company, slug)
        return _scrape_html_portal(company, portal)
    if kind == PortalKind.ORACLE_CX:
        return _scrape_html_portal(company, portal)
    return _scrape_html_portal(company, portal)


def _scrape_company_entry(entry: dict, stats: PortalCoverage) -> list[Job]:
    company = entry["name"]
    jobs: list[Job] = []
    urls = portal_candidates(entry, infer_placeholders=CAREERS_INFER_PLACEHOLDERS)
    limit = _max_urls_per_company()
    for url in urls[:limit]:
        if skip_portal(url):
            continue
        with _STATS_LOCK:
            stats.urls_probed += 1
        found = _route_portal(company, url)
        if found:
            jobs.extend(found)
            break
    return jobs


def _scrape_company(name: str) -> list[Job]:
    # stats object is attached by fetch_careers_jobs via thread-local / closure
    stats: PortalCoverage = getattr(_scrape_company, "_stats")  # type: ignore[attr-defined]
    entry = match_priority_company(name)
    with _STATS_LOCK:
        stats.companies_checked += 1
    if not entry:
        return []
    portal = best_portal_url(entry, infer_placeholders=CAREERS_INFER_PLACEHOLDERS)
    if not portal and not entry.get("gh_slug"):
        return []
    jobs = _scrape_company_entry(entry, stats)
    if jobs:
        with _STATS_LOCK:
            stats.companies_with_hits += 1
            stats.matches += len(jobs)
            for j in jobs:
                if "Workday" in j.source or "workday" in j.source.lower():
                    stats.workday_hits += 1
                if "Oracle" in j.source:
                    stats.oracle_hits += 1
    return jobs


def _careers_company_queue() -> list[str]:
    """Ordered company list for this run.

    CAREERS_MAX_SCRAPES <= 0 → full roster (rotated start day-to-day).
    Otherwise → fixed daily slice. Time budget still caps how many finish.
    """
    all_names = company_names_for_search()
    if not all_names:
        return []
    if CAREERS_MAX_SCRAPES <= 0:
        return rotated_names(len(all_names))
    return rotated_names(CAREERS_MAX_SCRAPES)


def _careers_time_budget() -> float | None:
    """Wall-clock cap for portal scraping. Required when scanning the full roster."""
    if CAREERS_TIME_BUDGET_SEC > 0:
        return float(CAREERS_TIME_BUDGET_SEC)
    # Safety: never run unbounded when queuing every company
    if CAREERS_MAX_SCRAPES <= 0:
        return 1200.0 if FAST_MODE else 1800.0
    return None


def fetch_careers_jobs() -> list[Job]:
    """Scrape career portals — as many companies as the time budget allows."""
    global LAST_PORTAL_COVERAGE
    names = _careers_company_queue()
    budget = _careers_time_budget()
    stats = PortalCoverage()
    _scrape_company._stats = stats  # type: ignore[attr-defined]

    if budget:
        log(
            f"Careers: queue={len(names)} companies, "
            f"budget={int(budget)}s, urls/company≤{_max_urls_per_company()} "
            f"— fill until time runs out"
        )
    else:
        log(f"Careers: queue={len(names)} companies (no time budget)")

    jobs = map_parallel(
        names,
        _scrape_company,
        label="careers",
        deadline_sec=budget,
    )
    # Approximate budget skips from attempted vs requested
    if budget and stats.companies_checked < len(names):
        stats.skipped_budget = len(names) - stats.companies_checked
    # Prefer exact match count from returned jobs (dedupe happens later in scout)
    stats.matches = len(jobs)
    LAST_PORTAL_COVERAGE = stats
    log(stats.line())
    if stats.workday_hits or stats.oracle_hits:
        log(
            f"Portal ATS yield: Workday={stats.workday_hits}, Oracle={stats.oracle_hits}, "
            f"companies with hits={stats.companies_with_hits}"
        )
    return jobs
