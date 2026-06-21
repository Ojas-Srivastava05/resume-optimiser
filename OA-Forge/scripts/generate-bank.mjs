/**
 * Generates questions.csv (20 OA classics) + occurrences.csv (20 per company)
 * Run: node scripts/generate-bank.mjs
 */
import fs from "fs";
import path from "path";

const root = process.cwd();
const scoutCsv = path.join(root, "..", "internship-scout", "data", "all_companies.csv");
const dataDir = path.join(root, "data");

const QUESTIONS = [
	{ slug: "two-sum", title: "Two Sum", difficulty: "Easy", category: "arrays-hashmap", order: 1 },
	{ slug: "valid-parentheses", title: "Valid Parentheses", difficulty: "Easy", category: "stack", order: 2 },
	{ slug: "merge-sorted-arrays", title: "Merge Sorted Array", difficulty: "Easy", category: "two-pointers", order: 3 },
	{ slug: "maximum-subarray", title: "Maximum Subarray", difficulty: "Medium", category: "dynamic-programming", order: 4 },
	{ slug: "jump-game", title: "Jump Game", difficulty: "Medium", category: "greedy", order: 5 },
	{ slug: "search-a-2d-matrix", title: "Search a 2D Matrix", difficulty: "Medium", category: "binary-search", order: 6 },
	{ slug: "number-of-islands", title: "Number of Islands", difficulty: "Medium", category: "graph-bfs-dfs", order: 7 },
	{ slug: "reverse-linked-list", title: "Reverse Linked List", difficulty: "Easy", category: "linked-list", order: 8 },
	{ slug: "best-time-to-buy-sell-stock", title: "Best Time to Buy and Sell Stock", difficulty: "Easy", category: "arrays", order: 9 },
	{ slug: "contains-duplicate", title: "Contains Duplicate", difficulty: "Easy", category: "hashing", order: 10 },
	{ slug: "climbing-stairs", title: "Climbing Stairs", difficulty: "Easy", category: "dynamic-programming", order: 11 },
	{ slug: "house-robber", title: "House Robber", difficulty: "Medium", category: "dynamic-programming", order: 12 },
	{ slug: "longest-substring-without-repeating", title: "Longest Substring Without Repeating Characters", difficulty: "Medium", category: "sliding-window", order: 13 },
	{ slug: "single-number", title: "Single Number", difficulty: "Easy", category: "bit-manipulation", order: 14 },
	{ slug: "move-zeroes", title: "Move Zeroes", difficulty: "Easy", category: "two-pointers", order: 15 },
	{ slug: "binary-search", title: "Binary Search", difficulty: "Easy", category: "binary-search", order: 16 },
	{ slug: "product-of-array-except-self", title: "Product of Array Except Self", difficulty: "Medium", category: "prefix-sum", order: 17 },
	{ slug: "rotate-array", title: "Rotate Array", difficulty: "Medium", category: "arrays", order: 18 },
	{ slug: "intersection-of-two-arrays-ii", title: "Intersection of Two Arrays II", difficulty: "Easy", category: "hashing", order: 19 },
	{ slug: "palindrome-number", title: "Palindrome Number", difficulty: "Easy", category: "math", order: 20 },
];

// OA-style pairs (both questions selected together when mock picks a pair)
const PAIRS = [
	["two-sum", "valid-parentheses"],
	["maximum-subarray", "merge-sorted-arrays"],
	["jump-game", "search-a-2d-matrix"],
	["number-of-islands", "reverse-linked-list"],
	["best-time-to-buy-sell-stock", "contains-duplicate"],
	["climbing-stairs", "house-robber"],
	["longest-substring-without-repeating", "single-number"],
	["move-zeroes", "binary-search"],
	["product-of-array-except-self", "rotate-array"],
	["intersection-of-two-arrays-ii", "palindrome-number"],
];

function slugify(name) {
	return name
		.toLowerCase()
		.replace(/&/g, " and ")
		.replace(/[^a-z0-9]+/g, "-")
		.replace(/^-+|-+$/g, "")
		.slice(0, 80);
}

function parseCsv(content) {
	const lines = content.trim().split("\n");
	const headers = lines[0].split(",").map((h) => h.trim());
	return lines.slice(1).map((line) => {
		const values = line.split(",").map((v) => v.trim());
		return Object.fromEntries(headers.map((h, i) => [h, values[i] || ""]));
	});
}

function csvEscape(v) {
	const s = String(v ?? "");
	if (s.includes(",") || s.includes('"') || s.includes("\n")) return `"${s.replace(/"/g, '""')}"`;
	return s;
}

function hash(s) {
	let h = 0;
	for (let i = 0; i < s.length; i++) h = (h * 31 + s.charCodeAt(i)) >>> 0;
	return h;
}

// questions.csv
const qCsv = [
	"slug,title,difficulty,category,question_order",
	...QUESTIONS.map((q) => [q.slug, q.title, q.difficulty, q.category, q.order].join(",")),
].join("\n");
fs.writeFileSync(path.join(dataDir, "questions.csv"), qCsv);

// pairs.csv
const pairCsv = [
	"pair_id,question_slug_a,question_slug_b",
	...PAIRS.map(([a, b], i) => `${i + 1},${a},${b}`),
].join("\n");
fs.writeFileSync(path.join(dataDir, "pairs.csv"), pairCsv);

// companies from scout
if (!fs.existsSync(scoutCsv)) {
	console.error("Missing", scoutCsv);
	process.exit(1);
}
const scout = parseCsv(fs.readFileSync(scoutCsv, "utf8"));
const companies = scout
	.filter((r) => r.Company && !r.Company.includes("http") && !r.Company.startsWith("<"))
	.map((r) => ({ slug: slugify(r.Company), name: r.Company }));

// companies.csv (for Supabase seed)
const companiesCsv = [
	"slug,name,default_duration_minutes,default_num_questions,target_role",
	...companies.map((c) => `${c.slug},${csvEscape(c.name)},90,2,SDE Intern`),
].join("\n");
fs.writeFileSync(path.join(dataDir, "companies.csv"), companiesCsv);

// pair lookup
const pairBySlug = new Map();
for (const [a, b] of PAIRS) {
	pairBySlug.set(a, b);
	pairBySlug.set(b, a);
}

// Keep existing occurrences.csv if it exists, otherwise write empty header
const occPath = path.join(dataDir, "occurrences.csv");
if (!fs.existsSync(occPath)) {
	fs.writeFileSync(occPath, "company_slug,question_slug,year,season,round_type,confidence_tier,pair_id,source_notes,source_url\n");
}
console.log(`Generated ${QUESTIONS.length} questions, ${companies.length} companies.`);
