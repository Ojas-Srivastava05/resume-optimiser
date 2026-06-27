"""Daily SAP job digest email — sent to Ananya + monitor copy to Ojas."""

from __future__ import annotations

import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from zoneinfo import ZoneInfo

from sap_job_scout.config import SAP_MONITOR_EMAIL, SAP_RECIPIENT_EMAIL, SMTP_APP_PASSWORD, SMTP_EMAIL
from sap_job_scout.models import SapJob


def _group_by_source(jobs: list[SapJob]) -> dict[str, list[SapJob]]:
    groups: dict[str, list[SapJob]] = {}
    for job in jobs:
        groups.setdefault(job.source, []).append(job)
    return groups


def build_digest_html(
    jobs: list[SapJob],
    *,
    new_only: bool,
    suppressed_count: int = 0,
    total_scanned: int = 0,
) -> str:
    ist = datetime.now(ZoneInfo("Asia/Kolkata"))
    date_str = ist.strftime("%d %b %Y")

    if not jobs:
        parts = [
            f"<h2>SAP Job Scout — {date_str}</h2>",
            "<p><strong>No new SAP UI5 / Fiori openings today.</strong></p>",
            "<p>Scan completed for LinkedIn, Naukri, Indeed, and Adzuna (SAP-focused queries).</p>",
        ]
        if suppressed_count:
            parts.append(
                f"<p><small>{suppressed_count} listing(s) still live but already emailed twice — skipped.</small></p>"
            )
        if total_scanned:
            parts.append(f"<p><small>{total_scanned} total SAP-relevant matches in today's pipeline.</small></p>")
        parts.append("<p><small>Next run: tomorrow ~8 AM IST · SAP UI5 / Fiori / BTP / OData roles · India</small></p>")
        return "\n".join(parts)

    headline = (
        f"{len(jobs)} new SAP job match{'es' if len(jobs) != 1 else ''}"
        if new_only
        else f"{len(jobs)} SAP job matches"
    )
    parts = [
        f"<h2>SAP Job Scout — {date_str}</h2>",
        f"<p><strong>{headline}</strong></p>",
        "<p><em>SAP UI5 · Fiori · BTP · CAP · OData · ABAP · India · 0–5 yrs experience band</em></p>",
    ]

    emoji = {"LinkedIn": "🔗", "Naukri": "📋", "Indeed": "🔍", "Adzuna": "📊"}
    for source, items in _group_by_source(jobs).items():
        parts.append(f"<h4>{emoji.get(source, '📌')} {source} ({len(items)})</h4><ul>")
        for job in items:
            parts.append(
                f"<li><a href=\"{job.url}\"><strong>{job.company}</strong> — {job.title}</a>"
                f"<br><small>{job.location}</small></li>"
            )
        parts.append("</ul>")

    if suppressed_count:
        parts.append(
            f"<p><small>{suppressed_count} additional match(es) suppressed (already emailed max times).</small></p>"
        )
    parts.append(
        f"<p><small>Profile: SAP UI5/Fiori developer · immediate joiner · "
        f"{total_scanned} scanned today · — SAP Job Scout</small></p>"
    )
    return "\n".join(parts)


def build_digest_text(
    jobs: list[SapJob],
    *,
    new_only: bool,
    suppressed_count: int = 0,
    total_scanned: int = 0,
) -> str:
    ist = datetime.now(ZoneInfo("Asia/Kolkata"))
    lines = [f"SAP Job Scout — {ist.strftime('%d %b %Y')}", ""]

    if not jobs:
        lines += [
            "No new SAP UI5 / Fiori openings today.",
            "Scan completed (LinkedIn, Naukri, Indeed, Adzuna).",
        ]
        if suppressed_count:
            lines.append(f"({suppressed_count} suppressed — already emailed.)")
        if total_scanned:
            lines.append(f"({total_scanned} total matches in pipeline.)")
        lines.append("Next run: tomorrow ~8 AM IST.")
        return "\n".join(lines)

    lines.append(f"{len(jobs)} SAP job match(es):")
    lines.append("")
    for job in jobs:
        lines.append(f"• [{job.source}] {job.company} — {job.title}")
        lines.append(f"  {job.location} | {job.url}")
        lines.append("")
    if suppressed_count:
        lines.append(f"({suppressed_count} suppressed)")
    return "\n".join(lines)


def send_digest(
    jobs: list[SapJob],
    *,
    new_only: bool = True,
    suppressed_count: int = 0,
    total_scanned: int = 0,
    dry_run: bool = False,
) -> list[str]:
    """Send identical digest to Ananya + monitor inbox. Returns list of recipient emails."""
    recipients = []
    for addr in (SAP_RECIPIENT_EMAIL, SAP_MONITOR_EMAIL):
        addr = (addr or "").strip()
        if addr and addr not in recipients:
            recipients.append(addr)

    ist = datetime.now(ZoneInfo("Asia/Kolkata"))
    if jobs:
        subject = f"SAP Scout: {len(jobs)} job{'s' if len(jobs) != 1 else ''} — {ist.strftime('%d %b')}"
    else:
        subject = f"SAP Scout: No new openings — {ist.strftime('%d %b')}"

    text = build_digest_text(
        jobs, new_only=new_only, suppressed_count=suppressed_count, total_scanned=total_scanned,
    )
    html = build_digest_html(
        jobs, new_only=new_only, suppressed_count=suppressed_count, total_scanned=total_scanned,
    )

    if dry_run:
        print("=== SAP JOB SCOUT DRY RUN ===")
        print(f"Would send to: {', '.join(recipients)}")
        print(f"Subject: {subject}")
        print(text[:4000])
        return recipients

    if not SMTP_APP_PASSWORD:
        raise RuntimeError("SMTP_APP_PASSWORD missing in internship-scout/.env")

    sent_to: list[str] = []
    for recipient in recipients:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = SMTP_EMAIL
        msg["To"] = recipient
        msg.attach(MIMEText(text, "plain"))
        msg.attach(MIMEText(html, "html"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=30) as server:
            server.login(SMTP_EMAIL, SMTP_APP_PASSWORD)
            server.sendmail(SMTP_EMAIL, [recipient], msg.as_string())
        sent_to.append(recipient)
        print(f"SAP digest sent to {recipient}")

    return sent_to
