"""Track how many times each opening was emailed (max 2 sends, then suppress)."""

import json
from dataclasses import dataclass
from datetime import datetime, timezone

import requests

from config import MAX_EMAIL_SENDS, SEEN_JOBS_PATH, SUPABASE_KEY, SUPABASE_URL
from logger import log, log_warn, log_warn

_TABLE = "internship_scout_seen"


@dataclass
class SendRecord:
    send_count: int = 0
    first_sent_at: str | None = None
    last_sent_at: str | None = None

    def can_send_again(self, *, max_sends: int = MAX_EMAIL_SENDS) -> bool:
        return self.send_count < max_sends


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _local_load() -> dict[str, SendRecord]:
    if not SEEN_JOBS_PATH.exists():
        return {}
    try:
        data = json.loads(SEEN_JOBS_PATH.read_text())
    except (json.JSONDecodeError, OSError):
        return {}

    out: dict[str, SendRecord] = {}
    # New format
    for key, row in (data.get("records") or {}).items():
        out[key] = SendRecord(
            send_count=int(row.get("send_count", 0)),
            first_sent_at=row.get("first_sent_at"),
            last_sent_at=row.get("last_sent_at"),
        )
    # Legacy: keys list means already sent once → count as 1
    for key in data.get("keys") or []:
        if key not in out:
            out[key] = SendRecord(send_count=1, first_sent_at=data.get("updated_at"))
    return out


def _local_save(records: dict[str, SendRecord], *, max_entries: int = 8000) -> None:
    items = list(records.items())[-max_entries:]
    payload = {
        "updated_at": _now(),
        "records": {
            k: {
                "send_count": v.send_count,
                "first_sent_at": v.first_sent_at,
                "last_sent_at": v.last_sent_at,
            }
            for k, v in items
        },
    }
    SEEN_JOBS_PATH.write_text(json.dumps(payload, indent=2))


def _sb_headers(*, prefer: str = "return=minimal") -> dict:
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": prefer,
    }


def _supabase_load() -> dict[str, SendRecord]:
    if not SUPABASE_URL or not SUPABASE_KEY:
        return {}
    try:
        url = (
            f"{SUPABASE_URL.rstrip('/')}/rest/v1/{_TABLE}"
            "?select=job_key,send_count,first_sent_at,last_sent_at"
        )
        resp = requests.get(url, headers=_sb_headers(), timeout=20)
        resp.raise_for_status()
        out: dict[str, SendRecord] = {}
        for row in resp.json():
            out[row["job_key"]] = SendRecord(
                send_count=int(row.get("send_count") or 1),
                first_sent_at=row.get("first_sent_at"),
                last_sent_at=row.get("last_sent_at"),
            )
        log(f"Supabase: loaded {len(out)} send records")
        return out
    except requests.RequestException as exc:
        log_warn(f"Supabase load failed (local only): {exc}")
        return {}


def _merge_records(*dicts: dict[str, SendRecord]) -> dict[str, SendRecord]:
    merged: dict[str, SendRecord] = {}
    for d in dicts:
        for key, rec in d.items():
            if key not in merged or rec.send_count > merged[key].send_count:
                merged[key] = rec
    return merged


def load_send_records() -> dict[str, SendRecord]:
    local = _local_load()
    remote = _supabase_load()
    merged = _merge_records(local, remote)
    log(f"Send history: {len(merged)} tracked openings")
    return merged


def should_email(job_key: str, records: dict[str, SendRecord], *, full: bool = False) -> bool:
    if full:
        return True
    rec = records.get(job_key)
    if rec is None:
        return True
    return rec.can_send_again()


def record_sends(job_keys: list[str]) -> None:
    if not job_keys:
        return
    records = _merge_records(_local_load(), _supabase_load())
    now = _now()
    for key in job_keys:
        rec = records.get(key) or SendRecord()
        if rec.send_count == 0:
            rec.first_sent_at = now
        rec.send_count += 1
        rec.last_sent_at = now
        records[key] = rec

    _local_save(records)
    _supabase_upsert(records, job_keys)
    log(f"Recorded {len(job_keys)} sends (max {MAX_EMAIL_SENDS} per opening)")


def _supabase_upsert(records: dict[str, SendRecord], keys: list[str]) -> None:
    if not SUPABASE_URL or not SUPABASE_KEY:
        return
    rows = []
    for key in keys:
        rec = records[key]
        rows.append(
            {
                "job_key": key,
                "send_count": rec.send_count,
                "first_sent_at": rec.first_sent_at,
                "last_sent_at": rec.last_sent_at,
            }
        )
    try:
        url = f"{SUPABASE_URL.rstrip('/')}/rest/v1/{_TABLE}"
        resp = requests.post(
            url,
            headers=_sb_headers(prefer="resolution=merge-duplicates"),
            json=rows,
            timeout=25,
        )
        resp.raise_for_status()
        log(f"Supabase: upserted {len(rows)} send records")
    except requests.RequestException as exc:
        log_warn(f"Supabase upsert failed: {exc}")


# Backward-compatible aliases
def load_seen() -> set[str]:
    return {k for k, v in load_send_records().items() if not v.can_send_again()}


def save_seen(keys: set[str], **_) -> None:
    record_sends(list(keys))
