"""Small thread-pool helper for I/O-bound fetchers."""

import time
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
from typing import Callable, TypeVar

from config import FETCH_WORKERS
from logger import log

T = TypeVar("T")
R = TypeVar("R")


def map_parallel(
    items: list[T],
    fn: Callable[[T], R],
    *,
    workers: int | None = None,
    label: str = "",
    deadline_sec: float | None = None,
) -> list[R]:
    if not items:
        return []
    w = workers or FETCH_WORKERS
    if label:
        budget = f", budget={deadline_sec}s" if deadline_sec else ""
        log(f"Parallel {label}: {len(items)} tasks, {w} workers{budget}")
    out: list[R] = []
    deadline = time.monotonic() + deadline_sec if deadline_sec else None
    with ThreadPoolExecutor(max_workers=w) as pool:
        futures = {pool.submit(fn, item): item for item in items}
        pending = set(futures.keys())
        completed = 0
        while pending:
            if deadline and time.monotonic() >= deadline:
                skipped = len(pending)
                log(
                    f"Parallel {label}: time budget reached after {completed}/{len(items)} "
                    f"({skipped} tasks skipped)",
                    level="WARN",
                )
                for fut in pending:
                    fut.cancel()
                pool.shutdown(wait=False, cancel_futures=True)
                break
            done, pending = wait(pending, timeout=2.0, return_when=FIRST_COMPLETED)
            for fut in done:
                completed += 1
                try:
                    result = fut.result()
                    if result:
                        if isinstance(result, list):
                            out.extend(result)
                        else:
                            out.append(result)
                except Exception as exc:
                    if label:
                        print(f"[parallel:{label}] skip {futures[fut]!r}: {exc}")
    return out
