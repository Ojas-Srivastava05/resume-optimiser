"""Structured logs for GitHub Actions and local runs."""

import sys
from datetime import datetime
from zoneinfo import ZoneInfo


def log(msg: str, *, level: str = "INFO") -> None:
    ts = datetime.now(ZoneInfo("Asia/Kolkata")).strftime("%Y-%m-%d %H:%M:%S IST")
    print(f"[{ts}] [{level}] {msg}", flush=True)


def log_section(title: str) -> None:
    log(f"{'─' * 12} {title} {'─' * 12}")


def log_warn(msg: str) -> None:
    log(msg, level="WARN")


def log_error(msg: str) -> None:
    log(msg, level="ERROR")
    print(msg, file=sys.stderr, flush=True)
