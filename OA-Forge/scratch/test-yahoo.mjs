async function testYahoo() {
	const query = "Apple online assessment coding questions 2026 leetcode";
	const url = `https://search.yahoo.com/search?p=${encodeURIComponent(query)}&n=10`;
	const headers = {
		"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
		"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
		"Accept-Language": "en-US,en;q=0.9",
		"Connection": "keep-alive",
		"Upgrade-Insecure-Requests": "1"
	};

	console.log(`Fetching Yahoo search: ${url}...`);
	const res = await fetch(url, { headers });
	console.log(`Status: ${res.status} ${res.statusText}`);
	
	const html = await res.text();
	console.log(`HTML length: ${html.length}`);

	// Let's print out all links found in the HTML to see if results are present.
	const regex = /<a[^>]+href="([^"]+)"[^>]*>([\s\S]*?)<\/a>/g;
	let match;
	const links = [];
	while ((match = regex.exec(html)) !== null) {
		const href = match[1];
		const text = match[2].replace(/<[^>]+>/g, "").trim();
		if (href.startsWith("http") && !href.includes("yahoo.com")) {
			links.push({ href, text });
		}
	}

	console.log(`Found ${links.length} external links:`);
	console.log(links.slice(0, 10));
}

testYahoo().catch(console.error);
