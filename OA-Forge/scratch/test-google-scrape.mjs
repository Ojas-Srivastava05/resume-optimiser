async function testGoogleScrape() {
	const query = "Apple online assessment coding questions 2026 leetcode";
	const url = `https://www.google.com/search?q=${encodeURIComponent(query)}&num=10`;
	const headers = {
		"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
		"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
		"Accept-Language": "en-US,en;q=0.5",
	};

	console.log(`Fetching Google search: ${url}...`);
	const res = await fetch(url, { headers });
	if (!res.ok) {
		console.error(`Google search failed with status: ${res.status}`);
		return;
	}

	const html = await res.text();
	console.log(`HTML length: ${html.length}`);
	
	// Write HTML to temporary file to inspect
	const fs = await import("fs");
	fs.writeFileSync("scratch/google-results.html", html);
	console.log("Wrote HTML to scratch/google-results.html");
}

testGoogleScrape().catch(console.error);
