import type { NextApiRequest, NextApiResponse } from "next";
import { getTestCases } from "@/lib/db";
import { problems } from "@/utils/problems";
import { buildCppHarness } from "@/lib/cppTemplates";
import { readDataCsv } from "@/lib/csv";
import { execFile } from "child_process";
import fs from "fs/promises";
import os from "os";
import path from "path";
import { promisify } from "util";

const execFileAsync = promisify(execFile);

import { getOrIngestDynamicQuestion } from "@/lib/dynamicQuestions";

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
	if (req.method !== "POST") return res.status(405).json({ error: "Method not allowed" });

	const { slug, code, language = "cpp" } = req.body as {
		slug: string;
		code: string;
		language?: "cpp";
	};

	if (!slug || !code) {
		return res.status(400).json({ error: "slug and code required" });
	}

	let problem = problems[slug];
	if (!problem) {
		const dynamicProb = await getOrIngestDynamicQuestion(slug);
		if (dynamicProb) {
			problem = dynamicProb;
		}
	}
	if (!problem) {
		return res.status(404).json({ error: "Problem not found" });
	}

	try {
		let dbTests = await getTestCases(slug, false);
		if (dbTests.length === 0) {
			dbTests = readDataCsv("test-cases.csv")
				.filter((row) => row.question_slug === slug)
				.map((row, idx) => ({
					id: `${slug}-${idx}`,
					input_text: row.input_text,
					expected_output: row.expected_output,
					is_sample: row.is_sample === "true",
					test_order: Number(row.test_order || idx),
				}));
		}

		if (language !== "cpp") {
			return res.status(400).json({ error: "Only C++ submissions are supported" });
		}

		if (dbTests.length === 0) {
			return res.status(500).json({ error: "No tests configured for this C++ problem" });
		}
		const result = await executeCpp(slug, code, dbTests);
		return res.status(200).json(result);
	} catch (error: unknown) {
		const message = error instanceof Error ? error.message : "Runtime error";
		const isAssertion = message.includes("AssertionError") || message.includes("strict deep-equal");
		return res.status(200).json({
			passed: false,
			verdict: isAssertion ? "Wrong Answer" : "Runtime Error",
			message,
		});
	}
}

async function executeCpp(
	slug: string,
	code: string,
	tests: { input_text: string; expected_output: string }[]
) {
	if (process.env.JUDGE_MODE === "local") {
		const source = buildCppHarness(slug, code, tests);
		return runCppLocally(source, tests.length);
	}
	return runCppWithRemoteJudge(slug, code, tests);
}

async function runCppWithRemoteJudge(
	slug: string,
	code: string,
	tests: { input_text: string; expected_output: string }[]
) {
	if (process.env.PISTON_API_URL) {
		return runCppWithPiston(slug, code, tests);
	}
	return runCppWithWandbox(slug, code, tests);
}

async function runCppWithWandbox(
	slug: string,
	code: string,
	tests: { input_text: string; expected_output: string }[]
) {
	const source = buildCppHarness(slug, code, tests);
	try {
		const response = await fetch("https://wandbox.org/api/compile.json", {
			method: "POST",
			headers: { "Content-Type": "application/json" },
			body: JSON.stringify({
				compiler: "gcc-head",
				code: source,
				options: "-O3,-std=c++17",
			}),
		});

		if (response.ok) {
			const payload = await response.json();
			const status = Number(payload.status || "0");
			const compilerError = payload.compiler_error || payload.compiler_message || "";
			const programError = payload.program_error || payload.program_message || "";
			const programOutput = payload.program_output || "";

			if (status !== 0) {
				if (compilerError) {
					let msg = compilerError;
					if (compilerError.includes("OCI runtime error") || compilerError.includes("clone: Resource temporarily unavailable")) {
						msg = `Wandbox public compilation service is currently overloaded or experiencing sandbox restrictions. To resolve this:\n1. If running locally, set JUDGE_MODE=local in .env.local to compile with your local g++ compiler.\n2. For deployed versions, deploy your own Piston instance and set PISTON_API_URL in your environment variables.`;
					}
					return {
						passed: false,
						verdict: "Compile Error",
						message: msg,
					};
				}
				let runMsg = programError || `Execution failed with status ${status} / signal ${payload.signal}`;
				if (runMsg.includes("OCI runtime error") || runMsg.includes("clone: Resource temporarily unavailable")) {
					runMsg = `Wandbox public compilation service is currently overloaded or experiencing sandbox restrictions. To resolve this:\n1. If running locally, set JUDGE_MODE=local in .env.local to compile with your local g++ compiler.\n2. For deployed versions, deploy your own Piston instance and set PISTON_API_URL in your environment variables.`;
				}
				return {
					passed: false,
					verdict: "Runtime Error",
					message: runMsg,
				};
			}

			const output = String(programOutput).trim();
			return {
				passed: output.endsWith("AC"),
				verdict: output.endsWith("AC") ? "Accepted" : "Wrong Answer",
				message: output,
				testsRun: tests.length,
			};
		} else {
			return {
				passed: false,
				verdict: "Remote Judge Error",
				message: `Wandbox service returned status ${response.status}. To resolve this:\n1. If running locally, set JUDGE_MODE=local in .env.local to compile with your local g++ compiler.\n2. For deployed versions, deploy your own Piston instance and set PISTON_API_URL in your environment variables.`,
			};
		}
	} catch (error: any) {
		return {
			passed: false,
			verdict: "Remote Judge Error",
			message: `Failed to connect to the remote compilation service: ${error.message || error}.\nTo resolve this, set JUDGE_MODE=local in .env.local if running locally.`,
		};
	}
}

