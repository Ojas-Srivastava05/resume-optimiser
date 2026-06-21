import fs from "fs";
import path from "path";

// Load .env.local
const envPath = path.join(process.cwd(), ".env.local");
if (fs.existsSync(envPath)) {
	for (const line of fs.readFileSync(envPath, "utf8").split(/\r?\n/)) {
		const match = line.match(/^([A-Z0-9_]+)=(.*)$/);
		if (match && !process.env[match[1]]) process.env[match[1]] = match[2].trim();
	}
}

const FIRECRAWL_KEY = process.env.FIRECRAWL_API_KEY;
console.log(`Using Firecrawl key: ${FIRECRAWL_KEY ? FIRECRAWL_KEY.substring(0, 10) + "..." : "undefined"}`);

async function testSearch() {
	const query = "Apple online assessment coding questions 2026 leetcode";
	const res = await fetch("https://api.firecrawl.dev/v1/search", {
		method: "POST",
		headers: {
			"Content-Type": "application/json",
			"Authorization": `Bearer ${FIRECRAWL_KEY}`
		},
		body: JSON.stringify({
			query,
			limit: 5
		})
	});

	console.log(`Status: ${res.status} ${res.statusText}`);
	const text = await res.text();
	console.log(`Response body: ${text}`);
}

testSearch().catch(console.error);
