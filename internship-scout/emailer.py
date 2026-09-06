"""Send concise HTML digest via Gmail SMTP — internships + hackathons."""

import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from zoneinfo import ZoneInfo

from config import EXTRA_RECIPIENTS, RECIPIENT_EMAIL, SMTP_APP_PASSWORD, SMTP_EMAIL
from filters import Job


def digest_recipients() -> list[str]:
    """Primary + extras, de-duplicated, order preserved."""
    recipients: list[str] = []
    for addr in (RECIPIENT_EMAIL, *EXTRA_RECIPIENTS):
        addr = (addr or "").strip()
        if addr and addr not in recipients:
            recipients.append(addr)
    return recipients


def _group_by_source(jobs: list[Job]) -> dict[str, list[Job]]:
    groups: dict[str, list[Job]] = {}
    for job in jobs:
        groups.setdefault(job.source, []).append(job)
    return groups


def _portal_line(portal_coverage) -> str:
    if not portal_coverage:
        return ""
    if hasattr(portal_coverage, "line"):
        return portal_coverage.line()
    return str(portal_coverage)


def build_digest_html(
    jobs: list[Job],
    *,
    new_only: bool,
    suppressed_count: int = 0,
    total_scanned: int = 0,
    hackathons: list | None = None,
    portal_coverage=None,
) -> str:
    ist = datetime.now(ZoneInfo("Asia/Kolkata"))
    date_str = ist.strftime("%d %b %Y")
    hackathons = hackathons or []
    coverage = _portal_line(portal_coverage)

    if not jobs and not hackathons:
        parts = [
            f"<h2>Internship + Hackathon Scout — {date_str}</h2>",
            "<p><strong>No new openings or hackathons for today.</strong></p>",
            "<p>The daily scan completed successfully. Nothing new to apply to right now.</p>",
        ]
        if coverage:
            parts.append(f"<p><small>🌐 {coverage}</small></p>")
        if suppressed_count:
            parts.append(
                f"<p><small>{suppressed_count} live listing{'s' if suppressed_count != 1 else ''} "
                f"still match your filters but were already emailed twice — skipped to avoid repeats.</small></p>"
            )
        if total_scanned:
            parts.append(
                f"<p><small>Scanned sources today · {total_scanned} total match{'es' if total_scanned != 1 else ''} in pipeline.</small></p>"
            )
        parts.append("<p><small>Next automatic run: tomorrow ~8 AM IST. — Internship + Hackathon Scout</small></p>")
        return "\n".join(parts)

    parts = [
        f"<h2>🔍 Internship + Hackathon Scout — {date_str}</h2>",
    ]
    if coverage:
        parts.append(
            f"<p style='background:#f4f6fb;padding:10px 12px;border-radius:6px;'>"
            f"<strong>🌐 Portal coverage:</strong> {coverage}</p>"
        )

    if jobs:
        headline = (
            f"{len(jobs)} new internship match{'es' if len(jobs) != 1 else ''}"
            if new_only
            else f"{len(jobs)} internship matches (full scan)"
        )
        parts.append("<h3>💼 Internships</h3>")
        parts.append(f"<p><strong>{headline}</strong></p>")

        for source, items in _group_by_source(jobs).items():
            emoji = {
                "Greenhouse": "🌿",
                "Lever": "🔧",
                "Ashby": "🔶",
                "Workday": "🏢",
                "SmartRecruiters": "📣",
                "Oracle CX": "🏛️",
                "Careers→GH": "🌿",
                "Careers→Lever": "🔧",
                "Careers→Ashby": "🔶",
                "LinkedIn": "🔗",
                "Careers Web": "🌐",
                "Unstop": "🛑",
                "Adzuna": "📊",
                "Internshala": "🎓",
                "Internshala★": "⭐",
                "Naukri": "📋",
                "Indeed": "🔍",
            }.get(source, "📌")

            parts.append(f"<h4>{emoji} {source} ({len(items)})</h4><ul>")
            for job in items:
                parts.append(
                    f"<li><a href=\"{job.url}\"><strong>{job.company}</strong> — "
                    f"{job.title}</a><br><small>{job.location}</small></li>"
                )
            parts.append("</ul>")

    if hackathons:
        parts.append("<hr style='border:1px solid #e94560;margin:20px 0;'>")
        parts.append(f"<h3>🏆 Elite Hackathons & Competitions ({len(hackathons)})</h3>")
        parts.append("<p><em>MNC-organized · PPI opportunities · ₹40k+ prizes</em></p>")
        parts.append(
            "<table style='border-collapse:collapse;width:100%;font-size:14px;'>"
            "<tr style='background:#1a1a2e;color:#e94560;'>"
            "<th style='padding:8px;text-align:left;'>Event</th>"
            "<th style='padding:8px;text-align:left;'>Organizer</th>"
            "<th style='padding:8px;text-align:left;'>Tags</th>"
            "<th style='padding:8px;text-align:left;'>Source</th>"
            "</tr>"
        )
        for i, h in enumerate(hackathons):
            bg = "#16213e" if i % 2 == 0 else "#0f3460"
            tags_str = " ".join(h.tags) if h.tags else "—"
            parts.append(
                f"<tr style='background:{bg};color:#eee;'>"
                f"<td style='padding:8px;'><a href='{h.url}' style='color:#e94560;text-decoration:underline;'>{h.title}</a></td>"
                f"<td style='padding:8px;'>{h.organizer}</td>"
                f"<td style='padding:8px;'>{tags_str}</td>"
                f"<td style='padding:8px;'>{h.platform}</td>"
                f"</tr>"
            )
        parts.append("</table>")

    source_summary = "10 internship sources + 3 hackathon platforms"
    footer_bits = [
        "Priority companies · CS-adjacent intern · batch 2028",
        "each opening emailed max 2 times",
        source_summary,
    ]
    if coverage:
        footer_bits.append(coverage)
    parts.append(
        f"<p><small>{' · '.join(footer_bits)} · — Internship + Hackathon Scout</small></p>"
    )
    return "\n".join(parts)


