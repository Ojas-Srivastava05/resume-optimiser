"""Internshala — India's largest internship platform, API-based scraper."""

import re
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from companies import match_priority_company
from filters import Job, make_job
from logger import log

BASE = "https://internshala.com"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}
SESSION = requests.Session()
SESSION.headers.update(HEADERS)

# Search paths for different tech internship categories on Internshala
SEARCH_PATHS = [
    "/internships/computer-science-internship",
    "/internships/web-development-internship",
    "/internships/python-django-internship",
    "/internships/machine-learning-internship",
    "/internships/full-stack-development-internship",
    "/internships/software-development-internship",
    "/internships/data-science-internship",
    "/internships/artificial-intelligence-ai-internship",
    "/internships/java-internship",
    "/internships/react-internship",
    "/internships/backend-development-internship",
    "/internships/cloud-computing-internship",
    "/internships/devops-internship",
]

MIN_STIPEND = 40000  # ₹40k/month minimum for non-priority companies

STIPEND_RE = re.compile(r"₹?\s*([\d,]+)\s*(?:/\s*month)?", re.I)


def _parse_stipend(text: str) -> int:
    """Parse stipend string like '₹40,000 /month' → 40000."""
    m = STIPEND_RE.search(text)
    if m:
        return int(m.group(1).replace(",", ""))
    return 0


def _scrape_page(path: str) -> list[dict]:
    """Scrape one Internshala listing page."""
    url = urljoin(BASE, path)
    items: list[dict] = []
    try:
        resp = SESSION.get(url, timeout=15)
        if resp.status_code != 200:
            return items
        soup = BeautifulSoup(resp.text, "html.parser")
    except requests.RequestException:
        return items

    # Internshala uses .individual_internship containers
    for card in soup.select(".individual_internship, .internship_meta, .container-fluid.individual_internship"):
        try:
            title_el = card.select_one(
                ".heading_4_5 a, h3.heading_4_5 a, .profile a, .job-internship-name a"
            )
            company_el = card.select_one(
                ".heading_6, h4.heading_6, .company_name a, .company-name a"
            )
            loc_el = card.select_one(
                ".location_link, #location_names .location_link, .individual_internship_details .ic-16-pin + span"
            )
            stipend_el = card.select_one(
                ".stipend, .desktop-text .stipend, span.stipend"
            )
            link_el = card.select_one(
                "a.view_detail_button, .heading_4_5 a, .profile a, a[href*='/internship/detail']"
            )

            title = title_el.get_text(strip=True) if title_el else ""
            company = company_el.get_text(strip=True) if company_el else ""
            location = loc_el.get_text(strip=True) if loc_el else "India"
            stipend_text = stipend_el.get_text(strip=True) if stipend_el else ""
            stipend = _parse_stipend(stipend_text)

            href = ""
            if link_el and link_el.get("href"):
                href = urljoin(BASE, link_el["href"])
            elif title_el and title_el.get("href"):
                href = urljoin(BASE, title_el["href"])

            if title and company and href:
                items.append({
                    "title": title,
                    "company": company,
                    "location": location,
                    "url": href,
                    "stipend": stipend,
                    "stipend_text": stipend_text,
                })
        except (AttributeError, TypeError):
            continue
    return items


def fetch_internshala_jobs() -> list[Job]:
    """Fetch tech internships from Internshala.

    Two-tier filtering:
      1. Priority company match → always include (any stipend)
      2. Non-priority company with ₹40k+ stipend → include as high-value
    """
    seen: set[str] = set()
    jobs: list[Job] = []
    priority_count = 0
    high_stipend_count = 0

    for path in SEARCH_PATHS:
        items = _scrape_page(path)
        for item in items:
            if item["url"] in seen:
                continue
            seen.add(item["url"])

            is_priority = bool(match_priority_company(item["company"]))
            is_high_stipend = item["stipend"] >= MIN_STIPEND

            if not is_priority and not is_high_stipend:
                continue

            # For Internshala, all listings are India-based internships
            source = "Internshala"
            if is_high_stipend and not is_priority:
                source = "Internshala★"  # Mark high-stipend non-priority

            job = make_job(
                item["title"],
                item["company"],
                item["location"],
                item["url"],
                source,
                india_platform=True,
                assume_intern=True,  # Internshala is an internship platform
            )
            if job:
                jobs.append(job)
                if is_priority:
                    priority_count += 1
                else:
                    high_stipend_count += 1

    log(f"Internshala: {len(jobs)} matches ({priority_count} priority, {high_stipend_count} high-stipend ₹{MIN_STIPEND // 1000}k+)")
    return jobs
