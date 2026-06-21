import fs from "fs";
import path from "path";

const root = "/Users/ojas/Desktop/Resume Optimiser/OA-Forge";

function parseCsv(text) {
	const rows = [];
	let row = [];
	let cell = "";
	let quoted = false;
	for (let i = 0; i < text.length; i++) {
		const ch = text[i];
		const next = text[i + 1];
		if (quoted && ch === '"' && next === '"') {
			cell += '"';
			i++;
		} else if (ch === '"') quoted = !quoted;
		else if (!quoted && ch === ",") {
			row.push(cell);
			cell = "";
		} else if (!quoted && (ch === "\n" || ch === "\r")) {
			if (ch === "\r" && next === "\n") i++;
			row.push(cell);
			rows.push(row);
			row = [];
			cell = "";
		} else cell += ch;
	}
	row.push(cell);
	rows.push(row);
	const [headers, ...body] = rows;
	if (!headers) return [];
	const cleanHeaders = headers.map(h => h.trim().replace(/^"/, "").replace(/"$/, ""));
	return body
		.filter(r => r.length > 0 && r.some(c => c.trim() !== ""))
		.map((r) => Object.fromEntries(cleanHeaders.map((h, i) => [h, r[i] ?? ""])));
}

function runAnalysis() {
	const companies = parseCsv(fs.readFileSync(path.join(root, "data", "companies.csv"), "utf8"));
	console.log(`Loaded ${companies.length} companies.`);

	// Load occurrences from git-repos/leetcode-companywise-interview-questions
	const repoPath = path.join(root, "scratch", "git-repos", "leetcode-companywise-interview-questions");
	const companyFolders = fs.existsSync(repoPath)
		? fs.readdirSync(repoPath).filter((item) => fs.statSync(path.join(repoPath, item)).isDirectory() && !item.startsWith("."))
		: [];
	console.log(`Found ${companyFolders.length} folders in github repo.`);

	const allowedSlugs = new Set(companies.map(c => c.slug));
	
	const canonicalMappping = {
		"1mg": "tata-1mg",
		"tata-1mg": "tata-1mg",
		"akamai": "akamai-technologies",
		"akamai-technologies": "akamai-technologies",
		"appdynamics": "appdynamics-cisco",
		"appdynamics-cisco": "appdynamics-cisco",
		"amazon": "amazon",
		"amazon-india": "amazon",
		"amazon-seller-services": "amazon",
		"goldman-sachs": "goldman-sachs",
		"goldman-sachs-india": "goldman-sachs",
		"google": "google",
		"google-india": "google",
		"microsoft": "microsoft",
		"microsoft-india": "microsoft",
		"mckinsey": "mckinsey-and-company",
		"mckinsey-and-company": "mckinsey-and-company",
		"eightfoldai": "eightfold-ai",
		"eigthfold": "eightfold-ai",
		"antropic": "anthropic",
		"anthropic": "anthropic",
		"byd-india": "byd",
		"byd": "byd",
		"walmart": "walmart-global-tech",
		"walmart-labs": "walmart-global-tech",
		"walmart-global-tech": "walmart-global-tech",
		"samsung": "samsung-r-and-d",
		"samsung-r-and-d": "samsung-r-and-d",
		"samsung-r-and-d-institute-india": "samsung-r-and-d",
		"intel": "intel",
		"intel-india": "intel",
		"ibm": "ibm",
		"ibm-consulting": "ibm",
		"ibm-india": "ibm",
		"ibm-research": "ibm",
		"oracle": "oracle",
		"oracle-india": "oracle",
		"salesforce": "salesforce",
		"salesforce-india": "salesforce",
		"adobe": "adobe",
		"adobe-india": "adobe",
		"nvidia": "nvidia",
		"nvidia-india": "nvidia",
		"cisco": "cisco",
		"cisco-india": "cisco",
		"ey": "ey",
		"ernst-and-young-ey": "ey",
		"ey-consulting": "ey",
		"deloitte": "deloitte",
		"deloitte-consulting": "deloitte",
		"monitor-deloitte": "deloitte",
		"phonepe": "phonepe",
		"phonepe-switch": "phonepe",
		"flipkart": "flipkart",
		"flipkart-wholesale": "flipkart",
		"razorpay": "razorpay",
		"razorpayx": "razorpay",
		"sony": "sony",
		"sony-japan": "sony",
		"toyota-india": "toyota",
		"volvo-india": "volvo",
		"bmw-india": "bmw",
		"hyundai-india": "hyundai",
		"jaguar-land-rover-india": "jaguar-land-rover",
		"jaguar-land-rover-technology-and-business-services-india-private-limited": "jaguar-land-rover",
		"wells-fargo": "wells-fargo",
		"wells-fargo-international-solutions-private-limited": "wells-fargo",
		"procter-and-gamble-home-products-private-limited": "procter-and-gamble",
		"imagine-marketing": "boat",
		"boat-imagine-marketing": "boat",
		"boat": "boat",
		"perplexity": "perplexity-ai",
		"perplexity-ai": "perplexity-ai",
	};

	function slugify(name) {
		return name
			.toLowerCase()
			.replace(/&/g, " and ")
			.replace(/[^a-z0-9]+/g, "-")
			.replace(/^-+|-+$/g, "")
			.slice(0, 80);
	}

	const realCompWithOccurrences = new Map();

	for (const folder of companyFolders) {
		let folderSlug = slugify(folder);
		if (folderSlug.endsWith("-india")) folderSlug = folderSlug.slice(0, -6);
		const companySlug = canonicalMappping[folderSlug] || folderSlug;
		if (allowedSlugs.has(companySlug)) {
			// Find how many questions are in this folder
			let totalQuestions = 0;
			const companyDir = path.join(repoPath, folder);
			const csvFiles = ["thirty-days.csv", "three-months.csv", "six-months.csv", "more-than-six-months.csv", "all.csv"];
			for (const file of csvFiles) {
				const p = path.join(companyDir, file);
				if (fs.existsSync(p)) {
					try {
						const rows = parseCsv(fs.readFileSync(p, "utf8"));
						for (const row of rows) {
							const url = row.URL || row.url;
							if (url && url.includes("/problems/")) totalQuestions++;
						}
					} catch {}
				}
			}
			if (totalQuestions > 0) {
				realCompWithOccurrences.set(companySlug, (realCompWithOccurrences.get(companySlug) || 0) + totalQuestions);
			}
		}
	}

	console.log(`Out of ${companies.length} canonical companies, ${realCompWithOccurrences.size} have real GitHub occurrences.`);
	console.log("Top 20 companies by real occurrences:");
	const sorted = Array.from(realCompWithOccurrences.entries()).sort((a,b) => b[1] - a[1]);
	for (const [c, count] of sorted.slice(0, 20)) {
		console.log(`  - ${c}: ${count} occurrences`);
	}
}

runAnalysis();
