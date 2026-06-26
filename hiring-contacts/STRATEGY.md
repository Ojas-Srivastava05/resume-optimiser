# Cold Outreach Strategy (Summer 2027)

Derived from 2025–2026 internship cold-email research ([InterviewChamp](https://interviewchamp.ai/learn/cold-email-recruiter-cs-new-grad-2026), [FirstSales](https://firstsales.io/blog/cold-emails-for-internships/), [JobHuntrr](https://www.jobhuntrr.com/blog/cold-email-for-internship)).

## What works (and what this MVP does)

| Principle | Implementation |
|-----------|----------------|
| **Quality > volume** | Default **3 emails/day**, **1 per run**, ≥1h apart (1 PM / 2 PM / 3 PM IST cron) |
| **Short body** | Bullet layout; direct opener; one clear ask |
| **Specific ask** | 10-min call or campus recruiting / referral pointer |
| **Proof in bullets** | School, LogiFlow, IFFCO, CP stats, stack — not dense paragraphs |
| **Plain text only** | No HTML (better Gmail deliverability for 1:1 cold outreach) |
| **Subject** | `Summer 2027 Intern SWE — {Company}` |
| **Tiered contacts** | Named recruiters & public HR first; skip `generic_inferred` unless `--include-generic` |
| **One follow-up** | Auto after **5 days**, max 1 follow-up per contact |
| **Resume attached** | `ojas_srivastava_resume.pdf` (generic filename, company-agnostic) |
| **Links block** | Portfolio, GitHub, LinkedIn, LeetCode, Codeforces, LogiFlow live + repo |
| **Weekday sends** | GitHub Action schedule (Mon–Fri 1 PM / 2 PM / 3 PM IST, 1 email each) |

## What does NOT work

- Mass-blasting 100+ generic templates/day (spam filters, &lt;2% reply)
- "I'm passionate about opportunities at [Company]" openers
- Long paragraphs or apologizing for being a student
- Emailing `inferred_pattern` addresses without LinkedIn verification

## Recommended weekly rhythm

1. **Sun** — `refresh_all.py` updates contact DB (GitHub Action)
2. **Mon–Fri** — up to 3 cold emails/day (one per hour slot: 1 PM, 2 PM, 3 PM IST)
3. **Same day** — LinkedIn connection note to same person (manual, not automated yet)
4. **Day 5+** — follow-up queue picks up non-replies automatically

## Contact priority order

1. **`discover:career_portal`** — live-scraped career pages + domain fallbacks (freshest)
2. **`manual:verified`** — bounce redirects / manually confirmed inboxes
3. `scraped_personal` — named recruiters **only if not from stale bulk lists**
4. ~~`github:careerLauncher` / Substack / devblogger lists~~ — **blocked** (high bounce rate)
5. `generic_inferred` — only with `--include-generic` (careers@ mailboxes)

Stale contacts (>45 days) from bulk scrapes are skipped automatically. Record bounces:

```bash
python cold_outreach.py --record-bounce tom@cerebras.net --bounce-reason "contact kaitlynn@cerebras.net"
python scripts/import_verified.py --from-blocklist
```

## Bulk internet harvest

```bash
# All ~964 scout companies — career page scrape + MX-validated inboxes
python scripts/bulk_discover.py --delay 0.2
python scripts/bulk_discover.py --resume   # continue if interrupted

# MX-verified named HR from public directories (scout overlap)
python scripts/harvest_web_verified.py

# Local HR email dumps (HREmailData.csv + HREmails.csv) — scout domain match + MX
python scripts/import_hr_csv.py
```

Emails are only added when the domain has **MX records** (can receive mail). Stale `careerLauncher` / raw Substack rows stay blocked.

## CLI

```bash
cd hiring-contacts
pip install -r requirements.txt

# Preview next email (no send)
python cold_outreach.py --dry-run --save-drafts

# Live send (local — needs internship-scout/.env SMTP)
python cold_outreach.py --limit 1

# One company test
python cold_outreach.py --company PhonePe --dry-run

# Follow-ups only
python cold_outreach.py --followups --limit 1
```

## Env (reuse Internship Scout)

```
SMTP_EMAIL=
SMTP_APP_PASSWORD=
COLD_EMAIL_DAILY_CAP=3
COLD_EMAIL_MAX_PER_RUN=1
COLD_EMAIL_MIN_INTERVAL_SEC=3600
COLD_EMAIL_RESUME_PATH=/path/to/resume.pdf
```

## Next phases (not built yet)

- Apollo/Hunter enrichment for scout companies missing named contacts
- LinkedIn note generator (companion to email, same day)
- A/B subject lines + reply tracking
- Personalization hooks from company engineering blogs
