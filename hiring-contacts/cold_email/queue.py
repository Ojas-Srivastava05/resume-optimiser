"""Outreach queue + send-state persistence."""

from __future__ import annotations

import csv
import json
import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from cold_email.config import (
	DEFAULT_TIERS,
	FOLLOWUP_DAYS,
	MASTER_CSV,
	MAX_FOLLOWUPS,
	MAX_PER_COMPANY_PER_DAY,
	SCOUT_CSV,
	STATE_PATH,
)


def _now() -> datetime:
	return datetime.now(timezone.utc)


def _today_ist() -> str:
	return datetime.now(ZoneInfo("Asia/Kolkata")).strftime("%Y-%m-%d")


def norm_company(name: str) -> str:
	return re.sub(r"[^a-z0-9]", "", (name or "").lower())


@dataclass
class ContactTarget:
	email: str
	company: str
	name: str
	role_title: str
	contact_type: str
	confidence: str
	in_scout_list: bool
	source_id: str
	career_portal: str = ""
	is_followup: bool = False
	prior_sent_at: str = ""


def load_scout_portals() -> dict[str, str]:
	out: dict[str, str] = {}
	if not SCOUT_CSV.exists():
		return out
	with SCOUT_CSV.open(encoding="utf-8") as f:
		for row in csv.DictReader(f):
			name = (row.get("Company") or "").strip()
			portal = (row.get("Career Portal") or "").strip()
			if name and portal:
				out[norm_company(name)] = portal
	return out


def load_state() -> dict:
	if STATE_PATH.exists():
		state = json.loads(STATE_PATH.read_text(encoding="utf-8"))
	else:
		state = {"sent": {}, "stats": {"total_sent": 0, "total_followups": 0}}
	state.setdefault("daily_log", {})
	state.setdefault("sent", {})
	state.setdefault("stats", {})
	return state


def save_state(state: dict) -> None:
	# Prune daily_log older than 14 days
	cutoff = (datetime.now(ZoneInfo("Asia/Kolkata")).date() - timedelta(days=14)).isoformat()
	daily = state.get("daily_log", {})
	state["daily_log"] = {k: v for k, v in daily.items() if k >= cutoff}
	STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
	STATE_PATH.write_text(json.dumps(state, indent=2), encoding="utf-8")


def _daily_usage(state: dict) -> tuple[set[str], set[str]]:
	"""Return (emails_sent_today, companies_contacted_today) in IST."""
	today = _today_ist()
	bucket = state.get("daily_log", {}).get(today, {})
	emails = set((bucket.get("emails") or []))
	companies = set((bucket.get("companies") or []))
	return emails, companies


def load_contacts() -> list[dict]:
	if not MASTER_CSV.exists():
		raise FileNotFoundError(f"Missing {MASTER_CSV} — run scripts/refresh_all.py first")
	with MASTER_CSV.open(encoding="utf-8") as f:
		return list(csv.DictReader(f))


def _tier_rank(confidence: str) -> int:
	order = {t: i for i, t in enumerate(DEFAULT_TIERS)}
	return order.get(confidence, 99)


