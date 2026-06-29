"""Fetch jobs from Oracle Recruiting Cloud (Candidate Experience) career sites."""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from urllib.parse import urljoin, urlparse

import requests

from companies import _norm, load_companies
from config import ROOT, ORACLE_PROBE_PER_RUN
from filters import Job, make_job
from logger import log
from portal_resolver import DOMAIN_OVERRIDES, best_portal_url

CACHE_PATH = ROOT / "data" / "oracle_boards_cache.json"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json",
}
ORACLE_SITE_RE = re.compile(r"/sites/(CX_\d+)", re.I)
ORACLE_API_RE = re.compile(r'data-apibaseurl="([^"]+)"', re.I)
ORACLE_SITE_NUM_RE = re.compile(r'data-sitenumber="([^"]+)"', re.I)
ORACLE_VANITY_RE = re.compile(r'data-vanitybaseurl="([^"]*)"', re.I)
SESSION = requests.Session()
SESSION.headers.update(HEADERS)


@dataclass(frozen=True)
class OracleBoard:
    api_base: str
    site_number: str
    vanity_base: str

    @property
    def key(self) -> str:
        return f"{self.api_base}|{self.site_number}"


def _jobs_page_url(portal: str) -> str:
    portal = portal.rstrip("/")
    if ORACLE_SITE_RE.search(portal):
        if portal.endswith("/jobs"):
            return portal
        return f"{portal}/jobs"
    return portal


def _parse_oracle_meta(html: str, fallback_url: str) -> OracleBoard | None:
    api_m = ORACLE_API_RE.search(html)
    site_m = ORACLE_SITE_NUM_RE.search(html)
    if not api_m or not site_m:
        return None
    vanity_m = ORACLE_VANITY_RE.search(html)
    vanity = (vanity_m.group(1) if vanity_m else "").strip().rstrip("/")
    if not vanity:
        parsed = urlparse(fallback_url)
        vanity = f"{parsed.scheme}://{parsed.netloc}"
    return OracleBoard(
        api_base=api_m.group(1).rstrip("/"),
        site_number=site_m.group(1),
        vanity_base=vanity,
    )


def discover_board(portal: str) -> OracleBoard | None:
    if not portal or not portal.startswith("http"):
        return None
    jobs_url = _jobs_page_url(portal)
    try:
        resp = SESSION.get(jobs_url, timeout=15, allow_redirects=True)
        if resp.status_code != 200:
            return None
        html = resp.text
    except requests.RequestException:
        return None

    return _parse_oracle_meta(html, resp.url)


def _job_url(board: OracleBoard, req_id: str) -> str:
    return urljoin(
        board.vanity_base.rstrip("/") + "/",
        f"en/sites/{board.site_number}/job/{req_id}",
    )


def _fetch_board(company: str, board: OracleBoard) -> list[Job]:
    jobs: list[Job] = []
    offset = 0
    limit = 25
    total = None
    pages = 0

    while pages < 12:
        try:
            resp = SESSION.get(
                f"{board.api_base}/hcmRestApi/resources/latest/recruitingCEJobRequisitions",
                params={
                    "onlyData": "true",
                    "finder": f"findReqs;siteNumber={board.site_number}",
                    "limit": limit,
                    "offset": offset,
                    "expand": "requisitionList",
                },
                timeout=25,
            )
            if resp.status_code != 200:
                break
            payload = resp.json()
        except requests.RequestException:
            break

        items = payload.get("items") or []
        if not items:
            break
        item = items[0]
        if total is None:
            total = int(item.get("TotalJobsCount") or 0)
        reqs = item.get("requisitionList") or []
        if not reqs:
            break

        for req in reqs:
            title = req.get("Title") or ""
            loc = req.get("PrimaryLocation") or ""
            country = req.get("PrimaryLocationCountry") or ""
            if country and country not in {"IN", "India"}:
                blob = f"{title} {loc}"
                if not re.search(
                    r"india|bangalore|bengaluru|hyderabad|mumbai|pune|gurgaon|gurugram|noida|chennai",
                    blob,
                    re.I,
                ):
                    continue
            req_id = req.get("Id") or ""
            if not req_id:
                continue
            job = make_job(
                title,
                company,
                loc,
                _job_url(board, req_id),
                "Oracle CX",
                board_company=company,
            )
            if job:
                jobs.append(job)

        offset += limit
        pages += 1
        if total is not None and offset >= total:
            break

    return jobs


def _load_cache() -> dict[str, dict]:
    if CACHE_PATH.exists():
        return json.loads(CACHE_PATH.read_text())
    return {}


def _save_cache(rows: dict[str, dict]) -> None:
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    CACHE_PATH.write_text(json.dumps(rows, indent=2))


def _might_be_oracle(portal: str, company: str) -> bool:
    if ORACLE_SITE_RE.search(portal):
        return True
    key = _norm(company)
    override = DOMAIN_OVERRIDES.get(key, "")
    return "/sites/CX_" in override


def collect_oracle_boards(companies: list[dict]) -> list[tuple[str, OracleBoard]]:
    cache = _load_cache()
    boards: dict[str, tuple[str, OracleBoard]] = {}
    for row in cache.values():
        board = OracleBoard(
            api_base=row["api_base"],
            site_number=row["site_number"],
            vanity_base=row["vanity_base"],
        )
        boards[board.key] = (row["company"], board)

    probed = 0
    for entry in companies:
        if probed >= ORACLE_PROBE_PER_RUN:
            break
        company = entry["name"]
        portal = best_portal_url(entry, infer_placeholders=True)
        if not portal or not _might_be_oracle(portal, company):
            continue
        if any(name == company for name, _ in boards.values()):
            continue
        board = discover_board(portal)
        probed += 1
        if board:
            boards[board.key] = (company, board)

    out_cache: dict[str, dict] = {}
    for company, board in boards.values():
        out_cache[board.key] = {"company": company, **asdict(board)}
    _save_cache(out_cache)
    return list(boards.values())


def fetch_oracle_from_html(company: str, portal: str, html: str) -> list[Job]:
    board = _parse_oracle_meta(html, portal)
    if not board:
        return []
    return _fetch_board(company, board)


def fetch_oracle_cx_jobs() -> list[Job]:
    companies = load_companies()
    boards = collect_oracle_boards(companies)
    log(f"Oracle CX: polling {len(boards)} career sites (full scan)")
    jobs: list[Job] = []
    for company, board in boards:
        found = _fetch_board(company, board)
        if found:
            log(f"  Oracle/{company}: {len(found)} intern matches")
        jobs.extend(found)
    return jobs
