# OA Daily Drill

Daily **2-question OA simulation** email — separate from Internship Scout.

## What it does

- **660 companies** from [snehasishroy/leetcode-companywise-interview-questions](https://github.com/snehasishroy/leetcode-companywise-interview-questions) (+ [rameshgitter/OA-Questions](https://github.com/rameshgitter/OA-Questions))
- **1 company per day**, fair rotation (full cycle before repeats)
- **2 questions** picked by recent LeetCode frequency (`six-months.csv` → `three-months.csv` fallback)
- Curated **campus OA problems** used when available (Google, Wells Fargo, BNY Mellon, etc.)
- Fetches problem statement + sample test cases from LeetCode GraphQL
- Email subject: `OA Drill: {Company} — 2 questions — {date}`

## Run locally

```bash
cd internship-scout
python3 -m venv venv && ./venv/bin/pip install -r requirements.txt
cp .env.example .env   # same SMTP as Internship Scout

./venv/bin/python oa_scout.py --dry-run
./venv/bin/python oa_scout.py --company amazon
./venv/bin/python oa_scout.py
```

## GitHub Actions

Workflow: `.github/workflows/daily-oa.yml` — runs **7:30 AM IST** daily.

Uses same secrets as Internship Scout: `RECIPIENT_EMAIL`, `SMTP_EMAIL`, `SMTP_APP_PASSWORD`.

Optional: `GITHUB_TOKEN` for faster company-list refresh.

## State files

- `data/oa_companies_cache.json` — company list (refreshed weekly)
- `data/oa_daily_state.json` — rotation queue (committed after each run)
