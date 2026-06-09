"""Optional Adzuna India internship search (requires API keys)."""

import requests

from config import ADZUNA_APP_ID, ADZUNA_APP_KEY
from companies import match_priority_company
from filters import Job, make_job

API = "https://api.adzuna.com/v1/api/jobs/in/search/{page}"


def fetch_adzuna_jobs() -> list[Job]:
    if not ADZUNA_APP_ID or not ADZUNA_APP_KEY:
        return []

    jobs: list[Job] = []
    params = {
        "app_id": ADZUNA_APP_ID,
        "app_key": ADZUNA_APP_KEY,
        "results_per_page": 50,
        "what": "software intern",
        "where": "india",
    }

    for page in range(1, 3):
        try:
            resp = requests.get(
                API.format(page=page),
                params=params,
                timeout=25,
            )
            if resp.status_code != 200:
                break
            payload = resp.json()
        except requests.RequestException:
            break

        for item in payload.get("results", []):
            title = item.get("title", "")
            company = (item.get("company") or {}).get("display_name", "")
            loc = item.get("location", {}).get("display_name", "India")
            url = item.get("redirect_url", "")
            if not match_priority_company(company):
                continue
            job = make_job(title, company, loc, url, "Adzuna", india_platform=True)
            if job:
                jobs.append(job)

    return jobs
