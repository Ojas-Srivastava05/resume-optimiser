import fs from "fs";

const html = fs.readFileSync("scratch/google-results.html", "utf8");

// Let's print all <h3> tag texts
const h3Regex = /<h3[^>]*>([\s\S]*?)<\/h3>/g;
let match;
console.log("H3 tags:");
while ((match = h3Regex.exec(html)) !== null) {
	console.log(`- ${match[1].replace(/<[^>]+>/g, "").trim()}`);
}

// Let's print some links with h3
console.log("\nLinks with H3:");
const linkH3Regex = /<a[^>]+href="([^"]+)"[^>]*>[\s\S]*?<h3[^>]*>([\s\S]*?)<\/h3>/g;
while ((match = linkH3Regex.exec(html)) !== null) {
	console.log(`URL: ${match[1]}\nTitle: ${match[2].replace(/<[^>]+>/g, "").trim()}\n`);
}
