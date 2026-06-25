#!/usr/bin/env python3
"""
Cross-check public HR email directories against MX + company domain match.

Only imports emails where the domain has MX records and matches a scout company.

Usage:
  python scripts/harvest_web_verified.py
"""

from __future__ import annotations

import csv
import json
import re
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
SOURCES_WEB = ROOT / "sources" / "web"

from cold_email.discovery import company_domain, contact_row  # noqa: E402
from cold_email.mx_check import has_mx_record, warm_mx_cache  # noqa: E402
from config import SCOUT_COMPANIES_CSV, WEB_SOURCES  # noqa: E402
from scripts.extract import extract_emails_from_text, norm_company  # noqa: E402
from scripts.merge_master import INCREMENTAL_CSV, merge_master  # noqa: E402


def now_iso() -> str:
	return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load_html(src: dict) -> str:
	cached = SOURCES_WEB / f"{src['id']}.html"
	if cached.exists():
		return cached.read_text(encoding="utf-8", errors="replace")
	req = urllib.request.Request(src["url"], headers={"User-Agent": "HiringContactsWebVerify/1.0"})
	try:
		with urllib.request.urlopen(req, timeout=45) as resp:
			text = resp.read(2_000_000).decode("utf-8", errors="replace")
		SOURCES_WEB.mkdir(parents=True, exist_ok=True)
		cached.write_text(text, encoding="utf-8")
		return text
	except OSError as exc:
		print(f"  warn: {src['url']}: {exc}")
		return ""


def build_scout_index() -> tuple[dict[str, str], dict[str, str]]:
	"""Returns (norm_key -> display name, email_domain -> display name)."""
	key_to_name: dict[str, str] = {}
	domain_to_name: dict[str, str] = {}
	with SCOUT_COMPANIES_CSV.open(encoding="utf-8") as f:
		for row in csv.DictReader(f):
			name = (row.get("Company") or "").strip()
			portal = (row.get("Career Portal") or "").strip()
			if not name:
				continue
			key = norm_company(name)
			key_to_name[key] = name
			domain = company_domain(name, portal)
			if domain:
				domain_to_name[domain.lower()] = name
				parts = domain.split(".")
				if len(parts) >= 2:
					domain_to_name[".".join(parts[-2:]).lower()] = name
			# Map common brand tokens (e.g. phonepe.com -> PhonePe).
			token = re.sub(r"[^a-z0-9]", "", name.lower())
			if len(token) >= 4:
				key_to_name.setdefault(token, name)
	return key_to_name, domain_to_name


def match_company(line: str, email: str, domain_to_name: dict[str, str], key_to_name: dict[str, str]) -> str:
	email_domain = email.split("@", 1)[1].lower()
	if email_domain in domain_to_name:
		return domain_to_name[email_domain]
	for domain, name in domain_to_name.items():
		if email_domain == domain or email_domain.endswith("." + domain):
			return name
	# Company name usually appears at the start of directory lines — keep snippet tiny.
	short = line[:180]
	short_key = norm_company(short)
	best: tuple[int, str] | None = None
	for key, name in key_to_name.items():
		if len(key) < 4:
			continue
		if key in short_key:
			score = len(key)
			if best is None or score > best[0]:
				best = (score, name)
	return best[1] if best else ""


def lines_from_substack(html: str) -> list[str]:
	m = re.search(r'window\._preloads\s*=\s*JSON\.parse\("(.+)"\)', html)
	if m:
		try:
			raw = m.group(1).encode("utf-8").decode("unicode_escape")
			data = json.loads(raw)
			body = data.get("post", {}).get("body_html") or data.get("post", {}).get("body") or ""
			plain = re.sub(r"<br\s*/?>", "\n", body, flags=re.I)
			plain = re.sub(r"</p>", "\n", plain, flags=re.I)
			plain = re.sub(r"<[^>]+>", "", plain)
			return [ln.strip() for ln in plain.splitlines() if "@" in ln]
		except (json.JSONDecodeError, UnicodeError):
			pass
	plain = re.sub(r"<[^>]+>", "\n", html)
	return [ln.strip() for ln in plain.splitlines() if "@" in ln]


