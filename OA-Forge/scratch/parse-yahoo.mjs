import fs from "fs";

function stripHtml(html) {
	return html
		.replace(/<script[\s\S]*?<\/script>/gi, "")
		.replace(/<style[\s\S]*?<\/style>/gi, "")
		.replace(/<[^>]+>/g, " ")
		.replace(/&quot;/g, '"')
		.replace(/&#x27;/g, "'")
		.replace(/&amp;/g, "&")
		.replace(/\s+/g, " ")
		.trim();
}

function extractRealUrl(yahooUrl) {
	const ruMatch = yahooUrl.match(/\/RU=([^/]+)/);
	if (ruMatch) {
		try {
			return decodeURIComponent(ruMatch[1]);
		} catch (e) {
			return yahooUrl;
		}
	}
	return yahooUrl;
}

function parseYahoo(html) {
	const results = [];
	
	// Yahoo result container block matches
	// We can split by <div class="dd ... algo algo-sr
	const blocks = html.split(/<div[^>]*class="[^"]*algo-sr[^"]*"/g);
	if (blocks.length <= 1) {
		// Fallback to splitting by class="compTitle"
		return parseYahooFallback(html);
	}

	for (let i = 1; i < blocks.length; i++) {
		const block = blocks[i];
		
		// Find first href after splitting
		const hrefMatch = block.match(/href="([^"]+)"/);
		const href = hrefMatch ? hrefMatch[1] : "";
		const realUrl = extractRealUrl(href);

		// Find title
		const titleMatch = block.match(/class="title[^>]*>([\s\S]*?)<\/h3>/);
		let title = "";
		if (titleMatch) {
			title = stripHtml(titleMatch[1]);
		}

		// Find snippet
		const snippetMatch = block.match(/class="compText[^>]*>([\s\S]*?)<\/div>/);
		let snippet = "";
		if (snippetMatch) {
			snippet = stripHtml(snippetMatch[1]);
		}

		if (realUrl && (title || snippet)) {
			results.push({
				title,
				url: realUrl,
				snippet
			});
		}
	}

	return results;
}

function parseYahooFallback(html) {
	const results = [];
	const regex = /<h3[^>]*class="title[^>]*>([\s\S]*?)<\/h3>[\s\S]*?<div[^>]*class="compText[^>]*>([\s\S]*?)<\/div>/g;
	// Let's also extract URLs from the block
	// For simplicity, we can regex match URLs and titles/snippets
	return results;
}

const html = fs.readFileSync("scratch/yahoo-results.html", "utf8");
const parsed = parseYahoo(html);
console.log(`Parsed ${parsed.length} results:`);
console.log(JSON.stringify(parsed, null, 2));
