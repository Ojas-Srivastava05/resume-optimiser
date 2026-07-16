#!/usr/bin/env python3
"""One-time / periodic reconcile: cancel stale follow-ups, block bad scrapes, sync company registry."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from cold_email.blocklist import record_bounce  # noqa: E402
from cold_email.config import STATE_PATH  # noqa: E402
from cold_email.json_state import load_json, save_json  # noqa: E402
from cold_email.selection import is_garbage_email, sync_company_registry  # noqa: E402


def main() -> int:
	try:
		state = load_json(STATE_PATH)
	except RuntimeError:
		import subprocess

		subprocess.run([sys.executable, str(ROOT / "scripts" / "repair_outreach_state.py")], check=True)
		state = load_json(STATE_PATH)
	sent = state.setdefault("sent", {})
	cancelled = 0
	blocked = 0

	for email, meta in list(sent.items()):
		if is_garbage_email(email):
			record_bounce(email, reason="garbage_scrape_reconcile")
			blocked += 1
		if not meta.get("followup_sent") and meta.get("sent_at"):
			meta["followup_sent"] = True
			meta["followup_count"] = meta.get("followup_count", 0) or 1
			meta["followup_cancelled"] = True
			meta["followup_cancel_reason"] = "policy:no_reply_followups_disabled"
			cancelled += 1
		meta.setdefault("reply_status", "no_reply")

	sync_company_registry(state)
	save_json(STATE_PATH, state)
	print(json.dumps({"cancelled_followups": cancelled, "blocked_garbage": blocked}, indent=2))
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
