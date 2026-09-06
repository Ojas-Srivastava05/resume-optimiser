#!/usr/bin/env python3
"""Diagnose EXTRA_RECIPIENTS + send a short test ping to every digest inbox."""

from __future__ import annotations

import email
import imaplib
import smtplib
import time
from datetime import datetime
from email.mime.text import MIMEText
from zoneinfo import ZoneInfo

from config import EXTRA_RECIPIENTS, RECIPIENT_EMAIL, SMTP_APP_PASSWORD, SMTP_EMAIL
from emailer import digest_recipients


def main() -> None:
    recipients = digest_recipients()
    print("SMTP_EMAIL set:", bool(SMTP_EMAIL))
    print("RECIPIENT_EMAIL set:", bool(RECIPIENT_EMAIL))
    print("EXTRA_RECIPIENTS count:", len(EXTRA_RECIPIENTS))
    for i, addr in enumerate(EXTRA_RECIPIENTS, 1):
        print(f"  extra[{i}]: {addr}")
    print("digest_recipients():", recipients)

    if not SMTP_APP_PASSWORD:
        raise SystemExit("SMTP_APP_PASSWORD missing")

    ist = datetime.now(ZoneInfo("Asia/Kolkata")).strftime("%d %b %Y %H:%M IST")
    subject = f"Scout recipient test — {ist}"
    body = (
        "This is a delivery test from Internship Scout.\n\n"
        f"If you received this, EXTRA_RECIPIENTS delivery works.\n"
        f"Sent at {ist} via Gmail SMTP.\n"
        f"Recipients this run: {', '.join(recipients)}\n"
    )

    print("\nSending test mail one-by-one…")
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=45) as server:
        server.login(SMTP_EMAIL, SMTP_APP_PASSWORD)
        for recipient in recipients:
            msg = MIMEText(body, "plain")
            msg["Subject"] = subject
            msg["From"] = SMTP_EMAIL
            msg["To"] = recipient
            refused = server.sendmail(SMTP_EMAIL, [recipient], msg.as_string())
            print(f"  sendmail → {recipient} refused={refused or '{}'}")
            time.sleep(1)

    print("\nChecking Gmail Sent (IMAP) for matching subjects…")
    try:
        imap = imaplib.IMAP4_SSL("imap.gmail.com", 993, timeout=45)
        imap.login(SMTP_EMAIL, SMTP_APP_PASSWORD)
        typ, boxes = imap.list()
        sent_box = "[Gmail]/Sent Mail"
        for b in boxes or []:
            line = b.decode(errors="replace")
            if "\\Sent" in line or "Sent Mail" in line:
                import re

                names = re.findall(r'"([^"]+)"', line)
                if names:
                    sent_box = names[-1]
                break
        typ, _ = imap.select(f'"{sent_box}"', readonly=True)
        print("IMAP select", typ, sent_box)
        typ, data = imap.search(None, '(SUBJECT "Scout recipient test")')
        ids = data[0].split() if data and data[0] else []
        print(f"Found {len(ids)} test message(s) in Sent")
        for mid in ids[-8:]:
            typ, fetched = imap.fetch(mid, "(BODY.PEEK[HEADER.FIELDS (SUBJECT TO DATE)])")
            if typ != "OK":
                continue
            hdr = email.message_from_bytes(fetched[0][1])
            print(
                f"  Sent copy: Date={hdr.get('Date')} To={hdr.get('To')} Subject={hdr.get('Subject')}"
            )
        imap.logout()
    except Exception as exc:
        print(f"IMAP check failed (non-fatal): {exc}")

    print("\nDONE")


if __name__ == "__main__":
    main()
