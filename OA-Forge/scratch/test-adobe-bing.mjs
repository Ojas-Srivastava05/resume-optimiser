async function testAdobeBing() {
	const query = "Adobe online assessment coding questions 2026 intern";
	const url = `https://www.bing.com/search?q=${encodeURIComponent(query)}`;
	const headers = {
		"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
		"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
		"Accept-Language": "en-US,en;q=0.5",
	};

	console.log(`Fetching Bing: ${url}`);
	const res = await fetch(url, { headers });
	const html = await res.text();
	
	const results = [];
	const blocks = html.split(/<li[^>]*class="[^"]*b_algo[^"]*"[^>]*>/g);
	console.log(`Blocks: ${blocks.length}`);

	for (let i = 1; i < blocks.length; i++) {
		const block = blocks[i].split("</li>")[0];
		
		const h2Match = block.match(/<h2[^>]*>([\s\S]*?)<\/h2>/);
		if (!h2Match) continue;
		const h2Content = h2Match[1];
		const hrefMatch = h2Content.match(/href="([^"]+)"/);
		if (!hrefMatch) continue;
		const href = hrefMatch[1];
		const title = h2Content.replace(/<[^>]+>/g, "").trim();

		const snippetMatch = block.match(/<p[^>]*>([\s\S]*?)<\/p>|<div class="b_caption"[^>]*>([\s\S]*?)<\/div>/);
		const rawSnippet = snippetMatch ? (snippetMatch[1] || snippetMatch[2] || "") : "";
		const snippet = rawSnippet.replace(/<[^>]+>/g, "").trim();

		results.push({ title, url: href, snippet });
	}

	console.log(JSON.stringify(results, null, 2));
}

testAdobeBing().catch(console.error);
