import fs from "fs";
import path from "path";

// Load .env.local
const envPath = path.join(process.cwd(), ".env.local");
if (fs.existsSync(envPath)) {
	for (const line of fs.readFileSync(envPath, "utf8").split(/\r?\n/)) {
		const match = line.match(/^([A-Z0-9_]+)=(.*)$/);
		if (match && !process.env[match[1]]) process.env[match[1]] = match[2].trim();
	}
}

const FIRECRAWL_KEY = process.env.FIRECRAWL_API_KEY;
const scoutCsv = path.join(process.cwd(), "..", "internship-scout", "data", "all_companies.csv");

if (FIRECRAWL_KEY) {
	console.log("🔑 Firecrawl API key detected. Will prioritize Firecrawl Search API.");
} else {
	console.log("ℹ️ No FIRECRAWL_API_KEY detected. Will use unauthenticated DuckDuckGo/Google search scraping.");
}

// ─── CSV helpers ────────────────────────────────────────────────────────────

function parseCsv(content) {
	const lines = content.trim().split("\n");
	const headers = lines[0].split(",").map((h) => h.trim());
	return lines.slice(1).map((line) => {
		const values = line.split(",").map((v) => v.trim());
		const obj = {};
		headers.forEach((h, i) => { obj[h] = values[i] || ""; });
		return obj;
	});
}

function csvEscape(value) {
	if (value === null || value === undefined) return "";
	const str = String(value);
	if (str.includes(",") || str.includes('"') || str.includes("\n")) {
		return `"${str.replace(/"/g, '""')}"`;
	}
	return str;
}

function slugifyCompany(name) {
	return name
		.toLowerCase()
		.replace(/[^a-z0-9\s-]/g, "")
		.trim()
		.replace(/\s+/g, "-")
		.replace(/-+/g, "-");
}

// ─── Search API ────────────────────────────────────────────────────────────

async function performSearch(query, count = 10) {
	if (FIRECRAWL_KEY) {
		try {
			const res = await fetch("https://api.firecrawl.dev/v1/search", {
				method: "POST",
				headers: {
					"Content-Type": "application/json",
					"Authorization": `Bearer ${FIRECRAWL_KEY}`
				},
				body: JSON.stringify({
					query,
					limit: count
				}),
				signal: AbortSignal.timeout(15000),
			});
			if (res.ok) {
				const json = await res.json();
				if (json.success && Array.isArray(json.data)) {
					return json.data.map((item) => ({
						title: item.metadata?.title ?? item.title ?? "",
						url: item.url ?? item.metadata?.sourceURL ?? "",
						snippet: item.metadata?.description ?? item.snippet ?? "",
					}));
				}
			}
			console.warn(`  Firecrawl API search failed. Falling back to DuckDuckGo/Google search scraping.`);
		} catch (err) {
			console.warn(`  Firecrawl Search API error: ${err.message}. Falling back to DuckDuckGo/Google search scraping.`);
		}
	}

	const url = `https://html.duckduckgo.com/html/?q=${encodeURIComponent(query)}`;
	const headers = {
		"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
		"Accept-Language": "en-US,en;q=0.9"
	};
	const res = await fetch(url, { headers, signal: AbortSignal.timeout(15000) });
	if (!res.ok) {
		throw new Error(`Unauthenticated scraper failed with status ${res.status}`);
	}
	const html = await res.text();
	const blockRegex = /<div class="[^"]*result__body[^"]*">([\s\S]*?)<div class="clear"><\/div>\s*<\/div>/g;
	let match;
	const results = [];
	while ((match = blockRegex.exec(html)) !== null && results.length < count) {
		const blockHtml = match[1];
		const titleMatch = blockHtml.match(/<a[^>]*class="result__a"[^>]*href="([^"]+)"[^>]*>([\s\S]*?)<\/a>/);
		if (!titleMatch) continue;

		let rawUrl = titleMatch[1];
		let title = titleMatch[2].trim().replace(/<[^>]*>/g, "");
		let cleanUrl = rawUrl;
		if (rawUrl.startsWith("//")) {
			rawUrl = "https:" + rawUrl;
		}
		const urlMatch = rawUrl.match(/[?&]uddg=([^&]+)/);
		if (urlMatch) {
			cleanUrl = decodeURIComponent(urlMatch[1]);
		}

		const snippetMatch = blockHtml.match(/<a[^>]*class="result__snippet"[^>]*>([\s\S]*?)<\/a>/);
		let snippet = "";
		if (snippetMatch) {
			snippet = snippetMatch[1].trim().replace(/<[^>]*>/g, "");
		}

		results.push({ title, url: cleanUrl, snippet });
	}
	return results;
}

// ─── Enrichment helpers ──────────────────────────────────────────────────────

function inferSource(url) {
	const lower = url.toLowerCase();
	if (lower.includes("leetcode.com/problems")) return "leetcode";
	if (lower.includes("leetcode.com/discuss")) return "lc_discuss";
	if (lower.includes("geeksforgeeks.org")) return "gfg";
	if (lower.includes("codeforces.com")) return "codeforces";
	if (lower.includes("hackerrank.com")) return "hackerrank";
	if (lower.includes("reddit.com")) return "reddit";
	if (lower.includes("github.com")) return "github";
	if (lower.includes("glassdoor.")) return "glassdoor";
	return "web";
}

function inferDifficulty(text) {
	const t = text.toLowerCase();
	if (/\beasy\b|beginner|basic/.test(t)) return "Easy";
	if (/\bhard\b|difficult|challenging/.test(t)) return "Hard";
	return "Medium";
}

