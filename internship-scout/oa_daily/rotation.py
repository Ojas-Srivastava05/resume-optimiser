"""Fair round-robin company rotation — full cycle before repeats."""

import json
import random
from datetime import datetime, timezone

from oa_daily.config import STATE_PATH


def _default_state(companies: list[str]) -> dict:
	queue = companies[:]
	random.shuffle(queue)
	return {
		"version": 1,
		"queue": queue,
		"queue_index": 0,
		"cycles": 0,
		"company_visits": {},
		"sent_pairs": {},
		"last_run": None,
	}


def load_state(companies: list[str]) -> dict:
	if STATE_PATH.exists():
		try:
			state = json.loads(STATE_PATH.read_text())
		except json.JSONDecodeError:
			state = _default_state(companies)
	else:
		state = _default_state(companies)

	# Drop companies no longer in repos; add new ones at end of queue
	current = set(companies)
	queue = [c for c in state.get("queue", []) if c in current]
	for c in companies:
		if c not in queue:
			queue.append(c)
	state["queue"] = queue
	if state.get("queue_index", 0) >= len(queue):
		state["queue_index"] = 0
	state.setdefault("company_visits", {})
	state.setdefault("sent_pairs", {})
	if not state.get("last_run") and state.get("cycles", 0) == 0 and len(state.get("queue", [])) == len(companies):
		# First run: reshuffle merged queue for unbiased rotation
		import random

		random.shuffle(state["queue"])
		state["queue_index"] = 0
	return state


def save_state(state: dict) -> None:
	STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
	state["last_run"] = datetime.now(timezone.utc).isoformat()
	STATE_PATH.write_text(json.dumps(state, indent=2))


def pick_today_company(state: dict) -> tuple[str, int, int]:
	queue: list[str] = state["queue"]
	if not queue:
		raise RuntimeError("No companies in rotation queue")

	idx = state["queue_index"]
	slug = queue[idx]

	# Advance pointer; reshuffle when cycle completes
	next_idx = idx + 1
	if next_idx >= len(queue):
		random.shuffle(queue)
		state["queue"] = queue
		state["cycles"] = state.get("cycles", 0) + 1
		next_idx = 0

	state["queue_index"] = next_idx
	visits = state["company_visits"]
	visits[slug] = visits.get(slug, 0) + 1

	return slug, idx, len(queue)
