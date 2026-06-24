#!/usr/bin/env python3
"""
Harvest hiring / recruiter contacts from public sources into hiring-contacts/data/merged/.

Usage:
  python scripts/refresh_all.py
  python scripts/refresh_all.py --skip-clone
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import subprocess
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from config import (  # noqa: E402
	COMPANY_DOMAIN_OVERRIDES,
	DATA_MERGED,
	DATA_NORMALIZED,
	DATA_RAW,
	EMAIL_FORMATS_BY_COMPANY,
	GENERIC_INBOX_PREFIXES,
	GITHUB_REPOS,
	OA_COMPANIES_CSV,
	PRIORITY_SHEET_ID,
	SCOUT_COMPANIES_CSV,
	SHEET_TAB_GIDS,
	SOURCES_GITHUB,
	SOURCES_WEB,
	TARGET_INTERNSHIP_YEAR,
	TARGET_SEASON,
	WEB_SOURCES,
)
from scripts.extract import (  # noqa: E402
	ContactRecord,
	classify_contact,
	clean_email,
	domain_from_url,
	extract_emails_from_text,
	infer_email_from_format,
	norm_company,
	parse_csv_name_company,
	parse_markdown_table_contacts,
	read_text_file,
	split_name,
)

USER_AGENT = "HiringContactsHarvester/1.0 (+resume-optimiser)"


def now_iso() -> str:
	return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def fetch_url(url: str, dest: Path) -> bool:
	req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
	try:
		with urllib.request.urlopen(req, timeout=60) as resp:
			dest.write_bytes(resp.read())
		return True
	except OSError as exc:
		print(f"  warn: fetch failed {url}: {exc}")
		return False


def clone_or_pull_repos(skip_clone: bool) -> list[str]:
	log: list[str] = []
	SOURCES_GITHUB.mkdir(parents=True, exist_ok=True)
	for repo in GITHUB_REPOS:
		name = repo["name"]
		dest = SOURCES_GITHUB / name
		if skip_clone and dest.exists():
			log.append(f"skip clone {name}")
			continue
		if dest.exists():
			cmd = ["git", "-C", str(dest), "pull", "--ff-only"]
		else:
			cmd = ["git", "clone", "--depth", "1", repo["url"], str(dest)]
		try:
			subprocess.run(cmd, check=True, capture_output=True, text=True)
			log.append(f"ok {name}")
		except subprocess.CalledProcessError as exc:
			log.append(f"fail {name}: {exc.stderr[:200]}")
	return log


def fetch_web_sources() -> list[str]:
	log: list[str] = []
	SOURCES_WEB.mkdir(parents=True, exist_ok=True)
	for src in WEB_SOURCES:
		dest = SOURCES_WEB / f"{src['id']}.html"
		if fetch_url(src["url"], dest):
			log.append(f"ok {src['id']}")
		else:
			log.append(f"fail {src['id']}")
	return log


def fetch_google_sheet_tabs() -> Path | None:
	out = DATA_RAW / "google_sheet_tabs"
	out.mkdir(parents=True, exist_ok=True)
	ok = 0
	for gid in SHEET_TAB_GIDS:
		url = f"https://docs.google.com/spreadsheets/d/{PRIORITY_SHEET_ID}/export?format=csv&gid={gid}"
		dest = out / f"sheet_{gid}.csv"
		if fetch_url(url, dest):
			ok += 1
	return out if ok else None


def load_scout_companies() -> dict[str, dict]:
	companies: dict[str, dict] = {}
	if not SCOUT_COMPANIES_CSV.exists():
		return companies
	with SCOUT_COMPANIES_CSV.open(encoding="utf-8") as f:
		for row in csv.DictReader(f):
			name = (row.get("Company") or "").strip()
			if not name:
				continue
			key = norm_company(name)
			companies[key] = {
				"name": name,
				"portal": (row.get("Career Portal") or "").strip(),
				"sector": (row.get("Sector") or "").strip(),
				"gh_slug": (row.get("GH Slug") or "").strip(),
			}
	return companies


def harvest_github_trees() -> list[ContactRecord]:
	records: list[ContactRecord] = []
	skip_suffix = {".png", ".jpg", ".gif", ".pdf", ".zip", ".git"}

	for repo_dir in sorted(SOURCES_GITHUB.iterdir()) if SOURCES_GITHUB.exists() else []:
		if not repo_dir.is_dir() or repo_dir.name.startswith("."):
			continue
		source_id = f"github:{repo_dir.name}"

		# Known structured files
		recruiters_csv = repo_dir / "recruiters.csv"
		if recruiters_csv.exists():
			records.extend(parse_csv_name_company(recruiters_csv, source_id))

		for rel in ("data/internship.csv", "data/placement.csv", "formats.csv"):
			p = repo_dir / rel
			if p.exists() and p.suffix == ".csv":
				records.extend(parse_csv_name_company(p, source_id))

		# Walk all text-ish files and regex emails
		for path in repo_dir.rglob("*"):
			if not path.is_file():
				continue
			if any(str(path).endswith(s) for s in skip_suffix):
				continue
			if path.suffix.lower() not in {".md", ".txt", ".csv", ".html", ".json", ".py"}:
				continue
			if ".git" in path.parts:
				continue
			text = read_text_file(path)
			emails = extract_emails_from_text(text)
			if not emails:
				continue

			# careerLauncher tables
			if path.name.lower() in {"readme.md", "readme"}:
				records.extend(
					parse_markdown_table_contacts(text, source_id, source_url=f"https://github.com/{repo_dir.name}")
				)

			# Generic line context: Company - email
			for line in text.splitlines():
				if "@" not in line:
					continue
				line_emails = extract_emails_from_text(line)
				if not line_emails:
					continue
				company_guess = ""
				# Flipkart - a@b.com patterns
				m = re.match(r"^[\-\*\d\.\s]*([A-Za-z0-9][A-Za-z0-9 &.'-]{1,60}?)\s*[-–:]\s*", line)
				if m:
					company_guess = m.group(1).strip()
				for email in line_emails:
					ctype, conf = classify_contact(email, notes=line)
					if email.split("@")[-1] in {"gmail.com", "yahoo.com", "hotmail.com"}:
						conf = "scraped_personal"
					records.append(
						ContactRecord(
							email=email,
							company=company_guess,
							contact_type=ctype,
							confidence=conf,
							source_id=source_id,
							source_url=str(path.relative_to(repo_dir)),
							notes=line.strip()[:240],
						)
					)
	return records


def harvest_web_pages() -> list[ContactRecord]:
	records: list[ContactRecord] = []
	for src in WEB_SOURCES:
		path = SOURCES_WEB / f"{src['id']}.html"
		if not path.exists():
			continue
		text = read_text_file(path)

		# Substack posts embed body in window._preloads JSON
		if src["id"] == "substack_atoz_50_hr":
			records.extend(_parse_substack_preloads(text, src))
			continue

		for line in text.splitlines():
			if "@" not in line:
				continue
			for email in extract_emails_from_text(line):
				company = ""
				m = re.match(r"^[\-\*\d\.\s]*([A-Za-z0-9][^<\n@]{1,50}?)\s*[-–:]", line)
				if m:
					company = re.sub(r"<[^>]+>", "", m.group(1)).strip()
				ctype, conf = classify_contact(email, notes=line)
				if email.endswith(("gmail.com", "yahoo.com", "hotmail.com", "outlook.com")):
					conf = "scraped_personal"
				records.append(
					ContactRecord(
						email=email,
						company=company,
						contact_type=ctype,
						confidence=conf,
						source_id=f"web:{src['id']}",
						source_url=src["url"],
						notes=line.strip()[:240],
					)
				)
	return records


def _parse_substack_preloads(html: str, src: dict) -> list[ContactRecord]:
	records: list[ContactRecord] = []
	m = re.search(r'window\._preloads\s*=\s*JSON\.parse\("(.+)"\)', html)
	if not m:
		return records
	try:
		raw = m.group(1).encode("utf-8").decode("unicode_escape")
		data = json.loads(raw)
		body = data.get("post", {}).get("body_html") or data.get("post", {}).get("body") or ""
	except (json.JSONDecodeError, UnicodeError):
		return records

	# Strip HTML to lines like "Flipkart - email@..."
	plain = re.sub(r"<br\s*/?>", "\n", body, flags=re.I)
	plain = re.sub(r"</p>", "\n", plain, flags=re.I)
	plain = re.sub(r"<[^>]+>", "", plain)
	for line in plain.splitlines():
		line = line.strip()
		if "@" not in line:
			continue
		company = ""
		cm = re.match(r"^([A-Za-z0-9][A-Za-z0-9 &.'-]{1,50}?)\s*[-–:]\s*", line)
		if cm:
			company = cm.group(1).strip()
		for email in extract_emails_from_text(line):
			ctype, conf = classify_contact(email, notes=line)
			if email.endswith(("gmail.com", "yahoo.com", "hotmail.com", "outlook.com")):
				conf = "scraped_personal"
			records.append(
				ContactRecord(
					email=email,
					company=company,
					contact_type=ctype,
					confidence=conf,
					source_id=f"web:{src['id']}",
					source_url=src["url"],
					notes=line[:240],
				)
			)
	return records


def harvest_google_sheets(sheet_dir: Path | None) -> list[ContactRecord]:
	records: list[ContactRecord] = []
	if not sheet_dir:
		return records
	for path in sorted(sheet_dir.glob("sheet_*.csv")):
		text = read_text_file(path)
		for email in extract_emails_from_text(text):
			records.append(
				ContactRecord(
					email=email,
					contact_type="unknown",
					confidence="google_sheet",
					source_id="google_sheet:referral",
					source_url=str(path.name),
				)
			)
		with path.open(encoding="utf-8", errors="replace") as f:
			reader = csv.DictReader(f)
			for row in reader:
				row_text = " ".join(str(v) for v in row.values())
				for email in extract_emails_from_text(row_text):
					company = (row.get("Company") or row.get("company") or "").strip()
					records.append(
						ContactRecord(
							email=email,
							company=company,
							confidence="google_sheet",
							source_id="google_sheet:referral",
							source_url=str(path.name),
						)
					)
	return records


def infer_recruiter_emails_from_csv() -> list[ContactRecord]:
	"""K02D recruiters.csv: infer work emails from name + company format patterns."""
	inferred: list[ContactRecord] = []
	recruiters_path = SOURCES_GITHUB / "recruiter-emailing-script" / "recruiters.csv"
	formats_path = SOURCES_GITHUB / "recruiter-emailing-script" / "formats.csv"
	if not recruiters_path.exists():
		return inferred

	fmt_map: dict[str, str] = dict(EMAIL_FORMATS_BY_COMPANY)
	if formats_path.exists():
		with formats_path.open(encoding="utf-8") as f:
			for row in csv.DictReader(f):
				co = (row.get("company") or "").strip().lower()
				fmt = (row.get(" format") or row.get("format") or "").strip()
				if co and fmt:
					fmt_map[co] = fmt

	with recruiters_path.open(encoding="utf-8") as f:
		for row in csv.DictReader(f):
			name = (row.get("name") or "").strip()
			co = (row.get("company") or "").strip().lower()
			if not name or not co:
				continue
			if ROLE_TITLE_RE.search(name) or name.lower() in {"early career", "campus programs", "senior university"}:
				continue
			fmt = fmt_map.get(co)
			if not fmt:
				continue
			first, last = split_name(name)
			if not first or not last:
				continue
			email = infer_email_from_format(fmt, first, last)
			cleaned = clean_email(email or "")
			if not cleaned:
				continue
			inferred.append(
				ContactRecord(
					email=cleaned,
					company=co,
					name=name,
					contact_type="recruiter",
					confidence="inferred_pattern",
					source_id="inferred:recruiter-emailing-script",
					source_url="https://github.com/K02D/recruiter-emailing-script",
					notes=f"pattern:{fmt}",
				)
			)
	return inferred


def infer_recruiter_emails(records: list[ContactRecord]) -> list[ContactRecord]:
	return infer_recruiter_emails_from_csv()


ROLE_TITLE_RE = re.compile(
	r"\b((?:technical\s+)?recruiter|talent acquisition|campus recruiter|university recruiter|"
	r"hiring manager|recruiting coordinator|sourcer|hr manager|people partner|"
	r"recruitment (?:manager|lead|specialist)|ta partner|microsoft university|recruiting leader)\b",
	re.I,
)


def generate_generic_inboxes(scout: dict[str, dict]) -> list[ContactRecord]:
	records: list[ContactRecord] = []
	seen: set[str] = set()

	def add(company: str, domain: str, prefix: str, source_id: str):
		email = clean_email(f"{prefix}@{domain}")
		if not email or email in seen:
			return
		seen.add(email)
		records.append(
			ContactRecord(
				email=email,
				company=company,
				contact_type="careers_inbox",
				confidence="generic_inferred",
				source_id=source_id,
				source_url="",
				notes=f"generated:{prefix}@{domain}",
			)
		)

	for key, meta in scout.items():
		name = meta["name"]
		domain = COMPANY_DOMAIN_OVERRIDES.get(key)
		if not domain:
			domain = domain_from_url(meta.get("portal") or "")
		if not domain:
			continue
		for prefix in GENERIC_INBOX_PREFIXES:
			add(name, domain, prefix, "generated:scout_domain")

	return records


def attach_scout_flags(rows: list[dict], scout: dict[str, dict]) -> None:
	scout_names = {norm_company(v["name"]): v["name"] for v in scout.values()}
	for row in rows:
		cn = row.get("company_normalized") or norm_company(row.get("company") or "")
		row["in_scout_list"] = cn in scout_names
		if cn in scout_names and not row.get("company"):
			row["company"] = scout_names[cn]


def dedupe_merge(all_records: list[ContactRecord], scout: dict[str, dict], fetched_at: str) -> list[dict]:
	by_key: dict[str, dict] = {}
	for r in all_records:
		if not r.email:
			continue
		key = r.email.lower()
		row = {
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
			"target_internship_year": TARGET_INTERNSHIP_YEAR,
			"target_season": TARGET_SEASON,
			"fetched_at": fetched_at,
		}
		if key not in by_key:
			by_key[key] = row
			continue
		# merge: prefer higher confidence
		rank = {
			"verified": 5,
			"public_listed": 4,
			"google_sheet": 4,
			"scraped": 3,
			"scraped_personal": 3,
			"inferred_pattern": 2,
			"generic_inferred": 1,
		}
		if rank.get(row["confidence"], 0) > rank.get(by_key[key]["confidence"], 0):
			by_key[key] = row
		elif rank.get(row["confidence"], 0) == rank.get(by_key[key]["confidence"], 0):
			if not by_key[key].get("company") and row.get("company"):
				by_key[key]["company"] = row["company"]

	rows = list(by_key.values())
	attach_scout_flags(rows, scout)
	rows.sort(key=lambda x: (x["confidence"], x["company"], x["email"]), reverse=True)
	return rows


def write_outputs(rows: list[dict], report: dict) -> None:
	DATA_MERGED.mkdir(parents=True, exist_ok=True)
	DATA_NORMALIZED.mkdir(parents=True, exist_ok=True)

	master = DATA_MERGED / "master_contacts.csv"
	fields = [
		"email",
		"name",
		"company",
		"company_normalized",
		"role_title",
		"contact_type",
		"confidence",
		"in_scout_list",
		"source_id",
		"source_url",
		"country",
		"target_internship_year",
		"target_season",
		"notes",
		"fetched_at",
	]
	with master.open("w", encoding="utf-8", newline="") as f:
		w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
		w.writeheader()
		w.writerows(rows)

	# Tier splits for cold-email tooling
	tiers = {
		"verified_and_public": [r for r in rows if r["confidence"] in {"verified", "public_listed", "google_sheet"}],
		"named_recruiters": [r for r in rows if r["contact_type"] == "recruiter" and r.get("name")],
		"personal_scraped": [r for r in rows if r["confidence"] == "scraped_personal"],
		"inferred_patterns": [r for r in rows if r["confidence"] == "inferred_pattern"],
		"generic_inboxes": [r for r in rows if r["confidence"] == "generic_inferred"],
		"scout_overlap": [r for r in rows if r.get("in_scout_list")],
	}
	for name, subset in tiers.items():
		p = DATA_MERGED / f"tier_{name}.csv"
		with p.open("w", encoding="utf-8", newline="") as f:
			w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
			w.writeheader()
			w.writerows(subset)

	report_path = DATA_MERGED / "ingest_report.json"
	report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

	# JSON lines for dynamic pipelines
	jsonl = DATA_MERGED / "master_contacts.jsonl"
	with jsonl.open("w", encoding="utf-8") as f:
		for row in rows:
			f.write(json.dumps(row) + "\n")


def main() -> int:
	parser = argparse.ArgumentParser()
	parser.add_argument("--skip-clone", action="store_true")
	args = parser.parse_args()

	fetched_at = now_iso()
	DATA_RAW.mkdir(parents=True, exist_ok=True)

	print("==> Clone / pull GitHub sources")
	clone_log = clone_or_pull_repos(args.skip_clone)

	print("==> Fetch web directories / blogs")
	web_log = fetch_web_sources()

	print("==> Fetch Google Sheet tabs")
	sheet_dir = fetch_google_sheet_tabs()

	print("==> Load scout company universe")
	scout = load_scout_companies()
	print(f"    scout companies: {len(scout)}")

	# Fallback when Google Sheet export is private (401)
	scout_copy = DATA_RAW / "scout_companies_snapshot.csv"
	if SCOUT_COMPANIES_CSV.exists():
		scout_copy.write_bytes(SCOUT_COMPANIES_CSV.read_bytes())

	print("==> Harvest contacts")
	all_records: list[ContactRecord] = []
	all_records.extend(harvest_github_trees())
	all_records.extend(harvest_web_pages())
	all_records.extend(harvest_google_sheets(sheet_dir))
	all_records.extend(infer_recruiter_emails(all_records))
	all_records.extend(generate_generic_inboxes(scout))

	rows = dedupe_merge(all_records, scout, fetched_at)

	report = {
		"fetched_at": fetched_at,
		"target_internship_year": TARGET_INTERNSHIP_YEAR,
		"target_season": TARGET_SEASON,
		"scout_company_count": len(scout),
		"total_unique_emails": len(rows),
		"by_confidence": {},
		"by_contact_type": {},
		"scout_overlap_emails": sum(1 for r in rows if r.get("in_scout_list")),
		"sources": {
			"github_clone": clone_log,
			"web_fetch": web_log,
			"google_sheet_tabs": len(list((DATA_RAW / "google_sheet_tabs").glob("*.csv"))) if sheet_dir else 0,
		},
	}
	for r in rows:
		report["by_confidence"][r["confidence"]] = report["by_confidence"].get(r["confidence"], 0) + 1
		report["by_contact_type"][r["contact_type"]] = report["by_contact_type"].get(r["contact_type"], 0) + 1

	write_outputs(rows, report)

	# Update sources catalog timestamp
	sources_path = ROOT / "data" / "sources.json"
	try:
		catalog = json.loads(sources_path.read_text(encoding="utf-8"))
	except (FileNotFoundError, json.JSONDecodeError):
		catalog = {}
	catalog["last_refresh"] = fetched_at
	catalog["total_unique_emails"] = len(rows)
	sources_path.write_text(json.dumps(catalog, indent=2) + "\n", encoding="utf-8")

	print(f"\nDone. {len(rows)} unique emails -> {DATA_MERGED / 'master_contacts.csv'}")
	print(json.dumps(report, indent=2))
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
