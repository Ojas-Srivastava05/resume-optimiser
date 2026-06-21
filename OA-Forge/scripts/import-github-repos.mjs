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
		"Missing NEXT_PUBLIC_SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY. Service role key is required to bypass RLS."
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

function parseCsvContent(text) {
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
	if (!headers) return [];
	const cleanHeaders = headers.map(h => h.trim().replace(/^"/, "").replace(/"$/, ""));
	return body
		.filter(r => r.length > 0 && r.some(c => c.trim() !== ""))
		.map((r) => Object.fromEntries(cleanHeaders.map((h, i) => [h, r[i] ?? ""])));
}

function getCategoryFromTags(tags) {
	if (!tags || tags.length === 0) return "arrays";
	const t = tags.join(" ").toLowerCase();
	if (t.includes("linked list")) return "linked-list";
	if (t.includes("binary tree") || t.includes("binary search tree") || t.includes("tree")) return "trees";
	if (t.includes("graph") || t.includes("depth-first search") || t.includes("breadth-first search") || t.includes("shortest path")) return "graphs";
	if (t.includes("dynamic programming")) return "dynamic-programming";
	if (t.includes("sorting")) return "sorting";
	if (t.includes("hash table") || t.includes("hash map") || t.includes("trie")) return "hashing";
	if (t.includes("stack") || t.includes("queue") || t.includes("monotonic stack")) return "stacks-queues";
	if (t.includes("backtracking") || t.includes("recursion")) return "recursion";
	if (t.includes("greedy")) return "greedy";
	if (t.includes("binary search")) return "binary-search";
	if (t.includes("bit manipulation")) return "bit-manipulation";
	if (t.includes("string")) return "strings";
	if (t.includes("math") || t.includes("geometry") || t.includes("number theory") || t.includes("combinatorics")) return "math";
	return "arrays";
}

async function upsertBatched(table, rows, onConflict) {
	for (let i = 0; i < rows.length; i += BATCH) {
		const chunk = rows.slice(i, i + BATCH);
		const { error } = await supabase.from(table).upsert(chunk, { onConflict });
		if (error) {
			console.error(`Error upserting into ${table}:`, error);
			throw error;
		}
		process.stdout.write(`  ${table}: ${Math.min(i + BATCH, rows.length)}/${rows.length}\r`);
	}
	console.log(`  ${table}: ${rows.length} rows`);
}

