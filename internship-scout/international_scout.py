#!/usr/bin/env python3
"""First-World Internship Radar — Summer 2027 (distinct emails from India scout).

Usage (from internship-scout/):
  python international_scout.py --dry-run
  python international_scout.py --send
  python international_scout.py --drafts-only --dry-run
  python international_scout.py --priority 1 --send
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Allow `python international_scout.py` from internship-scout/
sys.path.insert(0, str(Path(__file__).resolve().parent))

from international.application_templates import body_for_program, subject_for_program
from international.catalog import all_opportunities, by_priority, high_fit_for_ojas
from international.config import DIGEST_BRAND, PREVIEW_DIR, TARGET_SEASON
from international.emailer import build_html, build_text, send_radar_digest
from international.state import record_program_send, should_email_program


def _select(args: argparse.Namespace):
	if args.all_catalog:
		return all_opportunities()
	if args.priority:
		return by_priority(args.priority)
	return high_fit_for_ojas()


def main() -> int:
	parser = argparse.ArgumentParser(description=f"{DIGEST_BRAND} — {TARGET_SEASON}")
	parser.add_argument("--dry-run", action="store_true", help="Build digest, do not SMTP")
	parser.add_argument("--send", action="store_true", help="Send digest via Gmail SMTP")
	parser.add_argument(
		"--priority",
		type=int,
		choices=[1, 2, 3],
		help="Include programmes with priority ≤ N (default: high-fit set)",
	)
	parser.add_argument("--all-catalog", action="store_true", help="Include full curated catalog")
	parser.add_argument(
		"--drafts-only",
		action="store_true",
		help="Attach international application draft openers for top programmes",
	)
	parser.add_argument(
		"--force",
		action="store_true",
		help="Ignore send-count suppression (still uses separate intl state file)",
	)
	parser.add_argument(
		"--write-preview",
		action="store_true",
		help="Write HTML/text preview under international/previews/",
	)
	args = parser.parse_args()

	if not args.dry_run and not args.send:
		args.dry_run = True  # safe default

	candidates = _select(args)
	to_email = []
	suppressed = 0
	for opp in candidates:
		if args.force or should_email_program(opp.id):
			to_email.append(opp)
		else:
			suppressed += 1

	drafts: list[tuple[str, str]] = []
	if args.drafts_only or args.send or args.dry_run:
		for opp in to_email[:3]:
			if opp.priority <= 2 and "low-swe-fit" not in opp.fit_tags:
				drafts.append((subject_for_program(opp), body_for_program(opp)))

	print(f"{DIGEST_BRAND} | {TARGET_SEASON}")
	print(f"Selected {len(to_email)} programmes ({suppressed} suppressed)")
	for o in to_email:
		print(f"  P{o.priority} [{o.region}] {o.name} — {o.country}")
		print(f"      {o.url}")

	if args.write_preview or args.dry_run:
		PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
		html = build_html(to_email, suppressed=suppressed, draft_snippets=drafts)
		text = build_text(to_email, suppressed=suppressed, draft_snippets=drafts)
		(PREVIEW_DIR / "latest.html").write_text(html, encoding="utf-8")
		(PREVIEW_DIR / "latest.txt").write_text(text, encoding="utf-8")
		print(f"Preview → {PREVIEW_DIR / 'latest.html'}")

	if args.dry_run and not args.send:
		subj = send_radar_digest(
			to_email, suppressed=suppressed, draft_snippets=drafts, dry_run=True
		)
		print(f"[dry-run] Would send subject: {subj}")
		print("[dry-run] No SMTP call.")
		return 0

	subj = send_radar_digest(
		to_email, suppressed=suppressed, draft_snippets=drafts, dry_run=False
	)
	for opp in to_email:
		record_program_send(opp.id)
	print(f"Sent: {subj}")
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
