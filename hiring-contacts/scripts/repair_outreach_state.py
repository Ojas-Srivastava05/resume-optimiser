#!/usr/bin/env python3
"""Repair corrupted outreach_state.json after concurrent git-push races."""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATE_PATH = ROOT / "data" / "outreach_state.json"
BACKUP_PATH = ROOT / "data" / "archive" / "outreach_state.corrupt.bak"

EMAIL_KEY_RE = re.compile(r'"([^"]+@[^"]+)"\s*:\s*\{')


def _parse_sent_objects(text: str) -> dict[str, dict]:
	sent: dict[str, dict] = {}
	for match in EMAIL_KEY_RE.finditer(text):
		email = match.group(1).lower()
		start = match.end() - 1
		depth = 0
		end = None
		for idx in range(start, len(text)):
			ch = text[idx]
			if ch == "{":
				depth += 1
			elif ch == "}":
				depth -= 1
				if depth == 0:
					end = idx + 1
					break
		if end is None:
			continue
		try:
			obj = json.loads(text[start:end])
		except json.JSONDecodeError:
			continue
		prev = sent.get(email)
		if not prev:
			sent[email] = obj
			continue
		prev_at = prev.get("sent_at") or prev.get("followup_at") or ""
		new_at = obj.get("sent_at") or obj.get("followup_at") or ""
		if new_at >= prev_at:
			sent[email] = obj
	return sent


def _parse_tail(text: str) -> dict:
	idx = text.find('"stats"')
	if idx < 0:
		return {}
	wrapped = "{" + text[idx:]
	depth = 0
	end = None
	for i, ch in enumerate(wrapped):
		if ch == "{":
			depth += 1
		elif ch == "}":
			depth -= 1
			if depth == 0:
				end = i + 1
				break
	if end is None:
		return {}
	try:
		return json.loads(wrapped[:end])
	except json.JSONDecodeError:
		return {}


def repair_state(raw: str) -> dict:
	sent = _parse_sent_objects(raw)
	tail = _parse_tail(raw)
	state = {
		"sent": sent,
		"stats": tail.get("stats") or {"total_sent": len(sent), "total_followups": 0},
		"daily_log": tail.get("daily_log") or {},
		"companies": tail.get("companies") or {},
		"rotation_index": int(tail.get("rotation_index") or 0),
	}
	if tail.get("last_live_send_at"):
		state["last_live_send_at"] = tail["last_live_send_at"]
	state["stats"]["total_sent"] = max(int(state["stats"].get("total_sent") or 0), len(sent))
	return state


def main() -> int:
	if not STATE_PATH.exists():
		print(f"Missing {STATE_PATH}")
		return 1
	raw = STATE_PATH.read_text(encoding="utf-8")
	try:
		json.loads(raw)
		print("outreach_state.json is already valid")
		return 0
	except json.JSONDecodeError as exc:
		print(f"Invalid JSON ({exc}); repairing...")

	BACKUP_PATH.parent.mkdir(parents=True, exist_ok=True)
	BACKUP_PATH.write_text(raw, encoding="utf-8")
	state = repair_state(raw)
	STATE_PATH.write_text(json.dumps(state, indent=2), encoding="utf-8")
	json.loads(STATE_PATH.read_text(encoding="utf-8"))
	print(
		json.dumps(
			{
				"repaired_at": datetime.utcnow().replace(microsecond=0).isoformat() + "+00:00",
				"sent_entries": len(state["sent"]),
				"backup": str(BACKUP_PATH),
			},
			indent=2,
		)
	)
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
