"""Relevance filters — SAP UI5 / Fiori / BTP roles in India (0–5 yrs)."""

import re

from sap_job_scout.models import SapJob

SAP_SKILL_RE = re.compile(
    r"\b(sap\s*ui5|sapui5|sap\s*fiori|fiori\s*ui5|sap\s*btp|sap\s*cap|sap\s*capm|"
    r"odata|sap\s*abap|abap\b|s/?4\s*hana|sap\s*labs|sap\s*consultant|"
    r"packaged\s+application|sap\s*frontend|sap\s*web\s*ide|sap\s*business\s+application\s+studio|"
    r"sap\s*integration|sap\s*cloud|sap\s*successfactors|sap\s*ariba|sap\s*ewm|"
    r"sap\s*mm\b|sap\s*sd\b|sap\s*fi\b|sap\s*hr\b|sap\s*basis|sap\s*security)\b",
    re.I,
)

ROLE_RE = re.compile(
    r"\b(developer|engineer|consultant|analyst|programmer|associate|specialist|"
    r"implementation|technical|application|frontend|front[\s-]?end|ui\b|ux\b|"
    r"fresher|graduate|trainee|intern)\b",
    re.I,
)

INDIA_RE = re.compile(
    r"\b(india|indian|bangalore|bengaluru|hyderabad|mumbai|pune|gurgaon|"
    r"gurugram|noida|chennai|kolkata|bhubaneswar|remote\s+india|work\s+from\s+home)\b",
    re.I,
)

EXCLUDE_RE = re.compile(
    r"\b(marketing|sales\s+executive|business\s+development|recruiter|hr\b|"
    r"human\s+resources|mechanical|electrical\s+engineer|civil\s+engineer|"
    r"nurse|doctor|pharma|legal|accountant|ca\b|chartered|warehouse|driver|"
    r"telecaller|bpo|voice\s+process|data\s+entry|graphic\s+design)\b",
    re.I,
)

SENIOR_RE = re.compile(
    r"\b(director|vice\s+president|\bvp\b|head\s+of|chief|principal\s+architect|"
    r"10\+\s*years|12\+\s*years|15\+\s*years|20\+\s*years)\b",
    re.I,
)


def _score(title: str, company: str, location: str) -> int:
    blob = f"{title} {company} {location}".lower()
    score = 0
    if re.search(r"ui5|fiori|sapui5", blob, re.I):
        score += 8
    if re.search(r"odata|btp|cap\b|capm", blob, re.I):
        score += 5
    if re.search(r"abap|s/?4\s*hana", blob, re.I):
        score += 3
    if ROLE_RE.search(title):
        score += 3
    if INDIA_RE.search(blob):
        score += 2
    if re.search(r"consultant|developer|engineer", title, re.I):
        score += 2
    return score


def is_relevant(title: str, company: str, location: str = "", *, india_platform: bool = False) -> bool:
    title = (title or "").strip()
    company = (company or "").strip()
    location = (location or "").strip()
    if not title or EXCLUDE_RE.search(title):
        return False
    if SENIOR_RE.search(title):
        return False

    blob = f"{title} {company} {location}"
    skill_hit = bool(SAP_SKILL_RE.search(blob))
    role_hit = bool(ROLE_RE.search(title))

    # SAP skill in title/company, or SAP title with matching role wording
    if not skill_hit:
        return False
    if not role_hit and not re.search(r"sap", title, re.I):
        return False

    if not (INDIA_RE.search(blob) or india_platform):
        return False
    return True


def make_job(
    title: str,
    company: str,
    location: str,
    url: str,
    source: str,
    *,
    india_platform: bool = False,
) -> SapJob | None:
    title = (title or "").strip()
    company = (company or "").strip() or "Unknown"
    location = (location or "").strip() or "India"
    url = (url or "").strip()
    if not url or not is_relevant(title, company, location, india_platform=india_platform):
        return None
    return SapJob(
        title=title,
        company=company,
        location=location,
        url=url,
        source=source,
        score=_score(title, company, location),
    )


def dedupe_jobs(jobs: list[SapJob]) -> list[SapJob]:
    seen: set[str] = set()
    out: list[SapJob] = []
    for job in sorted(jobs, key=lambda j: (-j.score, j.company, j.title)):
        if job.key in seen:
            continue
        seen.add(job.key)
        out.append(job)
    return out
