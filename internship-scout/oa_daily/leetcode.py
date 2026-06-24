"""Fetch LeetCode problem statements and sample cases."""

import html
import re

import requests
from bs4 import BeautifulSoup

from oa_daily.models import OAQuestion, TestCase

GRAPHQL_URL = "https://leetcode.com/graphql"
QUERY = """
query questionData($titleSlug: String!) {
  question(titleSlug: $titleSlug) {
    title
    titleSlug
    difficulty
    content
    exampleTestcases
  }
}
"""


def _strip_html(content: str) -> str:
	soup = BeautifulSoup(content, "html.parser")
	for pre in soup.find_all("pre"):
		pre.replace_with("\n" + pre.get_text() + "\n")
	text = soup.get_text("\n")
	text = html.unescape(text)
	return re.sub(r"\n{3,}", "\n\n", text).strip()


def _examples_from_html(content: str) -> list[TestCase]:
	soup = BeautifulSoup(content, "html.parser")
	cases: list[TestCase] = []
	for pre in soup.find_all("pre"):
		raw = pre.get_text()
		in_match = re.search(r"Input:\s*(.+?)(?:\nOutput:|\Z)", raw, re.S | re.I)
		out_match = re.search(r"Output:\s*(.+?)(?:\nExplanation:|\Z)", raw, re.S | re.I)
		if in_match and out_match:
			cases.append(
				TestCase(
					input_text=in_match.group(1).strip(),
					output_text=out_match.group(1).strip(),
				)
			)
		if len(cases) >= 2:
			break
	return cases


def _examples_from_testcase_blob(blob: str) -> list[TestCase]:
	lines = [ln for ln in blob.strip().split("\n") if ln.strip()]
	cases: list[TestCase] = []
	i = 0
	while i < len(lines) - 1 and len(cases) < 2:
		cases.append(TestCase(input_text=lines[i].strip(), output_text=lines[i + 1].strip()))
		i += 2
	return cases


def fetch_leetcode_question(slug: str, *, title: str = "", difficulty: str = "", url: str = "") -> OAQuestion:
	resp = requests.post(
		GRAPHQL_URL,
		json={"query": QUERY, "variables": {"titleSlug": slug}},
		headers={"Content-Type": "application/json"},
		timeout=30,
	)
	resp.raise_for_status()
	q = resp.json()["data"]["question"]
	if not q:
		raise ValueError(f"LeetCode problem not found: {slug}")

	content = q.get("content") or ""
	test_cases = _examples_from_html(content)
	if not test_cases:
		test_cases = _examples_from_testcase_blob(q.get("exampleTestcases") or "")

	return OAQuestion(
		title=title or q["title"],
		slug=slug,
		difficulty=difficulty or q.get("difficulty") or "Unknown",
		statement=_strip_html(content)[:4000],
		test_cases=test_cases[:2],
		source_url=url or f"https://leetcode.com/problems/{slug}/",
		source="leetcode",
	)
