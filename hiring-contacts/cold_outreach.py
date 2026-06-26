#!/usr/bin/env python3
"""
Cold outreach CLI — Summer 2027 software internships.

Examples:
  python cold_outreach.py --dry-run
  python cold_outreach.py --limit 5
  python cold_outreach.py --followups --dry-run
  python cold_outreach.py --company flipkart --dry-run
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from cold_email.blocklist import record_bounce, record_bounce_from_message  # noqa: E402
from cold_email.config import DEFAULT_DAILY_CAP, DRAFTS_DIR, MAX_PER_RUN, MIN_SECONDS_BETWEEN_SENDS  # noqa: E402
from cold_email.mailer import send_email  # noqa: E402
from cold_email.queue import (  # noqa: E402
	daily_remaining_quota,
	daily_sent_count,
	mark_sent,
	pick_batch,
	seconds_until_next_send_allowed,
)
from cold_email.templates import body_followup, body_initial, subject_line  # noqa: E402


def main() -> int:
	parser = argparse.ArgumentParser(description="Summer 2027 internship cold outreach")
	parser.add_argument("--dry-run", action="store_true", help="Compose only, do not send")
	parser.add_argument(
		"--limit",
		type=int,
		default=min(MAX_PER_RUN, DEFAULT_DAILY_CAP),
		help=f"Max emails this run (hard-capped at {DEFAULT_DAILY_CAP}/day, {MAX_PER_RUN}/run)",
	)
	parser.add_argument("--include-generic", action="store_true", help="Include careers@ generated inboxes")
	parser.add_argument("--followups", action="store_true", help="Send follow-ups only")
	parser.add_argument("--company", default="", help="Filter to one company (normalized match)")
	parser.add_argument("--save-drafts", action="store_true", help="Write drafts to data/drafts/")
	parser.add_argument("--record-bounce", metavar="EMAIL", help="Block an email after bounce/rejection")
	parser.add_argument("--bounce-reason", default="", help="Reason text (auto-extracts replacement emails)")
	args = parser.parse_args()

	if args.record_bounce:
		email = args.record_bounce.strip().lower()
		if args.bounce_reason:
			replacements = record_bounce_from_message(email, args.bounce_reason)
			print(f"Blocked {email}; replacements found: {replacements or 'none'}")
		else:
			record_bounce(email, reason="manual")
			print(f"Blocked {email}")
		return 0

	run_limit = max(1, min(args.limit, MAX_PER_RUN, DEFAULT_DAILY_CAP))
	remaining = daily_remaining_quota()
	if remaining <= 0 and not args.dry_run:
		print(
			f"Daily cap reached ({daily_sent_count()}/{DEFAULT_DAILY_CAP} sent today IST). "
			"No more live sends until tomorrow."
		)
		return 0
	run_limit = min(run_limit, remaining) if not args.dry_run else run_limit

	if not args.dry_run:
		wait_sec = seconds_until_next_send_allowed()
		if wait_sec > 0:
			print(
				f"Rate limit: last send was <1 hour ago. Wait {wait_sec // 60}m {wait_sec % 60}s "
				f"(min interval {MIN_SECONDS_BETWEEN_SENDS}s). No email sent."
			)
			return 0

	targets = pick_batch(
		limit=run_limit,
		include_generic=args.include_generic,
		followups_only=args.followups,
		company_filter=args.company,
		enforce_interval=not args.dry_run,
	)

	if not targets:
		if not args.dry_run:
			wait = seconds_until_next_send_allowed()
			if wait > 0:
				mins = (wait + 59) // 60
				print(f"Rate limit: next live send allowed in ~{mins} min (min 1 hour between sends).")
				return 0
		print("No targets in queue (all caught up, daily cap hit, or empty contact DB).")
		return 0

	print(
		f"Queue: {len(targets)} email(s) | dry_run={args.dry_run} | followups={args.followups} | "
		f"daily={daily_sent_count()}/{DEFAULT_DAILY_CAP} sent (IST)"
	)

	if args.save_drafts or args.dry_run:
		DRAFTS_DIR.mkdir(parents=True, exist_ok=True)

	sent = 0
	for t in targets:
		subject = subject_line(t.company, is_followup=t.is_followup)
		if t.is_followup:
			body = body_followup(company=t.company, contact_name=t.name, email=t.email)
		else:
			body = body_initial(
				company=t.company,
				contact_name=t.name,
				email=t.email,
				career_portal=t.career_portal,
				contact_type=t.contact_type,
			)

		if args.save_drafts or args.dry_run:
			safe = t.email.replace("@", "_at_")
			draft = DRAFTS_DIR / f"{safe}.txt"
			draft.write_text(f"To: {t.email}\nSubject: {subject}\n\n{body}", encoding="utf-8")

		try:
			send_email(to_addr=t.email, subject=subject, body_text=body, dry_run=args.dry_run)
			if not args.dry_run:
				mark_sent(t, subject=subject, dry_run=False)
			sent += 1
			print(f"  {'[dry-run] ' if args.dry_run else ''}OK {t.email} @ {t.company} ({t.confidence})")
		except Exception as exc:
			print(f"  FAIL {t.email}: {exc}")

	print(json.dumps({"sent": sent, "dry_run": args.dry_run}, indent=2))
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
