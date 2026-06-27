"""Curated SAP ecosystem employers in India + daily rotation."""

from __future__ import annotations

import csv
import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from sap_job_scout.config import COMPANIES_CSV, DATA, COMPANY_BATCH_SIZE

_ROTATION_PATH = DATA / "sap_company_rotation.json"


def load_companies() -> list[dict]:
    if not COMPANIES_CSV.exists():
        return []
    with COMPANIES_CSV.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def company_names() -> list[str]:
    return [r["Company"].strip() for r in load_companies() if r.get("Company")]


def rotated_names(limit: int | None = None) -> list[str]:
    names = company_names()
    if not names:
        return []
    limit = limit or COMPANY_BATCH_SIZE
    state = {"index": 0}
    if _ROTATION_PATH.exists():
        try:
            state = json.loads(_ROTATION_PATH.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    idx = int(state.get("index", 0)) % len(names)
    batch = []
    for i in range(min(limit, len(names))):
        batch.append(names[(idx + i) % len(names)])
    return batch


def advance_rotation(batch_size: int) -> None:
    names = company_names()
    if not names:
        return
    state = {"index": 0, "updated": datetime.now(ZoneInfo("Asia/Kolkata")).isoformat()}
    if _ROTATION_PATH.exists():
        try:
            state = json.loads(_ROTATION_PATH.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    state["index"] = (int(state.get("index", 0)) + batch_size) % len(names)
    state["updated"] = datetime.now(ZoneInfo("Asia/Kolkata")).isoformat()
    _ROTATION_PATH.parent.mkdir(parents=True, exist_ok=True)
    _ROTATION_PATH.write_text(json.dumps(state, indent=2), encoding="utf-8")
