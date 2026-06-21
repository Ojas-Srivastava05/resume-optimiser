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

await upsertBatched(
	"oa_questions",
	parseCsv("questions.csv").map((q) => ({
		slug: q.slug,
		title: q.title,
		difficulty: q.difficulty,
		category: q.category,
		question_order: Number(q.question_order),
	})),
	"slug"
);

const { data: questionRows, error: questionError } = await supabase.from("oa_questions").select("id, slug");
if (questionError) throw questionError;
const questionBySlug = new Map(questionRows.map((q) => [q.slug, q.id]));

for (const c of companies) {
	const company_id = companyBySlug.get(c.slug);
	if (!company_id) continue;
	const { data: role, error: roleError } = await supabase
		.from("oa_roles")
		.upsert({ company_id, title: c.target_role || "SDE Intern", level: "intern" }, { onConflict: "company_id,title" })
		.select("id")
		.single();
	if (roleError) throw roleError;

	const templatePayload = {
		company_id,
		role_id: role.id,
		name: `${c.name} ${c.target_role || "SDE Intern"} Mock OA`,
		duration_minutes: Number(c.default_duration_minutes || 90),
		num_questions: Number(c.default_num_questions || 2),
		strict_tiers: ["A", "B"],
	};
	const { data: existingTemplate } = await supabase
		.from("oa_templates")
		.select("id")
		.eq("company_id", company_id)
		.eq("name", templatePayload.name)
		.maybeSingle();

	if (existingTemplate) {
		await supabase.from("oa_templates").update(templatePayload).eq("id", existingTemplate.id);
	} else {
		await supabase.from("oa_templates").insert(templatePayload);
	}
}

const occurrences = parseCsv("occurrences.csv")
	.map((o) => ({
		company_id: companyBySlug.get(o.company_slug),
		question_id: questionBySlug.get(o.question_slug),
		year: Number(o.year),
		season: o.season,
		round_type: o.round_type || "oa",
		confidence_tier: o.confidence_tier,
		source_notes: o.source_notes,
		source_url: o.source_url || null,
	}))
	.filter((o) => o.company_id && o.question_id);

console.log("Inserting occurrences...");
for (let i = 0; i < occurrences.length; i += BATCH) {
	const chunk = occurrences.slice(i, i + BATCH);
	const { error } = await supabase.from("oa_question_occurrences").upsert(chunk, {
		onConflict: "question_id,company_id,year,season,round_type",
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
