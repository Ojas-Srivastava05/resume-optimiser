#!/usr/bin/env python3
"""Daily OA drill — one company, two simulated OA questions, separate email."""

from __future__ import annotations

import argparse
import copy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from oa_daily.companies import load_company_slugs, slug_to_name
from oa_daily.emailer import build_text, send_oa_email
from oa_daily.models import OADayPlan
from oa_daily.questions import build_oa_questions, company_has_questions, remember_pair
from oa_daily.rotation import load_state, pick_today_company, save_state


def run(*, dry_run: bool = False, refresh_companies: bool = False, company: str | None = None) -> OADayPlan:
	companies = load_company_slugs(refresh=refresh_companies)
	if not companies:
		raise RuntimeError("No companies discovered from GitHub repos")

	state = load_state(companies)
	working = copy.deepcopy(state)

	if company:
		slug = company.lower().strip()
		if slug not in companies:
			raise RuntimeError(f"Company '{company}' not in OA repos")
		visit = working["company_visits"].get(slug, 0) + 1
		working["company_visits"][slug] = visit
		queue_pos = companies.index(slug)
		queue_total = len(companies)
	else:
		for _ in range(min(50, len(working["queue"]))):
			slug, queue_pos, queue_total = pick_today_company(working)
			if company_has_questions(slug):
				break
		else:
			raise RuntimeError("No company with question data found in rotation queue")
		visit = working["company_visits"][slug]

	sent_pairs = set(working.get("sent_pairs", {}).get(slug, []))
	questions = build_oa_questions(slug, visit=visit, sent_pairs=sent_pairs)
	remember_pair(working["sent_pairs"], slug, questions)

	plan = OADayPlan(
		company_slug=slug,
		company_name=slug_to_name(slug),
		questions=questions,
		visit_number=visit,
		queue_position=queue_pos,
		queue_total=queue_total,
	)

	if dry_run:
		print(build_text(plan))
		print(f"\n[dry-run] company={slug} visit={visit} next_queue_index={working.get('queue_index')}")
	else:
		send_oa_email(plan)
		save_state(working)
		print(f"Sent OA drill for {plan.company_name} ({len(questions)} questions)")


def main() -> None:
	parser = argparse.ArgumentParser(description="OA Daily mailer")
	parser.add_argument("--dry-run", action="store_true", help="Print email, do not send")
	parser.add_argument("--refresh-companies", action="store_true", help="Refresh company list from GitHub")
	parser.add_argument("--company", help="Force a specific company slug (e.g. amazon)")
	args = parser.parse_args()

	try:
		run(dry_run=args.dry_run, refresh_companies=args.refresh_companies, company=args.company)
	except Exception as exc:
		print(f"ERROR: {exc}", file=sys.stderr)
		sys.exit(1)


if __name__ == "__main__":
	main()
