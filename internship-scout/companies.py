"""Priority company list from referral sheet + name matching."""

import json
import re
from functools import lru_cache
from pathlib import Path

from config import ROOT

DATA_PATH = ROOT / "data" / "priority_companies.json"

# Greenhouse board slug → canonical company name on the sheet
KNOWN_GH_SLUGS: dict[str, str] = {
    "groww": "Groww",
    "phonepe": "PhonePe",
    "slice": "Slice",
    "stripe": "Stripe",
    "block": "Block",
    "robinhood": "Robinhood",
    "sofi": "SoFi",
    "brex": "Brex",
    "airbnb": "Airbnb",
    "databricks": "Databricks",
    "coinbase": "Coinbase",
    "plaid": "Plaid",
    "ramp": "Ramp",
    "mongodb": "MongoDB",
    "datadog": "Datadog",
    "anthropic": "Anthropic",
    "okta": "Okta",
    "janestreet": "Jane Street",
    "pinterest": "Pinterest",
    "cloudflare": "Cloudflare",
    "figma": "Figma",
    "elastic": "Elastic",
    "affirm": "Affirm",
    "reddit": "Reddit",
    "twilio": "Twilio",
    "gitlab": "GitLab",
    "asana": "Asana",
    "lyft": "Lyft",
    "imc": "IMC",
    "gusto": "Gusto",
    "vercel": "Vercel",
    "thoughtworks": "Thoughtworks",
    "discord": "Discord",
    "postman": "Postman",
    "worldquant": "WorldQuant",
    "davinciderivatives": "Da Vinci",
    "quberesearchandtechnologies": "Qube Research & Technologies",
    "citadel": "Citadel",
    "optiver": "Optiver",
    "jumptrading": "Jump Trading",
    "twosigma": "Two Sigma",
    "hudsonrivertrading": "Hudson River Trading",
    "virtu": "Virtu",
    "akuna": "Akuna Capital",
    "towerresearchcapital": "Tower Research Capital",
    "quadeye": "Quadeye",
    "gravitonresearchcapital": "Graviton",
    "alphagrep": "AlphaGrep",
    "deutschebank": "Deutsche Bank",
    "goldmansachs": "Goldman Sachs",
    "jpmorgan": "JPMorgan",
    "morganstanley": "Morgan Stanley",
    "barclays": "Barclays",
    "atlassian": "Atlassian",
    "browserstack": "BrowserStack",
    "chargebee": "Chargebee",
    "freshworks": "Freshworks",
    "zoho": "Zoho",
    "druva": "Druva",
    "cred": "CRED",
}


def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


def load_companies() -> list[dict]:
    if not DATA_PATH.exists():
        return []
    data = json.loads(DATA_PATH.read_text())
    return data.get("companies", [])


def _lookup_by_norm() -> dict[str, dict]:
    out: dict[str, dict] = {}
    for c in load_companies():
        out[_norm(c["name"])] = c
    return out


def _fuzzy_match(a: str, b: str) -> bool:
    """Match exact or close variants (Amazon / Amazon India), not unrelated substrings."""
    if a == b:
        return True
    if len(a) < 4 or len(b) < 4:
        return False
    if a.startswith(b) or b.startswith(a):
        return abs(len(a) - len(b)) <= 8
    return False


def match_priority_company(name: str) -> dict | None:
    """Return sheet entry if job company matches a priority company."""
    if not name:
        return None
    lookup = _lookup_by_norm()
    n = _norm(name)
    if n in lookup:
        return lookup[n]
    for key, entry in lookup.items():
        if _fuzzy_match(n, key):
            return entry
    return None


def greenhouse_slugs() -> dict[str, str]:
    """slug → display company name for boards we should poll."""
    slugs: dict[str, str] = dict(KNOWN_GH_SLUGS)
    cache_path = ROOT / "data" / "ats_cache.json"
    if cache_path.exists():
        cache = json.loads(cache_path.read_text())
        for info in cache.get("greenhouse", {}).values():
            slugs[info["slug"]] = info["company"]
    for c in load_companies():
        if c.get("gh_slug"):
            slugs[c["gh_slug"]] = c["name"]
    return slugs


def company_names_for_search() -> list[str]:
    return [c["name"] for c in load_companies()]
