import type { NextApiRequest, NextApiResponse } from "next";
import { supabase } from "@/supabase/supabase";
import { getCompanyBySlug, getQuestionsByCompany, getTemplateForCompany, pickRandomQuestions } from "@/lib/db";
import { ConfidenceTier } from "@/lib/types/oa";
import { startLocalMockSession } from "@/lib/localBank";

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
	if (req.method !== "POST") return res.status(405).json({ error: "Method not allowed" });

	const { companySlug, strictMode = false } = req.body as {
		companySlug: string;
		strictMode?: boolean;
	};

	if (!companySlug) {
		return res.status(400).json({ error: "companySlug required" });
	}

	try {
		const company = await getCompanyBySlug(companySlug);
		const template = company ? await getTemplateForCompany(company.id) : null;
		const numQuestions = template?.num_questions ?? 2;
		const durationMinutes = template?.duration_minutes ?? 90;
		const strictTiers: ConfidenceTier[] = strictMode
			? template?.strict_tiers ?? ["A", "B"]
			: ["A", "B", "C"];

		if (company) {
			const pool = await getQuestionsByCompany(companySlug, false);
			const eligible = pool.filter((q) => strictTiers.includes(q.confidence_tier));
			if (eligible.length >= numQuestions) {
				const picked = await pickRandomQuestions(companySlug, numQuestions, strictTiers);

				const { data: session, error: sessionError } = await supabase
					.from("oa_sessions")
					.insert({
						company_id: company.id,
						template_id: template?.id ?? null,
						duration_minutes: durationMinutes,
						status: "active",
					})
					.select("id, company_id, duration_minutes, started_at, status")
					.single();

				if (sessionError) throw sessionError;

				const sessionQuestions = picked.map((q, idx) => ({
					session_id: session.id,
					question_id: q.id,
					question_order: idx + 1,
				}));

				const { error: sqError } = await supabase.from("oa_session_questions").insert(sessionQuestions);
				if (sqError) throw sqError;

				return res.status(200).json({
					sessionId: session.id,
					company: company.name,
					durationMinutes,
					source: "supabase",
					questions: picked.map((q, idx) => ({
						order: idx + 1,
						slug: q.slug,
						title: null,
						difficulty: null,
						confidenceTier: null,
					})),
				});
			}
		}

		const localSession = startLocalMockSession(companySlug, strictMode);
		if (!localSession) {
			return res.status(400).json({
				error: `No questions available for this company. Run npm run generate:bank to rebuild the question pool.`,
			});
		}

		return res.status(200).json({
			sessionId: localSession.id,
			company: localSession.companyName,
			durationMinutes: localSession.durationMinutes,
			source: "local-csv",
			questions: localSession.questions.map((q) => ({
				order: q.order,
				slug: q.slug,
				title: null,
				difficulty: null,
				confidenceTier: null,
			})),
		});
	} catch (err) {
		console.error(err);
		const localSession = startLocalMockSession(companySlug, strictMode);
		if (localSession) {
			return res.status(200).json({
				sessionId: localSession.id,
				company: localSession.companyName,
				durationMinutes: localSession.durationMinutes,
				source: "local-csv",
			});
		}
		return res.status(500).json({ error: "Failed to start mock OA session" });
	}
}
