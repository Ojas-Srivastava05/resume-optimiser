async function testAsk() {
	const query = "Adobe online assessment coding questions 2026 intern";
	const url = `https://www.ask.com/web?q=${encodeURIComponent(query)}`;
	const headers = {
		"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
	};

	console.log(`Fetching Ask: ${url}`);
	const res = await fetch(url, { headers });
	console.log(`Status: ${res.status} ${res.statusText}`);
	const html = await res.text();
	console.log(`HTML length: ${html.length}`);

	// Look for search result links
	// Ask.com results typically have class="PartialSearchResults-item-title" or similar
	const results = [];
	const regex = /<a[^>]+class="[^"]*result-link[^"]*"[^>]+href="([^"]+)"[^>]*>([\s\S]*?)<\/a>/g;
	let match;
	while ((match = regex.exec(html)) !== null) {
		results.push({
			url: match[1],
			title: match[2].replace(/<[^>]+>/g, "").trim()
		});
	}

	console.log(`Found ${results.length} results:`);
	console.log(results.slice(0, 5));
}

testAsk().catch(console.error);
