import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const args = new Map(
	process.argv.slice(2).map((arg) => {
		const [key, value = "true"] = arg.replace(/^--/, "").split("=");
		return [key, value];
	})
);

const scoutCsv = path.join(root, "..", "internship-scout", "data", "all_companies.csv");
const maxCompanies = Number(args.get("max") || process.env.OA_REFRESH_MAX_COMPANIES || 0);
const onlyCompany = args.get("company")?.toLowerCase();
const year = args.get("year") || new Date().getFullYear().toString();

function parseCsv(text) {
	const rows = [];
	let row = [];
	let cell = "";
	let quoted = false;
	for (let i = 0; i < text.trim().length; i++) {
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
	return body.map((r) => Object.fromEntries(headers.map((h, i) => [h, r[i] || ""])));
}

function csvEscape(value) {
	const text = String(value ?? "");
	return /[",\n\r]/.test(text) ? `"${text.replace(/"/g, '""')}"` : text;
}

function slugifyCompany(name) {
	return name
		.toLowerCase()
		.replace(/&/g, " and ")
		.replace(/[^a-z0-9]+/g, "-")
		.replace(/^-+|-+$/g, "")
		.slice(0, 80);
}

function stripHtml(html) {
	return html
		.replace(/<script[\s\S]*?<\/script>/gi, "")
		.replace(/<style[\s\S]*?<\/style>/gi, "")
		.replace(/<[^>]+>/g, " ")
		.replace(/&quot;/g, '"')
		.replace(/&#x27;/g, "'")
		.replace(/&amp;/g, "&")
		.replace(/\s+/g, " ")
		.trim();
}

async function searchYahoo(query) {
	const url = `https://search.yahoo.com/search?p=${encodeURIComponent(query)}&n=15`;
	const headers = {
		"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
	};
	const res = await fetch(url, { headers });
	if (!res.ok) throw new Error(`Yahoo status ${res.status}`);
	const html = await res.text();
	
	const results = [];
	const blocks = html.split(/<div[^>]*class="[^"]*algo-sr[^"]*"/g);
	if (blocks.length <= 1) return results;

	for (let i = 1; i < blocks.length; i++) {
		const block = blocks[i];
		const hrefMatch = block.match(/href="([^"]+)"/);
		const href = hrefMatch ? hrefMatch[1] : "";
		
		let realUrl = href;
		const ruMatch = href.match(/\/RU=([^/]+)/);
		if (ruMatch) {
			try {
				realUrl = decodeURIComponent(ruMatch[1]);
			} catch (_) {}
		}

		const titleMatch = block.match(/class="title[^>]*>([\s\S]*?)<\/h3>/);
		let title = "";
		if (titleMatch) {
			title = stripHtml(titleMatch[1]);
		}

		const snippetMatch = block.match(/class="compText[^>]*>([\s\S]*?)<\/div>/);
		let snippet = "";
		if (snippetMatch) {
			snippet = stripHtml(snippetMatch[1]);
		}

		if (realUrl && (title || snippet)) {
			results.push({
				title,
				url: realUrl,
				snippet
			});
		}
	}
	return results;
}

function duckDuckGoUrl(query) {
	return `https://html.duckduckgo.com/html/?q=${encodeURIComponent(query)}`;
}

async function search(query) {
	try {
		const yahooResults = await searchYahoo(query);
		if (yahooResults.length > 0) return yahooResults;
	} catch (err) {
		console.warn(`Yahoo search failed: ${err.message}. Falling back to DuckDuckGo.`);
	}

	const res = await fetch(duckDuckGoUrl(query), {
		headers: {
			"user-agent":
				"Mozilla/5.0 (Macintosh; Intel Mac OS X) AppleWebKit/537.36 OAForgeResearch/1.0",
		},
	});
	if (!res.ok) throw new Error(`Search failed ${res.status}`);
	const html = await res.text();
	const blocks = html.split(/<div class="result /g).slice(1, 15);
	return blocks
		.map((block) => {
			const href = block.match(/class="result__a" href="([^"]+)"/)?.[1] || "";
			const titleHtml = block.match(/class="result__a"[^>]*>([\s\S]*?)<\/a>/)?.[1] || "";
			const snippetHtml = block.match(/class="result__snippet"[^>]*>([\s\S]*?)<\/a>|class="result__snippet"[^>]*>([\s\S]*?)<\/div>/)?.[1] || "";
			return {
				title: stripHtml(titleHtml),
				url: href.replace(/^\/\/duckduckgo.com\/l\/\?uddg=/, "").split("&rut=")[0],
				snippet: stripHtml(snippetHtml),
			};
		})
		.filter((r) => r.title && r.url);
}

const companies = parseCsv(fs.readFileSync(scoutCsv, "utf8"))
	.map((row) => ({ name: row.Company, slug: slugifyCompany(row.Company), sector: row.Sector || "" }))
	.filter((company) => company.name)
	.filter((company) => !onlyCompany || company.slug.includes(onlyCompany) || company.name.toLowerCase().includes(onlyCompany));

const selected = maxCompanies > 0 ? companies.slice(0, maxCompanies) : companies;
const leads = [];
const queries = [
	(company) => `${company.name} interview experience online assessment ${year} intern reddit`,
	(company) => `${company.name} OA experience ${year} SDE intern leetcode discuss`,
	(company) => `${company.name} online assessment my experience ${year} intern`,
	(company) => `${company.name} coding round interview ${year} intern blind`,
	(company) => `${company.name} online assessment questions ${year} intern`,
	(company) => `${company.name} OA questions ${year} intern`,
];

for (const [index, company] of selected.entries()) {
	console.log(`[${index + 1}/${selected.length}] ${company.name}`);
	for (const makeQuery of queries) {
		const query = makeQuery(company);
		try {
			const results = await search(query);
			for (const result of results) {
				const sourceType = inferSource(result.url);
				const confidenceHint = inferConfidence(result.title, result.snippet);
				
				// Only skip explicitly rejected sources
				if (sourceType === "reject" || confidenceHint === "reject") {
					continue;
				}
				
				leads.push({
					collected_at: new Date().toISOString(),
					company_slug: company.slug,
					company_name: company.name,
					sector: company.sector,
					query,
					title: result.title,
					url: normalizeUrl(result.url),
					snippet: result.snippet,
					source_type: sourceType,
					confidence_hint: confidenceHint,
				});
			}
			await new Promise((resolve) => setTimeout(resolve, 450));
		} catch (error) {
			leads.push({
				collected_at: new Date().toISOString(),
				company_slug: company.slug,
				company_name: company.name,
				sector: company.sector,
				query,
				title: "FETCH_ERROR",
				url: "",
				snippet: error instanceof Error ? error.message : "unknown",
				source_type: "error",
				confidence_hint: "reject",
			});
		}
	}
}

const out = path.join(root, "data", "oa-source-leads.csv");
const headers = [
	"collected_at",
	"company_slug",
	"company_name",
	"sector",
	"query",
	"title",
	"url",
	"snippet",
	"source_type",
	"confidence_hint",
];
fs.writeFileSync(out, [headers.join(","), ...leads.map((lead) => headers.map((h) => csvEscape(lead[h])).join(","))].join("\n"));
console.log(`Wrote ${leads.length} leads to ${out}`);

function inferSource(url) {
	const lower = url.toLowerCase();
	if (lower.includes("careers.") || lower.includes("/careers") || lower.includes(".jobs")) return "official";
	if (lower.includes("leetcode.com/discuss")) return "lc_discuss";
	if (lower.includes("reddit.com")) return "reddit";
	if (lower.includes("blind.com") || lower.includes("teamblind.com")) return "blind";
	if (lower.includes("glassdoor.")) return "glassdoor";
	if (lower.includes("github.com")) return "github";
	// Filter out only the worst SEO content
	if (lower.includes("prepinsta.com")) return "reject";
	if (lower.includes("graduatesfirst.com")) return "reject";
	// Keep GFG and others as "web" - let confidence scoring decide
	return "web";
}

function normalizeUrl(raw) {
	return decodeURIComponent(raw)
		.replace(/&amp;/g, "&")
		.replace(/\?rut=.*$/, "")
		.replace(/&rut=.*$/, "");
}

function inferConfidence(title, snippet) {
	const text = `${title} ${snippet}`.toLowerCase();
	
	// Only reject the most obvious SEO spam
	if (/important for all the contenders|before good before the test/.test(text)) {
		return "reject";
	}
	
	// Prioritize actual user experiences
	if (/my experience|i gave|i appeared|i took|my interview|my test|my assessment|my oa|online assessment experience|interview experience/.test(text) && /2026|2025/.test(text)) {
		return "review-fast";
	}
	
	// Good indicators of real reports
	if (/shared my|my experience with|report|discussion|thread|reddit|blind|leetcode discuss/.test(text)) {
		return "review";
	}
	
	// Accept OA-related content even if not perfect
	if (/online assessment|coding round|coding question|oa question|interview question/.test(text) && /2026|2025/.test(text)) {
		return "review";
	}
	
	// Weak but acceptable
	if (/online assessment|coding round|coding question|oa/.test(text)) {
		return "weak";
	}
	
	return "weak"; // Default to weak instead of reject
}
