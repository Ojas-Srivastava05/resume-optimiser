#!/usr/bin/env python3
"""One-shot: rebuild today's scout digest from a captured job list + live hackathons, email all recipients."""

from __future__ import annotations

from urllib.parse import quote_plus

from emailer import digest_recipients, send_digest
from fetchers import fetch_hackathons
from filters import Job

# Captured from Internship Scout run 33962604215 (5 Sep 2026, emailed ~17:05 IST).
# Full run had 78 listings; Actions only logs the first 25 — these are that sample.
_LOGGED_JOBS: list[tuple[str, str, str]] = [
    ("Careers Web", "Apple", "Software Engineering Intern – AI Tools for Hardware Engineering"),
    ("Careers Web", "Barclays", "2027 Technology Developer Expert Graduate Program Wilmington"),
    ("Careers Web", "Barclays", "2027 Technology Developer Graduate Program Whippany"),
    ("Careers Web", "Barclays", "2027 Technology Developer Summer Internship Program Whippany"),
    ("Careers Web", "Barclays", "2027 Technology Developer Summer Internship Program Wilmington"),
    ("Careers Web", "Figma", "Software Engineer Intern (Winter 2027)"),
    ("Careers Web", "Notion", "Software Engineer Intern (Summer 2027) San Francisco, California; New York, New York"),
    ("Careers Web", "Notion", "Software Engineer Intern (Winter 2027) San Francisco, California; New York, New York"),
    ("Careers Web", "WorldQuant", "Quant Developer Intern Singapore"),
    ("Careers Web", "Apple", "2027 Apple Internship - Information Systems and Technology"),
    ("Careers Web", "Apple", "2027 Apple Internship - Information Systems and Technology (AUS)"),
    ("Careers Web", "Apple", "Hardware System Integration Engineer Intern - AirPods"),
    ("Careers Web", "Barclays", "2027 Quantitative Analytics Analyst Graduate Program New York"),
    ("Careers Web", "Barclays", "2027 Technology Cyber & Security Summer Internship Program Whippany"),
    ("Careers→GH", "Discord", "Hardware Intern — Robotics & AI"),
    ("Careers→GH", "Discord", "IT Intern – Gadget & Tech Support Operations"),
    ("LinkedIn", "GE HealthCare", "Research Intern - AI"),
    ("Careers Web", "IMC Trading", "Machine Learning Research Intern - Summer 2027 - Chicago Intern Trading Amsterdam, Chicago"),
    ("LinkedIn", "Kotak Securities", "AI & Data Engineering Intern"),
]


def main() -> None:
    jobs: list[Job] = []
    seen: set[tuple[str, str, str]] = set()
    for source, company, title in _LOGGED_JOBS:
        key = (source, company, title)
        if key in seen:
            continue
        seen.add(key)
        url = f"https://www.google.com/search?q={quote_plus(company + ' ' + title + ' internship apply')}"
        jobs.append(
            Job(title=title, company=company, location="See listing", url=url, source=source)
        )

    print(f"Jobs from today's digest sample: {len(jobs)}")
    print("Fetching live hackathons…")
    hackathons = fetch_hackathons()
    print(f"Hackathons: {len(hackathons)}")
    print("Recipients:", digest_recipients())

    sent = send_digest(
        jobs,
        new_only=True,
        suppressed_count=0,
        total_scanned=78,
        hackathons=hackathons,
        portal_coverage=(
            "Shared copy of today's scout digest "
            "(sample of 5 Sep listings + live elite hackathons). Full cron resumes tomorrow."
        ),
    )
    print("Sent to:", ", ".join(sent))


if __name__ == "__main__":
    main()
