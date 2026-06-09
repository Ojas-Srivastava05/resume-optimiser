# Internship Scout

Daily digest of **software / ML / AI internships** for **batch 2028** at **547 priority companies** (referral sheet + curated similar firms). Sources: **LinkedIn**, career-page scraping, Greenhouse/Lever/Ashby APIs, Unstop, Adzuna.

## GitHub Actions (recommended — runs at 8 AM IST even when Mac is off)

Repo: **https://github.com/Ojas-Srivastava05/internship-scout** (private)

Add these [repository secrets](https://github.com/Ojas-Srivastava05/internship-scout/settings/secrets/actions):

| Secret | Value |
|--------|-------|
| `RECIPIENT_EMAIL` | `srivastavaojas454@gmail.com` |
| `SMTP_EMAIL` | `srivastavaojas454@gmail.com` |
| `SMTP_APP_PASSWORD` | Your Gmail app password (16 chars) |

Optional: `ADZUNA_APP_ID`, `ADZUNA_APP_KEY`

Manual run: **Actions → Internship Scout Daily → Run workflow**

## Local setup (optional)

1. **Gmail app password** (required for email):
   - Google Account → Security → 2-Step Verification → App passwords
   - Create one for "Mail" and paste it into `.env`

2. **Install & schedule** (macOS):

```bash
cd "/Users/ojas/Desktop/Resume Optimiser/internship-scout"
chmod +x install.sh
./install.sh
```

3. Edit `.env`:

```
SMTP_APP_PASSWORD=your_16_char_app_password
```

4. **Test**:

```bash
./venv/bin/python scout.py --dry-run          # fetch only
./venv/bin/python scout.py --full --no-email    # full list, no email
./venv/bin/python scout.py --full               # send everything once
```

After the first `--full` run, daily emails only include **new** listings (`seen_jobs.json` tracks what you already got).

## Schedule

Runs at **8:00 AM** via `launchd` (`com.ojas.internship-scout`). Uses your Mac's timezone — set System Settings → General → Date & Time to **India** if you want 8 AM IST.

Manual trigger:

```bash
launchctl kickstart -k "gui/$(id -u)/com.ojas.internship-scout"
```

## Optional: Adzuna India API

Sign up at [developer.adzuna.com](https://developer.adzuna.com/) and add to `.env`:

```
ADZUNA_APP_ID=...
ADZUNA_APP_KEY=...
```

## What gets filtered in

- **Company** must be on the referral sheet (all students' lists merged)
- **Role**: intern + software / SDE / ML / AI / backend / full-stack
- **Batch**: rejects "Batch of 2026/2027" etc.; keeps 2028 batch or no batch stated
- **Location**: India (or India remote on Unstop)
- **Excludes**: marketing, content, testing, market research, non-tech roles

## Refresh company list

```bash
./venv/bin/python sync_companies.py   # tries Google Sheet, falls back to sheet_*.csv cache
```

Master company CSV: `data/all_companies.csv` (referral + 132 curated additions).

Full scan takes **10–20 min** (LinkedIn + 547 companies + career-page rotation). Runs overnight via launchd at 8 AM.

## Logs

- `logs/scout.log` — stdout
- `logs/scout.err.log` — errors
