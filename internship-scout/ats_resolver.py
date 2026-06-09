"""Discover Greenhouse / Lever / Ashby board slugs for companies."""

import json
import re
import time
from pathlib import Path

import requests

from companies import _norm, load_companies
from config import ROOT

CACHE_PATH = ROOT / "data" / "ats_cache.json"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; InternshipScout/1.0)"}


def _load_cache() -> dict:
    if CACHE_PATH.exists():
        return json.loads(CACHE_PATH.read_text())
    return {"greenhouse": {}, "lever": {}, "ashby": {}}


def _save_cache(cache: dict) -> None:
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    CACHE_PATH.write_text(json.dumps(cache, indent=2))


def _probe(url: str) -> bool:
    try:
        r = requests.get(url, headers=HEADERS, timeout=8)
        return r.status_code == 200 and len(r.content) > 50
    except requests.RequestException:
        return False


def _slug_candidates(name: str) -> list[str]:
    base = _norm(name)
    cands = [base]
    # drop common suffixes
    for suffix in ("india", "labs", "global", "technologies", "technology", "corp"):
        if base.endswith(suffix) and len(base) > len(suffix) + 3:
            cands.append(base[: -len(suffix)])
    # hyphenated from words
    words = re.findall(r"[a-z0-9]+", name.lower())
    if len(words) > 1:
        cands.append("".join(words))
        cands.append("-".join(words))
    out: list[str] = []
    seen: set[str] = set()
    for c in cands:
        c = re.sub(r"[^a-z0-9-]", "", c)
        if c and c not in seen:
            seen.add(c)
            out.append(c)
    return out


def resolve_slugs(*, max_new: int = 80) -> dict:
    """Probe ATS APIs for companies missing slugs; update cache + company JSON."""
    cache = _load_cache()
    companies = load_companies()
    probed = 0

    for c in companies:
        if probed >= max_new:
            break
        name = c["name"]
        key = _norm(name)
        if c.get("gh_slug") or cache["greenhouse"].get(key):
            continue

        for slug in _slug_candidates(name):
            gh_url = f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs"
            if _probe(gh_url):
                cache["greenhouse"][key] = {"slug": slug, "company": name}
                c["gh_slug"] = slug
                probed += 1
                break

            lev_url = f"https://api.lever.co/v0/postings/{slug}?mode=json"
            if _probe(lev_url):
                cache["lever"][key] = {"slug": slug, "company": name}
                c["lever_slug"] = slug
                probed += 1
                break

            ash_url = f"https://api.ashbyhq.com/posting-api/job-board/{slug}"
            if _probe(ash_url):
                cache["ashby"][key] = {"slug": slug, "company": name}
                c["ashby_slug"] = slug
                probed += 1
                break

            time.sleep(0.05)

    _save_cache(cache)

    # persist slugs back into priority_companies.json
    json_path = ROOT / "data" / "priority_companies.json"
    if json_path.exists():
        data = json.loads(json_path.read_text())
        by_key = {_norm(c["name"]): c for c in companies}
        for i, row in enumerate(data.get("companies", [])):
            k = _norm(row["name"])
            if k in by_key:
                for field in ("gh_slug", "lever_slug", "ashby_slug"):
                    if by_key[k].get(field):
                        data["companies"][i][field] = by_key[k][field]
        json_path.write_text(json.dumps(data, indent=2))

    return cache
