"""SMTP mailer with resume attachment.

Plain text only — multipart HTML raises spam risk for 1:1 personal Gmail cold outreach.
Rate limiting is enforced in queue.py / cold_outreach.py (not here) so CI runs exit promptly.
"""

from __future__ import annotations

import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
from pathlib import Path

from cold_email.config import (
	RESUME_ATTACHMENT_NAME,
	RESUME_PATH,
	SMTP_APP_PASSWORD,
	SMTP_EMAIL,
)
from cold_email.profile import EMAIL, FULL_NAME


def send_email(
	*,
	to_addr: str,
	subject: str,
	body_text: str,
	resume_path: Path | None = None,
	dry_run: bool = False,
) -> None:
	if dry_run:
		print(f"[dry-run] Would send to {to_addr}")
		print(f"  Subject: {subject}")
		print(body_text[:800] + ("..." if len(body_text) > 800 else ""))
		return

	if not SMTP_APP_PASSWORD:
		raise RuntimeError("SMTP_APP_PASSWORD missing — set in internship-scout/.env or GitHub secrets")

	msg = MIMEMultipart()
	msg["From"] = formataddr((FULL_NAME, SMTP_EMAIL))
	msg["To"] = to_addr
	msg["Subject"] = subject
	msg["Reply-To"] = formataddr((FULL_NAME, EMAIL))
	msg.attach(MIMEText(body_text, "plain", "utf-8"))

	rpath = resume_path or RESUME_PATH
	if rpath.exists():
		with rpath.open("rb") as f:
			part = MIMEApplication(f.read(), Name=RESUME_ATTACHMENT_NAME)
		part["Content-Disposition"] = f'attachment; filename="{RESUME_ATTACHMENT_NAME}"'
		msg.attach(part)

	with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=60) as server:
		server.login(SMTP_EMAIL, SMTP_APP_PASSWORD)
		server.sendmail(SMTP_EMAIL, [to_addr], msg.as_string())
