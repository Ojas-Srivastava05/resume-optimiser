"""Local email enrichment for LinkedIn profiles — no API keys, web + optional SMTP verify."""

from __future__ import annotations

import random
import re
import smtplib
import socket
import subprocess
import time
import urllib.request
from dataclasses import dataclass

from cold_email.config import SMTP_VERIFY_TIMEOUT_SEC
from cold_email.linkedin_search import USER_AGENT, web_search
from cold_email.mx_check import has_mx_record

EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
SMTP_PORT = 25
GENERIC_LOCALS = frozenset(
	{"careers", "jobs", "hr", "recruiting", "talent", "hiring", "info", "contact", "support", "hello"}
)


@dataclass
class EnrichedEmail:
	email: str
	first_name: str
	last_name: str
	verification: str  # hunter | web_public | smtp | web_smtp
	confidence: int
	linkedin_url: str
	source_id: str = "linkedin:verified"


def enrichment_available() -> bool:
	from cold_email.hunter import hunter_configured

	return hunter_configured() or True


_smtp_usable: bool | None = None


def _smtp_available() -> bool:
	global _smtp_usable
	if _smtp_usable is not None:
		return _smtp_usable
	try:
		with socket.create_connection(("gmail-smtp-in.l.google.com", SMTP_PORT), timeout=4):
			_smtp_usable = True
	except OSError:
		_smtp_usable = False
	return _smtp_usable


def _email_matches_name(email: str, first: str, last: str) -> bool:
	local = email.split("@", 1)[0].lower()
	f = _normalize_token(first)
	l = _normalize_token(last)
	if len(local) < 4 or local in GENERIC_LOCALS:
		return False
	if f and l and (f"{f}.{l}" == local or f"{f}{l}" == local or f"{f[0]}{l}" == local):
		return True
	if l and len(l) >= 4 and l in local:
		return True
	if f and len(f) >= 4 and f in local:
		return True
	if f and l and f[0] in local and l[:4] in local:
		return True
	return False


def _mx_hosts(domain: str) -> list[str]:
	try:
		out = subprocess.check_output(
			["dig", "+short", "MX", domain],
			timeout=8,
			text=True,
			stderr=subprocess.DEVNULL,
		)
	except (OSError, subprocess.SubprocessError):
		return []
	hosts: list[tuple[int, str]] = []
	for line in out.splitlines():
		parts = line.strip().split()
		if len(parts) >= 2 and parts[1].endswith("."):
			try:
				priority = int(parts[0])
			except ValueError:
				priority = 10
			hosts.append((priority, parts[1].rstrip(".")))
	hosts.sort(key=lambda x: x[0])
	return [h for _, h in hosts]


def _smtp_rcpt_valid(email: str) -> bool:
	domain = email.split("@", 1)[1]
	for host in _mx_hosts(domain)[:2]:
		try:
			with smtplib.SMTP(host, SMTP_PORT, timeout=SMTP_VERIFY_TIMEOUT_SEC) as smtp:
				smtp.ehlo_or_helo_if_needed()
				smtp.mail("verify@example.com")
				code, _ = smtp.rcpt(email)
				return 200 <= code < 300
		except (OSError, smtplib.SMTPException):
			continue
	return False


def _is_catch_all(domain: str) -> bool:
	fake = f"notreal{random.randint(100000, 999999)}@{domain}"
	return _smtp_rcpt_valid(fake)


def _normalize_token(value: str) -> str:
	return re.sub(r"[^a-z]", "", value.lower())


def generate_patterns(first: str, last: str, domain: str) -> list[str]:
	f = _normalize_token(first)
	l = _normalize_token(last)
	if not f or not l or not domain:
		return []
	patterns = [
		f"{f}.{l}@{domain}",
		f"{f}{l}@{domain}",
		f"{f[0]}{l}@{domain}",
		f"{f}@{domain}",
	]
	seen: set[str] = set()
	out: list[str] = []
	for p in patterns:
		p = p.lower()
		if p not in seen:
			seen.add(p)
			out.append(p)
	return out


