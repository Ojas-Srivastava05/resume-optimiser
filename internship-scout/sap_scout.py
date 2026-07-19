#!/usr/bin/env python3
"""Daily SAP UI5 / Fiori job scout for Ananya Srivastava."""

from __future__ import annotations

import argparse
import smtplib
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from sap_job_scout.companies import advance_rotation, company_names, load_companies  # noqa: E402
from sap_job_scout.config import (  # noqa: E402
    COMPANY_BATCH_SIZE,
    SAP_EXTRA_RECIPIENTS,
    SAP_MONITOR_EMAIL,
    SAP_RECIPIENT_EMAIL,
)
from sap_job_scout.emailer import send_digest  # noqa: E402
from sap_job_scout.fetchers import collect_all_jobs  # noqa: E402
from sap_job_scout.storage import load_send_records, record_sends, should_email  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="SAP UI5 / Fiori job scout digest")
    parser.add_argument("--dry-run", action="store_true", help="Fetch + preview email, no SMTP")
    parser.add_argument("--no-email", action="store_true", help="Fetch only")
    parser.add_argument("--full", action="store_true", help="Include already-emailed openings")
    args = parser.parse_args()

    ist = datetime.now(ZoneInfo("Asia/Kolkata"))
    print(f"SAP Job Scout start — {ist.strftime('%Y-%m-%d %H:%M IST')}")
    print(f"Primary recipient: {SAP_RECIPIENT_EMAIL}")
    print(f"Monitor copy: {SAP_MONITOR_EMAIL}")
    if SAP_EXTRA_RECIPIENTS:
        print(f"Extra recipients: {', '.join(SAP_EXTRA_RECIPIENTS)}")

    companies = load_companies()
    print(f"SAP company universe: {len(companies)} firms ({len(company_names())} names)")

    all_jobs = collect_all_jobs()
    print(f"Total unique SAP matches: {len(all_jobs)}")

    records = load_send_records()
    to_send = [j for j in all_jobs if should_email(j.key, records, full=args.full)]
    suppressed = len(all_jobs) - len(to_send)

    if args.no_email:
        print(f"Fetched {len(all_jobs)} jobs; would email {len(to_send)} (suppressed {suppressed})")
        for job in to_send[:15]:
            print(f"  [{job.source}] {job.company} — {job.title}")
        return 0

    try:
        recipients = send_digest(
            to_send,
            new_only=not args.full,
            suppressed_count=suppressed,
            total_scanned=len(all_jobs),
            dry_run=args.dry_run,
        )
    except (RuntimeError, smtplib.SMTPAuthenticationError) as exc:
        print(f"Email failed: {exc}", file=sys.stderr)
        print(f"::warning::SAP digest email failed; job scan completed. {exc}", file=sys.stderr)
        return 0

    if not args.dry_run:
        record_sends([j.key for j in to_send])
        advance_rotation(COMPANY_BATCH_SIZE)
        print(f"Done — emailed {len(to_send)} opening(s) to {len(recipients)} inbox(es)")
    else:
        print(f"Dry run complete — would email {len(to_send)} opening(s)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
