"""Shared Unstop date parsing and closed-opportunity detection."""

from __future__ import annotations

import re
from datetime import datetime, timezone


def normalize_unstop_date(date_str: str) -> str:
    """Normalize ISO offsets like +05:30 → +0530 for strptime %z."""
    s = (date_str or "").strip()
    return re.sub(r"([+-]\d{2}):(\d{2})$", r"\1\2", s)


def parse_unstop_date(date_str: str) -> datetime | None:
    if not date_str:
        return None
    normalized = normalize_unstop_date(date_str)
    for fmt in (
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%S.%f%z",
        "%Y-%m-%d %H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
    ):
        try:
            dt = datetime.strptime(normalized, fmt)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except ValueError:
            continue
    return None


def is_expired(date_str: str) -> bool:
    """Return True if the given date string is in the past."""
    dt = parse_unstop_date(date_str)
    if dt is None:
        return False
    return dt < datetime.now(timezone.utc)


def unstop_opportunity_is_stale(item: dict) -> bool:
    """Return True if an Unstop listing is closed or no longer actionable."""
    regn = item.get("regnRequirements") or {}
    if isinstance(regn, dict):
        remaining = regn.get("remainingDaysArray") or {}
        if isinstance(remaining, dict):
            text = (remaining.get("text") or "").strip().lower()
            if text == "ended":
                return True

        regn_end = regn.get("end_regn_dt", "") or ""
        if regn_end and is_expired(regn_end):
            return True

    end_date = item.get("end_date", "") or ""
    if end_date and is_expired(end_date):
        return True

    return False
