# First-World Internship Radar (Summer 2027)

Separate automation from:

| Pipeline | What it emails | Subject style |
|----------|----------------|---------------|
| `internship-scout` | India-heavy intern + hackathon digest | `Scout: …` |
| `hiring-contacts` cold outreach | Domestic/company SWE referral asks | `Summer 2027 SWE intern — {Company}` |
| **This radar** | Paid first-world **companies + universities** | `🌍 Radar: …` |

## Inclusion rules (not a fixed “5 LinkedIn links” list)

1. **First-world / advanced economy** destinations (US, CA, UK, EU/CH, SG, JP, AU, …)
2. **Resume fit** — SWE / systems / backend / ML-eng / paid research coding (Ojas: AI + production APIs + CP)
3. **Pay sufficient** — tags `paid-high` / `paid-solid` / `paid-research` only  
   Unpaid, volunteer, and civil-society exchanges are **out of the default radar**

Add anything that meets those three bars in `catalog.py` (company careers page or university fellowship).

## Examples of what is covered

- **Companies:** Google, Microsoft, Meta, Amazon, Apple, NVIDIA, Stripe, Revolut, Shopify, Databricks, Cloudflare, Bloomberg, DES, Jane Street, HRT, Citadel, Optiver, IMC, Jump, JPM/GS/Barclays tech, Uber, Spotify, ASML, SAP, Booking, …
- **Universities / labs:** CERN, ETH, EPFL, Mitacs, A\*STAR, DAAD RISE, MPI, NUS/NTU, UK paid UROP, US paid RA routes, IAESTE paid placements, Erasmus+ only via SVNIT IR when grant-backed

## Run locally

```bash
cd internship-scout
python international_scout.py --dry-run --write-preview --drafts-only --priority 2
python international_scout.py --send --drafts-only --priority 2
```

## GitHub Action

`.github/workflows/international-internship-radar.yml` — **daily** ~9 AM IST  
Secrets: same `SMTP_EMAIL` / `SMTP_APP_PASSWORD` / `RECIPIENT_EMAIL` as India scout.
