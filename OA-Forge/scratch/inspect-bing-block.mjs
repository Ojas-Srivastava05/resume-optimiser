import fs from "fs";

const html = fs.readFileSync("scratch/bing-results.html", "utf8");
const match = html.match(/<li[^>]*class="[^"]*b_algo[^"]*"[^>]*>([\s\S]*?)<\/li>/);
if (match) {
	console.log("First block HTML:");
	console.log(match[1]);
} else {
	console.log("No block found");
}
