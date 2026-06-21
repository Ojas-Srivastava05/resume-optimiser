"""Elite hackathon & competition scout — MNC-level events only.

Targets hackathons that offer:
  1. PPI (Pre-Placement Interview) at MNCs
  2. Stipend/prize ₹40k+ or significant career value
  3. Organized by companies from the priority CSV
  4. Known elite programs (Amazon HackOn, Flipkart Grid, etc.)

Sources: Unstop, Devfolio, MLH, direct company pages.
"""

import re
from dataclasses import dataclass
from datetime import datetime, timezone
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from companies import load_companies, match_priority_company
from fetchers.parallel import map_parallel
from logger import log

BASE_UNSTOP = "https://unstop.com"
BASE_DEVFOLIO = "https://devfolio.co"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}
SESSION = requests.Session()
SESSION.headers.update(HEADERS)

# ─── Known elite hackathons (name patterns to always match) ───────────────────
ELITE_HACKATHONS = re.compile(
    r"\b("
    r"amazon\s+hack\s*on|hack\s*on\s+.*amazon|"
    r"flipkart\s+grid|grid\s+.*flipkart|"
    r"code\s+with\s+cisco|cisco\s+ideathon|"
    r"tcs\s+code\s*vita|codevita|"
    r"infosys\s+(hacks?athon|ingenious|springboard)|"
    r"microsoft\s+(imagine|hack\s*athon|engage|code[\s-]?fun[\s-]?do)|"
    r"google\s+(hash\s*code|code\s*jam|kick\s*start|summer\s+of\s+code|girl\s+hackathon|solution\s+challenge)|gsoc|"
    r"samsung\s+(solve\s+for\s+tomorrow|prism|innovation)|"
    r"wipro\s+(elite|nlth|topgear|challenge|hack\s*athon)|"
    r"adobe\s+gensolve|"
    r"goldman\s+sachs?\s+(engineer|hack\s*athon)|"
    r"jpmorgan\s+(code\s+for\s+good|hack\s*athon)|"
    r"morgan\s+stanley\s+(hackathon|code[\s-]?to[\s-]?give)|"
    r"wells?\s+fargo\s+(hack\s*athon|program)|"
    r"barclays\s+hack\s*athon|"
    r"deutsche\s+bank\s+hack\s*athon|"
    r"uber\s+hack\s*athon|"
    r"meesho\s+(spark|hack\s*athon)|"
    r"swiggy\s+hack\s*athon|"
    r"zomato\s+hack\s*athon|"
    r"myntra\s+(hack\s*a\s*thon|hackerramp)|"
    r"walmart\s+(code[\s-]?hers?|sparkathon|hack\s*athon)|"
    r"visa\s+hack\s*athon|"
    r"mastercard\s+hack\s*athon|"
    r"american\s+express\s+(hack\s*athon|makeathon)|"
    r"oracle\s+(code[\s-]?for\s+change|hack\s*athon)|"
    r"ibm\s+(call\s+for\s+code|hack\s*athon)|"
    r"intel\s+(oneapi|hack\s*athon)|"
    r"qualcomm\s+(innovation|hack\s*athon)|"
    r"nvidia\s+hack\s*athon|"
    r"accenture\s+(innovation|hack\s*athon)|"
    r"deloitte\s+hack\s*athon|"
    r"ey\s+(techathon|hack\s*athon)|"
    r"pwc\s+hack\s*athon|"
    r"kpmg\s+hack\s*athon|"
    r"hcl\s+(tech\s*bee|hack\s*athon)|"
    r"razorpay\s+hack\s*athon|"
    r"phonep[eh]\s+hack\s*athon|"
    r"cred\s+hack\s*athon|"
    r"atlassian\s+(unravel|hack\s*athon)|"
    r"sih|smart\s+india\s+hackathon|"
    r"kavach\s+hackathon|"
    r"toycathon|"
    r"ppi|pre[\s-]?placement|"
    r"open[\s-]?source[\s-]?(contribution|program)|"
    r"mlh\s+(fellowship|hack\s*athon)"
    r")\b",
    re.I,
)

# Prize money keywords
PRIZE_RE = re.compile(
    r"(?:₹|INR|Rs\.?)\s*([\d,]+)\s*(lakh|lac|k|cr|crore)?|"
    r"prize\s+(?:pool|money|worth)\s+(?:of\s+)?(?:₹|INR|Rs\.?)\s*([\d,]+)",
    re.I,
)
PPI_RE = re.compile(r"\b(ppi|pre[\s-]?placement[\s-]?interview|placement\s+offer)\b", re.I)
STIPEND_RE = re.compile(r"\b(stipend|paid\s+internship|intern\s+offer)\b", re.I)

