"""Hunter.io email finder + verifier for LinkedIn-sourced contacts."""

from __future__ import annotations

import json
import re
import urllib.parse
import urllib.request
from dataclasses import dataclass

from cold_email.config import HUNTER_API_KEY, HUNTER_MIN_SCORE

API_BASE = "https://api.hunter.io/v2"
USER_AGENT = "ResumeOptimiser-HiringContacts/1.0"

RECRUITER_POSITION_RE = re.compile(
	r"(recruit|talent|hiring|\bhr\b|people ops|people partner|campus|university|staffing|sourcer|acquisition|human resources)",
	re.I,
)


@dataclass
class HunterEmailResult:
	email: str
	score: int
	status: str
	linkedin_url: str
	first_name: str
	last_name: str
	position: str


@dataclass
class HunterRecruiter:
	email: str
	first_name: str
	last_name: str
	position: str
	linkedin_url: str
	score: int
	status: str


class HunterError(RuntimeError):
	pass


def hunter_configured() -> bool:
	return bool(HUNTER_API_KEY)


def _get(path: str, params: dict) -> dict:
	if not HUNTER_API_KEY:
		raise HunterError("HUNTER_API_KEY not configured")
	params = {**params, "api_key": HUNTER_API_KEY}
	url = f"{API_BASE}{path}?{urllib.parse.urlencode(params)}"
	req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
	try:
		with urllib.request.urlopen(req, timeout=25) as resp:
			payload = json.loads(resp.read().decode("utf-8"))
	except OSError as exc:
		raise HunterError(f"Hunter API request failed: {exc}") from exc
	if payload.get("errors"):
		msg = payload["errors"][0].get("details", str(payload["errors"]))
		raise HunterError(str(msg))
	return payload.get("data") or {}


def find_email(
	*,
	linkedin_url: str = "",
	first_name: str = "",
	last_name: str = "",
	domain: str = "",
	company: str = "",
) -> HunterEmailResult | None:
	params: dict[str, str] = {}
	if linkedin_url:
		params["linkedin_url"] = linkedin_url
	if first_name:
		params["first_name"] = first_name
	if last_name:
		params["last_name"] = last_name
	if domain:
		params["domain"] = domain
	elif company:
		params["company"] = company
	if not params.get("linkedin_url"):
		if not (params.get("domain") or params.get("company")):
			return None
		if not (first_name and last_name):
			return None

	data = _get("/email-finder", params)
	email = (data.get("email") or "").strip().lower()
	if not email:
		return None
	verification = data.get("verification", {}) or {}
	status = verification.get("status") or data.get("status") or ""
	return HunterEmailResult(
		email=email,
		score=int(data.get("score") or 0),
		status=status,
		linkedin_url=linkedin_url or data.get("linkedin_url") or "",
		first_name=data.get("first_name") or first_name,
		last_name=data.get("last_name") or last_name,
		position=data.get("position") or "",
	)


def verify_email(email: str) -> tuple[str, int]:
	data = _get("/email-verifier", {"email": email})
	return (data.get("status") or "", int(data.get("score") or 0))


def is_acceptable(result: HunterEmailResult, *, verified_status: str = "") -> bool:
	score = max(result.score, 0)
	status = (verified_status or result.status or "").lower()
	if status in {"invalid", "disposable", "webmail"}:
		return False
	if status == "valid":
		return score >= max(HUNTER_MIN_SCORE - 10, 70)
	return score >= HUNTER_MIN_SCORE


def find_company_recruiters(
	domain: str,
	*,
	company: str = "",
	limit: int = 10,
) -> list[HunterRecruiter]:
	"""Hunter domain search — HR/talent emails with LinkedIn URLs (1 credit per domain)."""
	if not domain:
		return []
	data = _get(
		"/domain-search",
		{
			"domain": domain,
			"department": "hr",
			"limit": str(limit),
		},
	)
	out: list[HunterRecruiter] = []
	for row in data.get("emails") or []:
		email = (row.get("value") or "").strip().lower()
		if not email:
			continue
		position = (row.get("position") or row.get("position_raw") or "").strip()
		if not RECRUITER_POSITION_RE.search(position):
			continue
		verification = row.get("verification") or {}
		status = (verification.get("status") or "").lower()
		score = int(row.get("confidence") or 0)
		if status == "invalid":
			continue
		if score < HUNTER_MIN_SCORE and status != "valid":
			continue
		first = (row.get("first_name") or "").strip()
		last = (row.get("last_name") or "").strip()
		if not first or not last:
			continue
		linkedin = (row.get("linkedin") or "").strip()
		if not linkedin or "linkedin.com/in/" not in linkedin:
			continue
		out.append(
			HunterRecruiter(
				email=email,
				first_name=first,
				last_name=last,
				position=position,
				linkedin_url=linkedin,
				score=score,
				status=status or "valid",
			)
		)
	return out
