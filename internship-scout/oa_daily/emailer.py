"""Send daily OA drill email (separate from Internship Scout digest)."""

import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from zoneinfo import ZoneInfo

from config import RECIPIENT_EMAIL, SMTP_APP_PASSWORD, SMTP_EMAIL
from oa_daily.models import OADayPlan, OAQuestion


def _escape(s: str) -> str:
	return (
		s.replace("&", "&amp;")
		.replace("<", "&lt;")
		.replace(">", "&gt;")
	)


def _render_question_html(q: OAQuestion, index: int) -> str:
	tests_html = ""
	for i, tc in enumerate(q.test_cases[:2], 1):
		tests_html += (
			f"<p><strong>Test case {i}</strong></p>"
			f"<pre style='background:#111;color:#eee;padding:10px;border-radius:6px;white-space:pre-wrap;'>"
			f"Input:\n{_escape(tc.input_text)}\n\nOutput:\n{_escape(tc.output_text)}"
			f"</pre>"
		)
	if not tests_html:
		tests_html = "<p><em>No sample cases in source — use statement.</em></p>"

	link = f"<p><a href='{_escape(q.source_url)}'>Source</a> · {q.source}</p>" if q.source_url else ""

	return (
		f"<div style='margin:18px 0;padding:14px;border:1px solid #333;border-radius:8px;'>"
		f"<h3>Q{index}: {_escape(q.title)} <span style='color:#888;'>({q.difficulty})</span></h3>"
		f"<pre style='white-space:pre-wrap;font-family:monospace;font-size:13px;'>{_escape(q.statement[:2500])}</pre>"
		f"{tests_html}{link}</div>"
	)


def build_html(plan: OADayPlan) -> str:
	ist = datetime.now(ZoneInfo("Asia/Kolkata"))
	qs = "".join(_render_question_html(q, i) for i, q in enumerate(plan.questions, 1))
	return f"""
<html><body style="font-family:Inter,Arial,sans-serif;background:#0b0b0f;color:#eee;padding:16px;">
<h2 style="color:#00e5ff;">OA Drill — {ist.strftime('%d %b %Y')}</h2>
<p><strong>Company:</strong> {_escape(plan.company_name)}</p>
<p><strong>Simulation:</strong> 2-question OA set (weighted-random from top-10 company frequency pool)</p>
<p style="color:#888;font-size:12px;">Rotation {plan.queue_position + 1}/{plan.queue_total} · visit #{plan.visit_number}</p>
<hr style="border-color:#333;"/>
{qs}
<hr style="border-color:#333;"/>
<p style="font-size:12px;color:#888;">Sources: snehasishroy/leetcode-companywise-interview-questions · rameshgitter/OA-Questions · LeetCode</p>
</body></html>
"""


def build_text(plan: OADayPlan) -> str:
	lines = [
		f"OA Drill — {plan.company_name}",
		f"Visit #{plan.visit_number} · rotation {plan.queue_position + 1}/{plan.queue_total}",
		"",
	]
	for i, q in enumerate(plan.questions, 1):
		lines += [f"Q{i}: {q.title} ({q.difficulty})", q.statement[:1500], ""]
		for j, tc in enumerate(q.test_cases[:2], 1):
			lines += [f"Test {j} Input: {tc.input_text}", f"Test {j} Output: {tc.output_text}", ""]
		if q.source_url:
			lines.append(q.source_url)
		lines.append("")
	return "\n".join(lines)


def send_oa_email(plan: OADayPlan) -> None:
	if not SMTP_APP_PASSWORD:
		raise RuntimeError("SMTP_APP_PASSWORD missing in .env")

	ist = datetime.now(ZoneInfo("Asia/Kolkata"))
	subject = f"OA Drill: {plan.company_name} — 2 questions — {ist.strftime('%d %b')}"

	msg = MIMEMultipart("alternative")
	msg["Subject"] = subject
	msg["From"] = SMTP_EMAIL
	msg["To"] = RECIPIENT_EMAIL
	msg.attach(MIMEText(build_text(plan), "plain"))
	msg.attach(MIMEText(build_html(plan), "html"))

	with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=30) as server:
		server.login(SMTP_EMAIL, SMTP_APP_PASSWORD)
		server.sendmail(SMTP_EMAIL, [RECIPIENT_EMAIL], msg.as_string())