# Minimum prize pool to consider (in INR)
MIN_PRIZE_POOL = 50000  # ₹50k


def _is_expired(date_str: str) -> bool:
    """Return True if the given ISO-ish date string is in the past."""
    if not date_str:
        return False  # No date → can't confirm expired, let it through
    for fmt in (
        "%Y-%m-%dT%H:%M:%S%z",      # 2025-07-19T12:27:11+05:30
        "%Y-%m-%dT%H:%M:%S.%f%z",   # with microseconds
        "%Y-%m-%d %H:%M:%S%z",      # 2025-07-19 12:27:11+05:30
        "%Y-%m-%dT%H:%M:%S",        # no tz
        "%Y-%m-%d %H:%M:%S",        # no tz
        "%Y-%m-%d",                  # date only
    ):
        try:
            dt = datetime.strptime(date_str.strip(), fmt)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt < datetime.now(timezone.utc)
        except ValueError:
            continue
    return False  # Unparseable → let it through


def _hackathon_is_stale(item: dict) -> bool:
    """Return True if an Unstop hackathon item has expired (all relevant dates in the past)."""
    # Collect all date fields that indicate the event is still relevant
    end_date = item.get("end_date", "") or ""
    regn = item.get("regnRequirements") or {}
    regn_end = regn.get("end_regn_dt", "") if isinstance(regn, dict) else ""

    # If we have an end_date and it's in the past, the hackathon is done
    if end_date and _is_expired(end_date):
        return True
    # If no end_date but registration ended, also stale
    if not end_date and regn_end and _is_expired(regn_end):
        return True
    return False


@dataclass(frozen=True)
class Hackathon:
    """Represents a discovered hackathon/competition."""
    title: str
    organizer: str
    platform: str
    url: str
    prize: str
    deadline: str
    tags: list[str]  # e.g. ["PPI", "₹5L Prize", "MNC"]
    score: int = 0

    @property
    def key(self) -> str:
        return f"hackathon|{self.platform}|{self.organizer}|{self.title}".lower()


def _parse_prize_value(text: str) -> int:
    """Parse prize text to approximate INR value."""
    m = PRIZE_RE.search(text)
    if not m:
        return 0
    raw = (m.group(1) or m.group(3) or "0").replace(",", "").strip()
    if not raw:
        return 0
    try:
        val = int(raw)
    except (ValueError, TypeError):
        return 0
    suffix = (m.group(2) or "").lower()
    if suffix in ("lakh", "lac"):
        val *= 100_000
    elif suffix == "k":
        val *= 1_000
    elif suffix in ("cr", "crore"):
        val *= 10_000_000
    return val


def _score_hackathon(title: str, organizer: str, description: str) -> tuple[int, list[str]]:
    """Score a hackathon's quality and return (score, tags)."""
    score = 0
    tags: list[str] = []
    blob = f"{title} {organizer} {description}"

    # Elite name match
    if ELITE_HACKATHONS.search(blob):
        score += 10
        tags.append("🏆 Elite")

    # MNC organizer
    if match_priority_company(organizer):
        score += 5
        tags.append("MNC")

    # PPI opportunity
    if PPI_RE.search(blob):
        score += 8
        tags.append("🎯 PPI")

    # Stipend/internship offer
    if STIPEND_RE.search(blob):
        score += 6
        tags.append("💼 Internship")

    # Prize pool
    prize_val = _parse_prize_value(blob)
    if prize_val >= 1_000_000:
        score += 5
        tags.append(f"💰 ₹{prize_val // 100_000}L+")
    elif prize_val >= MIN_PRIZE_POOL:
        score += 3
        tags.append(f"💰 ₹{prize_val // 1_000}k")

    return score, tags


# ═══════════════════════════════════════════════════════════════════════════════
# Unstop — Hackathons & Competitions
# ═══════════════════════════════════════════════════════════════════════════════

UNSTOP_API = f"{BASE_UNSTOP}/api/public/opportunity/search-result"

UNSTOP_HACKATHON_QUERIES = [
    "hackathon",
    "coding challenge",
    "ideathon",
    "codeathon",
    "tech challenge",
    "innovation challenge",
    "software development challenge",
    "AI hackathon",
    "machine learning challenge",
    "open source",
    "code challenge",
    "programming contest",
]


