import fs from "fs";
import path from "path";

// Load searchBing, searchYahoo, performSearch from scrape-questions.mjs
const content = fs.readFileSync("scripts/scrape-questions.mjs", "utf8");

// We can just define the functions here for easy testing
const FIRECRAWL_KEY = process.env.FIRECRAWL_API_KEY;

async function searchBing(query, count = 10) {
	const url = `https://www.bing.com/search?q=${encodeURIComponent(query)}`;
	const headers = {
		"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
		"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
		"Accept-Language": "en-US,en;q=0.5",
	};

	const res = await fetch(url, { headers });
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

async function searchYahoo(query, count = 10) {
	const url = `https://search.yahoo.com/search?p=${encodeURIComponent(query)}&n=${count}`;
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
			title = titleMatch[1].replace(/<[^>]+>/g, "").trim();
		}

		const snippetMatch = block.match(/class="compText[^>]*>([\s\S]*?)<\/div>/);
		let snippet = "";
		if (snippetMatch) {
			snippet = snippetMatch[1].replace(/<[^>]+>/g, "").trim();
		}

		if (realUrl && (title || snippet)) {
			results.push({ title, url: realUrl, snippet });
		}
	}
	return results;
}

async function performSearch(query, count = 10) {
	console.log("Trying DuckDuckGo...");
	try {
		const url = `https://html.duckduckgo.com/html/?q=${encodeURIComponent(query)}`;
		const headers = {
			"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
			"Accept-Language": "en-US,en;q=0.9"
		};
		const res = await fetch(url, { headers });
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
						.replace(/\s+/g, " ")
						.trim();

					const snippet = snippetHtml
						.replace(/<[^>]+>/g, " ")
						.replace(/\s+/g, " ")
						.trim();

					return { title, url: cleanUrl, snippet };
				})
				.filter((row) => row.title && row.url)
				.slice(0, count);

			if (results.length > 0) {
				console.log(`DuckDuckGo success: ${results.length} results`);
				return results;
			}
		}
		console.warn(`  DuckDuckGo search returned 0 results. Falling back to Bing.`);
	} catch (err) {
		console.warn(`  DuckDuckGo search failed: ${err.message}. Falling back to Bing.`);
	}

	// Try Bing search second
	try {
		console.log("Trying Bing...");
		const bingResults = await searchBing(query, count);
		if (bingResults.length > 0) {
			console.log(`Bing success: ${bingResults.length} results`);
			return bingResults;
		}
		console.warn(`  Bing search returned 0 results. Falling back to Yahoo.`);
	} catch (err) {
		console.warn(`  Bing search failed: ${err.message}. Falling back to Yahoo.`);
	}

	// Try Yahoo search third
	try {
		console.log("Trying Yahoo...");
		const yahooResults = await searchYahoo(query, count);
		if (yahooResults.length > 0) {
			console.log(`Yahoo success: ${yahooResults.length} results`);
			return yahooResults;
		}
		console.warn(`  Yahoo search returned 0 results.`);
	} catch (err) {
		console.warn(`  Yahoo search failed: ${err.message}`);
	}

	return [];
}

async function run() {
	const query = "Adobe online assessment coding questions 2026 intern";
	const results = await performSearch(query, 10);
	console.log("FINAL RESULTS:", JSON.stringify(results, null, 2));
}

run().catch(console.error);
