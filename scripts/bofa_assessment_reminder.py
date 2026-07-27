#!/usr/bin/env python3
"""Bank of America assessment deadline reminder — HTML email, thrice daily until cutoff.

Deadline: 3 days from invitation email (2026-07-28 00:55 IST) → 2026-07-31 00:55 IST.
Uses internship-scout/.env SMTP (same as Internship Scout).
"""

from __future__ import annotations

import argparse
import os
import smtplib
import sys
from datetime import datetime, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
SCOUT_ENV = ROOT / "internship-scout" / ".env"
IST = ZoneInfo("Asia/Kolkata")

# Invitation: 28 Jul 2026 ~00:55 IST → complete within 3 days
DEADLINE = datetime(2026, 7, 31, 0, 55, tzinfo=IST)
APP_ID = "4755860"
ROLE = "Global Investment Banking Summer Analyst — 2027 — Mumbai"
ASSESSMENT = "India Campus Assessment - F"
PORTAL_HINT = "Log in to your Application Center (link in the BofA invitation email)"
ACCOMMODATION_EMAIL = "apac_campus@bofa.com"


def _load_dotenv(path: Path) -> None:
    if not path.is_file():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        key, val = key.strip(), val.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = val


def _remaining(now: datetime) -> tuple[bool, str, str, int]:
    """Return (active, headline, subline, hours_left_floored)."""
    if now >= DEADLINE:
        return False, "DEADLINE PASSED", "Assessment window has closed — do not rely on this reminder.", 0
    delta = DEADLINE - now
    total_sec = int(delta.total_seconds())
    days, rem = divmod(total_sec, 86400)
    hours, rem = divmod(rem, 3600)
    mins = rem // 60
    hours_left = total_sec // 3600
    if days > 0:
        clock = f"{days}d {hours:02d}h {mins:02d}m"
    else:
        clock = f"{hours:02d}h {mins:02d}m"
    if hours_left <= 12:
        headline = "FINAL HOURS — COMPLETE TODAY"
    elif hours_left <= 36:
        headline = "UNDER 2 DAYS LEFT — DO NOT DELAY"
    else:
        headline = "REMINDER — COMPLETE YOUR ASSESSMENT"
    sub = f"Time remaining until cutoff: {clock}"
    return True, headline, sub, hours_left


def build_html(now: datetime, slot: str) -> tuple[str, str]:
    active, headline, sub, hours_left = _remaining(now)
    urgency = "#B91C1C" if hours_left <= 12 else ("#C2410C" if hours_left <= 36 else "#0F766E")
    status = "ACTIVE WINDOW" if active else "EXPIRED"
    now_str = now.strftime("%a %d %b %Y · %I:%M %p IST")
    deadline_str = DEADLINE.strftime("%a %d %b %Y · %I:%M %p IST")

    subject = (
        f"[BofA] {hours_left}h left — finish India Campus Assessment"
        if active
        else "[BofA] Assessment deadline passed — reminder stopped"
    )

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>BofA Assessment Reminder</title>
</head>
<body style="margin:0;padding:0;background:#0B1220;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;">
  <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background:#0B1220;padding:28px 12px;">
    <tr>
      <td align="center">
        <table role="presentation" width="560" cellspacing="0" cellpadding="0" style="max-width:560px;width:100%;background:#111827;border:1px solid #1F2937;border-radius:16px;overflow:hidden;">

          <!-- Header stripe -->
          <tr>
            <td style="background:linear-gradient(90deg,#012169 0%,#E31837 100%);height:6px;font-size:0;line-height:0;">&nbsp;</td>
          </tr>

          <!-- Brand -->
          <tr>
            <td style="padding:28px 28px 8px 28px;">
              <p style="margin:0 0 6px 0;font-size:11px;letter-spacing:0.18em;text-transform:uppercase;color:#94A3B8;font-weight:600;">
                Bank of America · Campus · {slot}
              </p>
              <h1 style="margin:0;font-size:26px;line-height:1.25;color:#F8FAFC;font-weight:700;">
                {headline}
              </h1>
              <p style="margin:10px 0 0 0;font-size:15px;color:#CBD5E1;line-height:1.5;">
                {sub}
              </p>
            </td>
          </tr>

          <!-- Countdown card -->
          <tr>
            <td style="padding:16px 28px 8px 28px;">
              <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background:#0B1220;border:1px solid #334155;border-radius:12px;">
                <tr>
                  <td style="padding:18px 20px;">
                    <p style="margin:0 0 4px 0;font-size:11px;letter-spacing:0.14em;text-transform:uppercase;color:#64748B;font-weight:600;">Hard cutoff</p>
                    <p style="margin:0;font-size:18px;color:#F8FAFC;font-weight:700;">{deadline_str}</p>
                    <p style="margin:8px 0 0 0;font-size:13px;color:#94A3B8;">Invitation: 28 Jul 2026 · 00:55 IST · complete within 3 days</p>
                    <p style="margin:12px 0 0 0;">
                      <span style="display:inline-block;padding:4px 10px;border-radius:999px;background:{urgency};color:#fff;font-size:11px;font-weight:700;letter-spacing:0.06em;">{status}</span>
                    </p>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- Role details -->
          <tr>
            <td style="padding:16px 28px 8px 28px;">
              <table role="presentation" width="100%" cellspacing="0" cellpadding="0">
                <tr>
                  <td style="padding:0 0 10px 0;font-size:13px;color:#94A3B8;width:120px;vertical-align:top;">Role</td>
                  <td style="padding:0 0 10px 0;font-size:14px;color:#F1F5F9;font-weight:600;">{ROLE}</td>
                </tr>
                <tr>
                  <td style="padding:0 0 10px 0;font-size:13px;color:#94A3B8;vertical-align:top;">Application ID</td>
                  <td style="padding:0 0 10px 0;font-size:14px;color:#F1F5F9;font-family:ui-monospace,Menlo,Consolas,monospace;">{APP_ID}</td>
                </tr>
                <tr>
                  <td style="padding:0 0 10px 0;font-size:13px;color:#94A3B8;vertical-align:top;">Assessment</td>
                  <td style="padding:0 0 10px 0;font-size:14px;color:#F1F5F9;font-weight:600;">{ASSESSMENT}</td>
                </tr>
                <tr>
                  <td style="padding:0;font-size:13px;color:#94A3B8;vertical-align:top;">Duration</td>
                  <td style="padding:0;font-size:14px;color:#F1F5F9;">Typically 25–60 minutes · use a laptop</td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- Checklist -->
          <tr>
            <td style="padding:18px 28px 8px 28px;">
              <p style="margin:0 0 12px 0;font-size:12px;letter-spacing:0.14em;text-transform:uppercase;color:#64748B;font-weight:700;">Before you start</p>
              <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background:#0F172A;border-radius:12px;border:1px solid #1E293B;">
                <tr><td style="padding:12px 16px;font-size:14px;color:#E2E8F0;border-bottom:1px solid #1E293B;">Quiet room · no distractions</td></tr>
                <tr><td style="padding:12px 16px;font-size:14px;color:#E2E8F0;border-bottom:1px solid #1E293B;">Laptop / desktop (not phone) · strong Wi‑Fi</td></tr>
                <tr><td style="padding:12px 16px;font-size:14px;color:#E2E8F0;border-bottom:1px solid #1E293B;">Disable pop‑up blockers</td></tr>
                <tr><td style="padding:12px 16px;font-size:14px;color:#E2E8F0;">Open assessment even if you took one for another role</td></tr>
              </table>
            </td>
          </tr>

          <!-- CTA -->
          <tr>
            <td style="padding:22px 28px 8px 28px;" align="center">
              <table role="presentation" cellspacing="0" cellpadding="0">
                <tr>
                  <td style="background:#E31837;border-radius:10px;">
                    <a href="https://campus.bankofamerica.com/" style="display:inline-block;padding:14px 28px;font-size:15px;font-weight:700;color:#FFFFFF;text-decoration:none;letter-spacing:0.02em;">
                      Open Application Center →
                    </a>
                  </td>
                </tr>
              </table>
              <p style="margin:14px 0 0 0;font-size:12px;color:#64748B;line-height:1.5;max-width:420px;">
                {PORTAL_HINT}. Use Application ID <strong style="color:#94A3B8;">{APP_ID}</strong> if asked.
              </p>
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="padding:24px 28px 28px 28px;">
              <p style="margin:0;font-size:12px;color:#64748B;line-height:1.6;">
                Sent {now_str} · slot: <strong style="color:#94A3B8;">{slot}</strong><br>
                Auto-reminder 3×/day until cutoff · accommodations: {ACCOMMODATION_EMAIL}<br>
                After the deadline this script stops sending.
              </p>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""
    return subject, html