def _unstop_search_hackathons(query: str) -> list[dict]:
    """Search Unstop for hackathons/competitions (open/upcoming only)."""
    params = {
        "opportunity": "hackathons",
        "page": 1,
        "per_page": 30,
        "searchTerm": query,
        "oppstatus": "upcoming",  # server-side hint (unreliable, we also filter client-side)
    }
    try:
        resp = SESSION.get(UNSTOP_API, params=params, timeout=15)
        resp.raise_for_status()
        items = (resp.json().get("data") or {}).get("data") or []
        return [i for i in items if not _hackathon_is_stale(i)]
    except requests.RequestException:
        return []


def _unstop_search_competitions(query: str) -> list[dict]:
    """Search Unstop for competitions (open/upcoming only)."""
    params = {
        "opportunity": "competitions",
        "page": 1,
        "per_page": 30,
        "searchTerm": query,
        "oppstatus": "upcoming",
    }
    try:
        resp = SESSION.get(UNSTOP_API, params=params, timeout=15)
        resp.raise_for_status()
        items = (resp.json().get("data") or {}).get("data") or []
        return [i for i in items if not _hackathon_is_stale(i)]
    except requests.RequestException:
        return []


def _parse_unstop_hackathon(item: dict) -> Hackathon | None:
    """Parse an Unstop hackathon item. Returns None for expired or low-quality events."""
    # ── Date gate: reject expired hackathons immediately ──
    if _hackathon_is_stale(item):
        return None

    title = item.get("title") or item.get("name") or ""
    org = item.get("organisation") or item.get("organization") or {}
    organizer = org.get("name", "") if isinstance(org, dict) else str(org)

    desc = item.get("seo_details", {}).get("description", "") if isinstance(item.get("seo_details"), dict) else ""
    desc = desc or item.get("details", "") or ""

    # Get registration info
    regn = item.get("regnRequirements") or {}
    deadline = ""
    if isinstance(regn, dict):
        deadline = regn.get("end_regn_dt", "") or ""

    # Prize info
    prizes = item.get("prizes") or []
    prize_text = ""
    if isinstance(prizes, list) and prizes:
        prize_text = str(prizes[0].get("cash", "")) if isinstance(prizes[0], dict) else str(prizes[0])
    prize_text = prize_text or item.get("prize", "") or ""

    # Build URL
    path = item.get("public_url") or ""
    url = urljoin(BASE_UNSTOP + "/", path.lstrip("/")) if path and not path.startswith("http") else path

    blob = f"{title} {organizer} {desc} {prize_text}"
    score, tags = _score_hackathon(title, organizer, blob)

    # Only include if it meets our quality bar
    if score < 3:
        return None

    return Hackathon(
        title=title,
        organizer=organizer,
        platform="Unstop",
        url=url,
        prize=prize_text,
        deadline=str(deadline),
        tags=tags,
        score=score,
    )


def _fetch_unstop_hackathons() -> list[Hackathon]:
    """Fetch hackathons from Unstop with multiple strategies."""
    seen: set[str] = set()
    hackathons: list[Hackathon] = []

    def add_items(items: list[dict]) -> None:
        for item in items:
            h = _parse_unstop_hackathon(item)
            if h and h.key not in seen:
                seen.add(h.key)
                hackathons.append(h)

    # Strategy 1: Search by hackathon-specific queries
    for query in UNSTOP_HACKATHON_QUERIES:
        add_items(_unstop_search_hackathons(query))
        add_items(_unstop_search_competitions(query))

    # Strategy 2: Search by company names from CSV
    companies = load_companies()
    mnc_names = [c["name"] for c in companies if c.get("sector") in (
        "FAANG", "Tech", "Technology", "FinTech", "Big Tech",
        "Consulting", "Banking", "Automotive",
    )][:50]

    def _search_company_hackathons(name: str) -> list[dict]:
        items = _unstop_search_hackathons(name)
        items.extend(_unstop_search_competitions(name))
        return items

    # map_parallel flattens list results, so result_batch contains dict items
    company_results = map_parallel(mnc_names[:30], _search_company_hackathons, label="unstop-hack-co")
    if company_results:
        add_items(company_results)

    log(f"Unstop hackathons: {len(hackathons)} elite matches")
    return hackathons


# ═══════════════════════════════════════════════════════════════════════════════
# Devfolio — Major Indian hackathon platform
# ═══════════════════════════════════════════════════════════════════════════════

DEVFOLIO_API = "https://api.devfolio.co/api/search/hackathons"


