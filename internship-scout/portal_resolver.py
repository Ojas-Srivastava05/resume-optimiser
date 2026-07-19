"""Classify career portal URLs and resolve scrape targets for priority companies."""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum
from urllib.parse import urlparse

from companies import _norm

SKIP_PORTAL_RE = re.compile(r"google\.com/search|careers\.google\.com", re.I)
WORKDAY_RE = re.compile(
    r"https?://([^.]+)\.wd(\d+)\.myworkdayjobs\.com/([^/?#]+)",
    re.I,
)
SMARTRECRUITERS_RE = re.compile(r"careers\.smartrecruiters\.com/([^/?#]+)", re.I)
GREENHOUSE_RE = re.compile(
    r"(?:boards|job-boards)\.greenhouse\.io/([^/?#\s\"']+)",
    re.I,
)
LEVER_RE = re.compile(r"jobs\.lever\.co/([^/?#\s\"']+)", re.I)
ASHBY_RE = re.compile(
    r"(?:jobs\.ashbyhq\.com|ashbyhq\.com)/([^/?#\s\"']+)",
    re.I,
)
ICIMS_RE = re.compile(r"\.icims\.com", re.I)
ORACLE_CX_RE = re.compile(r"(?:oraclecloud\.com|/sites/CX_\d+)", re.I)

# Known domains where name→slug.com inference is wrong or careers live elsewhere.
DOMAIN_OVERRIDES: dict[str, str] = {
    "americanexpress": "https://careers.americanexpress.com/en/sites/CX_1",
    "jpmorgan": "https://careers.jpmorgan.com/us/en/students/programs",
    "goldmansachs": "https://www.goldmansachs.com/careers/",
    "morganstanley": "https://www.morganstanley.com/careers",
    "google": "https://careers.google.com/jobs/results/?location=India",
    "meta": "https://www.metacareers.com/jobs",
    "amazon": "https://www.amazon.jobs/en/search?base_query=intern",
    "microsoft": "https://careers.microsoft.com/us/en/search-results?keywords=intern",
    "apple": "https://jobs.apple.com/en-us/search?team=internships-STDNT-INTRN",
    "netflix": "https://jobs.netflix.com/search",
    "uber": "https://www.uber.com/us/en/careers/list/",
    "flipkart": "https://www.flipkartcareers.com/",
    "myntra": "https://www.myntra.com/careers",
    "swiggy": "https://careers.swiggy.com/",
    "zomato": "https://careers.smartrecruiters.com/Zomato1",
    "paytm": "https://paytm.com/careers/",
    "phonepe": "https://www.phonepe.com/careers/",
    "razorpay": "https://razorpay.com/jobs/",
    "freshworks": "https://careers.smartrecruiters.com/freshworks",
    "nvidia": "https://nvidia.wd5.myworkdayjobs.com/NVIDIAExternalCareerSite",
    "adobe": "https://www.adobe.com/careers.html",
    "salesforce": "https://careers.salesforce.com/en/jobs/",
    "oracle": "https://careers.oracle.com/",
    "ibm": "https://www.ibm.com/careers/search",
    "intel": "https://jobs.intel.com/",
    "cisco": "https://jobs.cisco.com/jobs",
    "sap": "https://jobs.sap.com/",
    "accenture": "https://www.accenture.com/in-en/careers",
    "tcs": "https://www.tcs.com/careers/india",
    "infosys": "https://www.infosys.com/careers.html",
    "wipro": "https://careers.wipro.com/",
    "hcltech": "https://www.hcltech.com/careers",
    "capgemini": "https://www.capgemini.com/careers/",
    "deloitte": "https://apply.deloitte.com/careers/SearchJobs",
    "kpmg": "https://home.kpmg/in/en/home/careers.html",
    "ey": "https://careers.ey.com/",
    "baincompany": "https://www.bain.com/careers/",
    "bcg": "https://careers.bcg.com/",
    "mckinsey": "https://www.mckinsey.com/careers",
}


class PortalKind(Enum):
    WORKDAY = "workday"
    SMARTRECRUITERS = "smartrecruiters"
    GREENHOUSE = "greenhouse"
    LEVER = "lever"
    ASHBY = "ashby"
    ICIMS = "icims"
    ORACLE_CX = "oracle_cx"
    GENERIC = "generic"
    SKIP = "skip"


@dataclass(frozen=True)
class WorkdayBoard:
    tenant: str
    site: str
    wd_num: str
    base_url: str

    @property
    def key(self) -> str:
        return f"{self.tenant}:{self.site}"

    @property
    def jobs_api(self) -> str:
        return f"{self.base_url}/wday/cxs/{self.tenant}/{self.site}/jobs"

    @property
    def public_root(self) -> str:
        return f"{self.base_url}/{self.site}"


def skip_portal(url: str) -> bool:
    return not url or not url.startswith("http") or bool(SKIP_PORTAL_RE.search(url))


