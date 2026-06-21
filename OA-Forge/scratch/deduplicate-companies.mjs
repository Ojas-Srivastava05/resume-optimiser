import fs from "fs";
import path from "path";

const root = "/Users/ojas/Desktop/Resume Optimiser/OA-Forge";
const companiesFile = path.join(root, "data", "companies.csv");

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
	return body.map((r) => Object.fromEntries(headers.map((h, i) => [h, r[i] ?? ""])));
}

function slugify(name) {
	return name
		.toLowerCase()
		.replace(/&/g, " and ")
		.replace(/[^a-z0-9]+/g, "-")
		.replace(/^-+|-+$/g, "")
		.slice(0, 80);
}

function csvEscape(v) {
	const s = String(v ?? "");
	if (s.includes(",") || s.includes('"') || s.includes("\n")) return `"${s.replace(/"/g, '""')}"`;
	return s;
}

const rawText = fs.readFileSync(companiesFile, "utf8").trim();
const companies = parseCsv(rawText);

console.log(`Original count: ${companies.length}`);

// Mapping for manual merges and corrections
const canonicalMappping = {
	"1mg": { name: "Tata 1mg", slug: "tata-1mg" },
	"tata-1mg": { name: "Tata 1mg", slug: "tata-1mg" },
	"akamai": { name: "Akamai Technologies", slug: "akamai-technologies" },
	"akamai-technologies": { name: "Akamai Technologies", slug: "akamai-technologies" },
	"appdynamics": { name: "AppDynamics (Cisco)", slug: "appdynamics-cisco" },
	"appdynamics-cisco": { name: "AppDynamics (Cisco)", slug: "appdynamics-cisco" },
	"amazon": { name: "Amazon", slug: "amazon" },
	"amazon-india": { name: "Amazon", slug: "amazon" },
	"amazon-seller-services": { name: "Amazon", slug: "amazon" },
	"goldman-sachs": { name: "Goldman Sachs", slug: "goldman-sachs" },
	"goldman-sachs-india": { name: "Goldman Sachs", slug: "goldman-sachs" },
	"google": { name: "Google", slug: "google" },
	"google-india": { name: "Google", slug: "google" },
	"microsoft": { name: "Microsoft", slug: "microsoft" },
	"microsoft-india": { name: "Microsoft", slug: "microsoft" },
	"mckinsey": { name: "McKinsey & Company", slug: "mckinsey-and-company" },
	"mckinsey-and-company": { name: "McKinsey & Company", slug: "mckinsey-and-company" },
	"eightfoldai": { name: "Eightfold.ai", slug: "eightfold-ai" },
	"eigthfold": { name: "Eightfold.ai", slug: "eightfold-ai" },
	"antropic": { name: "Anthropic", slug: "anthropic" },
	"anthropic": { name: "Anthropic", slug: "anthropic" },
	"byd-india": { name: "BYD", slug: "byd" },
	"byd": { name: "BYD", slug: "byd" },
	"walmart": { name: "Walmart Global Tech", slug: "walmart-global-tech" },
	"walmart-labs": { name: "Walmart Global Tech", slug: "walmart-global-tech" },
	"walmart-global-tech": { name: "Walmart Global Tech", slug: "walmart-global-tech" },
	"samsung": { name: "Samsung R&D", slug: "samsung-r-and-d" },
	"samsung-r-and-d": { name: "Samsung R&D", slug: "samsung-r-and-d" },
	"samsung-r-and-d-institute-india": { name: "Samsung R&D", slug: "samsung-r-and-d" },
	"intel": { name: "Intel", slug: "intel" },
	"intel-india": { name: "Intel", slug: "intel" },
	"ibm": { name: "IBM", slug: "ibm" },
	"ibm-consulting": { name: "IBM", slug: "ibm" },
	"ibm-india": { name: "IBM", slug: "ibm" },
	"ibm-research": { name: "IBM", slug: "ibm" },
	"oracle": { name: "Oracle", slug: "oracle" },
	"oracle-india": { name: "Oracle", slug: "oracle" },
	"salesforce": { name: "Salesforce", slug: "salesforce" },
	"salesforce-india": { name: "Salesforce", slug: "salesforce" },
	"adobe": { name: "Adobe", slug: "adobe" },
	"adobe-india": { name: "Adobe", slug: "adobe" },
	"nvidia": { name: "NVIDIA", slug: "nvidia" },
	"nvidia-india": { name: "NVIDIA", slug: "nvidia" },
	"cisco": { name: "Cisco", slug: "cisco" },
	"cisco-india": { name: "Cisco", slug: "cisco" },
	"ey": { name: "EY", slug: "ey" },
	"ernst-and-young-ey": { name: "EY", slug: "ey" },
	"ey-consulting": { name: "EY", slug: "ey" },
	"deloitte": { name: "Deloitte", slug: "deloitte" },
	"deloitte-consulting": { name: "Deloitte", slug: "deloitte" },
	"monitor-deloitte": { name: "Deloitte", slug: "deloitte" },
	"phonepe": { name: "PhonePe", slug: "phonepe" },
	"phonepe-switch": { name: "PhonePe", slug: "phonepe" },
	"flipkart": { name: "Flipkart", slug: "flipkart" },
	"flipkart-wholesale": { name: "Flipkart", slug: "flipkart" },
	"razorpay": { name: "Razorpay", slug: "razorpay" },
	"razorpayx": { name: "Razorpay", slug: "razorpay" },
	"sony": { name: "Sony", slug: "sony" },
	"sony-japan": { name: "Sony", slug: "sony" },
	"toyota-india": { name: "Toyota", slug: "toyota" },
	"volvo-india": { name: "Volvo", slug: "volvo" },
	"bmw-india": { name: "BMW", slug: "bmw" },
	"hyundai-india": { name: "Hyundai", slug: "hyundai" },
	"jaguar-land-rover-india": { name: "Jaguar Land Rover", slug: "jaguar-land-rover" },
	"jaguar-land-rover-technology-and-business-services-india-private-limited": { name: "Jaguar Land Rover", slug: "jaguar-land-rover" },
	"wells-fargo": { name: "Wells Fargo", slug: "wells-fargo" },
	"wells-fargo-international-solutions-private-limited": { name: "Wells Fargo", slug: "wells-fargo" },
	"procter-and-gamble-home-products-private-limited": { name: "Procter & Gamble", slug: "procter-and-gamble" },
	"imagine-marketing": { name: "boAt (Imagine Marketing)", slug: "boat" },
	"boat-imagine-marketing": { name: "boAt (Imagine Marketing)", slug: "boat" },
	"boat": { name: "boAt (Imagine Marketing)", slug: "boat" },
	"perplexity": { name: "Perplexity AI", slug: "perplexity-ai" },
	"perplexity-ai": { name: "Perplexity AI", slug: "perplexity-ai" },
};

