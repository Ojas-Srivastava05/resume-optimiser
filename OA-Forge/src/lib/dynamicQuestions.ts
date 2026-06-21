import fs from "fs";
import path from "path";
import { supabase } from "@/supabase/supabase";
import { Problem } from "@/utils/types/problem";

function splitParams(raw: string): string[] {
	const params: string[] = [];
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

function parseSignature(userCode: string) {
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

export async function fetchLeetCodeProblem(slug: string) {
	const query = `
		query questionData($titleSlug: String!) {
			question(titleSlug: $titleSlug) {
				questionId
				questionFrontendId
				title
				titleSlug
				content
				difficulty
				codeSnippets {
					lang
					langSlug
					code
				}
				topicTags {
					name
					slug
				}
			}
		}
	`;

	const response = await fetch("https://leetcode.com/graphql/", {
		method: "POST",
		headers: {
			"Content-Type": "application/json",
			"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
		},
		body: JSON.stringify({
			query,
			variables: { titleSlug: slug }
		})
	});

	if (!response.ok) {
		throw new Error(`LeetCode GraphQL error! status: ${response.status}`);
	}

	const json = await response.json();
	return json.data?.question;
}

export function parseLeetcodeContent(contentHtml: string) {
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

	// 1. Extract examples from <pre> tags
	const examples: { input: string; output: string; explanation?: string }[] = [];
	const preRegex = /<pre>([\s\S]*?)<\/pre>/gi;
	let match;
	while ((match = preRegex.exec(clean)) !== null) {
		const text = match[1].trim();
		const inputMatch = text.match(/Input:\s*([\s\S]*?)\n\s*Output:/i);
		const outputMatch = text.match(/Output:\s*([\s\S]*?)(?:\n\s*Explanation:|\n\s*Constraints:|$)/i);
		
		if (inputMatch && outputMatch) {
			const rawInput = inputMatch[1].trim();
			const rawOutput = outputMatch[1].trim();
			
			const parsedInput: Record<string, any> = {};
			const varMatches = Array.from(rawInput.matchAll(/\b(\w+)\s*=\s*/g));
			for (let i = 0; i < varMatches.length; i++) {
				const name = varMatches[i][1];
				const start = varMatches[i].index! + varMatches[i][0].length;
				const end = (i + 1 < varMatches.length) ? varMatches[i + 1].index! : rawInput.length;
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

	// 2. Extract problem statement (text before the first Example 1 tag)
	let problemStatement = contentHtml;
	const exampleIdx = contentHtml.search(/(?:Example 1|Example\s*1)/i);
	if (exampleIdx !== -1) {
		problemStatement = contentHtml.substring(0, exampleIdx);
		// Strip trailing elements
		problemStatement = problemStatement.replace(/<p>&nbsp;<\/p>\s*$/i, "").replace(/<p><br><\/p>\s*$/i, "");
	}

	// 3. Extract constraints
	const constraintsMatch = contentHtml.match(/(?:Constraints:|Constraints<\/strong>)([\s\S]*?)$/i);
	let constraints = constraintsMatch ? constraintsMatch[1].trim() : "";
	constraints = constraints.replace(/<\/?ul[^>]*>/gi, "");

	return { problemStatement, examples, constraints };
}

function mapTagToCategory(tags: { slug: string }[]): string {
	if (!tags || tags.length === 0) return "arrays";
	const slugs = tags.map(t => t.slug);
	for (const slug of slugs) {
		if (slug === "array" || slug === "two-pointers" || slug === "sliding-window") return "arrays";
		if (slug === "string") return "strings";
		if (slug === "hash-table") return "hashing";
		if (slug === "dynamic-programming") return "dynamic-programming";
		if (slug === "binary-search") return "binary-search";
		if (slug === "sorting") return "sorting";
		if (slug === "greedy") return "greedy";
		if (slug === "bit-manipulation") return "bit-manipulation";
		if (slug === "math") return "math";
		if (slug === "stack" || slug === "queue" || slug === "monotonic-stack") return "stacks-queues";
		if (slug === "linked-list") return "linked-list";
		if (slug === "tree" || slug === "binary-tree" || slug === "binary-search-tree") return "trees";
		if (slug === "graph" || slug === "depth-first-search" || slug === "breadth-first-search" || slug === "union-find") return "graphs";
		if (slug === "backtracking" || slug === "recursion") return "recursion";
	}
	return "arrays";
}

const localMetaPath = path.join(process.cwd(), "data", "dynamic-questions.json");

function loadLocalMeta(): Record<string, Problem & { category: string; difficulty: string }> {
	if (!fs.existsSync(localMetaPath)) return {};
	try {
		return JSON.parse(fs.readFileSync(localMetaPath, "utf8"));
	} catch {
		return {};
	}
}

function saveLocalMeta(data: Record<string, Problem & { category: string; difficulty: string }>) {
	const dir = path.dirname(localMetaPath);
	if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
	fs.writeFileSync(localMetaPath, JSON.stringify(data, null, 2), "utf8");
}

function saveToLocalCsvs(
	slug: string,
	title: string,
	difficulty: string,
	category: string,
	examples: { input: string; output: string }[]
) {
	// 1. Append to questions.csv
	const qPath = path.join(process.cwd(), "data", "questions.csv");
	const qText = fs.readFileSync(qPath, "utf8");
	if (!qText.includes(`${slug},`)) {
		const line = `${slug},"${title.replace(/"/g, '""')}",${difficulty},${category},0`;
		fs.appendFileSync(qPath, "\n" + line);
	}

	// 2. Append to test-cases.csv
	const tcPath = path.join(process.cwd(), "data", "test-cases.csv");
	const tcText = fs.readFileSync(tcPath, "utf8");
	if (!tcText.includes(`${slug},`)) {
		examples.forEach((ex, idx) => {
			const escapedInput = ex.input.replace(/"/g, '""');
			const escapedOutput = ex.output.replace(/"/g, '""');
			const line = `${slug},"${escapedInput}","${escapedOutput}",true,${idx + 1}`;
			fs.appendFileSync(tcPath, "\n" + line);
		});
	}
}

export async function getOrIngestDynamicQuestion(slug: string): Promise<(Problem & { category: string; difficulty: string }) | null> {
	const localMeta = loadLocalMeta();
	if (localMeta[slug]) {
		return localMeta[slug];
	}

	try {
		const lcData = await fetchLeetCodeProblem(slug);
		if (!lcData) return null;

		const { problemStatement, examples, constraints } = parseLeetcodeContent(lcData.content);
		const cppSnippet = lcData.codeSnippets?.find((s: any) => s.langSlug === "cpp")?.code ?? "";
		const sig = parseSignature(cppSnippet.replace(/\/\/[^\n]*/g, "").replace(/\/\*[\s\S]*?\*\//g, ""));
		const starterFunctionName = sig ? sig.functionName : "";
		const category = mapTagToCategory(lcData.topicTags);

		const formattedExamples = examples.map((ex, idx) => ({
			id: idx + 1,
			inputText: ex.input,
			outputText: ex.output,
			explanation: ex.explanation
		}));

		const problem: Problem & { category: string; difficulty: string } = {
			id: slug,
			title: lcData.title,
			problemStatement,
			examples: formattedExamples,
			constraints,
			order: 0,
			starterCode: cppSnippet,
			handlerFunction: "",
			starterFunctionName,
			category,
			difficulty: lcData.difficulty
		};

		// Save locally to JSON
		localMeta[slug] = problem;
		saveLocalMeta(localMeta);

		// Save to local CSVs
		saveToLocalCsvs(
			slug,
			lcData.title,
			lcData.difficulty,
			category,
			examples
		);

		// Try to upsert into Supabase oa_questions and oa_test_cases
		try {
			const { data: qData, error: qErr } = await supabase
				.from("oa_questions")
				.upsert({
					slug,
					title: lcData.title,
					difficulty: lcData.difficulty,
					category
				}, { onConflict: "slug" })
				.select("id")
				.single();

			if (!qErr && qData) {
				const tcInserts = examples.map((ex, idx) => ({
					question_id: qData.id,
					input_text: ex.input,
					expected_output: ex.output,
					is_sample: true,
					test_order: idx + 1
				}));

				// Delete existing test cases first
				await supabase.from("oa_test_cases").delete().eq("question_id", qData.id);
				await supabase.from("oa_test_cases").insert(tcInserts);
			}
		} catch (dbErr) {
			console.warn("Could not insert dynamic question into Supabase, falling back to local files:", dbErr);
		}

		return problem;
	} catch (err) {
		console.error(`Error in getOrIngestDynamicQuestion for ${slug}:`, err);
		return null;
	}
}
