"""Discover OA companies from GitHub repos."""

import json
import os
import re
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import requests

from oa_daily.config import COMPANIES_CACHE_PATH, RAMESH_BRANCH, RAMESH_REPO, SNEHASISHROY_BRANCH, SNEHASISHROY_REPO

GITHUB_API = "https://api.github.com"
CACHE_TTL_HOURS = 168


def slug_to_name(slug: str) -> str:
	special = {
		"media-net": "media.net",
		"jpmorgan": "JPMorgan",
		"de-shaw": "D. E. Shaw",
		"goldman-sachs": "Goldman Sachs",
	}
	if slug in special:
		return special[slug]
	parts = slug.replace("_", "-").split("-")
	return " ".join(p.capitalize() for p in parts)


def name_to_slug(name: str) -> str:
	return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def _github_headers() -> dict:
	token = os.getenv("GITHUB_TOKEN", "")
	headers = {"Accept": "application/vnd.github+json"}
	if token:
		headers["Authorization"] = f"Bearer {token}"
	return headers


def _top_level_dirs_api(repo: str, branch: str) -> list[str]:
	url = f"{GITHUB_API}/repos/{repo}/git/trees/{branch}"
	resp = requests.get(url, params={"recursive": "1"}, headers=_github_headers(), timeout=90)
	resp.raise_for_status()
	slugs: set[str] = set()
	for item in resp.json().get("tree", []):
		path = item.get("path", "")
		if "/" not in path and item.get("type") == "tree":
			slugs.add(path)
	return sorted(slugs)


def _top_level_dirs_clone(repo: str, branch: str) -> list[str]:
	url = f"https://github.com/{repo}.git"
	with tempfile.TemporaryDirectory(prefix="oa-companies-") as tmp:
		subprocess.run(
			["git", "clone", "--depth", "1", "--branch", branch, url, tmp],
			check=True,
			capture_output=True,
			text=True,
		)
		return sorted(
			name
			for name in os.listdir(tmp)
			if os.path.isdir(os.path.join(tmp, name)) and not name.startswith(".")
		)


def _load_cache(*, allow_stale: bool = False) -> dict | None:
	if not COMPANIES_CACHE_PATH.exists():
		return None
	try:
		data = json.loads(COMPANIES_CACHE_PATH.read_text())
		if allow_stale:
			return data
		updated = datetime.fromisoformat(data["updated_at"])
		age_h = (datetime.now(timezone.utc) - updated).total_seconds() / 3600
		if age_h < CACHE_TTL_HOURS:
			return data
	except (json.JSONDecodeError, KeyError, ValueError):
		pass
	return None


def _save_cache(sneha: list[str], ramesh: list[str], union: list[str]) -> None:
	COMPANIES_CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
	COMPANIES_CACHE_PATH.write_text(
		json.dumps(
			{
				"updated_at": datetime.now(timezone.utc).isoformat(),
				"snehasishroy": sneha,
				"ramesh_oa": ramesh,
				"companies": union,
			},
			indent=2,
		)
	)


def _fetch_fresh() -> tuple[list[str], list[str]]:
	try:
		sneha = _top_level_dirs_api(SNEHASISHROY_REPO, SNEHASISHROY_BRANCH)
		ramesh = _top_level_dirs_api(RAMESH_REPO, RAMESH_BRANCH)
		return sneha, ramesh
	except requests.HTTPError:
		sneha = _top_level_dirs_clone(SNEHASISHROY_REPO, SNEHASISHROY_BRANCH)
		ramesh = _top_level_dirs_clone(RAMESH_REPO, RAMESH_BRANCH)
		return sneha, ramesh


def load_company_slugs(*, refresh: bool = False) -> list[str]:
	if not refresh:
		cached = _load_cache()
		if cached:
			return cached["companies"]

	try:
		sneha, ramesh_names = _fetch_fresh()
	except Exception:
		cached = _load_cache(allow_stale=True)
		if cached:
			return cached["companies"]
		raise

	ramesh_slugs = [name_to_slug(n) for n in ramesh_names]
	union = sorted(set(sneha) | set(ramesh_slugs))
	_save_cache(sneha, ramesh_names, union)
	return union
