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

	const problem = problems[slug];
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
		const result = await runCppWithPiston(slug, code, dbTests);
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

async function runCppWithPiston(
	slug: string,
	code: string,
	tests: { input_text: string; expected_output: string }[]
) {
	const source = buildCppHarness(slug, code, tests);
	const endpoint = process.env.PISTON_API_URL || "https://emkc.org/api/v2/piston/execute";
	if (process.env.JUDGE_MODE !== "local") {
		try {
			const response = await fetch(endpoint, {
				method: "POST",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify({
					language: "cpp",
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
			}
		} catch {
			// Fall through to local g++ when remote judge is unavailable.
		}
	}

	return runCppLocally(source, tests.length);
}

async function runCppLocally(source: string, testsRun: number) {
	const dir = await fs.mkdtemp(path.join(os.tmpdir(), "oa-forge-cpp-"));
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
