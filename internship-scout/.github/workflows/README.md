# GitHub Actions (repo root only)

GitHub **only** runs workflows from the repository root:

`.github/workflows/internship-scout.yml`

Do not add runnable workflow YAML here — nested `.github/workflows/` paths are ignored.

## Internship Scout schedule

| Setting | Value |
|---|---|
| Cron | **8:00 AM IST** daily (`30 2 * * *` UTC) |
| Timeout | 20 minutes |
| `CAREERS_MAX_SCRAPES` | **100** (not 964 — full-list scrape ≈ 64 min, exceeds CI budget) |
| `FETCH_WORKERS` | 16 |
| Manual inputs | `full_scan`, `no_hackathons` |

Measured run time with `CAREERS_MAX_SCRAPES=100`: **~11 minutes** end-to-end on GitHub Actions.
