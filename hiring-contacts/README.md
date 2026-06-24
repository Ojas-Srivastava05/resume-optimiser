# Hiring Contacts Harvester

Public-source aggregator for **Summer 2027 internship** cold-outreach contacts. Pulls from GitHub repos, blogs, Google referral sheet tabs, and generates tiered contact lists aligned with **Internship Scout** / **OA-Forge** company universes.

## Quick start

```bash
cd hiring-contacts
python3 scripts/refresh_all.py
```

Re-run anytime to refresh (clones/pulls sources, re-scrapes web pages, rebuilds master CSV).

## Outputs

| File | Description |
|------|-------------|
| `data/merged/master_contacts.csv` | Deduplicated master list |
| `data/merged/master_contacts.jsonl` | Same data, JSON lines |
| `data/merged/tier_*.csv` | Splits by confidence / type |
| `data/merged/ingest_report.json` | Counts + source health |
| `sources/github/` | Shallow-cloned public repos |
| `sources/web/` | Cached blog/directory HTML |

## Confidence tiers

| Tier | Meaning | Use for cold email |
|------|---------|-------------------|
| `public_listed` / `verified` | Email on official careers/contact page | Best |
| `scraped_personal` | Named recruiter from blog lists | Verify on LinkedIn first |
| `inferred_pattern` | Guessed from name + company email format (K02D) | Low — verify before send |
| `generic_inferred` | `careers@` / `talent@` on scout company domains | Inbox only, not a person |

## Sources (dynamic)

Configured in `config.py`:

- **GitHub:** careerLauncher, recruiter-emailing-script, List-of-companies, placement-data-2025, new-grad-tech-roles--india, Global-Internship-List, 250CompanyList, 2026-SWE-College-Jobs, Summer2026-Internships, …
- **Web:** Substack HR list, DevBlogger HR directory
- **Google Sheet:** All referral-sheet tabs (email columns if present)
- **Generated:** Generic inboxes from `internship-scout/data/all_companies.csv` domains

Add a repo: append to `GITHUB_REPOS` in `config.py`, re-run `refresh_all.py`.

## GitHub Actions

| Workflow | Schedule | What it does |
|----------|----------|--------------|
| `hiring-contacts-refresh.yml` | Sun 8 AM IST | Full re-clone + rebuild from all public sources |
| `hiring-contacts-discover.yml` | Mon/Wed/Fri/Sat 6:30 AM IST | **Incremental** HQ discovery (~50 companies/run, career portal probe) |
| `cold-outreach.yml` | Tue–Thu 9 AM IST | Sends up to **10** emails/day; **1 per contact & 1 per company per IST day** |

**Anti-spam guards** (in `cold_email/queue.py`):
- Max **10 emails/day** (configurable)
- **Never** email the same address twice in one IST day
- **Max 1 email per company per day** (no double-tapping Flipkart in one run)
- **45s** between SMTP sends
- Follow-ups only after **5 days**, max **1** follow-up per contact

**Contact growth over time:** Discover rotates through your 964 scout companies, probes career portals, merges new hiring emails into `master_contacts.csv`. Companies already with 2+ HQ contacts are skipped; re-probe cooldown is 21 days.

Uses same secrets as Internship Scout: `SMTP_EMAIL`, `SMTP_APP_PASSWORD`.

**Go live manually:** Actions → Cold Outreach → Run workflow → set `dry_run` to **false**.

## Cold outreach MVP

Full strategy: **`STRATEGY.md`**

```bash
pip install -r requirements.txt
python3 cold_outreach.py --dry-run --save-drafts   # preview next batch
python3 cold_outreach.py --limit 10                # send (needs SMTP in internship-scout/.env)
python3 cold_outreach.py --followups --limit 5     # 5-day follow-ups
```

## Reality check

Public internet sources do **not** contain lakhs of verified hiring-manager emails. This pipeline maximizes what's legally/publicly available. For scale beyond ~few thousand verified + generic inboxes, you'll need paid enrichment (Apollo, LinkedIn Sales Navigator, etc.) in a future phase.

## Ethics

- Only use **publicly listed** contacts or official career inboxes.
- Personalize messages; avoid bulk spam.
- Mark `inferred_pattern` and `generic_inferred` rows as unverified before sending.
- Target **Summer 2027** roles — many scraped lists reference 2025/2026 companies but contacts often persist year-over-year.

## Related

- Company universe: `../internship-scout/data/all_companies.csv` (966 companies)
- OA universe: `../OA-Forge/data/companies.csv` (926 companies)
