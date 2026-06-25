"""Hiring contacts harvester configuration."""

from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parent

SOURCES_GITHUB = ROOT / "sources" / "github"
SOURCES_WEB = ROOT / "sources" / "web"
DATA_RAW = ROOT / "data" / "raw"
DATA_NORMALIZED = ROOT / "data" / "normalized"
DATA_MERGED = ROOT / "data" / "merged"
LOGS = ROOT / "logs"

SCOUT_COMPANIES_CSV = REPO_ROOT / "internship-scout" / "data" / "all_companies.csv"
OA_COMPANIES_CSV = REPO_ROOT / "OA-Forge" / "data" / "companies.csv"

TARGET_INTERNSHIP_YEAR = 2027
TARGET_SEASON = "Summer 2027"

# Referral sheet — all known tab gids from internship-scout/sync_companies.py
PRIORITY_SHEET_ID = "1L-PwvyVyYnMQZfoFU4nKpUFQoiW02SC6_APS_HuWeQo"
SHEET_TAB_GIDS = [1037508969, 1280391286, 1384053570, 1863495069, 429470176, 773987803, 885057618, 285269648]

GITHUB_REPOS = [
	{"url": "https://github.com/byborh/careerLauncher.git", "name": "careerLauncher"},
	{"url": "https://github.com/K02D/recruiter-emailing-script.git", "name": "recruiter-emailing-script"},
	{"url": "https://github.com/abhishek-ssingh/List-of-companies.git", "name": "List-of-companies"},
	{"url": "https://github.com/anxkhn/placement-data-2025.git", "name": "placement-data-2025"},
	{"url": "https://github.com/samiranghosh04/new-grad-tech-roles--india.git", "name": "new-grad-tech-roles--india"},
	{"url": "https://github.com/RohanExploit/Global-Internship-List.git", "name": "Global-Internship-List"},
	{"url": "https://github.com/KushalVijay/250CompanyList.git", "name": "250CompanyList"},
	{"url": "https://github.com/speedyapply/2026-SWE-College-Jobs.git", "name": "2026-SWE-College-Jobs"},
	{"url": "https://github.com/SimplifyJobs/Summer2026-Internships.git", "name": "Summer2026-Internships"},
	{"url": "https://github.com/VikashPR/Global-Internship-List.git", "name": "Global-Internship-List-upstream"},
]

WEB_SOURCES = [
	{
		"id": "substack_atoz_50_hr",
		"url": "https://atozplacementkit.substack.com/p/hr-emails-of-50-companies",
		"label": "Avinash Singh — HR emails 50+ companies",
	},
	{
		"id": "devblogger_hr_500",
		"url": "https://www.devblogger.in/blogs/hr-email-directory-top-500-indian-companies",
		"label": "DevBlogger — HR directory top 500 India",
	},
	{
		"id": "github_raw_career_launcher",
		"url": "https://raw.githubusercontent.com/byborh/careerLauncher/main/README.md",
		"label": "careerLauncher README (live)",
	},
]

# Generic inbox prefixes applied to domains from scout company career URLs
GENERIC_INBOX_PREFIXES = (
	"careers",
	"talent",
	"hr",
	"recruiting",
	"university",
	"campus",
	"interns",
	"internships",
	"jobs",
	"hiring",
)

COMPANY_DOMAIN_OVERRIDES = {
	"google": "google.com",
	"microsoft": "microsoft.com",
	"amazon": "amazon.com",
	"meta": "meta.com",
	"apple": "apple.com",
	"netflix": "netflix.com",
	"flipkart": "flipkart.com",
	"phonepe": "phonepe.com",
	"zepto": "zeptonow.com",
	"paytm": "paytm.com",
	"swiggy": "swiggy.in",
	"zomato": "zomato.com",
	"adobe": "adobe.com",
	"salesforce": "salesforce.com",
	"oracle": "oracle.com",
	"ibm": "ibm.com",
	"intel": "intel.com",
	"nvidia": "nvidia.com",
	"cerebras": "cerebras.ai",
}

EMAIL_FORMATS_BY_COMPANY = {
	"google": "{f}{l}@google.com",
	"databricks": "{f}.{l}@databricks.com",
	"stripe": "{f}@stripe.com",
	"microsoft": "{f}.{l}@microsoft.com",
	"meta": "{f0}{l}@fb.com",
	"amazon": "{l}{f0}@amazon.com",
	"atlassian": "{f0}{l}@atlassian.com",
	"linkedin": "{f0}{l}@linkedin.com",
}