def build_digest_text(
    jobs: list[Job],
    *,
    new_only: bool,
    suppressed_count: int = 0,
    total_scanned: int = 0,
    hackathons: list | None = None,
    portal_coverage=None,
) -> str:
    ist = datetime.now(ZoneInfo("Asia/Kolkata"))
    lines = [f"Internship + Hackathon Scout — {ist.strftime('%d %b %Y')}", ""]
    hackathons = hackathons or []
    coverage = _portal_line(portal_coverage)
    if coverage:
        lines.append(f"Portal coverage: {coverage}")
        lines.append("")

    if not jobs and not hackathons:
        lines.append("No new openings or hackathons for today.")
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

    if jobs:
        lines.append("═══ INTERNSHIPS ═══")
        lines.append("")
        for job in jobs:
            lines.append(f"• [{job.source}] {job.company} — {job.title}")
            lines.append(f"  {job.location} | {job.url}")
            lines.append("")

    if hackathons:
        lines.append("═══ ELITE HACKATHONS & COMPETITIONS ═══")
        lines.append("MNC-organized · PPI opportunities · ₹40k+ prizes")
        lines.append("")
        for h in hackathons:
            tags_str = " | ".join(h.tags) if h.tags else ""
            lines.append(f"• [{h.platform}] {h.organizer} — {h.title}")
            if tags_str:
                lines.append(f"  {tags_str}")
            lines.append(f"  {h.url}")
            lines.append("")

    return "\n".join(lines)


def send_digest(
    jobs: list[Job],
    *,
    new_only: bool = True,
    suppressed_count: int = 0,
    total_scanned: int = 0,
    hackathons: list | None = None,
    portal_coverage=None,
) -> list[str]:
    """Send identical digest to all configured recipients. Returns emails sent to."""
    if not SMTP_APP_PASSWORD:
        raise RuntimeError(
            "SMTP_APP_PASSWORD missing. Copy .env.example to .env and add a Gmail app password."
        )

    recipients = digest_recipients()
    if not recipients:
        raise RuntimeError("No recipients configured (RECIPIENT_EMAIL / EXTRA_RECIPIENTS)")

    hackathons = hackathons or []
    ist = datetime.now(ZoneInfo("Asia/Kolkata"))

    parts = []
    if jobs:
        parts.append(f"{len(jobs)} internship{'s' if len(jobs) != 1 else ''}")
    if hackathons:
        parts.append(f"{len(hackathons)} hackathon{'s' if len(hackathons) != 1 else ''}")

    if parts:
        subject = f"Scout: {' + '.join(parts)} — {ist.strftime('%d %b')}"
    else:
        subject = f"Scout: No new openings today — {ist.strftime('%d %b')}"

    text = build_digest_text(
        jobs,
        new_only=new_only,
        suppressed_count=suppressed_count,
        total_scanned=total_scanned,
        hackathons=hackathons,
        portal_coverage=portal_coverage,
    )
    html = build_digest_html(
        jobs,
        new_only=new_only,
        suppressed_count=suppressed_count,
        total_scanned=total_scanned,
        hackathons=hackathons,
        portal_coverage=portal_coverage,
    )

    hint = (
        "Gmail rejected login. SMTP_APP_PASSWORD must be a 16-character "
        "Gmail *App Password*, not your normal Gmail password.\n"
        "Create one: Google Account → Security → 2-Step Verification → "
        "App passwords → Mail → copy the 16-char code into .env"
    )
    sent_to: list[str] = []
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=30) as server:
            try:
                server.login(SMTP_EMAIL, SMTP_APP_PASSWORD)
            except smtplib.SMTPAuthenticationError as exc:
                if b"Application-specific password required" in getattr(exc, "smtp_error", b""):
                    raise RuntimeError(hint) from exc
                raise RuntimeError(f"Gmail auth failed. {hint}") from exc

            # One SMTP transaction for everyone. Envelope RCPT TO includes all
            # addresses; To: header lists them so Sent Mail proves delivery targets.
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = SMTP_EMAIL
            msg["To"] = ", ".join(recipients)
            msg.attach(MIMEText(text, "plain"))
            msg.attach(MIMEText(html, "html"))
            refused = server.sendmail(SMTP_EMAIL, recipients, msg.as_string())
            if refused:
                raise RuntimeError(f"Gmail refused some recipients: {refused}")
            sent_to = list(recipients)
    except smtplib.SMTPAuthenticationError as exc:
        if b"Application-specific password required" in getattr(exc, "smtp_error", b""):
            raise RuntimeError(hint) from exc
        raise RuntimeError(f"Gmail auth failed. {hint}") from exc

    return sent_to
