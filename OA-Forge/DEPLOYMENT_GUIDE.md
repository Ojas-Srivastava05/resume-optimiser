# OA-Forge Deployment (Resume Optimiser monorepo)

Deploy **OA-Forge** from the `resume-optimiser` repo. No separate repository needed.

## 1. Vercel setup

1. Import `https://github.com/Ojas-Srivastava05/resume-optimiser`
2. Set **Root Directory** → `OA-Forge`
3. Framework: Next.js (auto-detected)

### Environment variables

| Variable | Required | Notes |
|----------|----------|-------|
| `NEXT_PUBLIC_SUPABASE_URL` | Yes | Supabase project URL |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Yes | Client reads |
| `SUPABASE_SERVICE_ROLE_KEY` | Yes | Server seed + writes |
| `JUDGE_MODE` | No | `local` (default) or `remote` |
| `BRAVE_SEARCH_API_KEY` | No | Optional; DuckDuckGo used by default |

## 2. Database seed (one-time)

```bash
cd OA-Forge
npm install
npm run generate:bank    # rebuild occurrences.csv (965 cos × 20 questions)
npm run seed:bank        # push to Supabase
```

Apply migrations in `supabase/migrations/` via Supabase SQL editor if tables don't exist.

## 3. Local dev

```bash
cd OA-Forge
cp .env.example .env.local   # fill Supabase keys
npm run dev
```

Open http://localhost:3000 → pick any company → **Start Mock OA** → solve in C++.

## 4. Git push

Everything lives in `resume-optimiser`. OA-Forge has **no nested git repo**.

```bash
cd "/Users/ojas/Desktop/Resume Optimiser"
git add OA-Forge internship-scout/data/all_companies.csv
git commit -m "OA-Forge MVP: full question bank, C++ only, deploy config"
git push origin main
```

## 5. What works

- **965 companies** from `internship-scout/data/all_companies.csv`
- **20 runnable questions** per company (LeetCode-classic pool)
- **Mock OA**: picks a random **pair** of questions (or 2 random if no pair)
- **C++ only** judge via local g++ or Piston API
- **Live OA reports** panel (DuckDuckGo search, non-blocking)
- **No sign-in**
