"""Email and contact extraction utilities."""

from __future__ import annotations

import csv
import hashlib
import io
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable
from urllib.parse import urlparse

EMAIL_RE = re.compile(r"\b[A-Za-z0-9][A-Za-z0-9._%+-]*@[A-Za-z0-9][A-Za-z0-9.-]*\.[A-Za-z]{2,}\b")
MAILTO_RE = re.compile(r"mailto:([^\s\"'>)]+)", re.I)

# Obfuscated patterns: name [at] domain [dot] com
OBFUSCATED_RE = re.compile(
	r"\b([A-Za-z0-9._%+-]+)\s*(?:\[at\]|@|\(at\))\s*([A-Za-z0-9.-]+)\s*(?:\[dot\]|\.|\(dot\))\s*([A-Za-z]{2,})\b",
	re.I,
)

SKIP_EMAIL_DOMAINS = {
	"example.com",
	"leetcode.com",
	"mail.com",
	"gmail.com",  # personal gmail from blog lists — keep but lower confidence
	"yahoo.com",
	"hotmail.com",
	"outlook.com",
	"sentry.io",
	"w3.org",
}

HIRING_KEYWORDS = re.compile(
	r"\b(recruit|talent|hr|hiring|campus|university|people|careers|jobs|acquisition|sourcer|staffing)\b",
	re.I,
)

ROLE_TITLE_RE = re.compile(
	r"\b((?:technical\s+)?recruiter|talent acquisition|campus recruiter|university recruiter|"
	r"hiring manager|recruiting coordinator|sourcer|hr manager|people partner|"
	r"recruitment (?:manager|lead|specialist)|ta partner)\b",
	re.I,
)


@dataclass
class ContactRecord:
	email: str
	company: str = ""
	name: str = ""
	role_title: str = ""
	contact_type: str = "unknown"
	confidence: str = "scraped"
	source_id: str = ""
	source_url: str = ""
	country: str = ""
	notes: str = ""
	extra: dict = field(default_factory=dict)

	def key(self) -> str:
		return hashlib.sha1(f"{self.email.lower()}|{self.company.lower()}".encode()).hexdigest()[:16]


def norm_company(name: str) -> str:
	return re.sub(r"[^a-z0-9]", "", (name or "").lower())


def clean_email(raw: str) -> str | None:
	email = raw.strip().strip("<>").lower()
	if email.startswith("mailto:"):
		email = email[7:]
	email = email.split("?")[0].strip()
	if not EMAIL_RE.fullmatch(email):
		return None
	domain = email.split("@", 1)[1]
	if domain in SKIP_EMAIL_DOMAINS and "career" not in email and "talent" not in email:
		# allow careers@gmail.com edge case — rare
		if domain in {"gmail.com", "yahoo.com", "hotmail.com", "outlook.com"}:
			return email  # keep personal emails from curated lists, mark later
		return None
	return email


def extract_emails_from_text(text: str) -> list[str]:
	found: set[str] = set()
	for match in EMAIL_RE.findall(text or ""):
		cleaned = clean_email(match)
		if cleaned:
			found.add(cleaned)
	for match in MAILTO_RE.findall(text or ""):
		cleaned = clean_email(match)
		if cleaned:
			found.add(cleaned)
	for user, dom, tld in OBFUSCATED_RE.findall(text or ""):
		cleaned = clean_email(f"{user}@{dom}.{tld}")
		if cleaned:
			found.add(cleaned)
	return sorted(found)


def classify_contact(email: str, name: str = "", role: str = "", notes: str = "") -> tuple[str, str]:
	blob = " ".join([email, name, role, notes]).lower()
	local = email.split("@", 1)[0]

	if role and ROLE_TITLE_RE.search(role):
		return "recruiter", "verified" if name else "public_listed"

	if any(k in local for k in ("recruit", "talent", "campus", "university", "hiring", "hr", "people", "jobs", "career")):
		return "hr_inbox", "public_listed"

	if name and not any(x in local for x in ("info", "hello", "support", "admin")):
		if HIRING_KEYWORDS.search(blob):
			return "recruiter", "scraped"
		return "hiring_manager", "scraped"

	if local in GENERIC_LOCALS:
		return "careers_inbox", "generic"

	return "unknown", "scraped"


GENERIC_LOCALS = {
	"careers",
	"talent",
	"hr",
	"recruiting",
	"jobs",
	"hiring",
	"university",
	"campus",
	"interns",
	"internships",
	"resume",
	"resumes",
	"recruitment",
}


