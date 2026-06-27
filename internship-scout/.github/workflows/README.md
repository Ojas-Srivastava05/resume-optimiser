# GitHub Actions (repo root only)

GitHub **only** runs workflows from the repository root:

`.github/workflows/internship-scout.yml`

Do not add runnable workflow YAML here — nested `.github/workflows/` paths are ignored.

The live schedule is **8:00 AM IST** daily (`cron: 30 2 * * *` UTC), with optional `workflow_dispatch` inputs (`full_scan`, `no_hackathons`) in that root file.