def _fetch_devfolio_hackathons() -> list[Hackathon]:
    """Fetch hackathons from Devfolio (upcoming/open only)."""
    hackathons: list[Hackathon] = []
    seen: set[str] = set()

    # Devfolio GraphQL-like API
    try:
        payload = {
            "type": "hackathon",
            "q": "",
            "filter": "upcoming",
            "page": 0,
            "per_page": 50,
        }
        resp = SESSION.post(DEVFOLIO_API, json=payload, timeout=15)
        if resp.status_code != 200:
            # Try alternative endpoint
            resp = SESSION.get(
                "https://api.devfolio.co/api/hackathons?filter=upcoming&page=0&per_page=50",
                timeout=15,
            )
        if resp.status_code == 200:
            data = resp.json()
            items = data.get("hackathons", []) or data.get("hits", []) or data.get("data", [])
            for item in items:
                title = item.get("name", "") or item.get("title", "")
                organizer = item.get("org_name", "") or item.get("organizer", "") or ""
                desc = item.get("desc", "") or item.get("tagline", "") or ""
                prize = item.get("prize_amount", "") or ""
                starts = item.get("starts_at", "") or ""
                ends = item.get("ends_at", "") or ""
                slug = item.get("slug", "")
                url = f"https://devfolio.co/hackathons/{slug}" if slug else ""

                # Skip expired Devfolio hackathons
                if ends and _is_expired(ends):
                    continue

                blob = f"{title} {organizer} {desc} {prize}"
                score, tags = _score_hackathon(title, organizer, blob)

                if score >= 3 and url and url not in seen:
                    seen.add(url)
                    hackathons.append(Hackathon(
                        title=title,
                        organizer=organizer,
                        platform="Devfolio",
                        url=url,
                        prize=str(prize),
                        deadline=str(ends),
                        tags=tags,
                        score=score,
                    ))
    except requests.RequestException as exc:
        log(f"Devfolio API failed: {exc}")

    log(f"Devfolio hackathons: {len(hackathons)} elite matches")
    return hackathons


# ═══════════════════════════════════════════════════════════════════════════════
# Direct company hackathon page scraper
# ═══════════════════════════════════════════════════════════════════════════════

# Known direct hackathon URLs to check (updated annually)
DIRECT_HACKATHON_URLS = [
    # Amazon HackOn
    ("Amazon", "https://unstop.com/hackathons?oppstatus=open&searchTerm=amazon"),
    # Flipkart Grid
    ("Flipkart", "https://unstop.com/hackathons?oppstatus=open&searchTerm=flipkart+grid"),
    # Code with Cisco
    ("Cisco", "https://unstop.com/hackathons?oppstatus=open&searchTerm=cisco"),
    # TCS CodeVita
    ("TCS", "https://unstop.com/competitions?oppstatus=open&searchTerm=tcs+codevita"),
    # Infosys
    ("Infosys", "https://unstop.com/hackathons?oppstatus=open&searchTerm=infosys"),
    # Walmart
    ("Walmart", "https://unstop.com/hackathons?oppstatus=open&searchTerm=walmart"),
    # Microsoft
    ("Microsoft", "https://unstop.com/hackathons?oppstatus=open&searchTerm=microsoft"),
    # Samsung
    ("Samsung", "https://unstop.com/hackathons?oppstatus=open&searchTerm=samsung"),
    # Goldman Sachs
    ("Goldman Sachs", "https://unstop.com/hackathons?oppstatus=open&searchTerm=goldman+sachs"),
    # JPMorgan
    ("JPMorgan", "https://unstop.com/hackathons?oppstatus=open&searchTerm=jpmorgan"),
    # Adobe
    ("Adobe", "https://unstop.com/hackathons?oppstatus=open&searchTerm=adobe"),
    # Myntra
    ("Myntra", "https://unstop.com/hackathons?oppstatus=open&searchTerm=myntra"),
    # Meesho
    ("Meesho", "https://unstop.com/hackathons?oppstatus=open&searchTerm=meesho"),
    # Razorpay
    ("Razorpay", "https://unstop.com/hackathons?oppstatus=open&searchTerm=razorpay"),
    # Qualcomm
    ("Qualcomm", "https://unstop.com/hackathons?oppstatus=open&searchTerm=qualcomm"),
    # Intel
    ("Intel", "https://unstop.com/hackathons?oppstatus=open&searchTerm=intel"),
    # Oracle
    ("Oracle", "https://unstop.com/hackathons?oppstatus=open&searchTerm=oracle"),
    # Wipro
    ("Wipro", "https://unstop.com/hackathons?oppstatus=open&searchTerm=wipro"),
]


