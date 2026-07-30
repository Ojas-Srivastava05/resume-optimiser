# Internship Scout

<div align="center">

**Daily internship & hackathon digest for batch 2028 — 964 priority companies, zero noise**

[![CI/CD Pipeline](https://github.com/Ojas-Srivastava05/resume-optimiser/actions/workflows/internship-scout.yml/badge.svg)](https://github.com/Ojas-Srivastava05/resume-optimiser/actions/workflows/internship-scout.yml)

*Software · ML · AI · Backend · Full-stack · India*

> **Also see:** [First-World Internship Radar](international/README.md) — separate Summer 2027 OECD/EU/US/CA/SG digests (`🌍 Radar:` subjects), not mixed into this India scout.

[How it works](#how-it-works) · [Career portals](#career-portal-coverage) · [Setup](#setup--installation) · [Configuration](#configuration) · [Performance](#performance)

</div>

---

## Mission

Internship Scout aggregates internships from **15+ sources**, filters for **batch 2028** SWE/ML/AI roles in **India**, deduplicates against prior digests, and emails you only what is new.

**Core promise:** You wake up to a curated list — not a firehose.

---

## How it works

Every run uses a **two-tier coverage model**. High-signal boards are scanned in full every morning; company-specific sources rotate so GitHub Actions finishes inside a **20-minute** budget.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         EVERY DAILY RUN (8 AM IST)                       │
├─────────────────────────────────────────────────────────────────────────┤
│  FULL SCAN — all known boards, every time                                │
│    Greenhouse · Lever · Ashby · Workday · SmartRecruiters · Oracle CX   │
│    LinkedIn broad (23 queries) · Unstop broad · Internshala · Naukri     │
│    Indeed · Adzuna · Hackathons (Unstop + Devfolio + direct MNC pages)   │
├─────────────────────────────────────────────────────────────────────────┤
│  ROTATED — staggered across the company list                             │
│    LinkedIn per-company · Unstop per-company · Naukri per-company      │
│    Career portal HTML scrape — 100 companies/day (see below)             │
└─────────────────────────────────────────────────────────────────────────┘
```

Broad queries catch most new postings same-day. Per-company rotation fills gaps for firms that do not surface in aggregate searches.

---

## Career portal coverage

### Why 100 companies per day?

The master list has **964 companies**. Scraping every career portal in one run was benchmarked on the **production code path** (`_scrape_company_entry` + 16 parallel workers):

| Batch size | Measured wall time | Per portal (avg) | Fits 20 min CI? |
|---:|---:|---:|---|
| 100 | **2m 8s** (local) · **2m 12s** (GitHub Actions) | 1.28 s | Yes |
| 964 | **63m 52s** (local, completed) | 3.97 s | No — GH run cancelled after **37+ min** still scraping |

Linear extrapolation from 100 → 964 **does not hold**. Many portals probe up to four URL candidates when no intern roles match, and generic HTML pages can trigger embedded Workday / Oracle / SmartRecruiters sub-requests (12–25 s timeouts each). The long tail dominates at scale.

**Production setting:** `CAREERS_MAX_SCRAPES=100` → full **964-company cycle in ~10 days**, comfortably inside the GitHub Actions timeout alongside health check and other sources (~**11 min** total per run).

### What gets scraped per company

`portal_resolver.py` classifies each firm's careers URL and routes to the right fetcher:

| Portal type | Handler | Examples |
|---|---|---|
| Greenhouse | API | Stripe, Discord |
| Lever | API | Many startups |
| Ashby | API | Modern ATS adopters |
| Workday | CX jobs API | NVIDIA, enterprise |
| SmartRecruiters | Public API | Zomato, Freshworks |
| Oracle CX | HCM REST API | American Express, Akamai |
| Generic HTML | JSON-LD + link scrape + embedded ATS discovery | Everyone else |

Placeholder `careers.google.com` sheet URLs are skipped or inferred via `DOMAIN_OVERRIDES` and slug heuristics when `CAREERS_INFER_PLACEHOLDERS=1`.

### Rotation mechanics

```text
Day 1 → companies 1–100
Day 2 → companies 101–200
  …
Day 10 → companies 901–964 → cycle restarts
```

Rotation index is deterministic (`rotation.py`) so each company gets a predictable slot in the 10-day window.

### Reproduce the benchmarks

```bash
cd internship-scout && source .venv/bin/activate
python scripts/benchmark_career_portals.py 10 25 50 100    # quick batches
python scripts/benchmark_career_portals.py 964             # full list (~64 min)
```

---

## Architecture

```
                    ┌──────────────────┐
  Google Sheet ────►│ sync_companies   │───► data/all_companies.csv (964 firms)
                    └──────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
  ┌───────────┐        ┌────────────┐        ┌─────────────┐
  │ ATS APIs  │        │ Careers Web│        │ Job boards  │
  │ GH/Lever  │        │ portal_    │        │ LinkedIn    │
  │ Ashby/WD  │        │ resolver   │        │ Unstop/Naukri│
  │ SR/Oracle │        │ + careers  │        │ Indeed/Adzuna│
  └─────┬─────┘        └─────┬──────┘        └──────┬──────┘
        │                    │                      │
        └────────────────────┼──────────────────────┘
                             ▼
                    ┌─────────────────┐
                    │ filters.py      │  batch 2028 · India · SWE/ML/AI
                    │ dedupe_jobs()   │  exclude marketing / wrong batch
                    └────────┬────────┘
                             ▼
                    ┌─────────────────┐
                    │ seen_jobs.json  │  + Supabase cross-runner dedup
                    │ emailer.py      │  HTML digest via Gmail SMTP
                    └─────────────────┘
```

**Orchestrator:** `scout.py` · **Parallel I/O:** `fetchers/parallel.py` (16 workers by default)

---

## Features

### Multi-source aggregation

| Source | Mode | Notes |
|---|---|---|
| Greenhouse | Full scan | All known `gh_slug` boards |
| Lever / Ashby | Full scan | ATS cache + sheet slugs |
| Workday | Full scan | CX public API, India-focused queries |
| SmartRecruiters | Full scan | Per-company public APIs |
| Oracle CX | Full scan | Cached boards + rotated discovery |
| LinkedIn | Broad + rotation | Guest search API |
| **Careers Web** | **100/day rotation** | HTML, JSON-LD, embedded ATS |
| Unstop | Broad + rotation | Campus internships |
| Internshala / Naukri / Indeed | Broad (+ rotation) | India job boards |
| Adzuna | Full scan | Optional API keys |
| Hackathons | Full scan | Unstop + Devfolio + direct pages |

### Intelligent filtering

- **Company whitelist** — 964 firms from referral sheet + curated additions
- **Role keywords** — intern, software, SDE, ML, AI, backend, full-stack
- **Batch 2028** — rejects 2026/2027 cohorts
- **Location** — India or remote-India signals
- **Exclusions** — marketing, content, pure QA, non-tech

### Delivery & dedup

- HTML email digest (new jobs only)
- `seen_jobs.json` + optional **Supabase** for GitHub Actions runners
- Max `MAX_EMAIL_SENDS` notifications per opening, then suppressed

---

## Setup & installation

### Prerequisites

- Python 3.12+
- Gmail account with [app password](https://myaccount.google.com/apppasswords)
- (Optional) Supabase project for shared dedup across CI runners
- (Optional) Adzuna API credentials

### Install

```bash
cd internship-scout
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill SMTP + Supabase
```

### Environment variables

```bash
# Required
RECIPIENT_EMAIL=you@gmail.com
SMTP_EMAIL=you@gmail.com
SMTP_APP_PASSWORD=xxxx xxxx xxxx xxxx

# Recommended for GitHub Actions parity
FAST_MODE=1
FETCH_WORKERS=16
CAREERS_MAX_SCRAPES=100          # 100/day → ~10-day full portal cycle
COMPANY_BATCH_SIZE=120           # LinkedIn / Unstop / Naukri rotation
CAREERS_INFER_PLACEHOLDERS=1     # infer URLs for Google placeholder cells

# Optional
SUPABASE_URL=...
SUPABASE_KEY=...
ADZUNA_APP_ID=...
ADZUNA_APP_KEY=...
ORACLE_PROBE_PER_RUN=10          # discover new Oracle CX boards per run
```

---

## Usage

### GitHub Actions (recommended)

Workflow: [`/.github/workflows/internship-scout.yml`](../.github/workflows/internship-scout.yml)

| Setting | Value |
|---|---|
| Schedule | **8:00 AM IST** daily (`cron: 30 2 * * *` UTC) |
| Timeout | 20 minutes |
| `CAREERS_MAX_SCRAPES` | **100** |
| `FETCH_WORKERS` | 16 |

**Secrets:** `RECIPIENT_EMAIL`, `SMTP_EMAIL`, `SMTP_APP_PASSWORD`, `SUPABASE_URL`, `SUPABASE_KEY`

Manual dispatch: Actions → *Internship Scout Daily* → optional `full_scan`, `no_hackathons`.

> Nested `internship-scout/.github/workflows/` is **not** executed by GitHub — only the repo-root workflow runs.

### Local runs

```bash
source .venv/bin/activate

python scout.py --fast --dry-run     # fetch only, no email
python scout.py --fast               # daily-equivalent run
python scout.py --full               # ignore send-count cap
python test_sources.py               # health check all sources
python sync_companies.py             # refresh from Google Sheet
```

### macOS launchd

```bash
launchctl kickstart -k "gui/$(id -u)/com.ojas.internship-scout"
```

---

## Configuration

| Variable | Default | Purpose |
|---|---:|---|
| `CAREERS_MAX_SCRAPES` | **100** | Career portals scraped per run |
| `COMPANY_BATCH_SIZE` | 120 | LinkedIn / Unstop / Naukri rotation size |
| `FETCH_WORKERS` | 16 | Thread pool for parallel HTTP |
| `FAST_MODE` | off locally | Skip slow setup; on in CI |
| `CAREERS_INFER_PLACEHOLDERS` | 1 | Guess careers URLs when sheet has placeholders |
| `ORACLE_PROBE_PER_RUN` | 40 (10 in CI) | New Oracle CX board discovery budget |
| `MAX_EMAIL_SENDS` | 2 | Emails per job before suppression |

Do **not** set `CAREERS_MAX_SCRAPES=964` on GitHub Actions — measured runtime exceeds the job timeout.

---

## Performance

Measured on production code (June 2026):

| Phase | Duration |
|---|---|
| Health check (`test_sources.py`, 3 career probes) | ~6 min |
| Career portals (100 companies, 16 workers) | **~2 min** |
| ATS APIs + job boards + hackathons | ~3 min |
| **Total GitHub Actions run** | **~11 min** |

Resource profile: ~100–200 MB RAM, I/O-bound, minimal CPU.

---

## File structure

```
internship-scout/
├── scout.py                 # Main orchestrator
├── portal_resolver.py       # ATS detection, URL inference, domain overrides
├── config.py                # Environment-driven settings
├── rotation.py              # Deterministic company rotation
├── filters.py               # Role / batch / location filters
├── emailer.py               # HTML digest
├── sync_companies.py        # Google Sheet → CSV
├── test_sources.py          # Source health check (CI step 1)
├── fetchers/
│   ├── careers.py           # Career portal scraper (rotated batch)
│   ├── greenhouse.py · lever.py · ashby.py
│   ├── workday.py · smartrecruiters.py · oracle_cx.py
│   ├── linkedin.py · unstop.py · naukri.py · indeed.py · internshala.py
│   ├── adzuna.py · hackathons.py
│   └── parallel.py          # Thread-pool helper
├── scripts/
│   ├── benchmark_career_portals.py   # Parallel timing benchmarks
│   └── audit_career_portals.py       # Reachability audit
├── data/
│   ├── all_companies.csv    # 964 companies
│   ├── oracle_boards_cache.json
│   └── ats_cache.json
├── seen_jobs.json           # Local dedup state
├── requirements.txt
└── .env.example
```

---

## Filtering reference

**Included:** intern / software / SDE / ML / AI roles at whitelisted companies, batch 2028 or unspecified, India or remote.

**Excluded:** marketing, content, sales, market research, wrong graduation years (2026/2027), non-tech internships.

Edit `filters.py` to tune keywords and exclusion patterns.

---

## Troubleshooting

| Symptom | Check |
|---|---|
| No email | SMTP app password, spam folder, `logs/scout.err.log` |
| No jobs | `python test_sources.py`, company list freshness, filter strictness |
| GH Actions timeout | Ensure `CAREERS_MAX_SCRAPES=100`, not 964 |
| Duplicate jobs | `seen_jobs.json` / Supabase connectivity |

---

## Integration with OA-Forge

`data/all_companies.csv` is the shared company universe for [OA-Forge](../OA-Forge/) question scraping and mock OA company selection.

---

## SAP Job Scout (separate digest)

Daily SAP UI5 / Fiori / BTP roles for Ananya — **isolated** from internship scout (own filters, state, schedule).

| Item | Value |
|---|---|
| Entry | `python sap_scout.py` |
| Workflow | `sap-job-scout.yml` — 8 AM IST |
| Companies | `data/sap_companies.csv` (50/day rotation) |

```bash
python sap_scout.py --dry-run
python sap_scout.py
```

---

## License

MIT — see parent repository.

---

<div align="center">

**964 companies · 15+ sources · 100 career portals per day · ~11 minute daily run**

*Automating internship discovery so you never miss an opportunity.*

</div>
