async function testDdgLite() {
	const query = "Adobe online assessment coding questions 2026 intern";
	const url = "https://lite.duckduckgo.com/lite/";
	
	console.log(`Fetching DDG Lite POST: ${url}`);
	const res = await fetch(url, {
		method: "POST",
		headers: {
			"Content-Type": "application/x-www-form-urlencoded",
			"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
		},
		body: `q=${encodeURIComponent(query)}`
	});
	
	console.log(`Status: ${res.status} ${res.statusText}`);
	const html = await res.text();
	console.log(`HTML length: ${html.length}`);

	// DDG Lite results use tables and td tags. Let's see if we can find result-link classes or normal table structure
	// Each result is typically in a table row with class="result-link" or contains a form or simple links.
	const results = [];
	
	// Let's match all standard links
	const regex = /<a[^>]+href="([^"]+)"[^>]*>([\s\S]*?)<\/a>/g;
	const hrefs = [];
	let match;
	while ((match = regex.exec(html)) !== null) {
		const href = match[1];
		const text = match[2].replace(/<[^>]+>/g, "").trim();
		if (href.startsWith("http") && !href.includes("duckduckgo.com")) {
			results.push({ url: href, title: text });
		}
	}

	console.log(`Found ${results.length} external results:`);
	console.log(results.slice(0, 10));
}

testDdgLite().catch(console.error);
