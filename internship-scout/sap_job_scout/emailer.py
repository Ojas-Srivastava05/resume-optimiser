"""Daily SAP job digest email — polished HTML for Ananya + monitor copies."""

from __future__ import annotations

import html
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from zoneinfo import ZoneInfo

from sap_job_scout.config import (
    SAP_EXTRA_RECIPIENTS,
    SAP_MONITOR_EMAIL,
    SAP_RECIPIENT_EMAIL,
    SMTP_APP_PASSWORD,
    SMTP_EMAIL,
)
from sap_job_scout.models import SapJob

# SAP brand-adjacent palette (email-safe inline styles)
_BLUE = "#0070F2"
_BLUE_DARK = "#004C99"
_INK = "#1A2332"
_MUTED = "#5B6B7C"
_BG = "#F0F5FA"
_CARD = "#FFFFFF"
_BORDER = "#D6E2EF"
_ACCENT = "#00B4A0"

_SOURCE_COLORS = {
    "LinkedIn": "#0A66C2",
    "Naukri": "#FF7555",
    "Indeed": "#2557A7",
    "Adzuna": "#1E8A5A",
}


def _group_by_source(jobs: list[SapJob]) -> dict[str, list[SapJob]]:
    groups: dict[str, list[SapJob]] = {}
    for job in jobs:
        groups.setdefault(job.source, []).append(job)
    return groups


def _esc(value: str) -> str:
    return html.escape(value or "", quote=True)


def _source_badge(source: str) -> str:
    color = _SOURCE_COLORS.get(source, _BLUE)
    return (
        f'<span style="display:inline-block;background:{color};color:#fff;'
        f'font-size:11px;font-weight:600;letter-spacing:0.03em;padding:3px 8px;'
        f'border-radius:4px;text-transform:uppercase;">{_esc(source)}</span>'
    )


def _stat_pill(label: str, value: str) -> str:
    return (
        f'<td style="padding:0 6px 0 0;vertical-align:top;">'
        f'<div style="background:rgba(255,255,255,0.14);border:1px solid rgba(255,255,255,0.22);'
        f'border-radius:10px;padding:10px 14px;min-width:88px;">'
        f'<div style="font-size:20px;font-weight:700;color:#fff;line-height:1.1;">{_esc(value)}</div>'
        f'<div style="font-size:11px;color:rgba(255,255,255,0.78);margin-top:4px;'
        f'text-transform:uppercase;letter-spacing:0.04em;">{_esc(label)}</div>'
        f"</div></td>"
    )


def _job_card(job: SapJob, index: int) -> str:
    company = _esc(job.company)
    title = _esc(job.title)
    location = _esc(job.location or "India")
    url = _esc(job.url)
    top_border = f"border-top:1px solid {_BORDER};" if index else ""
    return f"""
<tr>
  <td style="padding:16px 20px;{top_border}">
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
      <tr>
        <td style="vertical-align:top;padding-right:12px;">
          {_source_badge(job.source)}
          <div style="font-size:16px;font-weight:700;color:{_INK};margin:10px 0 4px;line-height:1.35;">
            <a href="{url}" style="color:{_INK};text-decoration:none;">{title}</a>
          </div>
          <div style="font-size:14px;color:{_BLUE_DARK};font-weight:600;margin-bottom:6px;">{company}</div>
          <div style="font-size:13px;color:{_MUTED};">📍 {location}</div>
        </td>
        <td style="vertical-align:middle;width:108px;text-align:right;">
          <a href="{url}"
             style="display:inline-block;background:{_BLUE};color:#ffffff;text-decoration:none;
                    font-size:13px;font-weight:600;padding:10px 14px;border-radius:8px;">
            Apply →
          </a>
        </td>
      </tr>
    </table>
  </td>
</tr>
"""


