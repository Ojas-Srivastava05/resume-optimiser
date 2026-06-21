import type { NextApiRequest, NextApiResponse } from "next";
import { supabase } from "@/supabase/supabase";
import { getLocalMockSession } from "@/lib/localBank";

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
	if (req.method !== "GET") return res.status(405).json({ error: "Method not allowed" });

	const sessionId = req.query.sessionId as string;
	if (!sessionId) return res.status(400).json({ error: "sessionId required" });

	try {
		if (sessionId.startsWith("local-")) {
			const local = getLocalMockSession(sessionId);
			if (!local) return res.status(404).json({ error: "Local session not found" });
			const startedMs = new Date(local.startedAt).getTime();
			const expired = Date.now() >= startedMs + local.durationMinutes * 60 * 1000;
			return res.status(200).json({
				session: {
					id: local.id,
					status: expired ? "completed" : local.status,
					durationMinutes: local.durationMinutes,
					startedAt: local.startedAt,
					endedAt: expired ? new Date(startedMs + local.durationMinutes * 60 * 1000).toISOString() : null,
					company: { slug: local.companySlug, name: local.companyName },
					isFallback: local.sourceMode === "classic-fallback",
				},
				questions: local.questions.map((q) => ({
					order: q.order,
					verdict: null,
					slug: q.slug,
					title: expired ? q.title : null,
					difficulty: q.difficulty,
					category: q.category,
					confidenceTier: q.confidenceTier,
				})),
			});
		}

		const { data: session, error: sessionError } = await supabase
			.from("oa_sessions")
			.select(
				`
        id,
        status,
        duration_minutes,
        started_at,
        ended_at,
        company_id,
        oa_companies ( slug, name )
      `
			)
			.eq("id", sessionId)
			.single();

		if (sessionError || !session) {
			return res.status(404).json({ error: "Session not found" });
		}

		const { data: sessionQuestions, error: sqError } = await supabase
			.from("oa_session_questions")
			.select(
				`
        id,
        question_order,
        verdict,
        oa_questions ( id, slug, title, difficulty, category )
      `
			)
			.eq("session_id", sessionId)
			.order("question_order");

		if (sqError) throw sqError;

		const questionIds = (sessionQuestions ?? [])
			.map((sq) => {
				const q = sq.oa_questions as unknown as { id: string } | null;
				return q?.id;
			})
			.filter((id): id is string => Boolean(id));

		const { data: tierRows } = await supabase
			.from("oa_question_occurrences")
			.select("question_id, confidence_tier")
			.eq("company_id", session.company_id)
			.in("question_id", questionIds);

		const tierByQuestion = new Map(
			(tierRows ?? []).map((r) => [r.question_id, r.confidence_tier as string])
		);

		const company = session.oa_companies as unknown as { slug: string; name: string };
		const startedMs = new Date(session.started_at).getTime();
		const expired = Date.now() >= startedMs + session.duration_minutes * 60 * 1000;
		const hideTitles = session.status === "active" && !expired;

		if (expired && session.status === "active") {
			await supabase
				.from("oa_sessions")
				.update({ status: "completed", ended_at: new Date().toISOString() })
				.eq("id", sessionId);
		}

		const isFallback = (tierRows ?? []).length === 0;

		return res.status(200).json({
			session: {
				id: session.id,
				status: session.status,
				durationMinutes: session.duration_minutes,
				startedAt: session.started_at,
				endedAt: session.ended_at,
				company,
				isFallback,
			},
			questions: (sessionQuestions ?? []).map((sq) => {
				const q = sq.oa_questions as unknown as {
					id: string;
					slug: string;
					title: string;
					difficulty: string;
					category: string;
				};
				return {
					order: sq.question_order,
					verdict: sq.verdict,
					slug: q.slug,
					title: hideTitles ? null : q.title,
					difficulty: q.difficulty,
					category: q.category,
					confidenceTier: tierByQuestion.get(q.id) ?? null,
				};
			}),
		});
	} catch (err) {
		console.error(err);
		return res.status(500).json({ error: "Failed to fetch session" });
	}
}
