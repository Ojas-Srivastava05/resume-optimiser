"""Parse rameshgitter/OA-Questions curated OA problems."""

import json
import re

import requests

from oa_daily.companies import name_to_slug
from oa_daily.config import COMPANIES_CACHE_PATH, RAMESH_BRANCH, RAMESH_REPO
from oa_daily.models import OAQuestion, TestCase

# Known folders in rameshgitter/OA-Questions (slug -> folder name)
RAMESH_FOLDERS: dict[str, str] = {
	"bny-mellon": "BNY Mellon",
	"google": "Google",
	"trilogy-innovations": "Trilogy Innovations",
	"wells-fargo": "Wells Fargo",
	"media-net": "media.net",
}


def _load_ramesh_map() -> dict[str, str]:
	if COMPANIES_CACHE_PATH.exists():
		try:
			data = json.loads(COMPANIES_CACHE_PATH.read_text())
			mapping = {name_to_slug(n): n for n in data.get("ramesh_oa", [])}
			mapping.update(RAMESH_FOLDERS)
			return mapping
		except json.JSONDecodeError:
			pass
	return RAMESH_FOLDERS.copy()


def _raw_url(folder: str, filename: str) -> str:
	from urllib.parse import quote

	return f"https://raw.githubusercontent.com/{RAMESH_REPO}/{RAMESH_BRANCH}/{quote(folder)}/{filename}"


def _parse_cpp_problem(text: str, filename: str) -> tuple[str, str, list[TestCase]]:
	lines = text.splitlines()
	title = filename.replace(".cpp", "").replace("_", " ")
	statement_lines: list[str] = []
	in_block = False
	for line in lines:
		if "/*" in line:
			in_block = True
		if in_block:
			clean = line.strip().lstrip("/*").rstrip("*/").strip()
			if clean and "Author:" not in clean and not clean.startswith("http"):
				statement_lines.append(clean)
		if "*/" in line:
			in_block = False
			break

	statement = "\n".join(statement_lines).strip()
	if statement_lines and len(statement_lines[0]) < 80:
		title = statement_lines[0]

	test_cases: list[TestCase] = []
	sample_ins = re.findall(r"Sample Input[:\s]*([\s\S]*?)(?:Sample Output|$)", text, re.I)
	sample_outs = re.findall(r"Sample Output[:\s]*([\s\S]*?)(?:\n\n|$)", text, re.I)
	if sample_ins and sample_outs:
		test_cases.append(TestCase(input_text=sample_ins[0].strip(), output_text=sample_outs[0].strip()))

	return title, statement or text[:2000], test_cases[:2]


def load_ramesh_questions(company_slug: str) -> list[OAQuestion]:
	folder = _load_ramesh_map().get(company_slug)
	if not folder:
		return []

	# Known filenames per company folder (avoid GitHub API)
	candidates = ["Question1.cpp", "Question2.cpp", "question1.cpp", "question2.cpp"]
	questions: list[OAQuestion] = []
	for name in candidates:
		resp = requests.get(_raw_url(folder, name), timeout=30)
		if resp.status_code != 200:
			continue
		title, statement, tests = _parse_cpp_problem(resp.text, name)
		slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-") or name.replace(".cpp", "")
		questions.append(
			OAQuestion(
				title=title,
				slug=slug,
				difficulty="OA",
				statement=statement,
				test_cases=tests,
				source_url=f"https://github.com/{RAMESH_REPO}/tree/{RAMESH_BRANCH}/{folder}/{name}",
				source="ramesh_oa",
			)
		)
	return questions
