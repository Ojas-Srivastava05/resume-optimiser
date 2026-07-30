"""Distinct HTML/text digest for First-World Internship Radar.

Subjects and branding intentionally differ from India Internship Scout
(e.g. never use 'Scout:' prefix used by internship-scout/emailer.py).
"""

from __future__ import annotations

import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from zoneinfo import ZoneInfo

from international.config import (
	CANDIDATE_FOCUS,
	CANDIDATE_NAME,
	DIGEST_BRAND,
	DIGEST_SUBJECT_PREFIX,
	RECIPIENT_EMAIL,
	SMTP_APP_PASSWORD,
	SMTP_EMAIL,
	TARGET_SEASON,
)
from international.models import LiveListing, Opportunity


def _ist_date() -> str:
	return datetime.now(ZoneInfo("Asia/Kolkata")).strftime("%d %b %Y")


def build_html(
	programs: list[Opportunity],
	*,
	listings: list[LiveListing] | None = None,
	suppressed: int = 0,
	draft_snippets: list[tuple[str, str]] | None = None,
) -> str:
	listings = listings or []
	draft_snippets = draft_snippets or []
	date_str = _ist_date()

	parts = [
		f"<div style='font-family:Georgia,serif;max-width:720px;'>",
		f"<h2 style='color:#0b3d5c;margin-bottom:4px;'>{DIGEST_BRAND}</h2>",
		f"<p style='color:#555;margin-top:0;'>{TARGET_SEASON} · First-world only · Paid companies + universities · "
		f"Tailored for {CANDIDATE_NAME} ({CANDIDATE_FOCUS})</p>",
		f"<p><small>{date_str} IST · Broad horizon (not a fixed LinkedIn list). "
		f"This is <strong>not</strong> your India Internship Scout digest.</small></p>",
		"<hr style='border:none;border-top:2px solid #0b3d5c;'>",
	]

	if not programs and not listings:
		parts.append("<p><strong>No priority programmes need a nudge today.</strong></p>")
		parts.append(
			"<p>Radar tracks <strong>paid</strong> first-world SWE/company + university targets "
			"(Big Tech, fintech, quant/systems, Mitacs/CERN/ETH/A*STAR, EU hubs, SG, …). "
			"Unpaid / civil-society programmes are excluded from the default list.</p>"
		)
	else:
		if programs:
			parts.append(f"<h3 style='color:#0b3d5c;'>Programmes & fellowships ({len(programs)})</h3>")
			parts.append("<ol>")
			for o in programs:
				tags = ", ".join(o.fit_tags) if o.fit_tags else "—"
				parts.append(
					"<li style='margin-bottom:14px;'>"
					f"<a href='{o.url}'><strong>{o.name}</strong></a> — {o.org}<br>"
					f"<small>{o.country} · {o.duration} · Priority P{o.priority} · "
					f"<em>{o.status}</em></small><br>"
					f"<small><strong>Who:</strong> {o.who_can_apply}</small><br>"
					f"<small><strong>Funding:</strong> {o.cost} · {o.stipend}</small><br>"
					f"<small><strong>Window:</strong> {o.typical_deadline_window}</small><br>"
					f"<small><strong>Visa:</strong> {o.visa_note or 'See host docs'}</small><br>"
					f"<small><strong>Fit:</strong> {tags}"
					f"{(' · ' + o.notes) if o.notes else ''}</small>"
					"</li>"
				)
			parts.append("</ol>")

		if listings:
			parts.append(f"<h3 style='color:#0b3d5c;'>Live company listings ({len(listings)})</h3>")
			parts.append("<ul>")
			for L in listings:
				parts.append(
					f"<li><a href='{L.url}'><strong>{L.company}</strong> — {L.title}</a><br>"
					f"<small>{L.location} ({L.country}) · {L.source}</small></li>"
				)
			parts.append("</ul>")

	if draft_snippets:
		parts.append("<h3 style='color:#0b3d5c;'>Ready-to-send application openers</h3>")
		parts.append(
			"<p><small>These drafts use the <em>international</em> voice "
			"(visa + programme framing) — different from domestic referral cold email.</small></p>"
		)
		for subj, body in draft_snippets[:3]:
			safe_body = body.replace("\n", "<br>")
			parts.append(
				f"<div style='background:#f0f6fa;padding:12px;border-radius:8px;margin-bottom:12px;'>"
				f"<strong>Subject:</strong> {subj}<br><br>{safe_body}</div>"
			)

	if suppressed:
		parts.append(
			f"<p><small>{suppressed} item(s) suppressed (already emailed "
			f"the max times for this radar).</small></p>"
		)

	parts.append(
		"<hr style='border:none;border-top:1px solid #ccc;'>"
		f"<p><small>{DIGEST_BRAND} · OECD / first-world destinations only · "
		f"{TARGET_SEASON} · separate from India scout & domestic cold outreach</small></p>"
		"</div>"
	)
	return "\n".join(parts)


