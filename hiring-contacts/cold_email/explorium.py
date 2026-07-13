"""Explorium AgentSource API — HR recruiter discovery + contact enrichment."""

from __future__ import annotations

import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass

from cold_email.config import EXPLORIUM_API_KEY

API_BASE = "https://api.explorium.ai/v1"
USER_AGENT = "ResumeOptimiser-HiringContacts/1.0"

RECRUITER_POSITION_RE = re.compile(
	r"(recruit|talent|hiring|\bhr\b|people ops|people partner|campus|university|staffing|sourcer|acquisition|human resources)",
	re.I,
)
LINKEDIN_SLUG_RE = re.compile(r"linkedin\.com/in/([a-zA-Z0-9\-_%]+)", re.I)
LINKEDIN_INTERNAL_RE = re.compile(r"^ACoA", re.I)


@dataclass
class ExploriumRecruiter:
	email: str
	first_name: str
	last_name: str
	position: str
	linkedin_url: str
	email_status: str
	prospect_id: str


class ExploriumError(RuntimeError):
	pass


def explorium_configured() -> bool:
	return bool(EXPLORIUM_API_KEY)


def _post(path: str, payload: dict) -> dict:
	if not EXPLORIUM_API_KEY:
		raise ExploriumError("EXPLORIUM_API_KEY not configured")
	url = f"{API_BASE}{path}"
	body = json.dumps(payload).encode("utf-8")
	req = urllib.request.Request(
		url,
		data=body,
		method="POST",
		headers={
			"api_key": EXPLORIUM_API_KEY,
			"Content-Type": "application/json",
			"User-Agent": USER_AGENT,
		},
	)
	try:
		with urllib.request.urlopen(req, timeout=45) as resp:
			data = json.loads(resp.read().decode("utf-8"))
	except urllib.error.HTTPError as exc:
		body = exc.read().decode("utf-8", errors="replace")
		try:
			detail = json.loads(body).get("details", body)
		except json.JSONDecodeError:
			detail = body
		raise ExploriumError(f"Explorium API HTTP {exc.code}: {detail}") from exc
	except OSError as exc:
		raise ExploriumError(f"Explorium API request failed: {exc}") from exc
	ctx = data.get("response_context") or {}
	if (ctx.get("request_status") or "").lower() == "failure":
		raise ExploriumError(f"Explorium API failure: {data}")
	return data


def _normalize_linkedin(url: str) -> str:
	url = (url or "").strip()
	if not url:
		return ""
	if not url.startswith("http"):
		url = f"https://{url.lstrip('/')}"
	return url.split("?", 1)[0].rstrip("/")


def _best_linkedin_url(prospect: dict) -> str:
	candidates: list[str] = []
	for key in ("linkedin_url_array",):
		for raw in prospect.get(key) or []:
			if raw:
				candidates.append(str(raw))
	raw = prospect.get("linkedin") or ""
	if raw:
		candidates.insert(0, str(raw))

	slug_urls: list[str] = []
	other_urls: list[str] = []
	for raw in candidates:
		url = _normalize_linkedin(raw)
		if not url or "linkedin.com/in/" not in url.lower():
			continue
		match = LINKEDIN_SLUG_RE.search(url)
		slug = match.group(1) if match else ""
		if slug and LINKEDIN_INTERNAL_RE.match(slug):
			other_urls.append(url)
		else:
			slug_urls.append(url)
	return slug_urls[0] if slug_urls else (other_urls[0] if other_urls else "")


def match_business(*, name: str, domain: str) -> str | None:
	payload = {
		"businesses_to_match": [
			{
				"name": name,
				"domain": domain,
			}
		]
	}
	data = _post("/businesses/match", payload)
	matched = (data.get("matched_businesses") or [{}])[0]
	business_id = matched.get("business_id")
	return business_id if business_id else None


def _fetch_hr_prospects(business_id: str, *, limit: int = 10) -> list[dict]:
	data = _post(
		"/prospects",
		{
			"mode": "full",
			"size": limit,
			"page_size": min(limit, 100),
			"page": 1,
			"filters": {
				"business_id": {"values": [business_id]},
				"job_department": {"values": ["human resources"]},
				"has_email": {"value": True},
			},
		},
	)
	return list(data.get("data") or [])


def _enrich_contact(prospect_id: str) -> dict:
	data = _post(
		"/prospects/contacts_information/enrich",
		{"prospect_id": prospect_id},
	)
	return data.get("data") or {}


def _is_recruiter_title(title: str) -> bool:
	return bool(RECRUITER_POSITION_RE.search(title or ""))


def _acceptable_email_status(status: str) -> bool:
	return (status or "").strip().lower() in {"valid", "accept_all"}


def _email_matches_company_domain(email: str, domain: str) -> bool:
	email_domain = email.split("@", 1)[1].lower()
	domain = domain.lower().removeprefix("www.")
	if email_domain == domain:
		return True
	base = domain.split(".", 1)[0]
	email_base = email_domain.split(".", 1)[0]
	return base == email_base and len(base) >= 4


def find_company_recruiters(
	*,
	company: str,
	domain: str,
	limit: int = 3,
) -> list[ExploriumRecruiter]:
	"""Match business → fetch HR prospects → enrich emails (per-person credits)."""
	if not domain:
		return []

	business_id = match_business(name=company, domain=domain)
	if not business_id:
		return []

	prospects = _fetch_hr_prospects(business_id, limit=12)
	out: list[ExploriumRecruiter] = []

	for prospect in prospects:
		if len(out) >= limit:
			break
		title = (prospect.get("job_title") or "").strip()
		if not _is_recruiter_title(title):
			continue
		first = (prospect.get("first_name") or "").strip()
		last = (prospect.get("last_name") or "").strip()
		if not first:
			continue
		linkedin = _best_linkedin_url(prospect)
		if not linkedin:
			continue
		prospect_id = (prospect.get("prospect_id") or "").strip()
		if not prospect_id:
			continue

		try:
			contact = _enrich_contact(prospect_id)
		except ExploriumError:
			continue

		email = (contact.get("professions_email") or "").strip().lower()
		if not email:
			for row in contact.get("emails") or []:
				if (row.get("type") or "").startswith("current_professional"):
					email = (row.get("address") or "").strip().lower()
					break
		if not email or "@" not in email:
			continue
		if not _email_matches_company_domain(email, domain):
			continue

		status = (contact.get("professional_email_status") or "").strip().lower()
		if status == "invalid":
			continue
		if not _acceptable_email_status(status):
			continue

		out.append(
			ExploriumRecruiter(
				email=email,
				first_name=first,
				last_name=last or "",
				position=title,
				linkedin_url=linkedin,
				email_status=status or "valid",
				prospect_id=prospect_id,
			)
		)
		time.sleep(0.15)

	return out