def _devblogger_lines(html: str) -> list[str]:
	"""Parse devblogger directory: h3 company heading + nearby email."""
	lines: list[str] = []
	for block in re.split(r"<h3[^>]*>", html, flags=re.I):
		if "@" not in block:
			continue
		heading = re.sub(r"<[^>]+>", " ", block.split("</h3>", 1)[0])
		heading = re.sub(r"\s+", " ", heading).strip()
		body = block.split("</h3>", 1)[-1] if "</h3>" in block else block
		body_plain = re.sub(r"<[^>]+>", " ", body)
		for email in extract_emails_from_text(body_plain):
			prefix = heading[:80] if heading else ""
			lines.append(f"{prefix} - {email}")
	if len(lines) >= 20:
		return lines
	# Fallback split.
	plain = re.sub(r"<br\s*/?>", "\n", html, flags=re.I)
	plain = re.sub(r"</p>", "\n", plain, flags=re.I)
	plain = re.sub(r"<[^>]+>", " ", plain)
	return [ln.strip()[:240] for ln in plain.splitlines() if "@" in ln]


def verify_lines(lines: list[str], source_id: str, source_url: str, domain_to_name: dict[str, str], key_to_name: dict[str, str]) -> list[dict]:
	fetched_at = now_iso()
	candidates: list[tuple[str, str]] = []
	for line in lines:
		for email in extract_emails_from_text(line):
			company = match_company(line, email, domain_to_name, key_to_name)
			if company:
				candidates.append((email, company))

	warm_mx_cache({e.split("@", 1)[1] for e, _ in candidates})

	out: list[dict] = []
	seen: set[str] = set()
	for email, company in candidates:
		if email in seen:
			continue
		email_domain = email.split("@", 1)[1]
		if not has_mx_record(email_domain):
			continue
		seen.add(email)
		named = "." in email.split("@", 1)[0] and not email.endswith(
			("gmail.com", "yahoo.com", "hotmail.com", "outlook.com")
		)
		out.append(
			contact_row(
				email,
				company,
				"scraped_personal" if named or email.endswith(("gmail.com", "yahoo.com", "hotmail.com", "outlook.com")) else "public_listed",
				"recruiter" if named else "hr_inbox",
				source_url,
				fetched_at,
				"web_directory_mx_verified",
				source_id=source_id,
			)
		)
	return out


def append_incremental(rows: list[dict]) -> int:
	if not rows:
		return 0
	INCREMENTAL_CSV.parent.mkdir(parents=True, exist_ok=True)
	exists = INCREMENTAL_CSV.exists()
	fieldnames = list(rows[0].keys())
	with INCREMENTAL_CSV.open("a", encoding="utf-8", newline="") as f:
		w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
		if not exists:
			w.writeheader()
		w.writerows(rows)
	return len(rows)


def main() -> int:
	key_to_name, domain_to_name = build_scout_index()
	all_rows: list[dict] = []

	for src in WEB_SOURCES:
		sid = src["id"]
		if sid not in {"devblogger_hr_500", "substack_atoz_50_hr"}:
			continue
		print(f"Loading {src['label']}...")
		html = load_html(src)
		if not html:
			continue
		lines = lines_from_substack(html) if "substack" in sid else _devblogger_lines(html)
		source_id = "web:substack_verified" if "substack" in sid else "web:devblogger_verified"
		rows = verify_lines(lines, source_id, src["url"], domain_to_name, key_to_name)
		print(f"  verified {len(rows)} email(s)")
		all_rows.extend(rows)

	added = append_incremental(all_rows)
	total, newly_merged = merge_master()
	print(f"Web verify done: appended={added}, newly_merged={newly_merged}, total={total}")
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
