#!/usr/bin/env python3
"""Daily internship + hackathon scout — priority companies, batch 2028, multi-source."""

import argparse
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

from ats_resolver import resolve_slugs
from companies import greenhouse_slugs, load_companies
from config import ATS_PROBE_PER_RUN, COMPANY_BATCH_SIZE, FAST_MODE, MAX_EMAIL_SENDS
from emailer import send_digest
from expand_companies import expand as expand_companies
from fetchers import (
    fetch_adzuna_jobs,
    fetch_ashby_jobs,
    fetch_careers_jobs,
    fetch_greenhouse_jobs,
    fetch_hackathons,
    fetch_indeed_jobs,
    fetch_internshala_jobs,
    fetch_lever_jobs,
    fetch_linkedin_jobs,
    fetch_naukri_jobs,
    fetch_unstop_jobs,
)
from filters import Job, dedupe_jobs
from logger import log, log_section, log_warn
from rotation import rotated_names
from storage import load_send_records, record_sends, should_email
from sync_companies import sync as sync_companies


def log_coverage_plan() -> None:
    n = len(load_companies())
    batch = len(rotated_names())
    days = (n + batch - 1) // batch if batch else 0
    gh = len(greenhouse_slugs())
    log_section("Coverage plan")
    log(f"Master company list: {n} firms")
    log(f"FULL SCAN every run (no openings missed on these boards):")
    log(f"  • Greenhouse: {gh} ATS boards — all intern roles polled")
    log(f"  • Lever + Ashby: all known boards")
    log(f"  • LinkedIn: 23 broad India intern queries (all priority companies)")
    log(f"  • Unstop: 14 broad sector queries (all priority companies)")
    log(f"  • Internshala: 13 tech intern categories (priority + ₹40k+ stipend)")
    log(f"  • Naukri: 10 broad + company rotation")
    log(f"  • Indeed India: 8 broad queries")
    log(f"  • Hackathons: Unstop + Devfolio + 19 direct MNC pages")
    log(f"ROTATED daily ({batch} companies/day, full cycle ~{days} days):")
    log(f"  • LinkedIn per-company + Unstop per-company + Naukri per-company + career portals")
    log(f"  → New postings on ATS/broad sources appear same day; company-specific")
    log(f"    sources rotate but broad queries catch the same live postings.")
    log(f"Email dedup: max {MAX_EMAIL_SENDS} sends per opening, then suppressed")


def collect_jobs() -> list[Job]:
    collectors = [
        ("Greenhouse", fetch_greenhouse_jobs, "full"),
        ("Lever", fetch_lever_jobs, "full"),
        ("Ashby", fetch_ashby_jobs, "full"),
        ("LinkedIn", fetch_linkedin_jobs, "broad+rotation"),
        ("Careers Web", fetch_careers_jobs, "rotation"),
        ("Unstop", fetch_unstop_jobs, "broad+rotation"),
        ("Adzuna", fetch_adzuna_jobs, "full"),
        ("Internshala", fetch_internshala_jobs, "full"),
        ("Naukri", fetch_naukri_jobs, "broad+rotation"),
        ("Indeed", fetch_indeed_jobs, "broad"),
    ]
    all_jobs: list[Job] = []
    for name, fn, mode in collectors:
        log_section(f"Fetching {name} ({mode})")
        try:
            found = fn()
            log(f"{name}: {len(found)} matches")
            all_jobs.extend(found)
        except Exception as exc:
            log(f"{name} FAILED: {exc}", level="ERROR")
            print(f"{name} ERROR: {exc}", file=sys.stderr)
    return dedupe_jobs(all_jobs)


