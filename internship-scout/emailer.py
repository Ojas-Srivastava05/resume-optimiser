"""Send concise HTML digest via Gmail SMTP."""

import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from zoneinfo import ZoneInfo

from config import RECIPIENT_EMAIL, SMTP_APP_PASSWORD, SMTP_EMAIL
from filters import Job


def _group_by_source(jobs: list[Job]) -> dict[str, list[Job]]:
    groups: dict[str, list[Job]] = {}
    for job in jobs:
        groups.setdefault(job.source, []).append(job)
    return groups


def build_digest_html(
    jobs: list[Job],
    *,
    new_only: bool,
    suppressed_count: int = 0,
    total_scanned: int = 0,
) -> str:
    ist = datetime.now(ZoneInfo("Asia/Kolkata"))
    date_str = ist.strftime("%d %b %Y")

    if not jobs:
        parts = [
            f"<h2>Internship Scout — {date_str}</h2>",
            "<p><strong>No new openings for today.</strong></p>",
            "<p>The daily scan completed successfully. Nothing new to apply to right now.</p>",
        ]
        if suppressed_count:
            parts.append(
                f"<p><small>{suppressed_count} live listing{'s' if suppressed_count != 1 else ''} "
                f"still match your filters but were already emailed twice — skipped to avoid repeats.</small></p>"
            )
        if total_scanned:
            parts.append(
                f"<p><small>Scanned sources today · {total_scanned} total match{'es' if total_scanned != 1 else ''} in pipeline.</small></p>"
            )
        parts.append("<p><small>Next automatic run: tomorrow ~8 AM IST. — Internship Scout</small></p>")
        return "\n".join(parts)

    headline = (
        f"{len(jobs)} new internship match{'es' if len(jobs) != 1 else ''}"
        if new_only
        else f"{len(jobs)} internship matches (full scan)"
    )

    parts = [
        f"<h2>Internship Scout — {date_str}</h2>",
        f"<p><strong>{headline}</strong></p>",
    ]

    for source, items in _group_by_source(jobs).items():
        parts.append(f"<h3>{source} ({len(items)})</h3><ul>")
        for job in items:
            parts.append(
                f"<li><a href=\"{job.url}\"><strong>{job.company}</strong> — "
                f"{job.title}</a><br><small>{job.location}</small></li>"
            )
        parts.append("</ul>")

    parts.append(
        "<p><small>Priority companies · software/ML intern · batch 2028 · "
        f"each opening emailed max 2 times · — Internship Scout</small></p>"
    )
    return "\n".join(parts)


def build_digest_text(
    jobs: list[Job],
    *,
    new_only: bool,
    suppressed_count: int = 0,
    total_scanned: int = 0,
) -> str:
    ist = datetime.now(ZoneInfo("Asia/Kolkata"))
    lines = [f"Internship Scout — {ist.strftime('%d %b %Y')}", ""]
    if not jobs:
        lines.append("No new openings for today.")
        lines.append("")
        lines.append("Daily scan completed OK — nothing new to apply to.")
        if suppressed_count:
            lines.append(
                f"({suppressed_count} listing(s) skipped — already emailed twice.)"
            )
        if total_scanned:
            lines.append(f"({total_scanned} total matches in today's scan.)")
        lines.append("")
        lines.append("Next run: tomorrow ~8 AM IST.")
        return "\n".join(lines)

    for job in jobs:
        lines.append(f"• [{job.source}] {job.company} — {job.title}")
        lines.append(f"  {job.location} | {job.url}")
        lines.append("")
    return "\n".join(lines)


def send_digest(
    jobs: list[Job],
    *,
    new_only: bool = True,
    suppressed_count: int = 0,
    total_scanned: int = 0,
) -> None:
    if not SMTP_APP_PASSWORD:
        raise RuntimeError(
            "SMTP_APP_PASSWORD missing. Copy .env.example to .env and add a Gmail app password."
        )

    ist = datetime.now(ZoneInfo("Asia/Kolkata"))
    if jobs:
        subject = (
            f"Internship Scout: {len(jobs)} new opening{'s' if len(jobs) != 1 else ''} "
            f"— {ist.strftime('%d %b')}"
        )
    else:
        subject = f"Internship Scout: No new openings today — {ist.strftime('%d %b')}"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = SMTP_EMAIL
    msg["To"] = RECIPIENT_EMAIL

    text = build_digest_text(
        jobs, new_only=new_only, suppressed_count=suppressed_count, total_scanned=total_scanned
    )
    html = build_digest_html(
        jobs, new_only=new_only, suppressed_count=suppressed_count, total_scanned=total_scanned
    )
    msg.attach(MIMEText(text, "plain"))
    msg.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=30) as server:
            server.login(SMTP_EMAIL, SMTP_APP_PASSWORD)
            server.sendmail(SMTP_EMAIL, [RECIPIENT_EMAIL], msg.as_string())
    except smtplib.SMTPAuthenticationError as exc:
        hint = (
            "Gmail rejected login. SMTP_APP_PASSWORD must be a 16-character "
            "Gmail *App Password*, not your normal Gmail password.\n"
            "Create one: Google Account → Security → 2-Step Verification → "
            "App passwords → Mail → copy the 16-char code into .env"
        )
        if b"Application-specific password required" in getattr(exc, "smtp_error", b""):
            raise RuntimeError(hint) from exc
        raise RuntimeError(f"Gmail auth failed. {hint}") from exc
