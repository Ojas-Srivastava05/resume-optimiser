# OA Forge

<div align="center">

**Company-specific Online Assessment practice platform**

[![CI/CD Pipeline](https://github.com/ojas-srivastava05/oa-forge/actions/workflows/ci.yml/badge.svg)](https://github.com/ojas-srivastava05/oa-forge/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

</div>

---

## 🎯 Mission

OA Forge is a **production-ready, authentic OA practice platform** that enforces evidence-based question selection. The core rule is simple:

> **A question can appear in a company pool only if it has documented occurrence records with year, role/season, confidence tier, and source notes.**

Unlike LeetCode clones with fake company tags, OA Forge behaves like a real assessment launcher:
- **Hidden metadata** during OA (title, topic, difficulty, tier, source)
- **Revealed only in debrief** after timer expires
- **Real-time web scraping** for fresh OA leads across 965+ companies
- **Strict company-specific questions only** - no random fallbacks

---

## 🏗️ Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         OA Forge Platform                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │   Frontend   │    │   Backend    │    │   Database   │      │
│  │   Next.js    │◄──►│   API Routes │◄──►│   Supabase   │      │
│  │   React 18   │    │   /api/*     │    │  PostgreSQL  │      │
│  └──────────────┘    └──────────────┘    └──────────────┘      │
│         │                   │                   │               │
│         │                   │                   │               │
│         ▼                   ▼                   ▼               │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │  CodeMirror  │    │   Judge API  │    │   Companies  │      │
│  │   Editor     │    │   C++/JS     │    │   Questions  │      │
│  │  (C++ first) │    │  Piston/g++  │    │ Occurrences  │      │
│  └──────────────┘    └──────────────┘    │   Sessions   │      │
│                                            │   Test Cases│      │
│                                            └──────────────┘      │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              Real-time Web Scraping Engine                 │   │
│  │  DuckDuckGo Search → Lead Extraction → Confidence Scoring│   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### Data Flow

```
User Selects Company
        │
        ▼
┌───────────────────┐
│ Check Availability│
│ - Has occurrences?│
│ - Enough questions?│
└───────────────────┘
        │
        ├─► No → Lock company
        │         Show error
        │
        ▼ Yes
┌───────────────────┐
│ Real-time Scrape  │◄── DuckDuckGo API
│ (OA Lead Search)  │
└───────────────────┘
        │
        ▼
┌───────────────────┐
│ Question Selection│
│ - Curated (A/B/C) │
│ - Company-specific│
└───────────────────┘
        │
        ▼
┌───────────────────┐
│ Mock OA Session   │
│ - Timer Active    │
│ - Hidden Metadata │
└───────────────────┘
        │
        ▼
┌───────────────────┐
│ Code Submission   │
│ - C++ (Piston/g++)│
│ - JS (Legacy)     │
└───────────────────┘
        │
        ▼
┌───────────────────┐
│ Judge Execution   │
│ - Test Cases      │
│ - Verdict         │
└───────────────────┘
        │
        ▼
┌───────────────────┐
│ Debrief           │
│ - Reveal Title    │
│ - Show Tier       │
│ - Source Notes    │
└───────────────────┘
```

---

## 🚀 Features

### Core Functionality
- **965+ Company Support**: Full integration with internship-scout company database
- **Real-time Web Scraping**: Automatic OA lead discovery via DuckDuckGo
- **Strict Company-Specific Questions**: Only questions with documented occurrences
- **Timed Mock Sessions**: Realistic OA simulation with countdown timer
- **Hidden Metadata**: Question identity concealed during active session
- **C++-First Editor**: Professional code editor with C++/JavaScript support
- **Hybrid Judge System**: Piston API + local g++ fallback
- **Evidence Tiers**: A (verified), B (corroborated), C (training-similar)

### Authenticity Guarantees
- **No Fake Claims**: Questions without evidence are completely excluded
- **No Random Fallbacks**: Companies without curated questions are locked, not given random questions
- **Source Tracking**: Every occurrence has source notes and URLs
- **Confidence Scoring**: Automatic confidence hints for scraped leads
- **Tier Promotion**: Manual curation workflow from C → B → A

### Developer Experience
- **CSV Pipeline**: Easy data import/export for curation
- **Admin Interface**: Web-based occurrence ingestion
- **API-First Design**: Clean separation of concerns
- **TypeScript**: Full type safety across codebase
- **Modern UI**: Professional dark theme with emerald accents

---

## 📦 Technology Stack

### Frontend
- **Framework**: Next.js 13.2.4 (React 18.2.0)
- **Language**: TypeScript 5.0.2
- **Styling**: TailwindCSS 3.2.7
- **Editor**: CodeMirror (@uiw/react-codemirror)
- **State**: Recoil 0.7.7
- **UI Components**: Custom components with Tailwind

### Backend
- **Runtime**: Node.js 18
- **API**: Next.js API Routes
- **Database**: Supabase (PostgreSQL)
- **Auth**: Supabase Auth (ready for implementation)
- **Judge**: Piston API + local g++

### Infrastructure
- **Deployment**: Vercel
- **CI/CD**: GitHub Actions
- **Version Control**: Git
- **Package Manager**: npm

---

## 🛠️ Setup & Installation

### Prerequisites
- Node.js 18+
- npm or yarn
- Supabase account (free tier works)
- (Optional) g++ compiler for local C++ judge

### Environment Variables

Create `.env.local`:

```bash
# Supabase Configuration
NEXT_PUBLIC_SUPABASE_URL=your_supabase_project_url
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key

# Judge Configuration
PISTON_API_URL=https://emkc.org/api/v2/piston/execute
JUDGE_MODE=local  # or 'remote' for Piston-only

# Optional: For internship-scout integration
INTERNSHIP_SCOUT_PATH=../internship-scout
```

### Installation

```bash
# Clone the repository
cd OA-Forge

# Install dependencies
npm install

# Seed the database (requires Supabase service role key)
npm run seed:bank

# Start development server
npm run dev
```

Open `http://localhost:3000`

---

## 📊 Data Pipeline

### CSV Structure

#### `data/companies.csv`
```csv
slug,name,default_duration_minutes,default_num_questions,target_role
amazon,Amazon,70,2,SDE Intern
google,Google,60,2,SWE Intern
```

#### `data/questions.csv`
```csv
slug,title,difficulty,category,question_order
two-sum,Two Sum,Easy,arrays-hashmap,1
reverse-linked-list,Reverse Linked List,Easy,linked-list,2
```

#### `data/occurrences.csv`
```csv
company_slug,question_slug,year,season,round_type,confidence_tier,source_notes,source_url
amazon,two-sum,2026,SDE Intern,oa,C,Training-similar starter row,https://example.com
```

#### `data/test-cases.csv`
```csv
question_slug,input_text,expected_output,is_sample,test_order
two-sum,"[2,7,11,15]\n9","[0,1]",true,1
two-sum,"[3,2,4]\n6","[1,2]",false,2
```

### Database Seeding

```bash
# Import all CSV data into Supabase
npm run seed:bank
```

This script:
1. Parses CSV files
2. Upserts companies, questions, roles, templates
3. Imports occurrences with tier metadata
4. Adds hidden test cases for judge execution

---

## 🔍 Real-time Web Scraping

### Automatic Lead Discovery

OA Forge automatically scrapes public sources when you select a company:

```bash
# Manual trigger for all companies
npm run refresh:oa-leads

# Scoped runs
npm run refresh:oa-leads -- --company=amazon
npm run refresh:oa-leads -- --max=50
npm run refresh:oa-leads -- --year=2026
```

### Search Queries

The system uses multiple query patterns:
- `{company} online assessment coding questions {year} intern`
- `{company} OA questions {year} SDE intern`
- `{company} interview experience online assessment coding {year}`

### Confidence Scoring

Leads are automatically scored:
- **review-fast**: Recent year + OA keywords
- **review**: Interview experience + coding questions
- **weak**: Generic or irrelevant content

### Source Classification

- **official**: Company careers pages
- **lc_discuss**: LeetCode Discuss
- **gfg**: GeeksforGeeks
- **reddit**: Reddit/Blind
- **github**: GitHub repositories
- **glassdoor**: Glassdoor
- **web**: Other sources

---

## ⚖️ Authenticity Tiers

### Tier A: Personally Verified
- You personally saw this question in the company's OA
- Highest confidence
- Requires your own source notes

### Tier B: Corroborated
- Multiple independent reports from trusted sources
- High confidence
- Requires source URLs and corroboration notes

### Tier C: Training-Similar
- Same pattern as known OA questions
- Clearly labeled as not exact
- Used for training mode only

### Promotion Workflow

```
Tier C (Training Pattern)
    │
    ├─► Add source notes/URLs
    │
    ▼
Tier B (Corroborated)
    │
    ├─► Multiple independent reports
    │
    ▼
Tier A (Personally Verified)
```

---

## 🧪 Judge System

### C++ Execution

**Remote Judge (Piston)**:
```bash
# Default mode
PISTON_API_URL=https://emkc.org/api/v2/piston/execute
```

**Local Judge (g++)**:
```bash
# Force local execution
JUDGE_MODE=local
```

### JavaScript Execution

Legacy handler support for backward compatibility.

### Test Case Format

```cpp
// Sample test (visible to user)
Input: [2,7,11,15]\n9
Output: [0,1]

// Hidden test (revealed only after submission)
Input: [3,2,4]\n6
Output: [1,2]
```

---

## 🎨 UI/UX Design

### Design System

**Colors**:
- Background: `#09090b` (Zinc 950)
- Surface: `#111113` (Zinc 900)
- Accent: `#34d399` (Emerald 400)
- Border: `rgba(255,255,255,0.08)`

**Typography**:
- Sans: Inter, system-ui
- Mono: JetBrains Mono, ui-monospace

**Components**:
- Panels: Rounded cards with subtle borders
- Buttons: Primary (emerald), Ghost (bordered)
- Chips: Small badges for metadata
- Tables: Clean data presentation

### User Flow

1. **Company Selection**: Choose from 965+ companies
2. **Pool Selection**: Training (A/B/C) vs Strict (A/B)
3. **Real-time Scrape**: Automatic OA lead discovery
4. **Mock OA Start**: Timed session with hidden metadata
5. **Code Submission**: C++ editor with judge execution
6. **Debrief**: Reveal title, tier, source notes

---

## 🚢 Deployment

### Vercel Deployment

**Quick Deploy**:
```bash
# Install Vercel CLI
npm i -g vercel

# Login
vercel login

# Deploy
vercel --prod
```

**Environment Variables on Vercel**:
- `NEXT_PUBLIC_SUPABASE_URL` - Your Supabase project URL
- `SUPABASE_SERVICE_ROLE_KEY` - Your Supabase service role key
- `PISTON_API_URL` - Piston API endpoint (optional)
- `JUDGE_MODE` - Judge mode: "local" or "remote" (optional)

### GitHub Actions CI/CD

**Automatic Pipeline**:
- Lint check on every push/PR
- Build verification
- Daily question scraping (8 AM UTC)
- Manual trigger available
- Auto-deploy to Vercel on main branch

**Setup**:
1. Add repository secrets:
   - `NEXT_PUBLIC_SUPABASE_URL`
   - `SUPABASE_SERVICE_ROLE_KEY`
   - `VERCEL_TOKEN`
   - `VERCEL_ORG_ID`
   - `VERCEL_PROJECT_ID`

2. Push to main branch to trigger deployment

### Background Scraping

**On Website Load**:
- Automatically scrapes top 10 companies on initial load
- Staggered by 2 seconds to avoid rate limiting
- Runs in background without blocking UI

**Manual Scraping**:
```bash
# Scrape all companies (20 questions each)
npm run scrape:questions

# Scrape specific company
npm run scrape:questions -- --company=google

# Customize number of questions
npm run scrape:questions -- --max=50
```

**Via API**:
```bash
curl -X POST https://your-domain.vercel.app/api/scrape-questions \
  -H "Content-Type: application/json" \
  -d '{"companySlug":"google","maxQuestions":20}'
```

---

## 📈 API Endpoints

### Public APIs

#### `GET /api/companies/stats`
Returns company readiness metrics for all companies.

**Response**:
```json
{
  "companies": [
    {
      "slug": "amazon",
      "name": "Amazon",
      "total_questions": 15,
      "strict_questions": 8,
      "tier_a": 3,
      "tier_b": 5,
      "tier_c": 7,
      "duration_minutes": 70,
      "num_questions": 2,
      "mock_ready": true,
      "strict_ready": true
    }
  ]
}
```

#### `GET /api/realtime-oa?companySlug={slug}`
Triggers real-time web scraping for OA leads.

**Response**:
```json
{
  "company": { "slug": "amazon", "name": "Amazon" },
  "leads": [
    {
      "title": "Amazon OA 2026 SDE Intern",
      "url": "https://leetcode.com/discuss/...",
      "snippet": "Shared my Amazon OA experience...",
      "source_type": "lc_discuss",
      "confidence_hint": "review-fast"
    }
  ],
  "mode": "curated-plus-live"
}
```

#### `POST /api/mock-oa/start`
Starts a new mock OA session.

**Request**:
```json
{
  "companySlug": "amazon",
  "strictMode": false
}
```

**Response**:
```json
{
  "sessionId": "uuid-here",
  "company": "Amazon",
  "durationMinutes": 70,
  "questions": [
    {
      "order": 1,
      "slug": "two-sum",
      "title": null,
      "difficulty": null,
      "confidenceTier": null
    }
  ]
}
```

#### `POST /api/judge`
Executes code against test cases.

**Request**:
```json
{
  "slug": "two-sum",
  "code": "vector<int> twoSum(vector<int>& nums, int target) { ... }",
  "language": "cpp"
}
```

**Response**:
```json
{
  "passed": true,
  "verdict": "Accepted",
  "testsRun": 5,
  "message": "AC"
}
```

#### `POST /api/scrape-questions`
Scrapes OA questions from public sources.

**Request**:
```json
{
  "companySlug": "google",
  "maxQuestions": 20
}
```

**Response**:
```json
{
  "success": true,
  "questionsScraped": 18,
  "output": "Scraping progress..."
}
```

---

## 🔧 Configuration

### Tailwind Config

Custom design system in `tailwind.config.js`:
- Extended color palette (forge, tier)
- Custom fonts (Inter, JetBrains Mono)
- Box shadows (glow, card)
- Animations (pulse-slow)

### Next.js Config

Standard Next.js configuration in `next.config.js`.

### Supabase Schema

See `supabase/migrations/` for complete database schema:
- Companies, Roles, OA Templates
- Questions, Test Cases
- Question Company Occurrences
- OA Sessions, Session Questions
- Submissions

---

## 📝 Admin Interface

### Occurrence Ingestion

Access at `/admin` to:
- Add new company-question occurrences
- Set confidence tier (A/B/C)
- Add source notes and URLs
- Promote questions between tiers

### CSV Management

Direct CSV editing for bulk operations:
- `data/companies.csv` - Company templates
- `data/questions.csv` - Question definitions
- `data/occurrences.csv` - Evidence ledger
- `data/test-cases.csv` - Test cases

---

## 🧭 Development Workflow

### Adding New Questions

1. Add question to `data/questions.csv`
2. Add test cases to `data/test-cases.csv`
3. Add occurrence to `data/occurrences.csv`
4. Run `npm run seed:bank`
5. Test via `/admin` or mock OA

### Curating Evidence

1. Run `npm run refresh:oa-leads -- --company={slug}`
2. Review leads in `data/oa-source-leads.csv`
3. Promote strong leads to `data/occurrences.csv`
4. Set appropriate tier (C → B → A)
5. Re-seed database

### UI Development

1. Component structure in `src/components/`
2. Pages in `src/pages/`
3. Styles in `src/styles/globals.css`
4. Use Tailwind classes for styling
5. Follow design system in `tailwind.config.js`

---

## 🐛 Troubleshooting

### White Screen on Mock OA Start

**Cause**: Missing question in local bank or database
**Solution**: 
- Check `data/questions.csv` has the question
- Run `npm run seed:bank`
- Verify question slug matches

### "No curated questions available" Error

**Cause**: Company has no documented occurrences in `data/occurrences.csv`
**Solution**:
- This is intentional - OA Forge only uses company-specific questions
- Add occurrences to `data/occurrences.csv` with proper source notes
- Run `npm run seed:bank` after adding occurrences
- Select a different company that has curated questions

### Judge Execution Fails

**Cause**: Piston API unavailable or g++ not installed
**Solution**:
- Set `JUDGE_MODE=local`
- Install g++: `brew install gcc` (macOS)
- Check network connectivity

### Real-time Scrape Returns No Leads

**Cause**: Company name not recognized or no authentic user experiences found
**Solution**:
- Verify company slug matches
- The system now filters out generic practice guides and SEO content
- This is intentional - only authentic user experiences are shown
- Use the scraped leads to research and add real occurrences to `data/occurrences.csv`

---

## 🗺️ Roadmap

### Phase 1: Core Foundation ✅
- [x] Next.js + Supabase architecture
- [x] CSV data pipeline
- [x] Real-time web scraping
- [x] C++ judge system
- [x] Mock OA flow
- [x] Strict company-specific questions only

### Phase 2: Hardening 🚧
- [ ] Python execution via Piston
- [ ] Full problem statements in Supabase
- [ ] MCQ engine for aptitude rounds
- [ ] Supabase Auth integration
- [ ] Submission history tracking
- [ ] Company readiness analytics

### Phase 3: Scale 📋
- [ ] 100+ curated questions per major company
- [ ] Tier A/B verification workflow
- [ ] Mobile-responsive design
- [ ] Performance optimization
- [ ] Advanced search filters
- [ ] Export/import functionality

---

## 🤝 Contributing

This is a personal project for OA preparation. Contributions welcome in the form of:
- Curated OA occurrences with source notes
- Test cases for existing questions
- UI/UX improvements
- Bug fixes and performance enhancements

---

## 📄 License

MIT License - See LICENSE file for details

---

## 🙏 Acknowledgments

- **Next.js** - React framework
- **Supabase** - Backend as a service
- **TailwindCSS** - Utility-first CSS
- **CodeMirror** - Code editor
- **Piston** - Code execution API
- **DuckDuckGo** - Web search API

---

## 📞 Support

For issues or questions:
- Open a GitHub issue
- Check existing documentation
- Review troubleshooting section

---

<div align="center">

**Built for authentic OA preparation**

*No fake questions. No gimmicks. Real evidence only.*

</div>
