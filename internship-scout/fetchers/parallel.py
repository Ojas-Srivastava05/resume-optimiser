"""Small thread-pool helper for I/O-bound fetchers."""

from concurrent.futures import ThreadPoolExecutor, as_completed
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
) -> list[R]:
    if not items:
        return []
    w = workers or FETCH_WORKERS
    if label:
        log(f"Parallel {label}: {len(items)} tasks, {w} workers")
    out: list[R] = []
    with ThreadPoolExecutor(max_workers=w) as pool:
        futures = {pool.submit(fn, item): item for item in items}
        for fut in as_completed(futures):
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
