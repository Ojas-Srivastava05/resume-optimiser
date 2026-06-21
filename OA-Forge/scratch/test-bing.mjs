async function testBing() {
	const query = "Apple online assessment coding questions 2026 leetcode";
	const url = `https://www.bing.com/search?q=${encodeURIComponent(query)}`;
	const headers = {
		"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
		"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
		"Accept-Language": "en-US,en;q=0.5",
	};

	console.log(`Fetching Bing search: ${url}...`);
	const res = await fetch(url, { headers });
	const html = await res.text();
	
	const results = [];
	const blocks = html.split(/<li[^>]*class="[^"]*b_algo[^"]*"[^>]*>/g);
	console.log(`Blocks found: ${blocks.length}`);

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

		const titleMatch = block.match(/<h2[^>]*>([\s\S]*?)<\/h2>/);
		let title = "";
		if (titleMatch) {
			title = titleMatch[1].replace(/<[^>]+>/g, "").replace(/\s+/g, " ").trim();
		}

		const snippetMatch = block.match(/<p[^>]*>([\s\S]*?)<\/p>|<div class="b_caption"[^>]*>([\s\S]*?)<\/div>/);
		let snippet = "";
		if (snippetMatch) {
			const rawSnippet = snippetMatch[1] || snippetMatch[2] || "";
			snippet = rawSnippet.replace(/<[^>]+>/g, "").replace(/\s+/g, " ").trim();
		}

		results.push({ title, url: realUrl, snippet });
	}

	console.log(`Parsed ${results.length} results:`);
	console.log(JSON.stringify(results, null, 2));
}

testBing().catch(console.error);
