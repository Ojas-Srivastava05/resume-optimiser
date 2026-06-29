#!/usr/bin/env python3
"""Measure wall-clock time for parallel career portal scraping (production code path)."""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

os.environ.setdefault("FAST_MODE", "1")
os.environ.setdefault("ORACLE_PROBE_PER_RUN", "0")
os.environ.setdefault("FETCH_WORKERS", "16")

from companies import load_companies, match_priority_company
from config import FETCH_WORKERS
from fetchers.careers import _scrape_company_entry
from fetchers.parallel import map_parallel
from rotation import rotated_names


def scrape_batch(size: int) -> tuple[int, int, float]:
    names = rotated_names(size)
    entries = [match_priority_company(n) for n in names]
    entries = [e for e in entries if e]

    t0 = time.perf_counter()
    results = map_parallel(entries, _scrape_company_entry, label=f"bench-{size}", workers=FETCH_WORKERS)
    elapsed = time.perf_counter() - t0

    jobs = 0
    for r in results:
        if isinstance(r, list):
            jobs += len(r)
    return len(entries), jobs, elapsed


def main() -> int:
    companies = load_companies()
    print(f"Parallel career portal benchmark")
    print(f"  companies in list: {len(companies)}")
    print(f"  workers: {FETCH_WORKERS}")
    print(f"  code path: fetchers.careers._scrape_company_entry + map_parallel")
    print()
    print(f"{'batch':>6}  {'wall_sec':>9}  {'sec/portal':>11}  {'jobs':>5}")
    print("-" * 40)

    sizes = []
    for arg in sys.argv[1:]:
        sizes.append(int(arg))
    if not sizes:
        sizes = [10, 25, 50, 100]

    rows: list[tuple[int, float, float, int]] = []
    for size in sizes:
        n, jobs, elapsed = scrape_batch(size)
        per = elapsed / n if n else 0
        rows.append((size, elapsed, per, jobs))
        print(f"{size:>6}  {elapsed:>9.1f}  {per:>11.2f}  {jobs:>5}")
        sys.stdout.flush()

    if len(rows) >= 2:
        # linear fit: time ≈ overhead + k * batch
        import statistics

        ratios = [r[1] / r[0] for r in rows if r[0] > 0]
        med = statistics.median(ratios)
        print()
        print(f"Median wall time per portal (parallel): {med:.2f}s")
        print(f"Estimated 964 portals: {med * 964 / 60:.1f} min (extrapolation from measured runs)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
