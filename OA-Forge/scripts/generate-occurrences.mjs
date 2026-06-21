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

const rows = [];
for (let ci = 0; ci < companies.length; ci++) {
	const c = companies[ci];
	if (!c.slug || !c.name) continue;
	// Rotate question order per company for variety
	const offset = ci % slugs.length;
	for (let qi = 0; qi < slugs.length; qi++) {
		const slug = slugs[(offset + qi) % slugs.length];
		const tier = qi < 4 ? "B" : "C"; // first 4 per company = tier B for strict pool
		rows.push([
			c.slug,
			slug,
			year,
			"SDE Intern",
			"oa",
			tier,
			`OA practice pool for ${c.name}. Tier B = common intern OA patterns.`,
			"",
		]);
	}
}

const csv = [headers.join(","), ...rows.map((r) => r.map(csvEscape).join(","))].join("\n");
fs.writeFileSync(outCsv, csv);
console.log(`Wrote ${rows.length} occurrences for ${companies.length} companies (${slugs.length} questions each).`);
