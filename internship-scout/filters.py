"""Relevance filters: priority companies, CS-adjacent intern roles, batch 2028.

Relaxed for Computer Science / AI students: accept tech-adjacent titles
(Applied Sciences, Technology Intern, Summer Analyst, SDET, etc.), not only
strict \"SWE Intern\" wording. Still blocks marketing/HR/content noise.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from companies import match_priority_company

INTERN_RE = re.compile(
    r"\b(intern(ship)?|trainee|co-?op|apprentice|"
    r"summer\s+(analyst|associate|intern)|"
    r"graduate\s+(trainee|engineer|program)|"
    r"campus\s+(hire|recruit|program)|"
    r"fellow(ship)?)\b",
    re.I,
)
NEW_GRAD_RE = re.compile(
    r"\b(new\s+grad|university\s+grad|graduate\s+(program|engineer)|campus|"
    r"early\s+career|entry[\s-]level|university\s+recruit)\b",
    re.I,
)
# Broad CS / engineering / applied-science signal — not SWE-only
TECH_ROLE_RE = re.compile(
    r"\b("
    r"software|sde|swe|sdet|developer|programmer|programming|coding|"
    r"engineer|engineering|backend|frontend|full[\s-]?stack|platform|"
    r"devops|site\s+reliability|sre|"
    r"ml|machine\s+learning|\bai\b|artificial\s+intelligence|"
    r"applied\s+science|data\s+(scientist|engineer|analyst|science)|"
    r"computer\s+science|computing|\bcs\b|information\s+technology|"
    r"android|ios|mobile|cloud|distributed|systems|quant|quantitative|"
    r"research|scientist|"
    r"cyber\s*security|infosec|information\s+security|blockchain|web3|"
    r"embedded|firmware|hardware|fpga|vlsi|asic|"
    r"nlp|natural\s+language|computer\s+vision|deep\s+learning|"
    r"automation|test\s+(automation|engineer)|qa\s+(automation|engineer)|"
    r"database|sql|nosql|infrastructure|networking|network\s+engineer|"
    r"compiler|language|runtime|kernel|os\s+engineer|"
    r"robotics|iot|internet\s+of\s+things|edge\s+computing|"
    r"technical|technology|tech(\s+intern|\s+program|\s+analyst)?|"
    r"product\s+(intern|analyst|manager|engineer)|"
    r"\bit\b|"
    r"analytics|algorithm|platform\s+intern|"
    r"chipset|modem|multimedia|wireless|connectivity"
    r")\b",
    re.I,
)
# Soft tech: titles that are fine at priority tech/finance firms without SWE wording
SOFT_TECH_TITLE_RE = re.compile(
    r"\b("
    r"summer\s+analyst|summer\s+associate|"
    r"analyst\s+intern|intern\s*[-–]\s*analyst|"
    r"campus\s+intern|technology\s+program|"
    r"graduate\s+trainee|get\b|engineer\s+trainee"
    r")\b",
    re.I,
)
INDIA_RE = re.compile(
    r"\b(india|indian|bangalore|bengaluru|hyderabad|mumbai|pune|gurgaon|"
    r"gurugram|noida|chennai|kolkata|surat|delhi|ahmedabad|"
    r"remote\s+india|work\s+from\s+home.*india|"
    r"multiple\s+locations|pan[\s-]india)\b",
    re.I,
)
# Non-CS noise only — keep QA/SDET/electronics/ops-tech pathways open
EXCLUDE_TITLE_RE = re.compile(
    r"\b("
    r"marketing|sales|hr\b|human\s+resources|recruiter|copy\s*writer|"
    r"content\s*(writer|creator)|graphic\s*design|campus\s+director|"
    r"business\s+development|bd\s+intern|campus\s+growth|digital\s+marketing|"
    r"social\s+media|video\s+editor|legal|"
    r"customer\s+support|talent\s+scout|"
    r"mechanical(\s+engineering)?|civil\s+engineering|chemical\s+engineering|"
    r"drone\s+(pilot|operator)|market\s+research|"
    r"corporate\s+communications|public\s+relations|\bpr\s+intern|"
    r"ui/?ux\s+design\s+intern|fashion|hospitality|pharmacy|nursing"
    r")\b",
    re.I,
)
# Graduation batch years that are NOT yours — e.g. Myntra "Batch of 2026"
WRONG_GRAD_BATCH_RE = re.compile(
    r"\b(?:batch\s+of|batch\s*[-–]\s*|class\s+of|graduating\s+in|"
    r"passing\s+(?:year|batch)|open\s+campus\s*[-–]\s*batch\s+of|"
    r"(?:bt\.?tech|b\.?tech)\s+batch\s+of?)\s*['\"]?(20(?:1\d|2[0-7])|[0-2][0-7])\b|"
    r"\b20(?:1\d|2[0-7])\s+intern",
    re.I,
)
BATCH_2028_RE = re.compile(
    r"\b(?:batch\s+of|batch\s*[-–]\s*|class\s+of|graduating\s+in|"
    r"passing\s+(?:year|batch)|(?:bt\.?tech|b\.?tech)\s+batch\s+of?)\s*['\"]?(2028|28)\b",
    re.I,
)

# Sectors where a bare "Intern" / Summer Analyst title is still CS-relevant
TECH_SECTOR_HINT = re.compile(
    r"tech|software|faang|fintech|bank|quant|ai|ml|cloud|saas|internet|"
    r"semiconductor|electronics|product|engineering|it\b|computer",
    re.I,
)


@dataclass(frozen=True)
class Job:
    title: str
    company: str
    location: str
    url: str
    source: str
    score: int = 0

    @property
    def key(self) -> str:
        return f"{self.source}|{self.company}|{self.title}|{self.url}".lower()


def batch_year_ok(title: str) -> bool:
    """Allow 2028 batch or no batch stated; reject other graduation batches."""
    if BATCH_2028_RE.search(title):
        return True
    if WRONG_GRAD_BATCH_RE.search(title):
        return False
    return True


def _is_tech_role(title: str, company_entry: dict | None) -> bool:
    if TECH_ROLE_RE.search(title) or SOFT_TECH_TITLE_RE.search(title):
        return True
    # Bare intern / trainee at a clearly tech-sector priority company
    if company_entry and INTERN_RE.search(title):
        sector = str(company_entry.get("sector") or "")
        if TECH_SECTOR_HINT.search(sector):
            return True
    return False


def is_relevant(
    title: str,
    company: str,
    location: str = "",
    *,
    board_company: str | None = None,
    require_priority: bool = True,
    india_platform: bool = False,
    assume_intern: bool = False,
) -> bool:
    if not title or EXCLUDE_TITLE_RE.search(title):
        return False
    if not batch_year_ok(title):
        return False

    check_name = board_company or company
    entry = match_priority_company(check_name) or match_priority_company(company)
    if require_priority and not entry:
        return False

    blob = f"{title} {location}"
    is_intern = bool(
        INTERN_RE.search(title) or NEW_GRAD_RE.search(blob) or assume_intern
    )
    is_tech = _is_tech_role(title, entry)
    if not (is_intern and is_tech):
        return False

    in_india = bool(INDIA_RE.search(blob)) or india_platform
    # ATS boards often omit India in the location string for multi-country postings
    if not in_india and entry and TECH_SECTOR_HINT.search(str(entry.get("sector") or "")):
        loc_l = (location or "").lower()
        if not loc_l or loc_l in {"—", "-", "remote", "n/a", "worldwide", "global"}:
            in_india = True
    if not in_india:
        return False
    return True


def _score_job(title: str, company: str, location: str) -> int:
    score = 0
    blob = f"{title} {company} {location}"
    if INTERN_RE.search(title):
        score += 5
    if TECH_ROLE_RE.search(title):
        score += 4
    elif SOFT_TECH_TITLE_RE.search(title):
        score += 2
    if BATCH_2028_RE.search(title):
        score += 6
    if INDIA_RE.search(blob):
        score += 3
    if match_priority_company(company):
        score += 2
    # Prefer classic SWE wording slightly in ranking
    if re.search(r"\b(software|sde|swe|developer)\b", title, re.I):
        score += 2
    return score


def make_job(
    title: str,
    company: str,
    location: str,
    url: str,
    source: str,
    *,
    board_company: str | None = None,
    india_platform: bool = False,
    assume_intern: bool = False,
) -> Job | None:
    title = (title or "").strip()
    company = (company or "").strip() or "Unknown"
    location = (location or "").strip() or "—"
    url = (url or "").strip()
    if not url or not is_relevant(
        title,
        company,
        location,
        board_company=board_company,
        india_platform=india_platform,
        assume_intern=assume_intern,
    ):
        return None
    score = _score_job(title, company, location)
    return Job(title=title, company=company, location=location, url=url, source=source, score=score)


def dedupe_jobs(jobs: list[Job]) -> list[Job]:
    seen: set[str] = set()
    out: list[Job] = []
    for job in sorted(jobs, key=lambda j: (-j.score, j.company, j.title)):
        if job.key in seen:
            continue
        seen.add(job.key)
        out.append(job)
    return out
