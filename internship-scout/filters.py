"""Relevance filters: priority companies, software intern, batch 2028."""

import re
from dataclasses import dataclass

from companies import match_priority_company

INTERN_RE = re.compile(
    r"\b(intern(ship)?|trainee|co-?op|apprentice|summer\s+(analyst|associate))\b",
    re.I,
)
NEW_GRAD_RE = re.compile(
    r"\b(new\s+grad|university\s+grad|graduate\s+(program|engineer)|campus|"
    r"early\s+career|entry[\s-]level)\b",
    re.I,
)
TECH_ROLE_RE = re.compile(
    r"\b(software|sde|swe|developer|engineer|engineering|backend|frontend|"
    r"full[\s-]?stack|platform|devops|site\s+reliability|sre|ml|machine\s+learning|"
    r"\bai\b|artificial\s+intelligence|data\s+(scientist|engineer|analyst)|"
    r"android|ios|mobile|cloud|distributed|systems|quant|research|"
    r"cyber\s*security|infosec|information\s+security|blockchain|web3|"
    r"embedded|firmware|hardware|fpga|vlsi|asic|"
    r"nlp|natural\s+language|computer\s+vision|deep\s+learning|"
    r"automation|test\s+automation|qa\s+automation|"
    r"database|sql|nosql|infrastructure|networking|network\s+engineer|"
    r"compiler|language|runtime|kernel|os\s+engineer|"
    r"robotics|iot|internet\s+of\s+things|edge\s+computing|"
    r"technical|technology|tech\s+intern|coding)\b",
    re.I,
)
INDIA_RE = re.compile(
    r"\b(india|indian|bangalore|bengaluru|hyderabad|mumbai|pune|gurgaon|"
    r"gurugram|noida|chennai|kolkata|surat|remote\s+india|work\s+from\s+home.*india)\b",
    re.I,
)
EXCLUDE_TITLE_RE = re.compile(
    r"\b(marketing|sales|hr\b|human\s+resources|recruiter|copy\s*writer|"
    r"content\s*(writer|creator|-\s*intern)|graphic\s*design|campus\s+director|"
    r"business\s+development|bd\s+intern|campus\s+growth|digital\s+marketing|"
    r"social\s+media|video\s+editor|architect\s+intern|legal|finance\s+intern|"
    r"operations\s+intern|customer\s+support|talent\s+scout|mechanical|electrical|"
    r"electronics\s+engineering|civil\s+engineering|chemical\s+engineering|drone|"
    r"market\s+research|corporate\s+internship|prompt\s+engineering|software\s+testing)\b",
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
    if require_priority and not match_priority_company(check_name):
        # Also try job poster name for Unstop listings
        if not match_priority_company(company):
            return False

    blob = f"{title} {location}"
    is_intern = bool(
        INTERN_RE.search(title) or NEW_GRAD_RE.search(blob) or assume_intern
    )
    is_tech = bool(TECH_ROLE_RE.search(title))
    if not (is_intern and is_tech):
        return False

    in_india = bool(INDIA_RE.search(blob)) or india_platform
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
    if BATCH_2028_RE.search(title):
        score += 6
    if INDIA_RE.search(blob):
        score += 3
    if match_priority_company(company):
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
