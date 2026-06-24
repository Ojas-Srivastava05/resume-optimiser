"""Load company-wise questions and pick OA-realistic pairs."""

import csv
import io
import random
from urllib.parse import urlparse

import requests

from oa_daily.config import (
	FREQ_CSV_PRIORITY,
	PAIR_PICK_ATTEMPTS,
	QUESTIONS_PER_OA,
	SNEHASISHROY_BRANCH,
	SNEHASISHROY_REPO,
	TOP_OA_POOL,
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
					"frequency": max(freq, 1.0),
					"url": url_val,
				}
			)
		if rows:
			rows.sort(key=lambda r: r["frequency"], reverse=True)
			return rows
	return []


def _weighted_sample(pool: list[dict], count: int, rng: random.Random) -> list[dict]:
	remaining = pool[:]
	picked: list[dict] = []
	for _ in range(count):
		if not remaining:
			break
		total = sum(item["frequency"] for item in remaining)
		roll = rng.uniform(0, total)
		cursor = 0.0
		for idx, item in enumerate(remaining):
			cursor += item["frequency"]
			if roll <= cursor:
				picked.append(remaining.pop(idx))
				break
	return picked


def _pick_leetcode_slugs(rows: list[dict], visit: int, sent_pairs: set[str]) -> list[dict]:
	pool = rows[:TOP_OA_POOL]
	if len(pool) < QUESTIONS_PER_OA:
		return pool[:QUESTIONS_PER_OA]

	# Unpredictable but realistic: weighted random pair from top 10.
	# High-frequency classics (Two Sum, etc.) stay likely — not guaranteed every day.
	rng = random.SystemRandom()
	candidates = pool[:]

	for attempt in range(PAIR_PICK_ATTEMPTS):
		# Slight shuffle noise so visit #2+ doesn't collide with visit #1 patterns
		if attempt > 0 and attempt % 7 == 0:
			rng.shuffle(candidates)

		pair = _weighted_sample(candidates, QUESTIONS_PER_OA, rng)
		if len(pair) < QUESTIONS_PER_OA:
			break
		key = "|".join(p["slug"] for p in pair)
		if key not in sent_pairs:
			return pair

	# Expand search: any unused pair in top pool, still prefer higher frequency
	for i in range(len(pool)):
		for j in range(i + 1, len(pool)):
			pair = [pool[i], pool[j]]
			key = "|".join(p["slug"] for p in pair)
			if key not in sent_pairs:
				return pair

	# Last resort: weighted random (may repeat a prior pair after many visits)
	return _weighted_sample(pool, QUESTIONS_PER_OA, rng)


def company_has_questions(company_slug: str) -> bool:
	if load_ramesh_questions(company_slug):
		return True
	for filename in FREQ_CSV_PRIORITY:
		url = _raw_csv_url(company_slug, filename)
		resp = requests.head(url, timeout=20)
		if resp.status_code == 200:
			return True
	return False


def _pick_ramesh_questions(ramesh: list[OAQuestion], visit: int, sent_pairs: set[str]) -> list[OAQuestion]:
	if len(ramesh) < QUESTIONS_PER_OA:
		return ramesh

	rng = random.SystemRandom()
	for _ in range(PAIR_PICK_ATTEMPTS):
		pair = rng.sample(ramesh, QUESTIONS_PER_OA)
		key = "|".join(q.slug for q in pair)
		if key not in sent_pairs:
			return pair

	start = ((visit - 1) * QUESTIONS_PER_OA) % len(ramesh)
	return [ramesh[(start + i) % len(ramesh)] for i in range(QUESTIONS_PER_OA)]


def build_oa_questions(
	company_slug: str,
	*,
	visit: int,
	sent_pairs: set[str],
) -> list[OAQuestion]:
	ramesh = load_ramesh_questions(company_slug)
	if len(ramesh) >= QUESTIONS_PER_OA:
		return _pick_ramesh_questions(ramesh, visit, sent_pairs)

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
	pair_key = "|".join(q.slug for q in questions)
	bucket = state_sent.setdefault(company_slug, [])
	if pair_key not in bucket:
		bucket.append(pair_key)
	state_sent[company_slug] = bucket[-30:]
