import fs from "fs";

function cleanText(text) {
	return text.replace(/<[^>]+>/g, "").replace(/\s+/g, " ").trim();
}

function parseGoogleHtml(html) {
	const results = [];
	
	// Try parsing standard Google result blocks
	// In the standard desktop HTML, each result block often has:
	// a link container: <div class="yuRUbf"><a href="URL"...><h3...>TITLE</h3></a>
	// a description container: <div class="VwiC3b...">...</div>
	// Let's find matches for href and title first.
	// Google link block regex:
	const blockRegex = /<div class="[a-zA-Z0-9_-]*g[a-zA-Z0-9_-]*"[\s\S]*?<a[^>]+href="([^"]+)"[^>]*>[\s\S]*?<h3[^>]*>([\s\S]*?)<\/h3>[\s\S]*?<div class="[a-zA-Z0-9_-]*(?:VwiC3b|MUwGbd|yDcjvd)[a-zA-Z0-9_-]*"[^>]*>([\s\S]*?)<\/div>/g;
	
	let match;
	while ((match = blockRegex.exec(html)) !== null) {
		const url = match[1];
		const title = cleanText(match[2]);
		const snippet = cleanText(match[3]);
		results.push({ title, url, snippet });
	}
	
	// If the specific regex failed, let's try a fallback: search for any <a href="..."> with an <h3> inside a result container,
	// and a snippet container near it.
	if (results.length === 0) {
		const genericLinkRegex = /<a[^>]+href="([^"]+)"[^>]*>[\s\S]*?<h3[^>]*>([\s\S]*?)<\/h3>/g;
		let linkMatch;
		while ((linkMatch = genericLinkRegex.exec(html)) !== null) {
			const url = linkMatch[1];
			// Ignore google internal links
			if (url.includes("google.com/") || url.startsWith("/")) continue;
			const title = cleanText(linkMatch[2]);
			
			// Let's find a snippet after this link in the HTML
			const remainingHtml = html.substring(genericLinkRegex.lastIndex, genericLinkRegex.lastIndex + 1500);
			const snippetMatch = remainingHtml.match(/<div class="[a-zA-Z0-9_-]*(?:VwiC3b|MUwGbd|yDcjvd)[a-zA-Z0-9_-]*"[^>]*>([\s\S]*?)<\/div>/);
			const snippet = snippetMatch ? cleanText(snippetMatch[1]) : "";
			
			results.push({ title, url, snippet });
		}
	}
	
	return results;
}

const html = fs.readFileSync("scratch/google-results.html", "utf8");
const parsed = parseGoogleHtml(html);
console.log(`Parsed ${parsed.length} results:`);
console.log(JSON.stringify(parsed, null, 2));
