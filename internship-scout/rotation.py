"""Rotate through the full company list — cover all 964 over ~12 days."""

from datetime import datetime
from zoneinfo import ZoneInfo

from companies import company_names_for_search
from config import COMPANY_BATCH_SIZE


def rotated_names(batch_size: int | None = None) -> list[str]:
    """Return today's slice of companies to query."""
    names = company_names_for_search()
    if not names:
        return []

    size = batch_size or COMPANY_BATCH_SIZE
    day = datetime.now(ZoneInfo("Asia/Kolkata")).timetuple().tm_yday
    start = (day * size) % len(names)

    batch: list[str] = []
    for i in range(min(size, len(names))):
        batch.append(names[(start + i) % len(names)])
    return batch
