"""Lightweight MX record check — filters dead domains before adding guessed inboxes."""

from __future__ import annotations

import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import lru_cache


@lru_cache(maxsize=8192)
def has_mx_record(domain: str) -> bool:
	domain = (domain or "").strip().lower()
	if not domain or "." not in domain:
		return False
	try:
		out = subprocess.check_output(
			["dig", "+short", "MX", domain],
			timeout=5,
			text=True,
			stderr=subprocess.DEVNULL,
		)
		return bool(out.strip())
	except (OSError, subprocess.SubprocessError):
		return True


def warm_mx_cache(domains: set[str], *, workers: int = 24) -> None:
	unique = {d.strip().lower() for d in domains if d and "." in d}
	if not unique:
		return
	with ThreadPoolExecutor(max_workers=workers) as pool:
		futs = [pool.submit(has_mx_record, d) for d in unique]
		for fut in as_completed(futs):
			try:
				fut.result()
			except Exception:
				pass


def mx_status(domain: str) -> str:
	return "mx_ok" if has_mx_record(domain) else "mx_fail"