def _fetch_page_text(url: str, *, max_chars: int = 8000) -> str:
	if not url.startswith("http"):
		return ""
	reader_url = f"https://r.jina.ai/{url}"
	req = urllib.request.Request(reader_url, headers={"User-Agent": USER_AGENT})
	try:
		with urllib.request.urlopen(req, timeout=20) as resp:
			return resp.read().decode("utf-8", errors="replace")[:max_chars]
	except OSError:
		return ""


def _web_emails(name: str, domain: str, linkedin_url: str) -> list[str]:
	slug = linkedin_url.rstrip("/").split("/")[-1]
	queries = [
		f'"{name}" "@{domain}"',
		f'"{name}" {domain} email',
		f"site:linkedin.com/in/{slug} email",
		f'"{name}" "{domain}" mail',
	]
	found: list[str] = []
	seen: set[str] = set()
	for query in queries:
		for title, page_url, snippet in web_search(query, max_results=8):
			for match in EMAIL_RE.findall(f"{title} {snippet}"):
				email = match.lower()
				if email.endswith(f"@{domain}") and email not in seen:
					seen.add(email)
					found.append(email)
			if page_url and domain in page_url:
				continue
			page_text = _fetch_page_text(page_url)
			for match in EMAIL_RE.findall(page_text):
				email = match.lower()
				if email.endswith(f"@{domain}") and email not in seen:
					seen.add(email)
					found.append(email)
		time.sleep(0.4)
	return found


def verify_email(email: str) -> tuple[bool, str]:
	if not has_mx_record(email.split("@", 1)[1]):
		return False, "mx_fail"
	if _smtp_available() and _smtp_rcpt_valid(email):
		return True, "smtp_ok"
	return True, "mx_ok_public"


def enrich_from_linkedin(
	*,
	linkedin_url: str,
	full_name: str,
	company: str,
	domain: str,
) -> EnrichedEmail | None:
	parts = full_name.strip().split()
	if len(parts) < 2:
		return None
	first, last = parts[0], parts[-1]
	domain = (domain or "").strip().lower()
	if not domain:
		return None
	if not has_mx_record(domain):
		return None

	# 0) Hunter.io — LinkedIn URL + name + domain (primary)
	try:
		from cold_email.hunter import (
			HunterError,
			find_email,
			hunter_configured,
			is_acceptable,
			verify_email as hunter_verify,
		)

		if hunter_configured():
			found = find_email(
				linkedin_url=linkedin_url,
				first_name=first,
				last_name=last,
				domain=domain,
				company=company,
			)
			if found:
				status = (found.status or "").lower()
				score = found.score
				if status not in {"valid", "accept_all"}:
					try:
						status, vscore = hunter_verify(found.email)
						score = max(score, vscore)
					except HunterError:
						pass
				if is_acceptable(found, verified_status=status):
					display_first = found.first_name or first
					display_last = found.last_name or last
					return EnrichedEmail(
						email=found.email,
						first_name=display_first,
						last_name=display_last,
						verification="hunter",
						confidence=max(score, 90),
						linkedin_url=linkedin_url,
						source_id="linkedin:hunter_verified",
					)
	except Exception:
		pass

	# 1) Emails found on public web tied to this person
	for email in _web_emails(full_name, domain, linkedin_url):
		if not _email_matches_name(email, first, last):
			continue
		ok, status = verify_email(email)
		if not ok:
			continue
		confidence = 92 if status == "smtp_ok" else 86
		return EnrichedEmail(
			email=email,
			first_name=first,
			last_name=last,
			verification="web_smtp" if status == "smtp_ok" else "web_public",
			confidence=confidence,
			linkedin_url=linkedin_url,
		)

	# 2) Pattern + SMTP (only when outbound port 25 works — e.g. GitHub Actions)
	if not _smtp_available():
		return None

	catch_all = _is_catch_all(domain)
	for email in generate_patterns(first, last, domain):
		if not _email_matches_name(email, first, last):
			continue
		if _smtp_rcpt_valid(email):
			if catch_all:
				continue
			return EnrichedEmail(
				email=email,
				first_name=first,
				last_name=last,
				verification="smtp",
				confidence=88,
				linkedin_url=linkedin_url,
			)
		time.sleep(0.1)

	return None