def main() -> int:
    parser = argparse.ArgumentParser(description="Internship + Hackathon scout digest")
    parser.add_argument("--dry-run", action="store_true", help="Fetch only, no email")
    parser.add_argument("--full", action="store_true", help="Ignore send-count limit")
    parser.add_argument("--no-email", action="store_true", help="Do not send email")
    parser.add_argument("--no-sync", action="store_true", help="Skip Google Sheet company sync")
    parser.add_argument("--fast", action="store_true", help="Skip slow setup steps")
    parser.add_argument("--no-hackathons", action="store_true", help="Skip hackathon scouting")
    args = parser.parse_args()

    fast = args.fast or FAST_MODE
    ist = datetime.now(ZoneInfo("Asia/Kolkata"))
    log_section("Internship + Hackathon Scout start")
    log(f"Run time: {ist.strftime('%Y-%m-%d %H:%M IST')} | fast={fast} | batch={COMPANY_BATCH_SIZE}")

    try:
        expanded = expand_companies()
        log(f"Company list: {expanded['count']} firms")
    except Exception as exc:
        log(f"Company list load failed: {exc}", level="ERROR")

    if not args.no_sync and not fast:
        try:
            payload = sync_companies()
            log(f"Referral sheet synced: {payload['count']} firms")
        except Exception as exc:
            log_warn(f"Sheet sync skipped: {exc}")

    if not fast:
        try:
            cache = resolve_slugs(max_new=ATS_PROBE_PER_RUN)
            log(
                f"ATS probe: GH={len(cache.get('greenhouse', {}))} "
                f"Lever={len(cache.get('lever', {}))} Ashby={len(cache.get('ashby', {}))}"
            )
        except Exception as exc:
            log_warn(f"ATS probe skipped: {exc}")

    log_coverage_plan()
    batch = rotated_names()
    log(f"Today's rotation sample: {', '.join(batch[:5])} … ({len(batch)} total)")

    # ─── Internships ──────────────────────────────────────────────────────────
    jobs = collect_jobs()
    log(f"Total unique matches after dedup: {len(jobs)}")

    records = load_send_records()
    to_send: list[Job] = []
    suppressed: list[Job] = []
    for job in jobs:
        if should_email(job.key, records, full=args.full):
            to_send.append(job)
        else:
            suppressed.append(job)

    log_section("Email filter")
    log(f"Eligible to email: {len(to_send)}")
    log(f"Suppressed (already sent {MAX_EMAIL_SENDS}x): {len(suppressed)}")
    if suppressed[:3]:
        for j in suppressed[:3]:
            rec = records[j.key]
            log(f"  suppressed: [{j.source}] {j.company} — {j.title} (sent {rec.send_count}x)")

    for job in to_send[:25]:
        rec = records.get(job.key)
        tag = "NEW" if not rec else f"repeat {rec.send_count + 1}/{MAX_EMAIL_SENDS}"
        log(f"  • [{tag}] [{job.source}] {job.company} — {job.title}")
    if len(to_send) > 25:
        log(f"  … and {len(to_send) - 25} more")

    # ─── Hackathons ───────────────────────────────────────────────────────────
    hackathons = []
    if not args.no_hackathons:
        log_section("Fetching Hackathons")
        try:
            hackathons = fetch_hackathons()
            log(f"Hackathons found: {len(hackathons)} elite events")

            # Filter hackathons through seen-jobs too (using hackathon keys)
            hackathon_to_send = []
            for h in hackathons:
                if should_email(h.key, records, full=args.full):
                    hackathon_to_send.append(h)
            hackathons = hackathon_to_send
            log(f"Hackathons eligible to email: {len(hackathons)}")
        except Exception as exc:
            log(f"Hackathon scouting FAILED: {exc}", level="ERROR")
            print(f"Hackathon ERROR: {exc}", file=sys.stderr)

    if args.dry_run:
        log("Dry run — no email sent")
        return 0

    if not args.no_email:
        try:
            send_digest(
                to_send,
                new_only=not args.full,
                suppressed_count=len(suppressed),
                total_scanned=len(jobs),
                hackathons=hackathons,
            )
            if to_send or hackathons:
                parts = []
                if to_send:
                    parts.append(f"{len(to_send)} internship listings")
                if hackathons:
                    parts.append(f"{len(hackathons)} hackathons")
                log(f"Email sent: {' + '.join(parts)} → configured recipient")
            else:
                log(
                    f"Email sent: No new openings today "
                    f"({len(suppressed)} suppressed at 2-send cap, {len(jobs)} total scanned)"
                )
        except RuntimeError as exc:
            log(f"Email failed: {exc}", level="ERROR")
            return 1

    if not args.full:
        all_keys = [j.key for j in to_send]
        all_keys.extend(h.key for h in hackathons)
        if all_keys:
            record_sends(all_keys)

    log_section("Done")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
