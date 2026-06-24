# Cold Outreach Strategy (Summer 2027)

Derived from 2025–2026 internship cold-email research ([InterviewChamp](https://interviewchamp.ai/learn/cold-email-recruiter-cs-new-grad-2026), [FirstSales](https://firstsales.io/blog/cold-emails-for-internships/), [JobHuntrr](https://www.jobhuntrr.com/blog/cold-email-for-internship)).

## What works (and what this MVP does)

| Principle | Implementation |
|-----------|----------------|
| **Quality > volume** | Default **10 emails/day** cap, 45s between sends |
| **Short body** | Templates ~100 words; one binary ask |
| **Specific ask** | Request **Summer 2027 intern portal / OA link / campus recruiter** |
| **Proof in one line** | LogiFlow Top 100 + IFFCO + DSA stats |
| **Tiered contacts** | Named recruiters & public HR first; skip `generic_inferred` unless `--include-generic` |
| **One follow-up** | Auto after **5 days**, max 1 follow-up per contact |
| **Resume attached** | `ojas_srivastava_google_swe_intern_2027.pdf` |
| **Links block** | Portfolio, GitHub, LinkedIn, LeetCode, Codeforces, LogiFlow live + repo |
| **Tue–Thu sends** | GitHub Action schedule (9 AM IST) |

## What does NOT work

- Mass-blasting 100+ generic templates/day (spam filters, &lt;2% reply)
- "I'm passionate about opportunities at [Company]" openers
- Long paragraphs or apologizing for being a student
- Emailing `inferred_pattern` addresses without LinkedIn verification

## Recommended weekly rhythm

1. **Sun** — `refresh_all.py` updates contact DB (GitHub Action)
2. **Tue/Wed/Thu** — 10 cold emails/day (named + public HR tier)
3. **Same day** — LinkedIn connection note to same person (manual, not automated yet)
4. **Day 5+** — follow-up queue picks up non-replies automatically

## Contact priority order

1. `tier_personal_scraped.csv` — named India recruiters (Flipkart, PhonePe, …)
2. `tier_verified_and_public.csv` — official careers/talent inboxes
3. `inferred_pattern` — verify on LinkedIn before enabling at scale
4. `generic_inferred` — only with `--include-generic` (careers@ mailboxes)

## CLI

```bash
cd hiring-contacts
pip install -r requirements.txt

# Preview next 10 emails (no send)
python cold_outreach.py --dry-run --save-drafts

# Live send (local — needs internship-scout/.env SMTP)
python cold_outreach.py --limit 10

# One company test
python cold_outreach.py --company PhonePe --dry-run

# Follow-ups only
python cold_outreach.py --followups --limit 5
```

## Env (reuse Internship Scout)

```
SMTP_EMAIL=
SMTP_APP_PASSWORD=
COLD_EMAIL_DAILY_CAP=10
COLD_EMAIL_RESUME_PATH=/path/to/resume.pdf
```

## Next phases (not built yet)

- Apollo/Hunter enrichment for scout companies missing named contacts
- LinkedIn note generator (companion to email, same day)
- A/B subject lines + reply tracking
- Personalization hooks from company engineering blogs