async function runImport() {
	console.log("Loading doocs/leetcode metadata database...");
	const doocsPath = path.join(root, "scratch", "git-repos", "leetcode", "solution", "result.json");
	if (!fs.existsSync(doocsPath)) {
		throw new Error(`Could not find doocs/leetcode result.json at: ${doocsPath}`);
	}
	const doocsData = JSON.parse(fs.readFileSync(doocsPath, "utf8"));
	
	// Map of slug -> question details
	const doocsMap = new Map();
	Object.values(doocsData).forEach((q) => {
		if (q.question_title_slug) {
			doocsMap.set(q.question_title_slug, q);
		}
	});
	console.log(`Loaded ${doocsMap.size} questions from doocs/leetcode index.`);

	// Load existing companies from Supabase
	console.log("Fetching existing companies from Supabase...");
	const { data: existingCompanies, error: compErr } = await supabase.from("oa_companies").select("slug, name");
	if (compErr) throw compErr;
	const companyBySlug = new Map(existingCompanies.map((c) => [c.slug, c.name]));
	console.log(`Supabase currently has ${companyBySlug.size} companies.`);

	// Scan company directories
	const repoPath = path.join(root, "scratch", "git-repos", "leetcode-companywise-interview-questions");
	if (!fs.existsSync(repoPath)) {
		throw new Error(`Could not find leetcode-companywise-interview-questions at: ${repoPath}`);
	}
	
	const items = fs.readdirSync(repoPath);
	const companyFolders = items.filter((item) => {
		const fullPath = path.join(repoPath, item);
		return fs.statSync(fullPath).isDirectory() && !item.startsWith(".");
	});
	console.log(`Found ${companyFolders.length} company folders in GitHub repo.`);

	// Ensure all company slugs exist or register them
	const companiesToUpsert = [];
	for (const folder of companyFolders) {
		const slug = slugify(folder);
		if (!companyBySlug.has(slug)) {
			// Human-readable name from folder name
			const name = folder
				.split("-")
				.map((word) => word.charAt(0).toUpperCase() + word.slice(1))
				.join(" ");
			companiesToUpsert.push({ slug, name });
			companyBySlug.set(slug, name);
		}
	}

	if (companiesToUpsert.length > 0) {
		console.log(`Registering ${companiesToUpsert.length} new companies in Supabase...`);
		await upsertBatched("oa_companies", companiesToUpsert, "slug");
	}

	// Refetch full list of company IDs
	const { data: allCompRows, error: compRefetchErr } = await supabase.from("oa_companies").select("id, slug");
	if (compRefetchErr) throw compRefetchErr;
	const companyIdBySlug = new Map(allCompRows.map((c) => [c.slug, c.id]));

	// Extract questions and occurrences
	console.log("Parsing company CSV files...");
	const questionsMap = new Map();
	const occurrencesMap = new Map();

	const csvPriorities = [
		{ name: "thirty-days.csv", year: 2026, season: "spring", confidence: "A" },
		{ name: "three-months.csv", year: 2026, season: "winter", confidence: "B" },
		{ name: "six-months.csv", year: 2025, season: "fall", confidence: "B" },
		{ name: "more-than-six-months.csv", year: 2025, season: "summer", confidence: "C" },
		{ name: "all.csv", year: 2024, season: "unknown", confidence: "C" }
	];

	for (const folder of companyFolders) {
		const companySlug = slugify(folder);
		const companyId = companyIdBySlug.get(companySlug);
		if (!companyId) continue;

		const companyDir = path.join(repoPath, folder);

		// Process CSVs in reverse priority so that high-priority files overwrite lower-priority settings
		for (const csvConfig of [...csvPriorities].reverse()) {
			const csvPath = path.join(companyDir, csvConfig.name);
			if (!fs.existsSync(csvPath)) continue;

			try {
				const csvText = fs.readFileSync(csvPath, "utf8");
				const rows = parseCsvContent(csvText);

				for (const row of rows) {
					const urlField = row.URL || row.url;
					if (!urlField) continue;

					// Extract slug from URL
					const cleanUrl = urlField.trim();
					const parts = cleanUrl.split("/problems/");
					if (parts.length < 2) continue;
					const questionSlug = parts[1].split("/")[0].trim();
					if (!questionSlug) continue;

					const title = row.Title || row.title || questionSlug;
					const difficulty = row.Difficulty || row.difficulty || "Medium";

					// Lookup category in doocs/leetcode tags
					let category = "arrays";
					const doocsQ = doocsMap.get(questionSlug);
					if (doocsQ && doocsQ.tags_en) {
						category = getCategoryFromTags(doocsQ.tags_en);
					}

					// Collect question
					if (!questionsMap.has(questionSlug)) {
						questionsMap.set(questionSlug, {
							slug: questionSlug,
							title: title,
							difficulty: difficulty.charAt(0).toUpperCase() + difficulty.slice(1).toLowerCase(),
							category: category,
							question_order: 1000 + questionsMap.size,
						});
					}

					// Record occurrence
					const occurrenceKey = `${questionSlug}-${companySlug}`;
					occurrencesMap.set(occurrenceKey, {
						company_id: companyId,
						question_slug: questionSlug,
						year: csvConfig.year,
						season: csvConfig.season,
						round_type: "oa",
						confidence_tier: csvConfig.confidence,
						source_notes: `GitHub: snehasishroy/leetcode-companywise-interview-questions - ${csvConfig.name}`,
						source_url: cleanUrl,
					});
				}
			} catch (err) {
				console.warn(`Error reading ${csvPath}:`, err.message);
			}
		}
	}

	console.log(`Parsed ${questionsMap.size} unique questions and ${occurrencesMap.size} occurrences.`);

	// Upsert questions
	console.log("Upserting questions into Supabase...");
	const questionsList = Array.from(questionsMap.values());
	await upsertBatched("oa_questions", questionsList, "slug");

	// Fetch full list of question IDs by slug to link occurrences
	const { data: allQuestRows, error: questRefetchErr } = await supabase.from("oa_questions").select("id, slug");
	if (questRefetchErr) throw questRefetchErr;
	const questionIdBySlug = new Map(allQuestRows.map((q) => [q.slug, q.id]));

	// Build occurrences with verified question IDs
	const occurrencesToInsert = [];
	for (const [key, occ] of occurrencesMap.entries()) {
		const qId = questionIdBySlug.get(occ.question_slug);
		if (qId) {
			occurrencesToInsert.push({
				company_id: occ.company_id,
				question_id: qId,
				role_id: null,
				year: occ.year,
				season: occ.season,
				round_type: occ.round_type,
				confidence_tier: occ.confidence_tier,
				source_notes: occ.source_notes,
				source_url: occ.source_url,
			});
		}
	}

	console.log(`Upserting ${occurrencesToInsert.length} occurrences into Supabase...`);
	// We use upsert on occurrences to avoid duplicates
	for (let i = 0; i < occurrencesToInsert.length; i += BATCH) {
		const chunk = occurrencesToInsert.slice(i, i + BATCH);
		const { error } = await supabase.from("oa_question_occurrences").upsert(chunk, {
			onConflict: "question_id,company_id,role_id,year,season,round_type",
			ignoreDuplicates: true,
		});
		if (error) throw error;
		process.stdout.write(`  oa_question_occurrences: ${Math.min(i + BATCH, occurrencesToInsert.length)}/${occurrencesToInsert.length}\r`);
	}
	console.log(`  oa_question_occurrences: ${occurrencesToInsert.length} rows`);

	console.log("GitHub Repository Ingest Completed Successfully!");
}

runImport().catch((err) => {
	console.error("Fatal error during import:", err);
	process.exit(1);
});