def domain_from_url(url: str) -> str | None:
	if not url:
		return None
	try:
		host = urlparse(url).netloc.lower()
	except Exception:
		return None
	if not host:
		return None
	host = host[4:] if host.startswith("www.") else host
	if host in {"greenhouse.io", "lever.co", "ashbyhq.com", "myworkdayjobs.com", "smartrecruiters.com"}:
		return None
	if "google.com" in host and "careers" in url:
		return None
	return host


def split_name(full: str) -> tuple[str, str]:
	parts = [p for p in re.split(r"\s+", full.strip()) if p]
	if len(parts) >= 2:
		return parts[0], parts[-1]
	if len(parts) == 1:
		return parts[0], ""
	return "", ""


def infer_email_from_format(fmt: str, first: str, last: str) -> str | None:
	if not first or not last:
		return None
	f = first.lower()
	l = last.lower()
	f0 = f[0] if f else ""
	mapping = {"first": f, "last": l, "first[0]": f0, "f": f, "l": l, "f0": f0}
	out = fmt
	for key, val in mapping.items():
		out = out.replace("{" + key + "}", val)
	if "{" in out or "}" in out:
		return None
	return out.lower()


def read_text_file(path: Path) -> str:
	for enc in ("utf-8", "latin-1"):
		try:
			return path.read_text(encoding=enc)
		except UnicodeDecodeError:
			continue
	return path.read_text(encoding="utf-8", errors="replace")


def parse_markdown_table_contacts(text: str, source_id: str, source_url: str = "") -> list[ContactRecord]:
	"""Parse careerLauncher-style markdown tables."""
	records: list[ContactRecord] = []
	lines = text.splitlines()
	for line in lines:
		if "|" not in line or "@" not in line:
			continue
		if re.match(r"^\s*\|?\s*-+\s*\|", line):
			continue
		cells = [c.strip() for c in line.strip().strip("|").split("|")]
		if len(cells) < 3:
			continue
		emails = extract_emails_from_text(line)
		if not emails:
			continue
		company = cells[0] if cells[0] and not cells[0].lower().startswith("company") else ""
		role = cells[3] if len(cells) > 3 else ""
		location = cells[4] if len(cells) > 4 else ""
		src = cells[6] if len(cells) > 6 and cells[6].startswith("http") else source_url
		for email in emails:
			ctype, conf = classify_contact(email, role=role, notes=line)
			records.append(
				ContactRecord(
					email=email,
					company=company,
					role_title=role,
					contact_type=ctype,
					confidence=conf,
					source_id=source_id,
					source_url=src,
					country=location,
					notes="markdown_table",
				)
			)
	return records


def parse_csv_name_company(path: Path, source_id: str) -> list[ContactRecord]:
	records: list[ContactRecord] = []
	with path.open(encoding="utf-8", errors="replace") as f:
		reader = csv.DictReader(f)
		fields = {k.lower(): k for k in (reader.fieldnames or [])}
		for row in reader:
			name = ""
			company = ""
			for nk in ("name", "recruiter", "full_name", "contact_name"):
				if nk in fields:
					name = (row.get(fields[nk]) or "").strip()
					break
			for ck in ("company", "organization", "employer"):
				if ck in fields:
					company = (row.get(fields[ck]) or "").strip()
					break
			if not name and not company:
				continue
			# direct email columns
			for ek in ("email", "work_email", "contact_email", "role email", "role_email"):
				if ek in fields:
					for email in extract_emails_from_text(row.get(fields[ek]) or ""):
						ctype, conf = classify_contact(email, name=name, role=name)
						records.append(
							ContactRecord(
								email=email,
								company=company,
								name=name if "@" not in name else "",
								role_title=name if ROLE_TITLE_RE.search(name) else "",
								contact_type=ctype,
								confidence=conf,
								source_id=source_id,
								source_url=str(path),
							)
						)
			if ROLE_TITLE_RE.search(name) or name.endswith(" Recruiter"):
				records.append(
					ContactRecord(
						email="",
						company=company,
						name="",
						role_title=name,
						contact_type="recruiter",
						confidence="name_only",
						source_id=source_id,
						source_url=str(path),
						notes=f"recruiter_name:{name}",
					)
				)
	return records


def records_to_dicts(records: Iterable[ContactRecord], fetched_at: str) -> list[dict]:
	out = []
	for r in records:
		if not r.email and r.confidence != "name_only":
			continue
		out.append(
			{
				"email": r.email,
				"name": r.name,
				"company": r.company,
				"company_normalized": norm_company(r.company),
				"role_title": r.role_title,
				"contact_type": r.contact_type,
				"confidence": r.confidence,
				"source_id": r.source_id,
				"source_url": r.source_url,
				"country": r.country,
				"notes": r.notes,
				"target_internship_year": 2027,
				"target_season": "Summer 2027",
				"fetched_at": fetched_at,
			}
		)
	return out
