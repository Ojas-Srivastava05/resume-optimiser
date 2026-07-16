#!/usr/bin/env python3
"""Preflight Gmail SMTP credentials for GitHub Actions workflows."""

from __future__ import annotations

import os
import smtplib
import sys


def main() -> int:
	email = os.getenv("SMTP_EMAIL", "").strip()
	password = os.getenv("SMTP_APP_PASSWORD", "").replace(" ", "")
	label = os.getenv("SMTP_VERIFY_LABEL", "workflow")

	if not email:
		print("::error::SMTP_EMAIL is not set in GitHub repository secrets.", file=sys.stderr)
		return 1
	if not password:
		print("::error::SMTP_APP_PASSWORD is not set in GitHub repository secrets.", file=sys.stderr)
		return 1
	if len(password) < 16:
		print(
			"::error::SMTP_APP_PASSWORD looks too short. "
			"Use a 16-character Gmail App Password (not your normal Gmail password).",
			file=sys.stderr,
		)
		return 1

	try:
		with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=20) as server:
			server.login(email, password)
	except smtplib.SMTPAuthenticationError as exc:
		print(
			f"::error::Gmail rejected SMTP login for workflow '{label}'. "
			"Regenerate an App Password: Google Account → Security → "
			"2-Step Verification → App passwords → Mail. "
			"Update the SMTP_APP_PASSWORD repository secret (Settings → Secrets → Actions).",
			file=sys.stderr,
		)
		print(f"SMTP detail: {exc}", file=sys.stderr)
		return 1
	except OSError as exc:
		print(f"::error::SMTP connection failed: {exc}", file=sys.stderr)
		return 1

	print(f"SMTP preflight OK for {label} ({email}).")
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