def parse_workday(url: str) -> WorkdayBoard | None:
    m = WORKDAY_RE.search(url or "")
    if not m:
        return None
    tenant, wd_num, site = m.group(1), m.group(2), m.group(3)
    base = f"https://{tenant}.wd{wd_num}.myworkdayjobs.com"
    return WorkdayBoard(tenant=tenant, site=site, wd_num=wd_num, base_url=base)


def parse_smartrecruiters_slug(url: str) -> str | None:
    m = SMARTRECRUITERS_RE.search(url or "")
    return m.group(1) if m else None


def parse_greenhouse_slug(url: str) -> str | None:
    m = GREENHOUSE_RE.search(url or "")
    return m.group(1) if m else None


def parse_lever_slug(url: str) -> str | None:
    m = LEVER_RE.search(url or "")
    return m.group(1) if m else None


def parse_ashby_slug(url: str) -> str | None:
    m = ASHBY_RE.search(url or "")
    return m.group(1) if m else None


def classify_portal(url: str) -> PortalKind:
    if skip_portal(url):
        return PortalKind.SKIP
    if parse_workday(url):
        return PortalKind.WORKDAY
    if parse_smartrecruiters_slug(url):
        return PortalKind.SMARTRECRUITERS
    if parse_greenhouse_slug(url):
        return PortalKind.GREENHOUSE
    if parse_lever_slug(url):
        return PortalKind.LEVER
    if parse_ashby_slug(url):
        return PortalKind.ASHBY
    if ICIMS_RE.search(url):
        return PortalKind.ICIMS
    if ORACLE_CX_RE.search(url):
        return PortalKind.ORACLE_CX
    return PortalKind.GENERIC


def infer_portal_url(company: str) -> str | None:
    """Guess a careers URL when the sheet has a Google placeholder."""
    key = _norm(company)
    if key in DOMAIN_OVERRIDES:
        return DOMAIN_OVERRIDES[key]

    name = company or ""
    for suffix in (
        " India",
        " Global",
        " Technologies",
        " Technology",
        " Labs",
        " Software",
        " Systems",
    ):
        if name.endswith(suffix):
            name = name[: -len(suffix)]

    slug = _norm(name)
    if len(slug) < 4 or len(slug) > 28:
        return None
    return f"https://www.{slug}.com/careers"


def best_portal_url(entry: dict, *, infer_placeholders: bool = True) -> str | None:
    key = _norm(entry.get("name", ""))
    if key in DOMAIN_OVERRIDES:
        return DOMAIN_OVERRIDES[key]

    portal = (entry.get("portal") or "").strip()
    if portal and not skip_portal(portal):
        return portal
    if infer_placeholders:
        return infer_portal_url(entry.get("name", ""))
    return None


def portal_candidates(entry: dict, *, infer_placeholders: bool = True) -> list[str]:
    """Ordered URLs to probe for one company (more candidates = higher portal yield)."""
    seen: set[str] = set()
    out: list[str] = []

    def add(url: str | None) -> None:
        if not url or skip_portal(url):
            return
        norm = url.split("#")[0].rstrip("/")
        if norm in seen:
            return
        seen.add(norm)
        out.append(url)

    add(best_portal_url(entry, infer_placeholders=infer_placeholders))
    portal = (entry.get("portal") or "").strip()
    add(portal)
    if entry.get("gh_slug"):
        add(f"https://boards.greenhouse.io/{entry['gh_slug']}")
        add(f"https://job-boards.greenhouse.io/{entry['gh_slug']}")

    primary = out[0] if out else None
    if primary:
        try:
            parsed = urlparse(primary)
            root = f"{parsed.scheme}://{parsed.netloc}"
            for suffix in (
                "/careers",
                "/jobs",
                "/careers/jobs",
                "/careers/students",
                "/careers/university",
                "/campus",
                "/university",
                "/students",
                "/early-careers",
                "/en/careers",
                "/en/jobs",
            ):
                add(f"{root}{suffix}")
            # India-focused query pages when the root is a searchable careers site
            for q in ("intern", "internship", "software+intern", "campus"):
                add(f"{root}/jobs?q={q}")
                add(f"{root}/careers?keywords={q}")
        except Exception:
            pass

    return out[:8]


def collect_workday_boards(companies: list[dict]) -> list[tuple[str, WorkdayBoard]]:
    boards: dict[str, tuple[str, WorkdayBoard]] = {}
    for entry in companies:
        for url in portal_candidates(entry):
            board = parse_workday(url)
            if board and board.key not in boards:
                boards[board.key] = (entry["name"], board)
    return list(boards.values())


def collect_smartrecruiters_slugs(companies: list[dict]) -> list[tuple[str, str]]:
    slugs: dict[str, str] = {}
    for entry in companies:
        for url in portal_candidates(entry):
            slug = parse_smartrecruiters_slug(url)
            if slug and slug not in slugs:
                slugs[slug] = entry["name"]
    return [(name, slug) for slug, name in slugs.items()]
