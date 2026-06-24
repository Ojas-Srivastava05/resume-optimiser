# Hiring Contact Sources Catalog

> Target: **Summer 2027** software internships  
> Last ingest: see `data/merged/ingest_report.json`

## In-repo harvested (`hiring-contacts/`)

| Source | Location | Type | Contacts |
|--------|----------|------|----------|
| careerLauncher | `sources/github/careerLauncher/` | Public careers emails (markdown table) | ~80 global tech |
| recruiter-emailing-script | `sources/github/recruiter-emailing-script/` | Recruiter names + email format patterns | 379 names → 332 inferred emails |
| List-of-companies | `sources/github/List-of-companies/` | India placement list + occasional mailto | Sparse emails |
| placement-data-2025 | `sources/github/placement-data-2025/data/*.csv` | Company/role/stipend (no emails) | Company names for crosswalk |
| new-grad-tech-roles--india | `sources/github/new-grad-tech-roles--india/` | Internship leads (markdown) | Regex email pass |
| Global-Internship-List (×2) | `sources/github/Global-Internship-List*` | India internship directory | Career URLs |
| 250CompanyList | `sources/github/250CompanyList/` | 250+ India tech employers | Company names |
| 2026-SWE-College-Jobs | `sources/github/2026-SWE-College-Jobs/` | Intl SWE intern markdown | Apply links |
| Summer2026-Internships | `sources/github/Summer2026-Internships/` | Pitt CSC / Simplify intern list | Apply links |
| Substack HR 50+ | `sources/web/substack_atoz_50_hr.html` | Named India startup recruiters | ~71 emails |
| DevBlogger HR 500 | `sources/web/devblogger_hr_500.html` | Legacy India HR inboxes | ~194 emails |
| Scout company domains | `internship-scout/data/all_companies.csv` | Generated `careers@` / `talent@` / … | ~4558 generic inboxes |
| Google referral sheet | `sync_companies.py` tabs | **401 when private** — use local scout CSV | — |

## Linked systems (no HR people stored)

| System | File | Has contacts? |
|--------|------|---------------|
| Internship Scout | `internship-scout/data/all_companies.csv` | Career portals only |
| OA-Forge | `OA-Forge/data/companies.csv` | Company slugs only |
| OA leads | `OA-Forge/data/oa-source-leads.csv` | Interview blog URLs |

## External sources to add next (not yet ingested)

- Apollo.io / Hunter.io / RocketReach (paid APIs)
- LinkedIn Sales Navigator exports (manual, ToS-sensitive)
- Company Greenhouse/Lever job postings → hiring team (per-job, not bulk)
- Your private Google referral sheet tabs if they contain referrer emails (export CSV locally → `data/raw/manual/`)

## Refresh

```bash
python3 hiring-contacts/scripts/refresh_all.py
```
