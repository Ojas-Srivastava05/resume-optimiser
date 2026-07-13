"""Resolve scout company names to corporate email domains."""

from __future__ import annotations

import re
from urllib.parse import urlparse

from config import COMPANY_DOMAIN_OVERRIDES
from cold_email.mx_check import has_mx_record

SKIP_HOSTS = frozenset(
	{
		"google.com",
		"www.google.com",
		"bing.com",
		"linkedin.com",
		"www.linkedin.com",
		"in.linkedin.com",
		"facebook.com",
		"twitter.com",
		"x.com",
		"youtube.com",
		"glassdoor.com",
		"indeed.com",
		"naukri.com",
		"unstop.com",
	}
)

ATS_HOST_SUFFIXES = (
	".avature.net",
	".myworkdayjobs.com",
	".greenhouse.io",
	".lever.co",
	".dejobs.org",
	".smartrecruiters.com",
	".bamboohr.com",
	".icims.com",
	".taleo.net",
	".jobvite.com",
	".successfactors.com",
	".oraclecloud.com",
)


def _is_unusable_portal_host(host: str, company_key: str) -> bool:
	if not host or host in SKIP_HOSTS:
		return True
	if host.endswith(".linkedin.com"):
		return True
	if host == "careers.google.com" and company_key != "google":
		return True
	return any(host.endswith(suffix) for suffix in ATS_HOST_SUFFIXES)


def norm_company(name: str) -> str:
	return re.sub(r"[^a-z0-9]", "", (name or "").lower())


def domain_from_portal(portal_url: str, company_key: str = "") -> str:
	if not portal_url:
		return ""
	try:
		host = urlparse(portal_url.strip()).netloc.lower()
	except ValueError:
		return ""
	host = host.removeprefix("www.")
	if _is_unusable_portal_host(host, company_key):
		return ""
	return host


def guess_domain_from_name(company_key: str) -> str:
	if not company_key or len(company_key) < 3:
		return ""
	candidates = [
		f"{company_key}.com",
		f"{company_key}.in",
		f"{company_key}.co.in",
		f"{company_key}.io",
	]
	for domain in candidates:
		if has_mx_record(domain):
			return domain
	return ""


def resolve_company_domain(company: str, career_portal: str = "") -> str:
	key = norm_company(company)
	if key in COMPANY_DOMAIN_OVERRIDES:
		return COMPANY_DOMAIN_OVERRIDES[key]
	portal_domain = domain_from_portal(career_portal, key)
	if portal_domain:
		return portal_domain
	return guess_domain_from_name(key)
