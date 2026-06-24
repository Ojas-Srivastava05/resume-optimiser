"""OA Daily mailer configuration."""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

STATE_PATH = DATA / "oa_daily_state.json"
COMPANIES_CACHE_PATH = DATA / "oa_companies_cache.json"

SNEHASISHROY_REPO = "snehasishroy/leetcode-companywise-interview-questions"
SNEHASISHROY_BRANCH = "master"
RAMESH_REPO = "rameshgitter/OA-Questions"
RAMESH_BRANCH = "main"

# Prefer recent frequency windows for OA simulation
FREQ_CSV_PRIORITY = ("six-months.csv", "three-months.csv", "thirty-days.csv", "all.csv")

QUESTIONS_PER_OA = 2
TOP_POOL_SIZE = 24  # draw pairs from top-N by frequency
