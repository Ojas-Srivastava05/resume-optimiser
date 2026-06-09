#!/usr/bin/env bash
# Daily automatic runner — used by macOS launchd at 8 AM
set -euo pipefail
SCOUT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCOUT_DIR"
mkdir -p logs

export FAST_MODE=1
export COMPANY_BATCH_SIZE=120
export FETCH_WORKERS=16
export MAX_EMAIL_SENDS=2

# Load SMTP + Supabase from .env
if [[ -f .env ]]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi

exec ./venv/bin/python scout.py --fast --no-sync >> logs/scout.log 2>> logs/scout.err.log