def build_text(
	programs: list[Opportunity],
	*,
	listings: list[LiveListing] | None = None,
	suppressed: int = 0,
	draft_snippets: list[tuple[str, str]] | None = None,
) -> str:
	listings = listings or []
	draft_snippets = draft_snippets or []
	lines = [
		f"{DIGEST_BRAND} — {_ist_date()}",
		f"{TARGET_SEASON} · first-world only · for {CANDIDATE_NAME}",
		"(This is NOT the India Internship Scout digest.)",
		"",
	]
	if programs:
		lines.append("=== PROGRAMMES & FELLOWSHIPS ===")
		lines.append("")
		for o in programs:
			lines.append(f"• {o.name} ({o.org}) — {o.country}")
			lines.append(f"  {o.duration} | P{o.priority} | {o.status}")
			lines.append(f"  Window: {o.typical_deadline_window}")
			lines.append(f"  {o.url}")
			lines.append("")
	if listings:
		lines.append("=== LIVE COMPANY LISTINGS ===")
		lines.append("")
		for L in listings:
			lines.append(f"• {L.company} — {L.title}")
			lines.append(f"  {L.location} | {L.url}")
			lines.append("")
	if draft_snippets:
		lines.append("=== INTERNATIONAL APPLICATION DRAFTS ===")
		lines.append("")
		for subj, body in draft_snippets[:2]:
			lines.append(f"Subject: {subj}")
			lines.append(body)
			lines.append("---")
	if suppressed:
		lines.append(f"({suppressed} suppressed — already emailed max times)")
	lines.append("")
	lines.append(f"— {DIGEST_BRAND}")
	return "\n".join(lines)


def send_radar_digest(
	programs: list[Opportunity],
	*,
	listings: list[LiveListing] | None = None,
	suppressed: int = 0,
	draft_snippets: list[tuple[str, str]] | None = None,
	dry_run: bool = False,
) -> str:
	"""Send (or preview) the international digest. Returns subject used."""
	listings = listings or []
	ist = datetime.now(ZoneInfo("Asia/Kolkata"))
	n = len(programs) + len(listings)
	if n:
		subject = f"{DIGEST_SUBJECT_PREFIX}: {n} Summer 2027 first-world lead{'s' if n != 1 else ''} — {ist.strftime('%d %b')}"
	else:
		subject = f"{DIGEST_SUBJECT_PREFIX}: quiet day — windows still tracked — {ist.strftime('%d %b')}"

	text = build_text(
		programs, listings=listings, suppressed=suppressed, draft_snippets=draft_snippets
	)
	html = build_html(
		programs, listings=listings, suppressed=suppressed, draft_snippets=draft_snippets
	)

	if dry_run:
		return subject

	if not SMTP_APP_PASSWORD:
		raise RuntimeError(
			"SMTP_APP_PASSWORD missing. Set it in internship-scout/.env "
			"(same secrets as India scout)."
		)

	msg = MIMEMultipart("alternative")
	msg["Subject"] = subject
	msg["From"] = SMTP_EMAIL
	msg["To"] = RECIPIENT_EMAIL
	# Explicit header so mail clients can filter international vs India scout
	msg["X-Resume-Optimiser"] = "international-radar-summer-2027"
	msg.attach(MIMEText(text, "plain"))
	msg.attach(MIMEText(html, "html"))

	with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=45) as server:
		server.login(SMTP_EMAIL, SMTP_APP_PASSWORD)
		server.sendmail(SMTP_EMAIL, [RECIPIENT_EMAIL], msg.as_string())
	return subject
