"""Load company-wise questions and pick OA-realistic pairs."""

import csv
import io
import re
from urllib.parse import urlparse

import requests

from oa_daily.companies import slug_to_name
from oa_daily.config import (
	FREQ_CSV_PRIORITY,
	QUESTIONS_PER_OA,
	SNEHASISHROY_BRANCH,
	SNEHASISHROY_REPO,
	TOP_POOL_SIZE,
)
from oa_daily.leetcode import fetch_leetcode_question
from oa_daily.models import OAQuestion
from oa_daily.ramesh_source import load_ramesh_questions


def _raw_csv_url(company_slug: str, filename: str) -> str:
	return (
		f"https://raw.githubusercontent.com/{SNEHASISHROY_REPO}/"
		f"{SNEHASISHROY_BRANCH}/{company_slug}/{filename}"
	)


def _load_frequency_rows(company_slug: str) -> list[dict]:
	for filename in FREQ_CSV_PRIORITY:
		url = _raw_csv_url(company_slug, filename)
		resp = requests.get(url, timeout=45)
		if resp.status_code != 200 or not resp.text.strip():
			continue
		reader = csv.DictReader(io.StringIO(resp.text))
		rows = []
		for row in reader:
			freq_raw = (row.get("Frequency %") or row.get("Frequency") or "0").replace("%", "").strip()
			try:
				freq = float(freq_raw)
			except ValueError:
				freq = 0.0
			url_val = row.get("URL") or ""
			slug = ""
			if url_val:
				path = urlparse(url_val).path.strip("/")
				slug = path.split("/")[-1] if path else ""
			if not slug:
				continue
			rows.append(
				{
					"id": row.get("ID", ""),
					"slug": slug,
					"title": row.get("Title", slug),
					"difficulty": row.get("Difficulty", ""),
					"frequency": freq,
					"url": url_val,
				}
			)
		if rows:
			rows.sort(key=lambda r: r["frequency"], reverse=True)
			return rows
	return []


def _slug_from_url(url: str) -> str:
	path = urlparse(url).path.strip("/")
	return path.split("/")[-1] if path else ""


def _pick_leetcode_slugs(rows: list[dict], visit: int, sent_pairs: set[str]) -> list[dict]:
	pool = rows[:TOP_POOL_SIZE]
	if len(pool) < QUESTIONS_PER_OA:
		return pool[:QUESTIONS_PER_OA]

	# Simulate OA: pair from high-frequency pool; rotate offset each revisit
	start = (max(visit, 1) - 1) * QUESTIONS_PER_OA
	for offset in range(0, len(pool) - 1, QUESTIONS_PER_OA):
		i = (start + offset) % max(1, len(pool) - 1)
		pair = pool[i : i + QUESTIONS_PER_OA]
		if len(pair) < QUESTIONS_PER_OA:
			pair = [pool[i], pool[0]]
		key = "|".join(p["slug"] for p in pair)
		if key not in sent_pairs:
			return pair

	# Fallback: top two by frequency
	return pool[:QUESTIONS_PER_OA]


def company_has_questions(company_slug: str) -> bool:
	if load_ramesh_questions(company_slug):
		return True
	for filename in FREQ_CSV_PRIORITY:
		url = _raw_csv_url(company_slug, filename)
		resp = requests.head(url, timeout=20)
		if resp.status_code == 200:
			return True
	return False


def build_oa_questions(
	company_slug: str,
	*,
	visit: int,
	sent_pairs: set[str],
) -> list[OAQuestion]:
	# Prefer curated OA repo when available (real campus OA problems)
	ramesh = load_ramesh_questions(company_slug)
	if len(ramesh) >= QUESTIONS_PER_OA:
		start = ((visit - 1) * QUESTIONS_PER_OA) % len(ramesh)
		chosen = []
		for i in range(QUESTIONS_PER_OA):
			chosen.append(ramesh[(start + i) % len(ramesh)])
		return chosen

	rows = _load_frequency_rows(company_slug)
	if not rows:
		raise RuntimeError(f"No question data for company '{company_slug}'")

	picked = _pick_leetcode_slugs(rows, visit, sent_pairs)
	questions: list[OAQuestion] = []
	for row in picked:
		questions.append(
			fetch_leetcode_question(
				row["slug"],
				title=row["title"],
				difficulty=row["difficulty"],
				url=row["url"],
			)
		)
	return questions


def remember_pair(state_sent: dict, company_slug: str, questions: list[OAQuestion]) -> None:
	key = company_slug
	pair_key = "|".join(q.slug for q in questions)
	bucket = state_sent.setdefault(key, [])
	if pair_key not in bucket:
		bucket.append(pair_key)
	# cap history
	state_sent[key] = bucket[-20:]
