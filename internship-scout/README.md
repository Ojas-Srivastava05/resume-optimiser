# Internship Scout

<div align="center">

**Automated Internship Job Aggregation Platform**

[![CI/CD Pipeline](https://github.com/Ojas-Srivastava05/resume-optimiser/actions/workflows/internship-scout.yml/badge.svg)](https://github.com/Ojas-Srivastava05/resume-optimiser/actions/workflows/internship-scout.yml)

</div>

---

## 🎯 Mission

Internship Scout is an **automated job aggregation system** that delivers daily digests of software/ML/AI internships for batch 2028 across 965+ priority companies. The system scrapes multiple sources, applies intelligent filtering, and delivers curated listings via email.

**Core Promise**: Never miss a relevant internship opportunity from your target companies.

---

## 🏗️ Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                      Internship Scout Platform                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │   Sources    │    │   Filters    │    │   Output     │      │
│  │              │    │              │    │              │      │
│  │ • LinkedIn   │───►│ • Company    │───►│ • Email      │      │
│  │ • Career     │    │ • Role       │    │ • CSV        │      │
│  │   Pages      │    │ • Batch      │    │ • JSON       │      │
│  │ • Greenhouse │    │ • Location   │    │              │      │
│  │ • Lever      │    │ • Keywords   │    │              │      │
│  │ • Ashby      │    │              │    │              │      │
│  │ • Unstop     │    │              │    │              │      │
│  │ • Adzuna     │    │              │    │              │      │
│  └──────────────┘    └──────────────┘    └──────────────┘      │
│         │                   │                   │               │
│         │                   │                   │               │
│         ▼                   ▼                   ▼               │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │  Fetchers    │    │   Storage    │    │  Scheduler   │      │
│  │              │    │              │    │              │      │
│  │ • ATS Parser │    │ • seen_jobs │    │ • launchd    │      │
│  │ • API Client │    │ • companies  │    │ • GitHub     │      │
│  │ • Scraper    │    │ • logs       │    │   Actions    │      │
│  └──────────────┘    └──────────────┘    └──────────────┘      │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### Data Flow

```
8:00 AM Trigger (GitHub Actions / launchd)
        │
        ▼
┌───────────────────┐
│ Sync Companies    │◄── Google Sheets / CSV Cache
│ (965+ companies)  │
└───────────────────┘
        │
        ▼
┌───────────────────┐
│ Fetch Jobs        │
│ - LinkedIn        │
│ - Career Pages    │
│ - ATS APIs        │
│ - Unstop          │
│ - Adzuna          │
└───────────────────┘
        │
        ▼
┌───────────────────┐
│ Apply Filters     │
│ - Company Match   │
│ - Role Keywords   │
│ - Batch 2028      │
│ - Location India  │
│ - Exclude Non-tech│
└───────────────────┘
        │
        ▼
┌───────────────────┐
│ Deduplicate       │
│ - seen_jobs.json  │
│ - URL matching    │
│ - Title similarity│
└───────────────────┘
        │
        ▼
┌───────────────────┐
│ Send Email Digest │
│ - New jobs only   │
│ - Formatted HTML  │
│ - SMTP via Gmail  │
└───────────────────┘
        │
        ▼
┌───────────────────┐
│ Update Storage    │
│ - seen_jobs.json  │
│ - logs/           │
└───────────────────┘
```

---

## 🚀 Features

### Multi-Source Aggregation
- **LinkedIn**: Job search API with keyword filters
- **Career Pages**: Direct scraping of 965+ company career sites
- **ATS Platforms**: Greenhouse, Lever, Ashby API integration
- **Unstop**: Campus recruitment platform
- **Adzuna**: Job board API (optional)

### Intelligent Filtering
- **Company Whitelist**: 965+ priority companies from referral sheets
- **Role Matching**: Software, SDE, ML, AI, Backend, Full-stack
- **Batch Filtering**: 2028 batch only (rejects 2026/2027)
- **Location**: India-based roles (or remote)
- **Keyword Exclusion**: Marketing, content, testing, non-tech roles

### Smart Deduplication
- **URL Matching**: Prevents duplicate job postings
- **Title Similarity**: Catches near-duplicates
- **Seen Jobs Tracking**: `seen_jobs.json` persistence
- **Cross-Source Dedup**: Same job from different sources

### Delivery Options
- **Email Digest**: Daily HTML email via Gmail SMTP
- **CSV Export**: Machine-readable job listings
- **JSON Storage**: Structured data for integrations
- **Logging**: Comprehensive stdout/stderr logs

### Scheduling
- **GitHub Actions**: Cloud-based 8 AM IST execution
- **launchd**: Local macOS scheduling
- **Manual Trigger**: On-demand execution
- **Dry Run Mode**: Testing without email delivery

---

## 📦 Technology Stack

### Core
- **Language**: Python 3.x
- **Package Management**: pip + requirements.txt
- **Environment Variables**: .env configuration

### Libraries
- **Requests**: HTTP client for API calls
- **BeautifulSoup4**: HTML parsing
- **SMTP**: Email delivery via Gmail
- **JSON**: Data persistence
- **CSV**: Data export/import

### Infrastructure
- **GitHub Actions**: Cloud CI/CD
- **launchd**: Local macOS scheduling
- **Gmail SMTP**: Email delivery
- **Google Sheets**: Company list management

---

## 🛠️ Setup & Installation

### Prerequisites
- Python 3.x
- Gmail account with app password
- (Optional) Adzuna API credentials
- (Optional) Google Sheets API access

### Environment Variables

Create `.env`:

```bash
# Email Configuration (Required)
SMTP_EMAIL=your_email@gmail.com
SMTP_APP_PASSWORD=your_16_char_app_password
RECIPIENT_EMAIL=your_email@gmail.com

# Optional: Adzuna API
ADZUNA_APP_ID=your_adzuna_app_id
ADZUNA_APP_KEY=your_adzuna_app_key

# Optional: Google Sheets
GOOGLE_SHEET_ID=your_sheet_id
```

### Installation

```bash
# Navigate to directory
cd "/Users/ojas/Desktop/Resume Optimiser/internship-scout"

# Run installer (macOS)
chmod +x install.sh
./install.sh

# Manual installation (alternative)
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Configuration

Edit `.env` with your credentials:

```bash
# Generate Gmail app password:
# Google Account → Security → 2-Step Verification → App passwords
SMTP_APP_PASSWORD=xxxx xxxx xxxx xxxx
```

---

## 📊 Data Sources

### Company List

**Primary Source**: Google Sheets (referral sheet + curated additions)
**Fallback**: Local CSV cache (`sheet_*.csv`)
**Output**: `data/all_companies.csv` (965+ companies)

**Sync Command**:
```bash
./venv/bin/python sync_companies.py
```

### Job Sources

#### LinkedIn
- Search API with company filters
- Keyword-based role matching
- Location-based filtering

#### Career Pages
- Direct scraping of company career sites
- ATS detection (Greenhouse/Lever/Ashby)
- Rotation system to distribute load

#### ATS Platforms
- **Greenhouse**: `/jobs` API endpoint
- **Lever`: `/jobs` API endpoint  
- **Ashby**: `/jobs` API endpoint
- Unified parser for all ATS types

#### Unstop
- Campus recruitment platform
- India-focused internships
- Batch-specific filtering

#### Adzuna (Optional)
- Job board API
- India region filtering
- Internship keyword search

---

## 🧭 Usage

### Daily Automated Run

#### GitHub Actions (Recommended)

**Setup**:
1. Add repository secrets:
   - `RECIPIENT_EMAIL`
   - `SMTP_EMAIL`
   - `SMTP_APP_PASSWORD`
   - (Optional) `ADZUNA_APP_ID`, `ADZUNA_APP_KEY`

2. Workflow runs daily at 8 AM IST

**Manual Trigger**:
- Go to Actions → Internship Scout Daily → Run workflow

#### Local macOS (Alternative)

**Schedule**: 8:00 AM via launchd

**Manual Trigger**:
```bash
launchctl kickstart -k "gui/$(id -u)/com.ojas.internship-scout"
```

### Manual Execution

```bash
# Activate virtual environment
source venv/bin/activate

# Dry run - fetch only, no email
python scout.py --dry-run

# Full run with email
python scout.py --full

# Full run without email (testing)
python scout.py --full --no-email

# Single source testing
python test_sources.py
```

### Company List Management

```bash
# Sync from Google Sheets
python sync_companies.py

# Expand company list with similar firms
python expand_companies.py

# Update priority companies
python companies.py
```

---

## 📧 Email Delivery

### Email Format

**Subject**: `Internship Scout Daily - {date} - {count} new jobs`

**Content**:
- Company name and logo
- Job title and location
- Application deadline (if available)
- Direct application link
- Role category (SDE/ML/AI)
- Batch verification

### SMTP Configuration

**Gmail Setup**:
1. Enable 2-Step Verification
2. Generate App Password
3. Add to `.env` as `SMTP_APP_PASSWORD`

**Troubleshooting**:
- Check app password is correct (16 chars)
- Verify "Less secure app access" is not needed (use app password instead)
- Check Gmail spam folder

---

## 🔍 Filtering Logic

### Inclusion Criteria

**Company Filter**:
- Must be in `data/all_companies.csv`
- 965+ priority companies from referral sheets
- Curated additions for similar firms

**Role Filter**:
- Keywords: intern, software, SDE, ML, AI, backend, full-stack
- Excludes: marketing, content, testing, market research
- Case-insensitive matching

**Batch Filter**:
- Includes: "2028", "batch of 2028", no batch mentioned
- Excludes: "2026", "2027", "2025", "2024"

**Location Filter**:
- Includes: India, India Remote, Remote (Unstop only)
- Excludes: Specific international locations

### Exclusion Criteria

**Non-Tech Roles**:
- Marketing intern
- Content writer
- Business development
- Sales intern
- Market research
- Data entry (non-technical)

**Wrong Batch**:
- "Batch of 2026"
- "Batch of 2027"
- "Graduate 2025"
- "Experienced"

**Wrong Location**:
- Specific international cities
- On-site only outside India

---

## 📁 File Structure

```
internship-scout/
├── scout.py              # Main orchestration script
├── fetchers/             # Source-specific fetchers
│   ├── linkedin.py      # LinkedIn API client
│   ├── career_pages.py  # Career page scraper
│   ├── ats_resolver.py  # ATS platform parser
│   ├── unstop.py        # Unstop platform
│   └── adzuna.py        # Adzuna API
├── filters.py            # Job filtering logic
├── emailer.py            # Email generation
├── storage.py            # Data persistence
├── sync_companies.py     # Company list sync
├── companies.py          # Company management
├── config.py             # Configuration management
├── logger.py             # Logging setup
├── data/
│   ├── all_companies.csv # Master company list
│   ├── priority_companies.csv # Priority firms
│   └── sheet_*.csv       # Google Sheets cache
├── logs/
│   ├── scout.log         # Standard output
│   └── scout.err.log     # Error logs
├── seen_jobs.json        # Deduplication tracking
├── requirements.txt       # Python dependencies
├── .env                  # Environment variables
├── .env.example          # Environment template
├── install.sh            # macOS installer
├── run_scout.sh          # Quick run script
└── README.md             # This file
```

---

## 🗺️ Workflow Diagrams

### Daily Execution Flow

```
START (8:00 AM)
    │
    ├─► Load Configuration
    │   └─► .env variables
    │   └─► Company list
    │
    ├─► Initialize Storage
    │   ├─► Load seen_jobs.json
    │   └─► Setup logging
    │
    ├─► Fetch Jobs (Parallel)
    │   ├─► LinkedIn Search
    │   ├─► Career Page Rotation
    │   ├─► ATS API Calls
    │   ├─► Unstop Scraping
    │   └─► Adzuna API (optional)
    │
    ├─► Apply Filters
    │   ├─► Company whitelist
    │   ├─► Role keywords
    │   ├─► Batch 2028
    │   ├─► Location India
    │   └─► Exclude non-tech
    │
    ├─► Deduplicate
    │   ├─► URL matching
    │   ├─► Title similarity
    │   └─► seen_jobs check
    │
    ├─► Generate Email
    │   ├─► HTML formatting
    │   ├─► Job categorization
    │   └─► Link validation
    │
    ├─► Send Email
    │   └─► SMTP via Gmail
    │
    ├─► Update Storage
    │   ├─► seen_jobs.json
    │   └─► Log results
    │
    └─► END
```

### Company Sync Flow

```
START sync_companies.py
    │
    ├─► Try Google Sheets API
    │   ├─► Success → Download CSV
    │   └─► Failure → Use cache
    │
    ├─► Parse CSV
    │   ├─► Extract company names
    │   ├─► Remove duplicates
    │   └─► Normalize names
    │
    ├─► Merge with Priority List
    │   ├─► priority_companies.csv
    │   └─► Curated additions
    │
    ├─► Write all_companies.csv
    │   └─► 965+ companies
    │
    └─► Update fetchers
        └─► Reload company list
```

---

## 🐛 Troubleshooting

### No Email Received

**Check**:
1. SMTP app password is correct (16 chars)
2. Gmail inbox and spam folder
3. `logs/scout.err.log` for errors
4. Network connectivity

**Solution**:
- Regenerate Gmail app password
- Check firewall settings
- Verify recipient email

### No Jobs Found

**Check**:
1. Company list is up to date
2. Source APIs are accessible
3. Filters aren't too restrictive
4. `logs/scout.log` for fetch results

**Solution**:
- Run `python sync_companies.py`
- Test individual sources: `python test_sources.py`
- Relax filters temporarily

### Duplicate Jobs in Email

**Check**:
1. `seen_jobs.json` is being updated
2. URL matching is working
3. Title similarity threshold

**Solution**:
- Clear `seen_jobs.json` for fresh start
- Adjust deduplication logic in `filters.py`

### GitHub Actions Fails

**Check**:
1. Repository secrets are set
2. Workflow file is valid YAML
3. Python version compatibility

**Solution**:
- Verify secrets in GitHub settings
- Check Actions logs for specific errors
- Test locally first

---

## 📈 Performance

### Execution Time

- **LinkedIn**: 2-3 minutes
- **Career Pages**: 5-8 minutes (rotation)
- **ATS APIs**: 1-2 minutes
- **Unstop**: 1-2 minutes
- **Adzuna**: 1 minute (optional)
- **Total**: 10-20 minutes

### Resource Usage

- **Memory**: ~100-200 MB
- **Network**: ~50-100 MB data transfer
- **CPU**: Minimal (I/O bound)

### Scaling

- **Companies**: 965+ (tested)
- **Jobs per run**: 50-200 typical
- **Email size**: 50-200 KB
- **Storage**: ~1 MB for `seen_jobs.json`

---

## 🔧 Configuration

### Filter Customization

Edit `filters.py` to adjust:
- Role keywords
- Exclusion patterns
- Location rules
- Batch matching

### Source Priorities

Edit `scout.py` to change:
- Source execution order
- Parallel vs sequential fetching
- Timeout values
- Retry logic

### Email Template

Edit `emailer.py` to customize:
- HTML formatting
- Job categorization
- Company logos
- Color scheme

---

## 🤝 Integration with OA-Forge

Internship Scout provides the company database for OA-Forge:

**Data Flow**:
```
Internship Scout
    │
    ├─► data/all_companies.csv (965+ companies)
    │
    └─► OA-Forge reads this file
        │
        ├─► Company selection dropdown
        ├─► Real-time OA scraping
        └─► Mock OA sessions
```

**Usage**:
- OA-Forge uses `../internship-scout/data/all_companies.csv`
- Automatic company universe synchronization
- Shared company taxonomy and naming

---

## 🗺️ Roadmap

### Phase 1: Core ✅
- [x] Multi-source job aggregation
- [x] Intelligent filtering
- [x] Email delivery
- [x] Deduplication
- [x] GitHub Actions integration

### Phase 2: Enhancement 🚧
- [ ] Machine learning for job ranking
- [ ] Slack/Discord notifications
- [ ] Mobile app integration
- [ ] Historical analytics
- [ ] Application tracking

### Phase 3: Scale 📋
- [ ] Additional job boards
- [ ] Company-specific filters
- [ ] Salary information
- [ ] Interview scheduling
- [ ] Referral automation

---

## 📄 License

MIT License - See parent repository LICENSE file

---

## 🙏 Acknowledgments

- **LinkedIn**: Job search API
- **Greenhouse/Lever/Ashby**: ATS platforms
- **Unstop**: Campus recruitment
- **Adzuna**: Job board API
- **Gmail**: SMTP service

---

## 📞 Support

For issues or questions:
- Check `logs/scout.err.log` for errors
- Review troubleshooting section
- Test with `--dry-run` mode first

---

<div align="center">

**Automating internship discovery so you never miss an opportunity**

*965+ companies • Multiple sources • Daily digest • Zero noise*

</div>
