"""Atomic JSON read/write helpers for workflow state files."""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

_EMAIL_KEY_RE = re.compile(r'^[\s"]*([a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,})"\s*:\s*\{')


def _repair_outreach_file(path: Path, raw: str) -> dict[str, Any]:
	import importlib.util

	repair_script = path.resolve().parent.parent / "scripts" / "repair_outreach_state.py"
	spec = importlib.util.spec_from_file_location("_repair_outreach_state", repair_script)
	if spec is None or spec.loader is None:
		raise RuntimeError(f"Missing repair script at {repair_script}")
	mod = importlib.util.module_from_spec(spec)
	spec.loader.exec_module(mod)
	repaired = mod.repair_state(raw)
	save_json(path, repaired)
	return repaired


def load_json(path: Path, *, default: dict[str, Any] | None = None) -> dict[str, Any]:
	"""Load JSON state; auto-repair outreach_state.json when merge corruption is detected."""
	raw = path.read_text(encoding="utf-8")
	try:
		return json.loads(raw)
	except json.JSONDecodeError as exc:
		if path.name == "outreach_state.json":
			return _repair_outreach_file(path, raw)
		raise RuntimeError(
			f"Corrupt JSON in {path} ({exc}). "
			"Run: python3 hiring-contacts/scripts/repair_outreach_state.py"
		) from exc


def save_json(path: Path, data: dict[str, Any]) -> None:
	"""Atomically write JSON (temp file + replace) so CI crashes cannot truncate state."""
	path.parent.mkdir(parents=True, exist_ok=True)
	text = json.dumps(data, indent=2)
	tmp = path.with_suffix(path.suffix + ".tmp")
	tmp.write_text(text, encoding="utf-8")
	os.replace(tmp, path)


def repair_sent_object(raw: str) -> dict[str, Any]:
	"""Best-effort repair for merge-corrupted outreach_state.json sent blocks."""
	lines = raw.splitlines()
	sent: dict[str, Any] = {}
	current_email: str | None = None
	current_lines: list[str] = []

	def flush() -> None:
		nonlocal current_email, current_lines
		if not current_email or not current_lines:
			current_email = None
			current_lines = []
			return
		block = "{\n" + "\n".join(current_lines) + "\n}"
		try:
			obj = json.loads(block)
		except json.JSONDecodeError:
			current_email = None
			current_lines = []
			return
		if current_email not in sent:
			sent[current_email] = obj
		current_email = None
		current_lines = []

	in_sent = False
	for line in lines:
		stripped = line.strip()
		if stripped.startswith('"sent"'):
			in_sent = True
			continue
		if not in_sent:
			continue
		if stripped.startswith('"stats"') or stripped.startswith('"daily_log"') or stripped.startswith('"companies"') or stripped.startswith('"rotation_index"'):
			flush()
			in_sent = False
			continue
		m = _EMAIL_KEY_RE.match(line)
		if m:
			flush()
			current_email = m.group(1).lower()
			current_lines = []
			continue
		if current_email is not None:
			if stripped in ("{", "},") or stripped == "}":
				continue
			current_lines.append(line)
	flush()
	return sent
