"""Persistent send state for international radar (separate from India scout)."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from international.config import MAX_PROGRAM_EMAILS, SEEN_PATH


def _load() -> dict[str, Any]:
	if not SEEN_PATH.exists():
		return {"programs": {}, "listings": {}}
	try:
		return json.loads(SEEN_PATH.read_text(encoding="utf-8"))
	except json.JSONDecodeError:
		return {"programs": {}, "listings": {}}


def _save(data: dict[str, Any]) -> None:
	SEEN_PATH.parent.mkdir(parents=True, exist_ok=True)
	SEEN_PATH.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def should_email_program(program_id: str) -> bool:
	data = _load()
	rec = data.get("programs", {}).get(program_id, {})
	return int(rec.get("sends", 0)) < MAX_PROGRAM_EMAILS


def record_program_send(program_id: str) -> None:
	data = _load()
	programs = data.setdefault("programs", {})
	rec = programs.get(program_id, {"sends": 0, "history": []})
	rec["sends"] = int(rec.get("sends", 0)) + 1
	hist = list(rec.get("history", []))
	hist.append(datetime.now(timezone.utc).isoformat())
	rec["history"] = hist[-10:]
	programs[program_id] = rec
	_save(data)


def listing_key(url: str) -> str:
	return url.strip().lower()


def should_email_listing(url: str) -> bool:
	data = _load()
	rec = data.get("listings", {}).get(listing_key(url), {})
	return int(rec.get("sends", 0)) < MAX_PROGRAM_EMAILS


def record_listing_send(url: str) -> None:
	data = _load()
	listings = data.setdefault("listings", {})
	key = listing_key(url)
	rec = listings.get(key, {"sends": 0, "history": []})
	rec["sends"] = int(rec.get("sends", 0)) + 1
	hist = list(rec.get("history", []))
	hist.append(datetime.now(timezone.utc).isoformat())
	rec["history"] = hist[-10:]
	listings[key] = rec
	_save(data)


def reset_state(path: Path | None = None) -> None:
	target = path or SEEN_PATH
	if target.exists():
		target.unlink()
