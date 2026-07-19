"""Small thread-pool helper for I/O-bound fetchers."""

import time
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
from typing import Callable, TypeVar

from config import FETCH_WORKERS
from logger import log

T = TypeVar("T")
R = TypeVar("R")

# After the wall-clock budget, wait this long for in-flight work before abandoning
_INFLIGHT_GRACE_SEC = 45.0


def map_parallel(
    items: list[T],
    fn: Callable[[T], R],
    *,
    workers: int | None = None,
    label: str = "",
    deadline_sec: float | None = None,
) -> list[R]:
    """Run fn over items in parallel.

    When deadline_sec is set, only *start* new work while time remains. In-flight
    tasks get a short grace period, then are abandoned so the job can finish.
    """
    if not items:
        return []
    w = workers or FETCH_WORKERS
    if label:
        budget = f", budget={deadline_sec}s" if deadline_sec else ""
        log(f"Parallel {label}: {len(items)} tasks, {w} workers{budget}")

    out: list[R] = []
    deadline = time.monotonic() + deadline_sec if deadline_sec else None
    remaining = iter(items)
    started = 0
    completed = 0
    logged_budget = False
    abandon_at: float | None = None
    abandoned = False

    def under_budget() -> bool:
        return deadline is None or time.monotonic() < deadline

    pool = ThreadPoolExecutor(max_workers=w)
    futures: dict = {}
    try:

        def submit_one() -> bool:
            nonlocal started
            if not under_budget():
                return False
            try:
                item = next(remaining)
            except StopIteration:
                return False
            futures[pool.submit(fn, item)] = item
            started += 1
            return True

        for _ in range(min(w * 2, len(items))):
            if not submit_one():
                break

        while futures:
            now = time.monotonic()
            can_start_more = under_budget()
            if not can_start_more and not logged_budget:
                logged_budget = True
                abandon_at = now + _INFLIGHT_GRACE_SEC
                log(
                    f"Parallel {label}: time budget reached — finishing {len(futures)} in-flight "
                    f"(grace {_INFLIGHT_GRACE_SEC:.0f}s), {len(items) - started} never started "
                    f"({completed} done so far)",
                    level="WARN",
                )

            if abandon_at is not None and now >= abandon_at:
                stuck = len(futures)
                log(
                    f"Parallel {label}: abandoning {stuck} hung in-flight task(s) after grace "
                    f"({completed}/{len(items)} completed)",
                    level="WARN",
                )
                abandoned = True
                for fut in list(futures):
                    fut.cancel()
                futures.clear()
                break

            done, _ = wait(set(futures.keys()), timeout=2.0, return_when=FIRST_COMPLETED)
            for fut in done:
                item = futures.pop(fut, None)
                completed += 1
                try:
                    result = fut.result(timeout=0)
                    if result:
                        if isinstance(result, list):
                            out.extend(result)
                        else:
                            out.append(result)
                except Exception as exc:
                    if label:
                        print(f"[parallel:{label}] skip {item!r}: {exc}")
                if can_start_more:
                    submit_one()
    finally:
        # wait=False after abandon so a stuck HTTP call cannot block the digest
        pool.shutdown(wait=not abandoned, cancel_futures=True)

    return out
