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

async function searchYahoo(query, count = 10) {
	const url = `https://search.yahoo.com/search?p=${encodeURIComponent(query)}&n=${count}`;
	const headers = {
		"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
	};
	const res = await fetch(url, { headers, signal: AbortSignal.timeout(15000) });
	if (!res.ok) throw new Error(`Yahoo status ${res.status}`);
	const html = await res.text();
	
	const results = [];
	const blocks = html.split(/<div[^>]*class="[^"]*algo-sr[^"]*"/g);
	if (blocks.length <= 1) return results;

	for (let i = 1; i < blocks.length; i++) {
		if (results.length >= count) break;
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
			title = titleMatch[1]
				.replace(/<script[\s\S]*?<\/script>/gi, "")
				.replace(/<style[\s\S]*?<\/style>/gi, "")
				.replace(/<[^>]+>/g, " ")
				.replace(/&quot;/g, '"')
				.replace(/&#x27;/g, "'")
				.replace(/&amp;/g, "&")
				.replace(/\s+/g, " ")
				.trim();
		}

		const snippetMatch = block.match(/class="compText[^>]*>([\s\S]*?)<\/div>/);
		let snippet = "";
		if (snippetMatch) {
			snippet = snippetMatch[1]
				.replace(/<script[\s\S]*?<\/script>/gi, "")
				.replace(/<style[\s\S]*?<\/style>/gi, "")
				.replace(/<[^>]+>/g, " ")
				.replace(/&quot;/g, '"')
				.replace(/&#x27;/g, "'")
				.replace(/&amp;/g, "&")
				.replace(/\s+/g, " ")
				.trim();
		}

		if (realUrl && (title || snippet)) {
			results.push({ title, url: realUrl, snippet });
		}
	}
	return results;
}

async function searchBing(query, count = 10) {
	const url = `https://www.bing.com/search?q=${encodeURIComponent(query)}`;
	const headers = {
		"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
		"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
		"Accept-Language": "en-US,en;q=0.5",
	};

	const res = await fetch(url, { headers, signal: AbortSignal.timeout(15000) });
	if (!res.ok) throw new Error(`Bing status ${res.status}`);
	const html = await res.text();
	
	const results = [];
	const blocks = html.split(/<li[^>]*class="[^"]*b_algo[^"]*"[^>]*>/g);
	if (blocks.length <= 1) return results;

	for (let i = 1; i < blocks.length; i++) {
		if (results.length >= count) break;
		const block = blocks[i].split("</li>")[0];

		const h2Match = block.match(/<h2[^>]*>([\s\S]*?)<\/h2>/);
		if (!h2Match) continue;
		const h2Content = h2Match[1];
		
		const hrefMatch = h2Content.match(/href="([^"]+)"/);
		if (!hrefMatch) continue;
		const href = hrefMatch[1];
		
		let realUrl = href;
		if (href.includes("bing.com/ck/a")) {
			try {
				const urlObj = new URL(href);
				const u = urlObj.searchParams.get("u");
				if (u) {
					for (let offset = 0; offset < 5; offset++) {
						try {
							const candidate = Buffer.from(u.substring(offset), "base64").toString("utf8");
							if (candidate.startsWith("http")) {
								realUrl = candidate;
								break;
							}
						} catch (_) {}
					}
				}
			} catch (_) {}
		}

		const titleMatch = h2Content.replace(/<[^>]+>/g, "").replace(/\s+/g, " ").trim();
		const title = titleMatch || "";

		const snippetMatch = block.match(/<p[^>]*>([\s\S]*?)<\/p>|<div class="b_caption"[^>]*>([\s\S]*?)<\/div>/);
		let snippet = "";
		if (snippetMatch) {
			const rawSnippet = snippetMatch[1] || snippetMatch[2] || "";
			snippet = rawSnippet
				.replace(/<script[\s\S]*?<\/script>/gi, "")
				.replace(/<style[\s\S]*?<\/style>/gi, "")
				.replace(/<[^>]+>/g, " ")
				.replace(/&quot;/g, '"')
				.replace(/&#x27;/g, "'")
				.replace(/&amp;/g, "&")
				.replace(/\s+/g, " ")
				.trim();
		}

		if (realUrl && (title || snippet)) {
			results.push({ title, url: realUrl, snippet });
		}
	}
	return results;
}

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
				} else {
					console.warn(`  Firecrawl API search response unsuccessful: ${JSON.stringify(json)}`);
				}
			} else {
				let errText = "";
				try { errText = await res.text(); } catch (_) {}
				console.warn(`  Firecrawl API search failed with status ${res.status}: ${res.statusText}. Response: ${errText.substring(0, 200)}`);
			}
			console.warn(`  Falling back to unauthenticated search scraping.`);
		} catch (err) {
			console.warn(`  Firecrawl Search API error: ${err.message}. Falling back to unauthenticated search scraping.`);
		}
	}

	// Try DuckDuckGo first
	try {
		const url = `https://html.duckduckgo.com/html/?q=${encodeURIComponent(query)}`;
		const headers = {
			"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
			"Accept-Language": "en-US,en;q=0.9"
		};
		const res = await fetch(url, { headers, signal: AbortSignal.timeout(15000) });
		if (res.ok) {
			const html = await res.text();
			const results = html
				.split(/<div class="result /g)
				.slice(1)
				.map((block) => {
					const href = block.match(/class="result__a" href="([^"]+)"/)?.[1] || "";
					const titleHtml = block.match(/class="result__a"[^>]*>([\s\S]*?)<\/a>/)?.[1] || "";
					const snippetHtml =
						block.match(/class="result__snippet"[^>]*>([\s\S]*?)<\/a>|class="result__snippet"[^>]*>([\s\S]*?)<\/div>/)?.[1] ||
						"";
					
					let cleanUrl = href;
					if (href.startsWith("//")) {
						cleanUrl = "https:" + href;
					}
					const urlMatch = cleanUrl.match(/[?&]uddg=([^&]+)/);
					if (urlMatch) {
						cleanUrl = decodeURIComponent(urlMatch[1]);
					}

					const title = titleHtml
						.replace(/<[^>]+>/g, " ")
						.replace(/&quot;/g, '"')
						.replace(/&#x27;/g, "'")
						.replace(/&amp;/g, "&")
						.replace(/\s+/g, " ")
						.trim();

					const snippet = snippetHtml
						.replace(/<[^>]+>/g, " ")
						.replace(/&quot;/g, '"')
						.replace(/&#x27;/g, "'")
						.replace(/&amp;/g, "&")
						.replace(/\s+/g, " ")
						.trim();

					return { title, url: cleanUrl, snippet };
				})
				.filter((row) => row.title && row.url)
				.slice(0, count);

			if (results.length > 0) {
				return results;
			}
		}
		console.warn(`  DuckDuckGo search returned 0 results. Falling back to Bing.`);
	} catch (err) {
		console.warn(`  DuckDuckGo search failed: ${err.message}. Falling back to Bing.`);
	}

	// Try Bing search second
	try {
		const bingResults = await searchBing(query, count);
		if (bingResults.length > 0) {
			return bingResults;
		}
		console.warn(`  Bing search returned 0 results. Falling back to Yahoo.`);
	} catch (err) {
		console.warn(`  Bing search failed: ${err.message}. Falling back to Yahoo.`);
	}

	// Try Yahoo search third
	try {
		const yahooResults = await searchYahoo(query, count);
		if (yahooResults.length > 0) {
			return yahooResults;
		}
		console.warn(`  Yahoo search returned 0 results.`);
	} catch (err) {
		console.warn(`  Yahoo search failed: ${err.message}`);
	}

	return [];
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

function parseCsvRobust(content) {
	const lines = [];
	let currentLine = [];
	let currentVal = "";
	let inQuotes = false;
	
	let i = 0;
	while (i < content.length) {
		const char = content[i];
		const nextChar = content[i + 1];
		
		if (inQuotes) {
			if (char === '"') {
				if (nextChar === '"') {
					currentVal += '"';
					i += 2;
					continue;
				} else {
					inQuotes = false;
					i++;
					continue;
				}
			}
			currentVal += char;
			i++;
		} else {
			if (char === '"') {
				inQuotes = true;
				i++;
			} else if (char === ',') {
				currentLine.push(currentVal.trim());
				currentVal = "";
				i++;
			} else if (char === '\n' || char === '\r') {
				currentLine.push(currentVal.trim());
				if (currentLine.length > 0 && currentLine.some(x => x)) {
					lines.push(currentLine);
				}
				currentLine = [];
				currentVal = "";
				if (char === '\r' && nextChar === '\n') {
					i += 2;
				} else {
					i++;
				}
			} else {
				currentVal += char;
				i++;
			}
		}
	}
	if (currentVal || currentLine.length > 0) {
		currentLine.push(currentVal.trim());
		lines.push(currentLine);
	}
	
	if (lines.length === 0) return [];
	const headers = lines[0];
	return lines.slice(1).map((row) => {
		const obj = {};
		headers.forEach((h, idx) => {
			obj[h] = row[idx] || "";
		});
		return obj;
	});
}

async function main() {
	const args = process.argv.slice(2);
	const onlyCompany = args.find((a) => a.startsWith("--company="))?.split("=")[1];
	const maxQuestions = parseInt(args.find((a) => a.startsWith("--max="))?.split("=")[1] || "10");
	const maxCompanies = parseInt(args.find((a) => a.startsWith("--limit="))?.split("=")[1] || "0");
	const concurrency = parseInt(args.find((a) => a.startsWith("--concurrency="))?.split("=")[1] || "15");

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

	console.log(`📊 Processing ${selected.length} companies (max ${maxQuestions} questions each, concurrency: ${concurrency})...`);

	const outPath = path.join(process.cwd(), "data", "scraped-questions.csv");
	const allQuestions = [];
	const scrapedCompanies = new Set();

	if (fs.existsSync(outPath)) {
		try {
			const existingCsvContent = fs.readFileSync(outPath, "utf8");
			const existingRows = parseCsvRobust(existingCsvContent);
			for (const row of existingRows) {
				if (row.company_slug) {
					scrapedCompanies.add(row.company_slug);
					allQuestions.push(row);
				}
			}
			console.log(`ℹ️ Found existing scraped questions CSV. Loaded ${allQuestions.length} questions for ${scrapedCompanies.size} companies.`);
		} catch (err) {
			console.warn(`⚠️ Error reading existing CSV: ${err.message}. Starting fresh.`);
		}
	}

	const queue = [...selected];
	let completedCount = 0;

	async function worker() {
		while (queue.length > 0) {
			const company = queue.shift();
			if (!company) continue;

			if (scrapedCompanies.has(company.slug) && !onlyCompany) {
				completedCount++;
				continue;
			}

			const currentIndex = completedCount + 1;
			console.log(`[${currentIndex}/${selected.length}] Scraping ${company.name}...`);
			
			try {
				const questions = await scrapeQuestionsForCompany(company.name, company.slug, maxQuestions);
				console.log(`[${currentIndex}/${selected.length}] Finished ${company.name}: ✓ ${questions.length} leads`);

				// Remove any previously existing questions for this company to avoid duplicates
				if (onlyCompany) {
					for (let i = allQuestions.length - 1; i >= 0; i--) {
						if (allQuestions[i].company_slug === company.slug) {
							allQuestions.splice(i, 1);
						}
					}
				}

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

				// Save progress incrementally after each company
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
				scrapedCompanies.add(company.slug);
			} catch (error) {
				console.log(`[${currentIndex}/${selected.length}] Failed ${company.name}: ✗ ${error.message}`);
			}

			completedCount++;
			// Polite delay between requests for this worker
			await new Promise((r) => setTimeout(r, 500));
		}
	}

	const workers = Array.from({ length: concurrency }, () => worker());
	await Promise.all(workers);

	console.log(`\n✅ Finished scraping! Saved ${allQuestions.length} leads to data/scraped-questions.csv`);
	console.log(`   Review leads, then promote strong ones to data/occurrences.csv with tier A or B.`);
}

main().catch((e) => {
	console.error("Fatal:", e.message);
	process.exit(1);
});
