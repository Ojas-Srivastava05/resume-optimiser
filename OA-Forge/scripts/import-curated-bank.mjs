import { createClient } from "@supabase/supabase-js";
import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const envPath = path.join(root, ".env.local");
if (fs.existsSync(envPath)) {
	for (const line of fs.readFileSync(envPath, "utf8").split(/\r?\n/)) {
		const match = line.match(/^([A-Za-z0-9_]+)=(.*)$/);
		if (match && !process.env[match[1]]) process.env[match[1]] = match[2];
	}
}

const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
const key = process.env.SUPABASE_SERVICE_ROLE_KEY;
if (!url || !key) {
	throw new Error(
		"Missing NEXT_PUBLIC_SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY. The anon key cannot seed OA Forge because RLS blocks writes."
	);
}

const supabase = createClient(url, key);
const BATCH = 500;

function slugify(name) {
	return name
		.toLowerCase()
		.replace(/&/g, " and ")
		.replace(/[^a-z0-9]+/g, "-")
		.replace(/^-+|-+$/g, "")
		.slice(0, 80);
}

function loadAllCompanies() {
	const configured = parseCsv("companies.csv");
	const scoutPath = path.join(root, "..", "internship-scout", "data", "all_companies.csv");
	const scout = fs.existsSync(scoutPath)
		? parseCsvFile(scoutPath).map((row) => ({
				slug: slugify(row.Company),
				name: row.Company,
				default_duration_minutes: "90",
				default_num_questions: "2",
				target_role: "SDE Intern",
			}))
		: [];
	const bySlug = new Map(scout.map((c) => [c.slug, c]));
	for (const c of configured) bySlug.set(c.slug, c);
	return Array.from(bySlug.values()).filter((c) => c.slug && c.name);
}

