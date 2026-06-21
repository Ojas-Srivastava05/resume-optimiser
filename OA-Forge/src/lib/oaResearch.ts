import { slugifyCompany } from "./csv";

export type OALead = {
	collected_at: string;
	company_slug: string;
	company_name: string;
	query: string;
	title: string;
	url: string;
	snippet: string;
	source_type: string;
	confidence_hint: string;
};

function stripHtml(html: string) {
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

function normalizeUrl(raw: string) {
	return decodeURIComponent(raw)
		.replace(/^\/\/duckduckgo.com\/l\/\?uddg=/, "")
		.replace(/&amp;/g, "&")
		.replace(/\?rut=.*$/, "")
		.replace(/&rut=.*$/, "");
}

function inferSource(url: string) {
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

function inferConfidence(title: string, snippet: string) {
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

async function searchBing(query: string) {
	const url = `https://www.bing.com/search?q=${encodeURIComponent(query)}`;
	const headers = {
		"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
		"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
		"Accept-Language": "en-US,en;q=0.5",
	};

	const res = await fetch(url, { headers });
	if (!res.ok) throw new Error(`Bing status ${res.status}`);
	const html = await res.text();
	
	const results: { title: string; url: string; snippet: string }[] = [];
	const blocks = html.split(/<li[^>]*class="[^"]*b_algo[^"]*"[^>]*>/g);
	if (blocks.length <= 1) return results;

	for (let i = 1; i < blocks.length; i++) {
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

async function searchYahoo(query: string) {
	const url = `https://search.yahoo.com/search?p=${encodeURIComponent(query)}&n=15`;
	const res = await fetch(url, {
		headers: {
			"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
		},
	});
	if (!res.ok) throw new Error(`Yahoo status ${res.status}`);
	const html = await res.text();
	
	const results: { title: string; url: string; snippet: string }[] = [];
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
			results.push({ title, url: realUrl, snippet });
		}
	}
	return results;
}

async function search(query: string) {
	// Try DuckDuckGo first
	try {
		const url = `https://html.duckduckgo.com/html/?q=${encodeURIComponent(query)}`;
		const res = await fetch(url, {
			headers: {
				"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
			},
		});
		if (res.ok) {
			const html = await res.text();
			const results = html
				.split(/<div class="result /g)
				.slice(1, 15)
				.map((block) => {
					const href = block.match(/class="result__a" href="([^"]+)"/)?.[1] || "";
					const titleHtml = block.match(/class="result__a"[^>]*>([\s\S]*?)<\/a>/)?.[1] || "";
					const snippetHtml =
						block.match(/class="result__snippet"[^>]*>([\s\S]*?)<\/a>|class="result__snippet"[^>]*>([\s\S]*?)<\/div>/)?.[1] ||
						"";
					return {
						title: stripHtml(titleHtml),
						url: normalizeUrl(href),
						snippet: stripHtml(snippetHtml),
					};
				})
				.filter((row) => row.title && row.url);
			if (results.length > 0) return results;
		}
	} catch (err) {
		console.warn("DuckDuckGo search failed:", err);
	}

	// Try Bing second
	try {
		const bingResults = await searchBing(query);
		if (bingResults.length > 0) return bingResults;
	} catch (err) {
		console.warn("Bing search failed:", err);
	}

	// Try Yahoo third
	try {
		const yahooResults = await searchYahoo(query);
		if (yahooResults.length > 0) return yahooResults;
	} catch (err) {
		console.warn("Yahoo search failed:", err);
	}

	return [];
}

export async function getRealtimeOALeads(companyName: string, companySlug = slugifyCompany(companyName)) {
	const year = new Date().getFullYear();
	const queries = [
		`${companyName} interview experience online assessment ${year} intern reddit`,
		`${companyName} OA experience ${year} SDE intern leetcode discuss`,
		`${companyName} online assessment my experience ${year} intern`,
		`${companyName} coding round interview ${year} intern blind`,
		`${companyName} online assessment questions ${year} intern`,
		`${companyName} OA questions ${year} intern`,
	];
	const leads: OALead[] = [];
	for (const query of queries) {
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
				company_slug: companySlug,
				company_name: companyName,
				query,
				title: result.title,
				url: result.url,
				snippet: result.snippet,
				source_type: sourceType,
				confidence_hint: confidenceHint,
			});
		}
	}
	const seen = new Set<string>();
	return leads.filter((lead) => {
		if (seen.has(lead.url)) return false;
		seen.add(lead.url);
		return true;
	});
}
