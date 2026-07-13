"""Find recruiter LinkedIn profiles via public web search (Bing/Yahoo/DDG — no API keys)."""

from __future__ import annotations

import base64
import html
import re
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass

LINKEDIN_IN_RE = re.compile(
	r"https?://(?:[a-z]{2,3}\.)?linkedin\.com/in/[a-zA-Z0-9\-_%]+/?",
	re.I,
)
RECRUITER_HINT_RE = re.compile(
	r"\b(recruit|talent|hiring|hr|people|campus|university|staffing|sourcer|acquisition)\b",
	re.I,
)
TITLE_SPLIT_RE = re.compile(r"\s*[-–|]\s*")

USER_AGENT = (
	"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
	"AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)


@dataclass
class LinkedInProfile:
	url: str
	name: str
	title: str
	snippet: str


def _strip_tags(text: str) -> str:
	text = re.sub(r"<script[\s\S]*?</script>", " ", text, flags=re.I)
	text = re.sub(r"<style[\s\S]*?</style>", " ", text, flags=re.I)
	text = re.sub(r"<[^>]+>", " ", text)
	text = html.unescape(text)
	return re.sub(r"\s+", " ", text).strip()


def _name_from_slug(url: str) -> str:
	slug = url.rstrip("/").split("/")[-1]
	slug = re.sub(r"-[a-f0-9]{5,}$", "", slug, flags=re.I)
	parts = [p for p in re.split(r"[-_]", slug) if p and not p.isdigit()]
	if len(parts) >= 2:
		return " ".join(p.capitalize() for p in parts[:3])
	return ""


def _looks_like_person_name(name: str) -> bool:
	if not name or "@" in name:
		return False
	if RECRUITER_HINT_RE.search(name):
		return False
	parts = name.split()
	return len(parts) >= 2 and all(part.isalpha() for part in parts[:2])


def _clean_linkedin_url(url: str) -> str:
	url = urllib.parse.unquote(url.split("?", 1)[0]).rstrip("/")
	m = LINKEDIN_IN_RE.search(url)
	return m.group(0).rstrip("/") if m else ""


def _parse_name_title(result_title: str, company: str) -> tuple[str, str]:
	title = (result_title or "").replace(" | LinkedIn", "").strip()
	parts = TITLE_SPLIT_RE.split(title)
	name = parts[0].strip() if parts else ""
	role = parts[1].strip() if len(parts) > 1 else ""
	if company and role.lower().endswith(f" at {company.lower()}"):
		role = role[: -len(company) - 4].strip()
	return name, role


def _decode_bing_redirect(href: str) -> str:
	if "bing.com/ck/a" not in href:
		return href
	try:
		parsed = urllib.parse.urlparse(href)
		u = urllib.parse.parse_qs(parsed.query).get("u", [""])[0]
		if not u:
			return href
		for offset in range(5):
			try:
				candidate = base64.b64decode(u[offset:]).decode("utf-8", errors="ignore")
				if candidate.startswith("http"):
					return candidate
			except (ValueError, UnicodeDecodeError):
				continue
	except (ValueError, IndexError):
		pass
	return href


def _search_bing(query: str, *, max_results: int = 10) -> list[tuple[str, str, str]]:
	url = f"https://www.bing.com/search?q={urllib.parse.quote(query)}"
	req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept-Language": "en-US,en;q=0.9"})
	try:
		with urllib.request.urlopen(req, timeout=15) as resp:
			page = resp.read().decode("utf-8", errors="replace")
	except OSError:
		return []

	results: list[tuple[str, str, str]] = []
	for block in page.split('<li class="b_algo"'):
		if len(results) >= max_results:
			break
		h2_m = re.search(r"<h2[^>]*>([\s\S]*?)</h2>", block)
		if not h2_m:
			continue
		h2 = h2_m.group(1)
		href_m = re.search(r'href="([^"]+)"', h2)
		if not href_m:
			continue
		real_url = _decode_bing_redirect(href_m.group(1))
		title = _strip_tags(h2)
		snip_m = re.search(r'<p[^>]*>([\s\S]*?)</p>', block)
		snippet = _strip_tags(snip_m.group(1)) if snip_m else ""
		if real_url and (title or snippet):
			results.append((title, real_url, snippet))
	return results


def _search_yahoo(query: str, *, max_results: int = 10) -> list[tuple[str, str, str]]:
	url = f"https://search.yahoo.com/search?p={urllib.parse.quote(query)}&n=15"
	req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
	try:
		with urllib.request.urlopen(req, timeout=15) as resp:
			page = resp.read().decode("utf-8", errors="replace")
	except OSError:
		return []

	results: list[tuple[str, str, str]] = []
	for block in page.split('class="algo-sr"'):
		if len(results) >= max_results:
			break
		href_m = re.search(r'href="([^"]+)"', block)
		if not href_m:
			continue
		href = href_m.group(1)
		ru_m = re.search(r"/RU=([^/]+)/", href)
		real_url = urllib.parse.unquote(ru_m.group(1)) if ru_m else href
		title_m = re.search(r'class="title[^>]*>([\s\S]*?)</h3>', block)
		title = _strip_tags(title_m.group(1)) if title_m else ""
		snip_m = re.search(r'class="compText[^>]*>([\s\S]*?)</div>', block)
		snippet = _strip_tags(snip_m.group(1)) if snip_m else ""
		if real_url and (title or snippet):
			results.append((title, real_url, snippet))
	return results


def _search_ddg(query: str, *, max_results: int = 8) -> list[tuple[str, str, str]]:
	data = urllib.parse.urlencode({"q": query, "kl": "us-en"}).encode("utf-8")
	req = urllib.request.Request(
		"https://html.duckduckgo.com/html/",
		data=data,
		headers={"User-Agent": USER_AGENT, "Content-Type": "application/x-www-form-urlencoded"},
		method="POST",
	)
	try:
		with urllib.request.urlopen(req, timeout=15) as resp:
			page = resp.read().decode("utf-8", errors="replace")
	except OSError:
		return []
	if "anomaly.js" in page or "challenge-form" in page:
		return []

	results: list[tuple[str, str, str]] = []
	for block in page.split('class="result__body"'):
		if len(results) >= max_results:
			break
		link_m = re.search(r'class="result__a"[^>]*href="([^"]+)"[^>]*>([^<]+)</a>', block)
		if not link_m:
			continue
		href, title = link_m.group(1), link_m.group(2)
		href = urllib.parse.unquote(href)
		if "uddg=" in href:
			parsed = urllib.parse.parse_qs(urllib.parse.urlparse(href).query)
			href = (parsed.get("uddg") or [href])[0]
		snip_m = re.search(r'class="result__snippet"[^>]*>([^<]+)', block)
		snippet = snip_m.group(1) if snip_m else ""
		results.append((title.strip(), href.strip(), snippet.strip()))
	return results


def web_search(query: str, *, max_results: int = 10) -> list[tuple[str, str, str]]:
	try:
		from ddgs import DDGS

		rows = DDGS().text(query, max_results=max_results)
		out: list[tuple[str, str, str]] = []
		for row in rows:
			title = (row.get("title") or "").strip()
			url = (row.get("href") or "").strip()
			snippet = (row.get("body") or "").strip()
			if url and (title or snippet):
				out.append((title, url, snippet))
		if out:
			return out
	except Exception:
		pass

	for engine in (_search_bing, _search_yahoo, _search_ddg):
		results = engine(query, max_results=max_results)
		if results:
			return results
	return []


def recruiter_search_queries(company: str) -> list[str]:
	company = company.strip()
	return [
		f'site:linkedin.com/in ("campus recruiter" OR "university recruiting") "{company}" India',
		f'site:linkedin.com/in ("talent acquisition" OR "technical recruiter") "{company}"',
		f'site:linkedin.com/in recruiter hiring intern "{company}"',
		f'"{company}" campus recruiter linkedin.com/in',
	]


def find_recruiter_profiles(
	company: str,
	*,
	max_profiles: int = 3,
	delay_sec: float = 1.0,
) -> list[LinkedInProfile]:
	seen_urls: set[str] = set()
	out: list[LinkedInProfile] = []

	for query in recruiter_search_queries(company):
		if len(out) >= max_profiles:
			break
		for title, url, snippet in web_search(query, max_results=12):
			li_url = _clean_linkedin_url(url)
			if not li_url or li_url in seen_urls:
				continue
			if "/in/" not in li_url.lower():
				continue
			combined = f"{title} {snippet}"
			if not RECRUITER_HINT_RE.search(combined):
				continue
			name, role = _parse_name_title(title, company)
			if not _looks_like_person_name(name):
				name = _name_from_slug(li_url)
			if not name:
				continue
			seen_urls.add(li_url)
			out.append(LinkedInProfile(url=li_url, name=name, title=role, snippet=snippet))
			if len(out) >= max_profiles:
				break
		time.sleep(delay_sec)

	return out
