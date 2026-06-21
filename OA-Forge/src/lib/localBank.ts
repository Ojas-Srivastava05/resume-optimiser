import path from "path";
import { ConfidenceTier, OACompanyReadiness } from "./types/oa";
import { readCsvFile, readDataCsv, slugifyCompany } from "./csv";

type LocalSession = {
	id: string;
	companySlug: string;
	companyName: string;
	durationMinutes: number;
	sourceMode?: "curated" | "live-pattern";
	startedAt: string;
	status: "active" | "completed";
	questions: {
		order: number;
		slug: string;
		title: string;
		difficulty: string;
		category: string;
		confidenceTier: ConfidenceTier;
	}[];
};

const TIER_WEIGHT: Record<ConfidenceTier, number> = { A: 5, B: 3, C: 1 };

declare global {
	var __oaForgeLocalSessions: Map<string, LocalSession> | undefined;
}

const sessions = global.__oaForgeLocalSessions ?? new Map<string, LocalSession>();
global.__oaForgeLocalSessions = sessions;

function encodeSession(session: Omit<LocalSession, "id">) {
	return `local-${Buffer.from(JSON.stringify(session)).toString("base64url")}`;
}

function decodeSession(id: string): LocalSession | null {
	if (!id.startsWith("local-")) return null;
	try {
		const raw = Buffer.from(id.slice("local-".length), "base64url").toString("utf8");
		const parsed = JSON.parse(raw) as Omit<LocalSession, "id">;
		return { ...parsed, id };
	} catch {
		return null;
	}
}

export function getLocalCompanyReadiness(): OACompanyReadiness[] {
	const configuredCompanies = readDataCsv("companies.csv");
	const scoutPath = path.join(process.cwd(), "..", "internship-scout", "data", "all_companies.csv");
	const scoutCompanies = readCsvFile(scoutPath)
		.filter((row) => row.Company && !row.Company.includes("http") && !row.Company.startsWith("<"))
		.map((row) => ({
		slug: slugifyCompany(row.Company),
		name: row.Company,
		default_duration_minutes: "90",
		default_num_questions: "2",
		target_role: "SDE Intern",
	}));
	const configuredBySlug = new Map(configuredCompanies.map((company) => [company.slug, company]));
	const companies = scoutCompanies.map((company) => configuredBySlug.get(company.slug) ?? company);
	for (const company of configuredCompanies) {
		if (!companies.some((c) => c.slug === company.slug)) companies.push(company);
	}
	const occurrences = readDataCsv("occurrences.csv");
	const leads = readDataCsv("oa-source-leads.csv");
	return companies.map((company) => {
		const rows = occurrences.filter((o) => o.company_slug === company.slug);
		const leadCount = leads.filter((lead) => lead.company_slug === company.slug && lead.title !== "FETCH_ERROR").length;
		const unique = new Set(rows.map((o) => o.question_slug));
		const strict = new Set(
			rows.filter((o) => o.confidence_tier === "A" || o.confidence_tier === "B").map((o) => o.question_slug)
		);
		const numQuestions = Number(company.default_num_questions || 2);
		return {
			id: company.slug,
			slug: company.slug,
			name: company.name,
			total_questions: unique.size,
			strict_questions: strict.size,
			tier_a: rows.filter((o) => o.confidence_tier === "A").length,
			tier_b: rows.filter((o) => o.confidence_tier === "B").length,
			tier_c: rows.filter((o) => o.confidence_tier === "C").length,
			duration_minutes: Number(company.default_duration_minutes || 90),
			num_questions: numQuestions,
			mock_ready: unique.size >= numQuestions,
			strict_ready: strict.size >= numQuestions,
			source_leads: leadCount,
		};
	});
}

function weightedSample<T extends { confidenceTier: ConfidenceTier }>(items: T[], count: number): T[] {
	const pool = [...items];
	const picked: T[] = [];
	while (picked.length < count && pool.length > 0) {
		const total = pool.reduce((sum, item) => sum + TIER_WEIGHT[item.confidenceTier], 0);
		let cursor = Math.random() * total;
		let index = 0;
		for (let i = 0; i < pool.length; i++) {
			cursor -= TIER_WEIGHT[pool[i].confidenceTier];
			if (cursor <= 0) {
				index = i;
				break;
			}
		}
		picked.push(pool[index]);
		pool.splice(index, 1);
	}
	return picked;
}

type EligibleQ = {
	slug: string;
	title: string;
	difficulty: string;
	category: string;
	confidenceTier: ConfidenceTier;
	pairId: string;
};

function pickQuestions(pool: EligibleQ[], count: number): EligibleQ[] {
	if (count === 2 && pool.length >= 2) {
		const pairs = readDataCsv("pairs.csv");
		const pairable = pairs.filter((p) => {
			const a = pool.find((q) => q.slug === p.question_slug_a);
			const b = pool.find((q) => q.slug === p.question_slug_b);
			return a && b;
		});
		if (pairable.length > 0 && Math.random() < 0.6) {
			const pair = pairable[Math.floor(Math.random() * pairable.length)];
			const a = pool.find((q) => q.slug === pair.question_slug_a)!;
			const b = pool.find((q) => q.slug === pair.question_slug_b)!;
			return [a, b];
		}
	}
	return weightedSample(pool, count);
}

export function startLocalMockSession(companySlug: string, strictMode: boolean) {
	const companies = getLocalCompanyReadiness();
	const questions = readDataCsv("questions.csv");
	const occurrences = readDataCsv("occurrences.csv");
	const company = companies.find((c) => c.slug === companySlug);
	if (!company) return null;

	const questionBySlug = new Map(questions.map((q) => [q.slug, q]));
	const eligible = occurrences
		.filter((o) => o.company_slug === companySlug)
		.filter((o) => !strictMode || o.confidence_tier === "A" || o.confidence_tier === "B")
		.map((o) => {
			const q = questionBySlug.get(o.question_slug);
			if (!q) return null;
			return {
				slug: q.slug,
				title: q.title,
				difficulty: q.difficulty,
				category: q.category,
				confidenceTier: o.confidence_tier as ConfidenceTier,
				pairId: o.pair_id || "",
			};
		})
		.filter((q): q is EligibleQ => Boolean(q));

	const uniqueBySlug = new Map<string, EligibleQ>();
	for (const q of eligible) uniqueBySlug.set(q.slug, q);
	const pool = Array.from(uniqueBySlug.values());
	const count = Number(company.num_questions || 2);

	if (pool.length < count) return null;

	const payload: Omit<LocalSession, "id"> = {
		companySlug,
		companyName: company.name,
		durationMinutes: Number(company.duration_minutes || 90),
		sourceMode: "curated",
		startedAt: new Date().toISOString(),
		status: "active",
		questions: pickQuestions(pool, count).map((q, idx) => ({ ...q, order: idx + 1 })),
	};
	const session: LocalSession = { ...payload, id: encodeSession(payload) };
	sessions.set(session.id, session);
	return session;
}

export function getLocalMockSession(id: string) {
	return sessions.get(id) ?? decodeSession(id);
}
