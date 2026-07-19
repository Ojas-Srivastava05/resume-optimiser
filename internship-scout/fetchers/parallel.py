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
    """Run fn over items in parallel.

    When deadline_sec is set, only *start* new work while time remains — covering
    as many items as fit. In-flight tasks are allowed to finish after the budget.
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

    def under_budget() -> bool:
        return deadline is None or time.monotonic() < deadline

    with ThreadPoolExecutor(max_workers=w) as pool:
        futures: dict = {}

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

        # Keep a small ready queue so workers stay saturated
        for _ in range(min(w * 2, len(items))):
            if not submit_one():
                break

        while futures:
            done, _ = wait(set(futures.keys()), timeout=2.0, return_when=FIRST_COMPLETED)
            can_start_more = under_budget()
            if not can_start_more and not logged_budget:
                logged_budget = True
                log(
                    f"Parallel {label}: time budget reached — finishing {len(futures)} in-flight, "
                    f"{len(items) - started} never started ({completed} done so far)",
                    level="WARN",
                )

            for fut in done:
                item = futures.pop(fut, None)
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
                        print(f"[parallel:{label}] skip {item!r}: {exc}")
                if can_start_more:
                    submit_one()

    return out