function parseCsvFile(filePath) {
	const text = fs.readFileSync(filePath, "utf8").trim();
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

function parseCsv(file) {
	const text = fs.readFileSync(path.join(root, "data", file), "utf8").trim();
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

async function upsertBatched(table, rows, onConflict) {
	for (let i = 0; i < rows.length; i += BATCH) {
		const chunk = rows.slice(i, i + BATCH);
		const { error } = await supabase.from(table).upsert(chunk, { onConflict });
		if (error) throw error;
		process.stdout.write(`  ${table}: ${Math.min(i + BATCH, rows.length)}/${rows.length}\r`);
	}
	console.log(`  ${table}: ${rows.length} rows`);
}

const companies = loadAllCompanies();
await upsertBatched(
	"oa_companies",
	companies.map((c) => ({ slug: c.slug, name: c.name })),
	"slug"
);

const { data: companyRows, error: companyError } = await supabase.from("oa_companies").select("id, slug");
if (companyError) throw companyError;
const companyBySlug = new Map(companyRows.map((c) => [c.slug, c.id]));

// Load curated questions
const curatedQuestions = parseCsv("questions.csv").map((q) => ({
	slug: q.slug,
	title: q.title,
	difficulty: q.difficulty,
	category: q.category,
	question_order: Number(q.question_order),
}));

// Load scraped questions if they exist
let scrapedQuestions = [];
const scrapedPath = path.join(root, "data", "scraped-questions.csv");
if (fs.existsSync(scrapedPath)) {
	try {
		scrapedQuestions = parseCsv("scraped-questions.csv");
	} catch (err) {
		console.warn("Could not read scraped-questions.csv:", err.message);
	}
}

const questionsMap = new Map(curatedQuestions.map((q) => [q.slug, q]));
scrapedQuestions.forEach((sq, idx) => {
	if (sq.slug && !questionsMap.has(sq.slug)) {
		questionsMap.set(sq.slug, {
			slug: sq.slug,
			title: sq.title || sq.slug,
			difficulty: sq.difficulty || "Medium",
			category: sq.category || "arrays",
			question_order: 1000 + idx,
		});
	}
});

const allQuestionsToInsert = Array.from(questionsMap.values());

await upsertBatched("oa_questions", allQuestionsToInsert, "slug");

const { data: questionRows, error: questionError } = await supabase.from("oa_questions").select("id, slug");
if (questionError) throw questionError;
const questionBySlug = new Map(questionRows.map((q) => [q.slug, q.id]));

console.log("Upserting roles in batches...");
const rolesToUpsert = companies.map((c) => ({
	company_id: companyBySlug.get(c.slug),
	title: c.target_role || "SDE Intern",
	level: "intern",
})).filter((r) => r.company_id);

const { data: upsertedRoles, error: rolesError } = await supabase
	.from("oa_roles")
	.upsert(rolesToUpsert, { onConflict: "company_id,title" })
	.select("id, company_id, title");
if (rolesError) throw rolesError;

console.log(`  upserted ${upsertedRoles.length} roles`);

console.log("Fetching existing templates...");
const { data: existingTemplates, error: templatesError } = await supabase
	.from("oa_templates")
	.select("id, company_id, name");
if (templatesError) throw templatesError;

const existingTemplatesMap = new Map(
	existingTemplates.map((t) => [`${t.company_id}-${t.name}`, t.id])
);

console.log("Upserting templates in batches...");
const templatesToInsert = [];
const templatesToUpdate = [];
const roleByCompanyAndTitle = new Map(
	upsertedRoles.map((r) => [`${r.company_id}-${r.title}`, r.id])
);

for (const c of companies) {
	const company_id = companyBySlug.get(c.slug);
	if (!company_id) continue;
	const role_id = roleByCompanyAndTitle.get(`${company_id}-${c.target_role || "SDE Intern"}`);
	if (!role_id) continue;

	const name = `${c.name} ${c.target_role || "SDE Intern"} Mock OA`;
	const existingId = existingTemplatesMap.get(`${company_id}-${name}`);

	const payload = {
		company_id,
		role_id,
		name,
		duration_minutes: Number(c.default_duration_minutes || 90),
		num_questions: Number(c.default_num_questions || 2),
		strict_tiers: ["A", "B"],
	};

	if (existingId) {
		templatesToUpdate.push({ id: existingId, ...payload });
	} else {
		templatesToInsert.push(payload);
	}
}

if (templatesToInsert.length > 0) {
	for (let i = 0; i < templatesToInsert.length; i += BATCH) {
		const chunk = templatesToInsert.slice(i, i + BATCH);
		const { error: insertError } = await supabase
			.from("oa_templates")
			.insert(chunk);
		if (insertError) throw insertError;
		process.stdout.write(`  templates insert: ${Math.min(i + BATCH, templatesToInsert.length)}/${templatesToInsert.length}\r`);
	}
	console.log(`  templates insert: ${templatesToInsert.length} rows`);
}

if (templatesToUpdate.length > 0) {
	for (let i = 0; i < templatesToUpdate.length; i += BATCH) {
		const chunk = templatesToUpdate.slice(i, i + BATCH);
		const { error: updateError } = await supabase
			.from("oa_templates")
			.upsert(chunk, { onConflict: "id" });
		if (updateError) throw updateError;
		process.stdout.write(`  templates update: ${Math.min(i + BATCH, templatesToUpdate.length)}/${templatesToUpdate.length}\r`);
	}
	console.log(`  templates update: ${templatesToUpdate.length} rows`);
}

const curatedOccurrences = parseCsv("occurrences.csv")
	.map((o) => ({
		company_id: companyBySlug.get(o.company_slug),
		question_id: questionBySlug.get(o.question_slug),
		role_id: null,
		year: Number(o.year),
		season: o.season,
		round_type: o.round_type || "oa",
		confidence_tier: o.confidence_tier,
		source_notes: o.source_notes,
		source_url: o.source_url || null,
	}))
	.filter((o) => o.company_id && o.question_id);

const scrapedOccurrences = scrapedQuestions
	.map((o) => ({
		company_id: companyBySlug.get(o.company_slug),
		question_id: questionBySlug.get(o.slug),
		role_id: null,
		year: Number(o.year || new Date().getFullYear()),
		season: "Intern",
		round_type: "oa",
		confidence_tier: o.confidence_tier || "C",
		source_notes: `Scraped lead: ${o.snippet || ""}`.substring(0, 500),
		source_url: o.source_url || null,
	}))
	.filter((o) => o.company_id && o.question_id);

const allOccurrencesMap = new Map();
curatedOccurrences.forEach((o) => {
	const key = `${o.question_id}-${o.company_id}-${o.year}-${o.season}-${o.round_type}`;
	allOccurrencesMap.set(key, o);
});
scrapedOccurrences.forEach((o) => {
	const key = `${o.question_id}-${o.company_id}-${o.year}-${o.season}-${o.round_type}`;
	if (!allOccurrencesMap.has(key)) {
		allOccurrencesMap.set(key, o);
	}
});

const occurrences = Array.from(allOccurrencesMap.values());

console.log("Inserting occurrences...");
for (let i = 0; i < occurrences.length; i += BATCH) {
	const chunk = occurrences.slice(i, i + BATCH);
	const { error } = await supabase.from("oa_question_occurrences").upsert(chunk, {
		onConflict: "question_id,company_id,role_id,year,season,round_type",
		ignoreDuplicates: true,
	});
	if (error) throw error;
	process.stdout.write(`  occurrences: ${Math.min(i + BATCH, occurrences.length)}/${occurrences.length}\r`);
}
console.log(`  occurrences: ${occurrences.length} rows`);

const tests = parseCsv("test-cases.csv")
	.map((t) => ({
		question_id: questionBySlug.get(t.question_slug),
		input_text: t.input_text,
		expected_output: t.expected_output,
		is_sample: t.is_sample === "true",
		test_order: Number(t.test_order),
	}))
	.filter((t) => t.question_id);

for (const id of new Set(tests.map((t) => t.question_id))) {
	await supabase.from("oa_test_cases").delete().eq("question_id", id);
}
for (let i = 0; i < tests.length; i += BATCH) {
	const { error } = await supabase.from("oa_test_cases").insert(tests.slice(i, i + BATCH));
	if (error) throw error;
}
console.log(`  oa_test_cases: ${tests.length} rows`);

console.log(`Done: ${companies.length} companies, ${occurrences.length} occurrences, ${tests.length} tests.`);
