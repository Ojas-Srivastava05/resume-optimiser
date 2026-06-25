"""Shared internet contact discovery helpers."""

from __future__ import annotations

import re
import urllib.parse
import urllib.request
from urllib.parse import urljoin, urlparse

from cold_email.mx_check import has_mx_record
from config import COMPANY_DOMAIN_OVERRIDES, TARGET_INTERNSHIP_YEAR, TARGET_SEASON
from scripts.extract import (
	classify_contact,
	clean_email,
	domain_from_url,
	extract_emails_from_text,
	norm_company,
)

USER_AGENT = "HiringContactsDiscover/1.1 (+resume-optimiser)"
MAX_HTML_BYTES = 750_000
FETCH_TIMEOUT = 12

HIRING_LOCAL_RE = re.compile(
	r"(recruit|talent|career|campus|university|hr|hiring|intern|people|jobs|acquisition|"
	r"early|emerging|graduate|universityrelations|campusrecruiting)",
	re.I,
)

CAREER_PATH_SUFFIXES = (
	"/careers",
	"/careers/",
	"/jobs",
	"/jobs/",
	"/campus",
	"/campus-recruiting",
	"/university",
	"/contact",
	"/contact-us",
	"/about/careers",
	"/company/careers",
)

CAREER_HREF_RE = re.compile(
	r"""href=["']([^"']*(?:career|campus|recruit|talent|university|jobs|contact|hiring)[^"']*)["']""",
	re.I,
)