def build_text(now: datetime, slot: str) -> str:
    active, headline, sub, _ = _remaining(now)
    return "\n".join(
        [
            headline,
            sub,
            "",
            f"Role: {ROLE}",
            f"Application ID: {APP_ID}",
            f"Assessment: {ASSESSMENT}",
            f"Deadline: {DEADLINE.strftime('%Y-%m-%d %H:%M IST')}",
            f"Now: {now.strftime('%Y-%m-%d %H:%M IST')} ({slot})",
            "",
            PORTAL_HINT,
            "Use a laptop, quiet room, disable pop-ups. Typically 25–60 min.",
            "" if active else "Window closed — no further reminders needed.",
        ]
    )


def send_email(*, dry_run: bool, force: bool, slot: str) -> int:
    _load_dotenv(SCOUT_ENV)
    recipient = os.getenv("RECIPIENT_EMAIL", "srivastavaojas454@gmail.com").strip()
    smtp_email = os.getenv("SMTP_EMAIL", recipient).strip()
    smtp_password = os.getenv("SMTP_APP_PASSWORD", "").replace(" ", "")

    now = datetime.now(IST)
    active, _, _, _ = _remaining(now)
    if not active and not force:
        print(f"Past deadline ({DEADLINE.isoformat()}). Skipping send. Use --force to override.")
        return 0

    subject, html = build_html(now, slot)
    text = build_text(now, slot)

    if dry_run:
        out = ROOT / "scripts" / "bofa_reminder_preview.html"
        out.write_text(html, encoding="utf-8")
        print(f"Dry run — wrote preview: {out}")
        print(f"Subject: {subject}")
        print(f"To: {recipient}")
        return 0

    if not smtp_password:
        print("SMTP_APP_PASSWORD missing in internship-scout/.env", file=sys.stderr)
        return 1

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = smtp_email
    msg["To"] = recipient
    msg.attach(MIMEText(text, "plain", "utf-8"))
    msg.attach(MIMEText(html, "html", "utf-8"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=30) as server:
        server.login(smtp_email, smtp_password)
        server.sendmail(smtp_email, [recipient], msg.as_string())

    print(f"Sent to {recipient}: {subject}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="BofA assessment HTML reminder email")
    parser.add_argument("--dry-run", action="store_true", help="Write HTML preview only")
    parser.add_argument("--force", action="store_true", help="Send even after deadline")
    parser.add_argument(
        "--slot",
        default="manual",
        choices=["morning", "afternoon", "evening", "manual", "test"],
        help="Label for this send window",
    )
    args = parser.parse_args()
    return send_email(dry_run=args.dry_run, force=args.force, slot=args.slot)


if __name__ == "__main__":
    raise SystemExit(main())
