import fs from "fs";

async function inspectYahoo() {
	// First fetch Yahoo and save HTML
	const query = "Apple online assessment coding questions 2026 leetcode";
	const url = `https://search.yahoo.com/search?p=${encodeURIComponent(query)}&n=10`;
	const headers = {
		"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
	};

	const res = await fetch(url, { headers });
	const html = await res.text();
	fs.writeFileSync("scratch/yahoo-results.html", html);

	// Let's print out the first 20 href attributes
	const regex = /href="([^"]+)"/g;
	let match;
	const hrefs = [];
	while ((match = regex.exec(html)) !== null) {
		hrefs.push(match[1]);
	}
	console.log(`Total hrefs found: ${hrefs.length}`);
	console.log("First 40 hrefs:");
	console.log(hrefs.slice(0, 40));
}

inspectYahoo().catch(console.error);
