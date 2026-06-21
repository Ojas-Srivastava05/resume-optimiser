import { supabase } from "@/supabase/supabase";
import {
	ConfidenceTier,
	OACompany,
	OACompanyReadiness,
	OAQuestionWithMeta,
	OATemplate,
	OATestCase,
} from "./types/oa";

const TIER_WEIGHT: Record<ConfidenceTier, number> = { A: 5, B: 3, C: 1 };

export async function getCompanies(): Promise<OACompany[]> {
	const { data, error } = await supabase.from("oa_companies").select("id, slug, name").order("name");
	if (error) throw error;
	return data ?? [];
}

export async function getCompanyBySlug(slug: string): Promise<OACompany | null> {
	const { data, error } = await supabase
		.from("oa_companies")
		.select("id, slug, name")
		.eq("slug", slug)
		.single();
	if (error) return null;
	return data;
}

export async function getQuestionsByCompany(
	companySlug: string,
	strictOnly = false
): Promise<OAQuestionWithMeta[]> {
	const company = await getCompanyBySlug(companySlug);
	if (!company) return [];

	let query = supabase
		.from("oa_question_occurrences")
		.select(
			`
      confidence_tier,
      year,
      season,
      source_notes,
      source_url,
      oa_questions (
        id,
        slug,
        title,
        difficulty,
        category,
        question_order
      )
    `
		)
		.eq("company_id", company.id);

	if (strictOnly) {
		query = query.in("confidence_tier", ["A", "B"]);
	}

	const { data, error } = await query;
	if (error) throw error;

	const rows = (data ?? []).filter((row) => row.oa_questions);
	const seen = new Set<string>();
	const results: OAQuestionWithMeta[] = [];

	for (const row of rows) {
		const q = row.oa_questions as unknown as OAQuestionWithMeta;
		if (seen.has(q.slug)) continue;
		seen.add(q.slug);
		results.push({
			...q,
			confidence_tier: row.confidence_tier as ConfidenceTier,
			year: row.year,
			season: row.season,
			source_notes: row.source_notes,
			source_url: row.source_url,
		});
	}

	return results.sort((a, b) => a.question_order - b.question_order);
}

export async function getCompanyReadiness(): Promise<OACompanyReadiness[]> {
	const companies = await getCompanies();
	const { data: templates, error: templateError } = await supabase
		.from("oa_templates")
		.select("company_id, duration_minutes, num_questions");
	if (templateError) throw templateError;

	const templateByCompany = new Map(
		(templates ?? []).map((t) => [t.company_id, t as { duration_minutes: number; num_questions: number }])
	);

	const { data: rows, error } = await supabase
		.from("oa_question_occurrences")
		.select("company_id, question_id, confidence_tier");
	if (error) throw error;

	const byCompany = new Map<
		string,
		{ questionIds: Set<string>; strictIds: Set<string>; tier_a: number; tier_b: number; tier_c: number }
	>();

	for (const row of rows ?? []) {
		if (!byCompany.has(row.company_id)) {
			byCompany.set(row.company_id, {
				questionIds: new Set(),
				strictIds: new Set(),
				tier_a: 0,
				tier_b: 0,
				tier_c: 0,
			});
		}
		const bucket = byCompany.get(row.company_id)!;
		bucket.questionIds.add(row.question_id);
		if (row.confidence_tier === "A" || row.confidence_tier === "B") bucket.strictIds.add(row.question_id);
		if (row.confidence_tier === "A") bucket.tier_a += 1;
		if (row.confidence_tier === "B") bucket.tier_b += 1;
		if (row.confidence_tier === "C") bucket.tier_c += 1;
	}

	return companies.map((company) => {
		const template = templateByCompany.get(company.id);
		const required = template?.num_questions ?? 2;
		const bucket = byCompany.get(company.id);
		const total = bucket?.questionIds.size ?? 0;
		const strict = bucket?.strictIds.size ?? 0;
		return {
			...company,
			total_questions: total,
			strict_questions: strict,
			tier_a: bucket?.tier_a ?? 0,
			tier_b: bucket?.tier_b ?? 0,
			tier_c: bucket?.tier_c ?? 0,
			duration_minutes: template?.duration_minutes ?? 90,
			num_questions: required,
			mock_ready: total >= required,
			strict_ready: strict >= required,
		};
	});
}

export async function getTestCases(questionSlug: string, sampleOnly = false): Promise<OATestCase[]> {
	const { data: question } = await supabase
		.from("oa_questions")
		.select("id")
		.eq("slug", questionSlug)
		.single();
	if (!question) return [];

	let query = supabase
		.from("oa_test_cases")
		.select("id, input_text, expected_output, is_sample, test_order")
		.eq("question_id", question.id)
		.order("test_order");

	if (sampleOnly) query = query.eq("is_sample", true);

	const { data, error } = await query;
	if (error) throw error;
	return (data ?? []) as OATestCase[];
}

function weightedSample<T extends { confidence_tier: ConfidenceTier }>(items: T[], count: number): T[] {
	if (items.length <= count) return [...items].sort(() => Math.random() - 0.5);

	const pool = [...items];
	const picked: T[] = [];

	while (picked.length < count && pool.length > 0) {
		const total = pool.reduce((s, q) => s + TIER_WEIGHT[q.confidence_tier], 0);
		let r = Math.random() * total;
		let idx = 0;
		for (let i = 0; i < pool.length; i++) {
			r -= TIER_WEIGHT[pool[i].confidence_tier];
			if (r <= 0) {
				idx = i;
				break;
			}
		}
		picked.push(pool[idx]);
		pool.splice(idx, 1);
	}

	return picked;
}

export async function getQuestionBySlug(slug: string) {
	const { data, error } = await supabase
		.from("oa_questions")
		.select("id, slug, title, difficulty, category")
		.eq("slug", slug)
		.single();
	if (error) return null;
	return data;
}

export async function getQuestionMeta(slug: string) {
	const question = await getQuestionBySlug(slug);
	if (!question) return { question: null, occurrences: [] };

	const { data, error } = await supabase
		.from("oa_question_occurrences")
		.select(
			`
      confidence_tier, year, season, round_type, source_notes, source_url,
      oa_companies ( slug, name )
    `
		)
		.eq("question_id", question.id);

	if (error) throw error;
	return { question, occurrences: data ?? [] };
}

export async function getTemplateForCompany(companyId: string): Promise<OATemplate | null> {
	const { data, error } = await supabase
		.from("oa_templates")
		.select("id, company_id, name, duration_minutes, num_questions, strict_tiers")
		.eq("company_id", companyId)
		.limit(1)
		.single();
	if (error) return null;
	return data as OATemplate;
}

export async function pickRandomQuestions(
	companySlug: string,
	count: number,
	strictTiers: ConfidenceTier[] = ["A", "B"]
): Promise<OAQuestionWithMeta[]> {
	const pool = await getQuestionsByCompany(companySlug, false);
	const eligible = pool.filter((q) => strictTiers.includes(q.confidence_tier));

	if (eligible.length === 0) {
		throw new Error(`No questions in pool for ${companySlug} with tiers ${strictTiers.join(", ")}`);
	}

	const shuffled = weightedSample(eligible, count);
	return shuffled;
}
