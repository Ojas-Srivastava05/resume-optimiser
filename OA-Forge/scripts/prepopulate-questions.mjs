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
		"Missing NEXT_PUBLIC_SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY."
	);
}

const supabase = createClient(url, key);
const BATCH = 500;

function splitParams(raw) {
	const params = [];
	let current = "";
	let depth = 0;
	for (let i = 0; i < raw.length; i++) {
		const char = raw[i];
		if (char === "<") depth++;
		else if (char === ">") depth--;
		
		if (char === "," && depth === 0) {
			params.push(current.trim());
			current = "";
		} else {
			current += char;
		}
	}
	if (current.trim()) {
		params.push(current.trim());
	}
	return params;
}

function parseSignature(userCode) {
	const match = userCode.match(/class\s+Solution\s*\{[^]*?public\s*:[^]*?([\w<>\*&\s]+)\s+(\w+)\s*\(([^)]*)\)/);
	if (!match) return null;
	const returnType = match[1].trim();
	const functionName = match[2].trim();
	const paramsRaw = match[3].trim();
	
	const paramsList = splitParams(paramsRaw);
	const params = paramsList.map(p => {
		const parts = p.trim().split(/\s+/);
		const name = parts[parts.length - 1].replace(/^[*&]+/, "");
		const type = p.slice(0, p.lastIndexOf(name)).trim();
		const normType = type.replace(/\s+/g, "").replace(/const/g, "").replace(/&/g, "");
		return { name, type, normType };
	});
	
	return { returnType, functionName, params };
}

