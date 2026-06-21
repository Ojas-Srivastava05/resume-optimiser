/**
 * Generates data/occurrences.csv — 20 questions per company from all_companies.csv.
 * Run: node scripts/generate-occurrences.mjs
 */
import fs from "fs";
import path from "path";

const root = process.cwd();
const scoutCsv = path.join(root, "..", "internship-scout", "data", "all_companies.csv");
const questionsCsv = path.join(root, "data", "questions.csv");
const outCsv = path.join(root, "data", "occurrences.csv");

function parseCsv(text) {
	const rows = [];
	let row = [];
	let cell = "";
	let quoted = false;
	for (let i = 0; i < text.length; i++) {
		const ch = text[i];
		const next = text[i + 1];
		if (quoted && ch === '"' && next === '"') {
			cell += '"';
			i++;
		} else if (ch === '"') quoted = !quoted;
		else if (!quoted && ch === ",") {
			row.push(cell);
			cell = "";
		} else if (!quoted && (ch === "\n" || ch === "\r")) {
			if (ch === "\r" && next === "\n") i++;
			row.push(cell);
			rows.push(row);
			row = [];
			cell = "";
		} else cell += ch;
	}
	row.push(cell);
	rows.push(row);
	const [headers, ...body] = rows;
	return body.map((r) => Object.fromEntries(headers.map((h, i) => [h, r[i] ?? ""])));
}

function slugify(name) {
	return name
		.toLowerCase()
		.replace(/&/g, " and ")
		.replace(/[^a-z0-9]+/g, "-")
		.replace(/^-+|-+$/g, "")
		.slice(0, 80);
}

function csvEscape(v) {
	const s = String(v ?? "");
	if (s.includes(",") || s.includes('"') || s.includes("\n")) return `"${s.replace(/"/g, '""')}"`;
	return s;
}

const questions = parseCsv(fs.readFileSync(questionsCsv, "utf8"));
const slugs = questions.map((q) => q.slug);
const companies = parseCsv(fs.readFileSync(scoutCsv, "utf8")).map((r) => ({
	slug: slugify(r.Company),
	name: r.Company,
}));

const year = new Date().getFullYear();
const headers = [
	"company_slug",
	"question_slug",
	"year",
	"season",
	"round_type",
	"confidence_tier",
	"source_notes",
	"source_url",
];

// Keep existing occurrences.csv if it exists, otherwise write empty header
if (!fs.existsSync(outCsv)) {
	fs.writeFileSync(outCsv, "company_slug,question_slug,year,season,round_type,confidence_tier,pair_id,source_notes,source_url\n");
}
console.log("generate-occurrences.mjs is deprecated. Occurrences are now ingested from the GitHub repository and scraped-questions.csv.");