def _scrape_direct_hackathon(args: tuple[str, str]) -> list[Hackathon]:
    """Scrape a known hackathon listing page."""
    company, url = args
    hackathons: list[Hackathon] = []
    try:
        resp = SESSION.get(url, timeout=15)
        if resp.status_code != 200:
            return hackathons
        soup = BeautifulSoup(resp.text, "html.parser")

        for card in soup.select("a[href*='/hackathon'], a[href*='/competition']"):
            title = card.get_text(strip=True)[:120]
            href = card.get("href", "")
            if href and not href.startswith("http"):
                href = urljoin(url, href)
            if not title or not href:
                continue

            score, tags = _score_hackathon(title, company, "")
            if match_priority_company(company):
                score += 5
                if "MNC" not in tags:
                    tags.append("MNC")

            if score >= 3:
                hackathons.append(Hackathon(
                    title=title,
                    organizer=company,
                    platform="Direct",
                    url=href,
                    prize="",
                    deadline="",
                    tags=tags,
                    score=score,
                ))
    except requests.RequestException:
        pass
    return hackathons


# ═══════════════════════════════════════════════════════════════════════════════
# Main entry point
# ═══════════════════════════════════════════════════════════════════════════════

def fetch_hackathons() -> list[Hackathon]:
    """Master hackathon collector — all sources combined."""
    all_hackathons: list[Hackathon] = []
    seen: set[str] = set()

    def add(hacks: list[Hackathon], label: str) -> None:
        n = 0
        for h in hacks:
            if h.key not in seen:
                seen.add(h.key)
                all_hackathons.append(h)
                n += 1
        log(f"Hackathons from {label}: +{n} unique")

    # Source 1: Unstop (largest Indian hackathon platform)
    add(_fetch_unstop_hackathons(), "Unstop")

    # Source 2: Devfolio
    add(_fetch_devfolio_hackathons(), "Devfolio")

    # Source 3: Direct company hackathon pages
    direct_results = map_parallel(
        DIRECT_HACKATHON_URLS, _scrape_direct_hackathon, label="hack-direct"
    )
    for batch in direct_results:
        if isinstance(batch, list):
            add(batch, "Direct")
        elif isinstance(batch, Hackathon):
            add([batch], "Direct")

    # Sort by quality score (best first)
    all_hackathons.sort(key=lambda h: (-h.score, h.organizer, h.title))
    log(f"Total elite hackathons: {len(all_hackathons)}")
    return all_hackathons


def hackathons_to_html(hackathons: list[Hackathon]) -> str:
    """Build HTML section for hackathon digest email."""
    if not hackathons:
        return ""

    parts = [
        "<h2>🏆 Elite Hackathons & Competitions</h2>",
        "<p><em>MNC-organized · PPI opportunities · ₹40k+ prizes</em></p>",
        "<table style='border-collapse:collapse;width:100%;'>",
        "<tr style='background:#1a1a2e;color:#e94560;'>"
        "<th style='padding:8px;text-align:left;'>Event</th>"
        "<th style='padding:8px;text-align:left;'>Organizer</th>"
        "<th style='padding:8px;text-align:left;'>Tags</th>"
        "<th style='padding:8px;text-align:left;'>Platform</th>"
        "</tr>",
    ]

    for i, h in enumerate(hackathons):
        bg = "#16213e" if i % 2 == 0 else "#0f3460"
        tags_str = " ".join(h.tags) if h.tags else "—"
        parts.append(
            f"<tr style='background:{bg};color:#eee;'>"
            f"<td style='padding:8px;'><a href='{h.url}' style='color:#e94560;'>{h.title}</a></td>"
            f"<td style='padding:8px;'>{h.organizer}</td>"
            f"<td style='padding:8px;'>{tags_str}</td>"
            f"<td style='padding:8px;'>{h.platform}</td>"
            f"</tr>"
        )

    parts.append("</table>")
    return "\n".join(parts)


def hackathons_to_text(hackathons: list[Hackathon]) -> str:
    """Build plain-text section for hackathon digest."""
    if not hackathons:
        return ""

    lines = [
        "═══ ELITE HACKATHONS & COMPETITIONS ═══",
        "MNC-organized · PPI opportunities · ₹40k+ prizes",
        "",
    ]
    for h in hackathons:
        tags_str = " | ".join(h.tags) if h.tags else ""
        lines.append(f"• [{h.platform}] {h.organizer} — {h.title}")
        if tags_str:
            lines.append(f"  {tags_str}")
        lines.append(f"  {h.url}")
        lines.append("")
    return "\n".join(lines)
