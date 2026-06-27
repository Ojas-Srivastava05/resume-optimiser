"""Local send-history for SAP scout (does not touch internship_scout_seen)."""

import json
from dataclasses import dataclass
from datetime import datetime, timezone

from sap_job_scout.config import MAX_EMAIL_SENDS, SEEN_PATH


@dataclass
class SendRecord:
    send_count: int = 0
    first_sent_at: str | None = None
    last_sent_at: str | None = None

    def can_send_again(self) -> bool:
        return self.send_count < MAX_EMAIL_SENDS


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_send_records() -> dict[str, SendRecord]:
    if not SEEN_PATH.exists():
        return {}
    try:
        data = json.loads(SEEN_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}
    out: dict[str, SendRecord] = {}
    for key, row in (data.get("records") or {}).items():
        out[key] = SendRecord(
            send_count=int(row.get("send_count", 0)),
            first_sent_at=row.get("first_sent_at"),
            last_sent_at=row.get("last_sent_at"),
        )
    return out


def _save(records: dict[str, SendRecord]) -> None:
    SEEN_PATH.parent.mkdir(parents=True, exist_ok=True)
    SEEN_PATH.write_text(
        json.dumps(
            {
                "updated_at": _now(),
                "records": {
                    k: {
                        "send_count": v.send_count,
                        "first_sent_at": v.first_sent_at,
                        "last_sent_at": v.last_sent_at,
                    }
                    for k, v in list(records.items())[-6000:]
                },
            },
            indent=2,
        ),
        encoding="utf-8",
    )


def should_email(job_key: str, records: dict[str, SendRecord], *, full: bool = False) -> bool:
    if full:
        return True
    rec = records.get(job_key)
    return rec is None or rec.can_send_again()


def record_sends(job_keys: list[str]) -> None:
    if not job_keys:
        return
    records = load_send_records()
    now = _now()
    for key in job_keys:
        rec = records.get(key) or SendRecord()
        if rec.send_count == 0:
            rec.first_sent_at = now
        rec.send_count += 1
        rec.last_sent_at = now
        records[key] = rec
    _save(records)
