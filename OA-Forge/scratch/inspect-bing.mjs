import fs from "fs";

async function inspectBing() {
	// First fetch Bing and save HTML
	const query = "Apple online assessment coding questions 2026 leetcode";
	const url = `https://www.bing.com/search?q=${encodeURIComponent(query)}`;
	const headers = {
		"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
		"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
		"Accept-Language": "en-US,en;q=0.5",
	};

	const res = await fetch(url, { headers });
	const html = await res.text();
	fs.writeFileSync("scratch/bing-results.html", html);

	// Let's print out all <h2> tags
	const h2Regex = /<h2[^>]*>([\s\S]*?)<\/h2>/g;
	let match;
	console.log("H2 tags:");
	while ((match = h2Regex.exec(html)) !== null) {
		console.log(`- ${match[1].replace(/<[^>]+>/g, "").trim()}`);
	}

	// Print some divs with typical result classes or text
	const bAlgoRegex = /<li[^>]*class="[^"]*b_algo[^"]*"[^>]*>([\s\S]*?)<\/li>/g;
	let count = 0;
	while ((match = bAlgoRegex.exec(html)) !== null) {
		count++;
	}
	console.log(`\nFound b_algo class matches: ${count}`);
}

inspectBing().catch(console.error);