def _wrap_email(body_inner: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>SAP Job Scout</title>
</head>
<body style="margin:0;padding:0;background:{_BG};font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="background:{_BG};padding:24px 12px;">
    <tr>
      <td align="center">
        <table role="presentation" width="640" cellpadding="0" cellspacing="0" border="0"
               style="max-width:640px;width:100%;background:{_CARD};border-radius:16px;
                      overflow:hidden;border:1px solid {_BORDER};box-shadow:0 8px 28px rgba(0,76,153,0.08);">
          {body_inner}
        </table>
        <div style="max-width:640px;width:100%;margin-top:14px;font-size:11px;color:{_MUTED};text-align:center;line-height:1.5;">
          SAP Job Scout · India · UI5 / Fiori / BTP / CAP / OData / ABAP / RAP<br>
          You receive this digest because you are on the scout recipient list.
        </div>
      </td>
    </tr>
  </table>
</body>
</html>
"""


def build_digest_html(
    jobs: list[SapJob],
    *,
    new_only: bool,
    suppressed_count: int = 0,
    total_scanned: int = 0,
) -> str:
    ist = datetime.now(ZoneInfo("Asia/Kolkata"))
    date_str = ist.strftime("%d %b %Y")
    sources = len(_group_by_source(jobs)) if jobs else 0

    header = f"""
<tr>
  <td style="background:linear-gradient(135deg,{_BLUE_DARK} 0%,{_BLUE} 55%,{_ACCENT} 140%);
             padding:28px 24px 22px;">
    <div style="font-size:12px;font-weight:600;letter-spacing:0.12em;text-transform:uppercase;
                color:rgba(255,255,255,0.78);margin-bottom:8px;">Daily Digest</div>
    <div style="font-size:26px;font-weight:700;color:#ffffff;letter-spacing:-0.02em;line-height:1.2;">
      SAP Job Scout
    </div>
    <div style="font-size:14px;color:rgba(255,255,255,0.88);margin-top:8px;">{_esc(date_str)} · India focus</div>
    <table role="presentation" cellpadding="0" cellspacing="0" border="0" style="margin-top:18px;">
      <tr>
        {_stat_pill("Matches", str(len(jobs)))}
        {_stat_pill("Sources", str(sources or 4))}
        {_stat_pill("Scanned", str(total_scanned or len(jobs)))}
      </tr>
    </table>
  </td>
</tr>
"""

    if not jobs:
        empty = f"""
<tr>
  <td style="padding:28px 24px;">
    <div style="font-size:18px;font-weight:700;color:{_INK};margin-bottom:8px;">
      No new openings today
    </div>
    <p style="margin:0 0 12px;font-size:14px;color:{_MUTED};line-height:1.55;">
      Scan finished across LinkedIn, Naukri, Indeed, and Adzuna. Nothing fresh matched
      the UI5 / Fiori / BTP filters that has not already been emailed.
    </p>
"""
        if suppressed_count:
            empty += (
                f'<p style="margin:0 0 8px;font-size:13px;color:{_MUTED};">'
                f"{suppressed_count} listing(s) still live but already emailed the max times — skipped.</p>"
            )
        if total_scanned:
            empty += (
                f'<p style="margin:0;font-size:13px;color:{_MUTED};">'
                f"{total_scanned} SAP-relevant matches in today's pipeline.</p>"
            )
        empty += f"""
    <p style="margin:18px 0 0;font-size:12px;color:{_MUTED};">Next run · tomorrow ~8 AM IST</p>
  </td>
</tr>
"""
        return _wrap_email(header + empty)

    headline = (
        f"{len(jobs)} new SAP match{'es' if len(jobs) != 1 else ''}"
        if new_only
        else f"{len(jobs)} SAP job matches"
    )
    intro = f"""
<tr>
  <td style="padding:22px 24px 8px;">
    <div style="font-size:18px;font-weight:700;color:{_INK};">{_esc(headline)}</div>
    <div style="font-size:13px;color:{_MUTED};margin-top:6px;line-height:1.5;">
      UI5 · Fiori · BTP · CAP · RAP · OData · ABAP · S/4HANA · 0–5 yrs band · India
    </div>
  </td>
</tr>
"""

    sections: list[str] = []
    for source, items in _group_by_source(jobs).items():
        cards = "".join(_job_card(job, i) for i, job in enumerate(items))
        sections.append(f"""
<tr>
  <td style="padding:12px 24px 4px;">
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
      <tr>
        <td style="font-size:13px;font-weight:700;color:{_INK};text-transform:uppercase;
                   letter-spacing:0.06em;">
          {_source_badge(source)}
          <span style="margin-left:8px;color:{_MUTED};font-weight:600;">{len(items)} role{'s' if len(items) != 1 else ''}</span>
        </td>
      </tr>
    </table>
  </td>
</tr>
<tr>
  <td style="padding:8px 24px 16px;">
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"
           style="background:{_CARD};border:1px solid {_BORDER};border-radius:12px;overflow:hidden;">
      {cards}
    </table>
  </td>
</tr>
""")

    footer_bits = [
        "Profile: SAP UI5 / Fiori developer · immediate joiner",
        f"{total_scanned} scanned today" if total_scanned else "",
        f"{suppressed_count} suppressed" if suppressed_count else "",
    ]
    footer_line = " · ".join(bit for bit in footer_bits if bit)
    footer = f"""
<tr>
  <td style="padding:8px 24px 24px;">
    <div style="background:{_BG};border-radius:10px;padding:14px 16px;font-size:12px;color:{_MUTED};line-height:1.55;">
      {_esc(footer_line)}
    </div>
  </td>
</tr>
"""
    return _wrap_email(header + intro + "".join(sections) + footer)


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
    """Send identical digest to all configured recipients. Returns list of recipient emails."""
    recipients = []
    for addr in (SAP_RECIPIENT_EMAIL, SAP_MONITOR_EMAIL, *SAP_EXTRA_RECIPIENTS):
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
    html_body = build_digest_html(
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
        msg.attach(MIMEText(html_body, "html"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=30) as server:
            try:
                server.login(SMTP_EMAIL, SMTP_APP_PASSWORD)
            except smtplib.SMTPAuthenticationError as exc:
                raise RuntimeError(
                    "Gmail auth failed. SMTP_APP_PASSWORD must be a 16-character Gmail App Password. "
                    "Regenerate in Google Account → Security → App passwords."
                ) from exc
            server.sendmail(SMTP_EMAIL, [recipient], msg.as_string())
        sent_to.append(recipient)
        print(f"SAP digest sent to {recipient}")

    return sent_to