FREEMAIL = frozenset({"gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "icloud.com"})

DOMAIN_FALLBACK_PREFIXES = (
	"careers",
	"talent",
	"campus",
	"university",
	"recruiting",
	"hr",
	"jobs",
	"hiring",
	"interns",
	"emergingtalent",
	"earlycareers",
	"graduates",
)


def company_domain(company: str, portal: str) -> str | None:
	key = norm_company(company)
	if key in COMPANY_DOMAIN_OVERRIDES:
		return COMPANY_DOMAIN_OVERRIDES[key]
	domain = domain_from_url(portal)
	if domain:
		return domain
	base = re.sub(r"[^a-z0-9]", "", (company or "").lower())
	if len(base) >= 3:
		return f"{base}.com"
	return None


SKIP_FETCH_HOSTS = ("google.com", "bing.com", "linkedin.com")
MEGA_FETCH_HOSTS = ("amazon.com", "apple.com", "microsoft.com", "google.com", "meta.com", "facebook.com")


def fetch_url_text(url: str) -> str:
	if not url or not url.startswith("http"):
		return ""
	try:
		host = urlparse(url).netloc.lower()
	except Exception:
		return ""
	if any(h in host for h in SKIP_FETCH_HOSTS):
		return ""
	if any(h in host for h in MEGA_FETCH_HOSTS):
		return ""
	req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
	try:
		with urllib.request.urlopen(req, timeout=FETCH_TIMEOUT) as resp:
			final = resp.geturl()
			data = resp.read(MAX_HTML_BYTES)
		text = data.decode("utf-8", errors="replace")
		# Greenhouse / Lever boards often embed contact emails in JSON blobs.
		return text
	except OSError:
		return ""


def _root_site(portal: str) -> str | None:
	try:
		parsed = urlparse(portal)
		if not parsed.scheme or not parsed.netloc:
			return None
		return f"{parsed.scheme}://{parsed.netloc}"
	except Exception:
		return None


def candidate_urls(company: str, portal: str, *, max_urls: int = 4) -> list[str]:
	seen: set[str] = set()
	out: list[str] = []

	def add(url: str) -> None:
		if not url or not url.startswith("http"):
			return
		try:
			host = urlparse(url).netloc.lower()
		except Exception:
			return
		if any(h in host for h in SKIP_FETCH_HOSTS):
			return
		norm = url.split("#")[0].rstrip("/")
		if norm in seen:
			return
		seen.add(norm)
		out.append(url if url.endswith("/") or "?" in url else norm)

	if portal.startswith("http"):
		add(portal)

	root = _root_site(portal)
	if root:
		for suffix in CAREER_PATH_SUFFIXES:
			if len(out) >= max_urls:
				break
			add(urljoin(root, suffix))

	domain = company_domain(company, portal)
	if domain and len(out) < max_urls:
		for scheme in ("https", "http"):
			add(f"{scheme}://{domain}/careers")
			add(f"{scheme}://www.{domain}/careers")
			if len(out) >= max_urls:
				break

	return out[:max_urls]


def follow_career_links(base_url: str, html: str, *, max_links: int = 2) -> list[str]:
	if not html:
		return []
	base_host = urlparse(base_url).netloc
	found: list[str] = []
	for href in CAREER_HREF_RE.findall(html):
		if len(found) >= max_links:
			break
		abs_url = urljoin(base_url, href)
		parsed = urlparse(abs_url)
		if parsed.scheme not in {"http", "https"}:
			continue
		if parsed.netloc and base_host and parsed.netloc != base_host:
			# Allow greenhouse/lever/ashby job boards on other hosts.
			if not any(h in parsed.netloc for h in ("greenhouse.io", "lever.co", "ashbyhq.com", "myworkdayjobs.com")):
				continue
		found.append(abs_url.split("#")[0])
	return found


def is_hiring_email(email: str, company_domain_hint: str | None = None) -> bool:
	local = email.split("@", 1)[0]
	domain = email.split("@", 1)[1] if "@" in email else ""
	if domain in FREEMAIL:
		return HIRING_LOCAL_RE.search(local) is not None
	if HIRING_LOCAL_RE.search(local):
		return True
	if company_domain_hint and domain.endswith(company_domain_hint.split(".", 1)[-1]):
		return "." in local and len(local) > 3
	return "." in local and len(local) > 3 and HIRING_LOCAL_RE.search(email) is not None


def contact_row(
	email: str,
	company: str,
	confidence: str,
	contact_type: str,
	source_url: str,
	fetched_at: str,
	notes: str,
	*,
	source_id: str = "discover:career_portal",
) -> dict:
	return {
		"email": email,
		"name": "",
		"company": company,
		"company_normalized": norm_company(company),
		"role_title": "",
		"contact_type": contact_type,
		"confidence": confidence,
		"in_scout_list": "True",
		"source_id": source_id,
		"source_url": source_url,
		"country": "India",
		"target_internship_year": str(TARGET_INTERNSHIP_YEAR),
		"target_season": TARGET_SEASON,
		"notes": notes,
		"fetched_at": fetched_at,
	}


def domain_fallback_rows(
	company: str,
	portal: str,
	fetched_at: str,
	*,
	existing: set[str],
) -> list[dict]:
	domain = company_domain(company, portal)
	if not domain or not has_mx_record(domain):
		return []
	rows: list[dict] = []
	for prefix in DOMAIN_FALLBACK_PREFIXES:
		email = clean_email(f"{prefix}@{domain}")
		if not email or email in existing:
			continue
		ctype, conf = classify_contact(email)
		if conf == "generic":
			conf = "public_listed"
		rows.append(
			contact_row(
				email,
				company,
				conf,
				ctype,
				portal,
				fetched_at,
				f"domain_fallback:{prefix};mx_ok",
			)
		)
	return rows


def discover_company(company: str, portal: str, fetched_at: str) -> list[dict]:
	domain_hint = company_domain(company, portal)
	rows: list[dict] = []
	seen_emails: set[str] = set()
	scraped_count = 0

	urls = candidate_urls(company, portal)
	fetched_pages: list[tuple[str, str]] = []

	for url in urls:
		text = fetch_url_text(url)
		if text:
			fetched_pages.append((url, text))
			for extra in follow_career_links(url, text):
				if extra not in urls:
					urls.append(extra)
			if len(fetched_pages) >= 4:
				break

	for page_url, text in fetched_pages:
		for email in extract_emails_from_text(text):
			if email in seen_emails or not is_hiring_email(email, domain_hint):
				continue
			seen_emails.add(email)
			ctype, conf = classify_contact(email)
			if conf == "generic":
				conf = "public_listed"
			if ctype == "unknown" and conf == "scraped":
				conf = "public_listed"
			# Named person at company domain = higher value.
			if "." in email.split("@", 1)[0] and email.split("@", 1)[1] not in FREEMAIL:
				if HIRING_LOCAL_RE.search(email) or (domain_hint and email.endswith(domain_hint)):
					conf = "scraped_personal"
					ctype = "recruiter"
			rows.append(
				contact_row(
					email,
					company,
					conf,
					ctype,
					page_url,
					fetched_at,
					"career_portal_scrape",
				)
			)
			scraped_count += 1

	# Only guess inboxes when live scrape found nothing — but MX must exist.
	if scraped_count == 0:
		for fallback in domain_fallback_rows(company, portal, fetched_at, existing=seen_emails):
			rows.append(fallback)
			seen_emails.add(fallback["email"])

	return rows
