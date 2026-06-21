async function testBraveSearch() {
	const query = "Adobe online assessment coding questions 2026 intern";
	const url = `https://search.brave.com/search?q=${encodeURIComponent(query)}`;
	const headers = {
		"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
		"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
		"Accept-Language": "en-US,en;q=0.5",
	};

	console.log(`Fetching Brave Search: ${url}`);
	const res = await fetch(url, { headers });
	console.log(`Status: ${res.status} ${res.statusText}`);
	const html = await res.text();
	console.log(`HTML length: ${html.length}`);

	// Brave results typically have class="svelte-..." or search result containers
	// Let's look for result titles and urls
	const results = [];
	const regex = /<a[^>]+href="([^"]+)"[^>]*class="[^"]*svelte-[^"]*"[^>]*>([\s\S]*?)<\/a>/g;
	// Or a more generic href extractor
	const hrefRegex = /href="([^"]+)"/g;
	const hrefs = [];
	let match;
	while ((match = hrefRegex.exec(html)) !== null) {
		hrefs.push(match[1]);
	}
	console.log(`Found ${hrefs.length} hrefs total`);
	console.log(hrefs.filter(h => h.startsWith("http") && !h.includes("brave.com")).slice(0, 10));
}

testBraveSearch().catch(console.error);