const uniqueCompanies = new Map();

for (const c of companies) {
	let name = c.name.trim();
	let slug = c.slug.trim();

	// 1. Remove URLs and html-like entries
	if (
		name.includes("http") ||
		name.includes("www") ||
		name.includes("<") ||
		name.includes(">") ||
		name.includes("/") && !name.includes(" / ") ||
		slug.includes("http") ||
		slug.includes("www")
	) {
		console.log(`Skipping fake company: ${name}`);
		continue;
	}

	// 2. Rule-based normalization
	// Strip " India" from suffix
	if (name.endsWith(" India")) {
		name = name.slice(0, -6).trim();
		slug = slugify(name);
	}

	// Strip " Consulting" suffix from major consulting agencies
	if (name.endsWith(" Consulting") && (name.startsWith("Accenture") || name.startsWith("Deloitte") || name.startsWith("KPMG") || name.startsWith("PwC") || name.startsWith("Infosys") || name.startsWith("Cognizant") || name.startsWith("Wipro"))) {
		name = name.slice(0, -11).trim();
		slug = slugify(name);
	}

	// 3. Map to canonical if listed in manual overrides
	if (canonicalMappping[slug]) {
		name = canonicalMappping[slug].name;
		slug = canonicalMappping[slug].slug;
	}

	// Check if this canonical slug already exists
	if (uniqueCompanies.has(slug)) {
		// Keep the one with better formatting / shorter name
		const existing = uniqueCompanies.get(slug);
		if (name.length < existing.name.length) {
			uniqueCompanies.set(slug, {
				slug,
				name,
				default_duration_minutes: c.default_duration_minutes || "90",
				default_num_questions: c.default_num_questions || "2",
				target_role: c.target_role || "SDE Intern",
			});
		}
	} else {
		uniqueCompanies.set(slug, {
			slug,
			name,
			default_duration_minutes: c.default_duration_minutes || "90",
			default_num_questions: c.default_num_questions || "2",
			target_role: c.target_role || "SDE Intern",
		});
	}
}

// Sort alphabetically by name
const sortedCompanies = Array.from(uniqueCompanies.values()).sort((a, b) =>
	a.name.localeCompare(b.name, "en", { sensitivity: "base" })
);

// Save to companies.csv
const headers = ["slug", "name", "default_duration_minutes", "default_num_questions", "target_role"];
const csvRows = [
	headers.join(","),
	...sortedCompanies.map((c) =>
		[c.slug, c.name, c.default_duration_minutes, c.default_num_questions, c.target_role]
			.map(csvEscape)
			.join(",")
	),
];

fs.writeFileSync(companiesFile, csvRows.join("\n"));
console.log(`Cleaned count: ${sortedCompanies.length}`);