function parseLeetcodeContent(contentHtml) {
	if (!contentHtml) return { problemStatement: "", examples: [], constraints: "" };
	const clean = contentHtml
		.replace(/<strong[^>]*>/gi, "")
		.replace(/<\/strong>/gi, "")
		.replace(/<em[^>]*>/gi, "")
		.replace(/<\/em>/gi, "")
		.replace(/&nbsp;/g, " ")
		.replace(/&lt;/g, "<")
		.replace(/&gt;/g, ">")
		.replace(/&amp;/g, "&")
		.replace(/&quot;/g, '"');

	const examples = [];
	const preRegex = /<pre>([\s\S]*?)<\/pre>/gi;
	let match;
	while ((match = preRegex.exec(clean)) !== null) {
		const text = match[1].trim();
		const inputMatch = text.match(/Input:\s*([\s\S]*?)\n\s*Output:/i);
		const outputMatch = text.match(/Output:\s*([\s\S]*?)(?:\n\s*Explanation:|\n\s*Constraints:|$)/i);
		
		if (inputMatch && outputMatch) {
			const rawInput = inputMatch[1].trim();
			const rawOutput = outputMatch[1].trim();
			
			const parsedInput = {};
			const varMatches = Array.from(rawInput.matchAll(/\b(\w+)\s*=\s*/g));
			for (let i = 0; i < varMatches.length; i++) {
				const name = varMatches[i][1];
				const start = varMatches[i].index + varMatches[i][0].length;
				const end = (i + 1 < varMatches.length) ? varMatches[i + 1].index : rawInput.length;
				let valStr = rawInput.slice(start, end).trim();
				if (valStr.endsWith(",")) valStr = valStr.slice(0, -1).trim();
				
				try {
					parsedInput[name] = JSON.parse(valStr);
				} catch {
					if (valStr.startsWith('"') && valStr.endsWith('"')) {
						parsedInput[name] = valStr.slice(1, -1);
					} else if (valStr === "true") {
						parsedInput[name] = true;
					} else if (valStr === "false") {
						parsedInput[name] = false;
					} else {
						parsedInput[name] = valStr;
					}
				}
			}
			
			let finalOutput = rawOutput;
			try {
				finalOutput = JSON.parse(rawOutput);
			} catch {}
			
			const explanationMatch = text.match(/Explanation:\s*([\s\S]*?)$/i);
			const explanation = explanationMatch ? explanationMatch[1].trim() : undefined;

			examples.push({
				input: JSON.stringify(parsedInput),
				output: JSON.stringify(finalOutput),
				explanation
			});
		}
	}

	let problemStatement = contentHtml;
	const exampleIdx = contentHtml.search(/(?:Example 1|Example\s*1)/i);
	if (exampleIdx !== -1) {
		problemStatement = contentHtml.substring(0, exampleIdx);
		problemStatement = problemStatement.replace(/<p>&nbsp;<\/p>\s*$/i, "").replace(/<p><br><\/p>\s*$/i, "");
	}

	const constraintsMatch = contentHtml.match(/(?:Constraints:|Constraints<\/strong>)([\s\S]*?)$/i);
	let constraints = constraintsMatch ? constraintsMatch[1].trim() : "";
	constraints = constraints.replace(/<\/?ul[^>]*>/gi, "");

	return { problemStatement, examples, constraints };
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

async function runPrepopulate() {
	console.log("Loading doocs/leetcode metadata database...");
	const doocsPath = path.join(root, "scratch", "git-repos", "leetcode", "solution", "result.json");
	if (!fs.existsSync(doocsPath)) {
		throw new Error(`Could not find doocs/leetcode result.json at: ${doocsPath}`);
	}
	const doocsData = JSON.parse(fs.readFileSync(doocsPath, "utf8"));
	
	const doocsMap = new Map();
	Object.values(doocsData).forEach((q) => {
		if (q.question_title_slug) {
			doocsMap.set(q.question_title_slug, q);
		}
	});

	console.log("Fetching questions from Supabase...");
	const dbQuestions = [];
	let page = 0;
	const pageSize = 1000;
	while (true) {
		const { data, error } = await supabase
			.from("oa_questions")
			.select("id, slug, title, difficulty, category")
			.range(page * pageSize, (page + 1) * pageSize - 1);
		if (error) throw error;
		if (!data || data.length === 0) break;
		dbQuestions.push(...data);
		page++;
	}
	console.log(`Found ${dbQuestions.length} questions in Supabase.`);

	const localMetaPath = path.join(root, "data", "dynamic-questions.json");
	let localMeta = {};
	if (fs.existsSync(localMetaPath)) {
		try {
			localMeta = JSON.parse(fs.readFileSync(localMetaPath, "utf8"));
		} catch {}
	}

	const testCasesToInsert = [];
	let populatedCount = 0;

	for (const q of dbQuestions) {
		if (localMeta[q.slug] && localMeta[q.slug].problemStatement) {
			// Already populated in JSON cache, let's make sure we have its test cases mapped
			const cached = localMeta[q.slug];
			if (cached.examples && cached.examples.length > 0) {
				cached.examples.forEach((ex, idx) => {
					testCasesToInsert.push({
						question_id: q.id,
						input_text: ex.inputText,
						expected_output: ex.outputText,
						is_sample: true,
						test_order: idx + 1,
					});
				});
			}
			continue;
		}

		const doocsQ = doocsMap.get(q.slug);
		if (!doocsQ) continue;

		const content = doocsQ.content_en || "";
		const { problemStatement, examples, constraints } = parseLeetcodeContent(content);
		const cppSnippet = doocsQ.code_snippets?.find((s) => s.langSlug === "cpp")?.code ?? "";
		const sig = parseSignature(cppSnippet.replace(/\/\/[^\n]*/g, "").replace(/\/\*[\s\S]*?\*\//g, ""));
		const starterFunctionName = sig ? sig.functionName : "";

		const formattedExamples = examples.map((ex, idx) => ({
			id: idx + 1,
			inputText: ex.input,
			outputText: ex.output,
			explanation: ex.explanation,
		}));

		const problem = {
			id: q.slug,
			title: q.title,
			problemStatement,
			examples: formattedExamples,
			constraints,
			order: 0,
			starterCode: cppSnippet,
			handlerFunction: "",
			starterFunctionName,
			category: q.category || getCategoryFromTags(doocsQ.tags_en),
			difficulty: q.difficulty,
		};

		localMeta[q.slug] = problem;
		populatedCount++;

		formattedExamples.forEach((ex, idx) => {
			testCasesToInsert.push({
				question_id: q.id,
				input_text: ex.inputText,
				expected_output: ex.outputText,
				is_sample: true,
				test_order: idx + 1,
			});
		});
	}

	console.log(`Writing dynamic-questions.json... (Added/Updated ${populatedCount} questions)`);
	fs.writeFileSync(localMetaPath, JSON.stringify(localMeta, null, 2), "utf8");

	console.log(`Writing examples to test-cases.csv...`);
	const tcCsvPath = path.join(root, "data", "test-cases.csv");
	// Let's load existing csv rows to avoid duplicates
	let existingCsvText = "";
	if (fs.existsSync(tcCsvPath)) {
		existingCsvText = fs.readFileSync(tcCsvPath, "utf8");
	} else {
		existingCsvText = "question_slug,input_text,expected_output,is_sample,test_order";
		fs.writeFileSync(tcCsvPath, existingCsvText, "utf8");
	}

	const csvRows = [];
	for (const q of dbQuestions) {
		const meta = localMeta[q.slug];
		if (!meta || !meta.examples) continue;
		if (existingCsvText.includes(`${q.slug},`)) continue; // Already exists in CSV

		meta.examples.forEach((ex, idx) => {
			const escapedInput = ex.inputText.replace(/"/g, '""');
			const escapedOutput = ex.outputText.replace(/"/g, '""');
			csvRows.push(`${q.slug},"${escapedInput}","${escapedOutput}",true,${idx + 1}`);
		});
	}

	if (csvRows.length > 0) {
		fs.appendFileSync(tcCsvPath, "\n" + csvRows.join("\n"));
		console.log(`Added ${csvRows.length} test cases to data/test-cases.csv.`);
	}

	console.log(`Upserting ${testCasesToInsert.length} test cases into Supabase oa_test_cases...`);
	// Clear existing test cases for all target question IDs to avoid duplicates
	const uniqueQuestionIds = Array.from(new Set(testCasesToInsert.map((t) => t.question_id)));
	for (let i = 0; i < uniqueQuestionIds.length; i += BATCH) {
		const chunk = uniqueQuestionIds.slice(i, i + BATCH);
		const { error: delErr } = await supabase
			.from("oa_test_cases")
			.delete()
			.in("question_id", chunk);
		if (delErr) throw delErr;
	}

	// Insert new ones in batches
	for (let i = 0; i < testCasesToInsert.length; i += BATCH) {
		const chunk = testCasesToInsert.slice(i, i + BATCH);
		const { error: insErr } = await supabase
			.from("oa_test_cases")
			.insert(chunk);
		if (insErr) {
			console.error("Error inserting test cases:", insErr);
			throw insErr;
		}
		process.stdout.write(`  oa_test_cases: ${Math.min(i + BATCH, testCasesToInsert.length)}/${testCasesToInsert.length}\r`);
	}
	console.log(`  oa_test_cases: ${testCasesToInsert.length} rows inserted.`);
	console.log("Prepopulation complete!");
}

runPrepopulate().catch((err) => {
	console.error("Prepopulation failed:", err);
	process.exit(1);
});