async function runCppWithPiston(
	slug: string,
	code: string,
	tests: { input_text: string; expected_output: string }[]
) {
	const source = buildCppHarness(slug, code, tests);
	const endpoint = process.env.PISTON_API_URL || "https://emkc.org/api/v2/piston/execute";
	try {
		const response = await fetch(endpoint, {
			method: "POST",
			headers: { "Content-Type": "application/json" },
			body: JSON.stringify({
				language: "c++",
				version: "10.2.0",
				files: [{ name: "main.cpp", content: source }],
			}),
		});

		if (response.ok) {
			const payload = await response.json();
			const compile = payload.compile;
			const run = payload.run;
			if (compile?.code && compile.code !== 0) {
				return { passed: false, verdict: "Compile Error", message: compile.stderr || compile.output };
			}
			if (!run || run.code !== 0) {
				return { passed: false, verdict: "Wrong Answer", message: run?.stderr || run?.output || "Execution failed" };
			}
			const output = String(run.output || "").trim();
			return {
				passed: output.endsWith("AC"),
				verdict: output.endsWith("AC") ? "Accepted" : "Wrong Answer",
				message: output,
				testsRun: tests.length,
			};
		} else {
			let message = `Remote compilation service returned status ${response.status}.`;
			if (response.status === 401) {
				message = `Remote compilation service returned status 401 (Unauthorized). The public Piston API is now restricted. To resolve this:\n1. If running locally, set JUDGE_MODE=local in .env.local to compile with your local g++ compiler.\n2. For deployed versions, host your own Piston instance and configure PISTON_API_URL in your environment variables.`;
			}
			return {
				passed: false,
				verdict: "Remote Judge Error",
				message: message,
			};
		}
	} catch (error: any) {
		return {
			passed: false,
			verdict: "Remote Judge Error",
			message: `Failed to connect to the remote compilation service: ${error.message || error}.\nTo resolve this, set JUDGE_MODE=local in .env.local if running locally.`,
		};
	}
}

async function runCppLocally(source: string, testsRun: number) {
	const dir = await fs.mkdtemp(path.join(os.tmpdir(), "oa-crucible-cpp-"));
	const sourcePath = path.join(dir, "main.cpp");
	const binaryPath = path.join(dir, "main");
	try {
		await fs.writeFile(sourcePath, source);
		try {
			await execFileAsync("g++", [sourcePath, "-std=c++17", "-O2", "-pipe", "-o", binaryPath], {
				timeout: 8000,
				maxBuffer: 1024 * 1024,
			});
		} catch (error: any) {
			return {
				passed: false,
				verdict: "Compile Error",
				message: error.stderr || error.message || "C++ compile failed",
			};
		}

		try {
			const { stdout, stderr } = await execFileAsync(binaryPath, [], {
				timeout: 3000,
				maxBuffer: 1024 * 1024,
			});
			const output = String(stdout || stderr || "").trim();
			return {
				passed: output.endsWith("AC"),
				verdict: output.endsWith("AC") ? "Accepted" : "Wrong Answer",
				message: output,
				testsRun,
			};
		} catch (error: any) {
			const output = String(error.stdout || error.stderr || error.message || "").trim();
			return {
				passed: false,
				verdict: error.killed ? "Time Limit Exceeded" : "Wrong Answer",
				message: output,
				testsRun,
			};
		}
	} finally {
		await fs.rm(dir, { recursive: true, force: true });
	}
}