def pick_batch(
	*,
	limit: int,
	include_generic: bool = False,
	followups_only: bool = False,
	company_filter: str = "",
) -> list[ContactTarget]:
	state = load_state()
	portals = load_scout_portals()
	rows = load_contacts()
	allowed = set(DEFAULT_TIERS)
	if include_generic:
		allowed.add("generic_inferred")

	emails_today, companies_today = _daily_usage(state)
	now = _now()
	targets: list[ContactTarget] = []
	companies_in_batch: set[str] = set()

	def company_blocked(company: str) -> bool:
		cn = norm_company(company)
		if not cn:
			return False
		if MAX_PER_COMPANY_PER_DAY and cn in companies_today:
			return True
		if MAX_PER_COMPANY_PER_DAY and cn in companies_in_batch:
			return True
		return False

	def add_followup(meta: dict, email: str) -> None:
		if email.lower() in emails_today:
			return
		if company_blocked(meta.get("company", "")):
			return
		targets.append(
			ContactTarget(
				email=email,
				company=meta.get("company", ""),
				name=meta.get("name", ""),
				role_title=meta.get("role_title", ""),
				contact_type=meta.get("contact_type", ""),
				confidence=meta.get("confidence", ""),
				in_scout_list=bool(meta.get("in_scout_list")),
				source_id=meta.get("source_id", ""),
				career_portal=meta.get("career_portal", ""),
				is_followup=True,
				prior_sent_at=meta.get("sent_at", ""),
			)
		)
		companies_in_batch.add(norm_company(meta.get("company", "")))

	for email, meta in state.get("sent", {}).items():
		if len(targets) >= limit:
			break
		if meta.get("followup_sent") or meta.get("followup_count", 0) >= MAX_FOLLOWUPS:
			continue
		sent_at = meta.get("sent_at")
		if not sent_at:
			continue
		try:
			sent_dt = datetime.fromisoformat(sent_at)
		except ValueError:
			continue
		if now - sent_dt < timedelta(days=FOLLOWUP_DAYS):
			continue
		if company_filter and norm_company(meta.get("company", "")) != norm_company(company_filter):
			continue
		add_followup(meta, email)

	if followups_only:
		return targets[:limit]

	sent_emails = set(state.get("sent", {}).keys())
	candidates: list[dict] = []
	for row in rows:
		conf = row.get("confidence") or ""
		if conf not in allowed:
			continue
		email = (row.get("email") or "").strip().lower()
		if not email or email in sent_emails:
			continue
		if email in emails_today:
			continue
		if company_blocked(row.get("company") or ""):
			continue
		if company_filter and norm_company(row.get("company", "")) != norm_company(company_filter):
			continue
		candidates.append(row)

	candidates.sort(
		key=lambda r: (
			0 if str(r.get("in_scout_list")).lower() == "true" else 1,
			_tier_rank(r.get("confidence") or ""),
			r.get("company") or "",
		)
	)

	for row in candidates:
		if len(targets) >= limit:
			break
		company = row.get("company") or ""
		if company_blocked(company):
			continue
		cn = norm_company(company)
		targets.append(
			ContactTarget(
				email=row["email"].strip().lower(),
				company=company,
				name=row.get("name") or "",
				role_title=row.get("role_title") or "",
				contact_type=row.get("contact_type") or "",
				confidence=row.get("confidence") or "",
				in_scout_list=str(row.get("in_scout_list")).lower() == "true",
				source_id=row.get("source_id") or "",
				career_portal=portals.get(cn, ""),
			)
		)
		companies_in_batch.add(cn)

	return targets[:limit]


def mark_sent(target: ContactTarget, *, subject: str, dry_run: bool) -> None:
	state = load_state()
	key = target.email.lower()
	today = _today_ist()
	daily = state.setdefault("daily_log", {})
	day = daily.setdefault(today, {"emails": [], "companies": []})

	if key not in day["emails"]:
		day["emails"].append(key)
	cn = norm_company(target.company)
	if cn and cn not in day["companies"]:
		day["companies"].append(cn)

	entry = {
		"email": target.email,
		"company": target.company,
		"name": target.name,
		"role_title": target.role_title,
		"contact_type": target.contact_type,
		"confidence": target.confidence,
		"in_scout_list": target.in_scout_list,
		"source_id": target.source_id,
		"career_portal": target.career_portal,
		"subject": subject,
		"dry_run": dry_run,
	}
	if target.is_followup:
		prev = state["sent"].get(key, {})
		prev["followup_sent"] = True
		prev["followup_count"] = prev.get("followup_count", 0) + 1
		prev["followup_at"] = _now().isoformat()
		state["sent"][key] = prev
		state["stats"]["total_followups"] = state["stats"].get("total_followups", 0) + 1
	else:
		entry["sent_at"] = _now().isoformat()
		entry["followup_sent"] = False
		entry["followup_count"] = 0
		state["sent"][key] = entry
		state["stats"]["total_sent"] = state["stats"].get("total_sent", 0) + 1
	save_state(state)