function inferCategory(text) {
	const t = text.toLowerCase();
	if (/linked list/.test(t)) return "linked-list";
	if (/binary tree|bst/.test(t)) return "trees";
	if (/\bgraph\b|dfs|bfs/.test(t)) return "graphs";
	if (/dynamic programming|\bdp\b/.test(t)) return "dynamic-programming";
	if (/\bsort\b|merge sort|quick sort/.test(t)) return "sorting";
	if (/hash map|hashmap|dictionary/.test(t)) return "hashing";
	if (/\bstack\b|\bqueue\b/.test(t)) return "stacks-queues";
	if (/backtrack|recursion/.test(t)) return "recursion";
	if (/\bgreedy\b/.test(t)) return "greedy";
	if (/binary search/.test(t)) return "binary-search";
	if (/bit manipulation/.test(t)) return "bit-manipulation";
	if (/\bstring\b/.test(t)) return "strings";
	if (/\bmath\b|number theory/.test(t)) return "math";
	return "arrays";
}

function isRelevant(title, snippet, url) {
	const text = `${title} ${snippet} ${url}`.toLowerCase();
	return (
		/interview|assessment|oa\b|coding|leetcode|problem|question/.test(text) &&
		!/job posting|apply now|salary|resume|career page/.test(text)
	);
}

// ─── Per-company scrape ───────────────────────────────────────────────────────

async function scrapeQuestionsForCompany(companyName, companySlug, maxQuestions = 10) {
	const year = new Date().getFullYear();
	const queries = [
		`${companyName} online assessment coding questions ${year} intern`,
		`${companyName} OA questions ${year} leetcode`,
		`${companyName} coding interview questions ${year}`,
	];

	const questions = [];
	const seenUrls = new Set();

	for (const query of queries) {
		if (questions.length >= maxQuestions) break;
		try {
			const results = await performSearch(query, 10);
			for (const result of results) {
				if (questions.length >= maxQuestions) break;
				if (seenUrls.has(result.url)) continue;
				if (!isRelevant(result.title, result.snippet, result.url)) continue;

				const text = `${result.title} ${result.snippet}`;
				const slug = `${companySlug}-${result.title
					.toLowerCase()
					.replace(/[^a-z0-9\s-]/g, "")
					.trim()
					.replace(/\s+/g, "-")
					.substring(0, 50)}`;

				questions.push({
					slug,
					title: result.title,
					difficulty: inferDifficulty(text),
					category: inferCategory(text),
					source_url: result.url,
					source_type: inferSource(result.url),
					snippet: result.snippet,
				});

				seenUrls.add(result.url);
			}
		} catch (error) {
			console.error(`  Error searching "${query}": ${error.message}`);
		}

		// Polite delay between queries (Brave free tier: 1 req/sec)
		await new Promise((r) => setTimeout(r, 1100));
	}

	return questions;
}

// ─── Main ────────────────────────────────────────────────────────────────────

async function main() {
	const args = process.argv.slice(2);
	const onlyCompany = args.find((a) => a.startsWith("--company="))?.split("=")[1];
	const maxQuestions = parseInt(args.find((a) => a.startsWith("--max="))?.split("=")[1] || "10");
	const maxCompanies = parseInt(args.find((a) => a.startsWith("--limit="))?.split("=")[1] || "0");

	if (!fs.existsSync(scoutCsv)) {
		console.error(`❌ Cannot find ${scoutCsv}`);
		console.error("   Make sure internship-scout/data/all_companies.csv exists next to OA-Forge.");
		process.exit(1);
	}

	console.log("🔍 Starting OA question scraper...");

	const companies = parseCsv(fs.readFileSync(scoutCsv, "utf8"))
		.map((row) => ({ name: row.Company, slug: slugifyCompany(row.Company) }))
		.filter((c) => c.name);

	let selected = onlyCompany
		? companies.filter((c) => c.slug.includes(onlyCompany) || c.name.toLowerCase().includes(onlyCompany.toLowerCase()))
		: companies;

	if (maxCompanies > 0) selected = selected.slice(0, maxCompanies);

	console.log(`📊 Processing ${selected.length} companies (max ${maxQuestions} questions each)...`);

	const allQuestions = [];

	for (const [index, company] of selected.entries()) {
		process.stdout.write(`[${index + 1}/${selected.length}] ${company.name}... `);
		try {
			const questions = await scrapeQuestionsForCompany(company.name, company.slug, maxQuestions);
			console.log(`✓ ${questions.length} leads`);
			for (const q of questions) {
				allQuestions.push({
					company_slug: company.slug,
					company_name: company.name,
					...q,
					confidence_tier: "C",
					year: new Date().getFullYear(),
					scraped_at: new Date().toISOString(),
				});
			}
		} catch (error) {
			console.log(`✗ ${error.message}`);
		}

		// Polite delay between companies
		await new Promise((r) => setTimeout(r, 500));
	}

	const outPath = path.join(process.cwd(), "data", "scraped-questions.csv");
	const headers = [
		"company_slug", "company_name", "slug", "title", "difficulty",
		"category", "source_url", "source_type", "snippet",
		"confidence_tier", "year", "scraped_at",
	];
	const csv = [
		headers.join(","),
		...allQuestions.map((q) => headers.map((h) => csvEscape(q[h])).join(",")),
	].join("\n");

	fs.writeFileSync(outPath, csv);
	console.log(`\n✅ Saved ${allQuestions.length} leads to data/scraped-questions.csv`);
	console.log(`   Review leads, then promote strong ones to data/occurrences.csv with tier A or B.`);
}

main().catch((e) => {
	console.error("Fatal:", e.message);
	process.exit(1);
});
