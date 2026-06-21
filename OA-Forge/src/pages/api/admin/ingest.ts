import type { NextApiRequest, NextApiResponse } from "next";
import { supabase } from "@/supabase/supabase";
import { ConfidenceTier } from "@/lib/types/oa";

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
	if (req.method !== "POST") return res.status(405).json({ error: "Method not allowed" });

	const {
		companySlug,
		questionSlug,
		year,
		season,
		confidenceTier,
		sourceNotes,
		sourceUrl,
	} = req.body as {
		companySlug: string;
		questionSlug: string;
		year: number;
		season?: string;
		confidenceTier: ConfidenceTier;
		sourceNotes: string;
		sourceUrl?: string;
	};

	if (!companySlug || !questionSlug || !year || !confidenceTier || !sourceNotes) {
		return res.status(400).json({ error: "Missing required fields" });
	}

	try {
		const { data: company } = await supabase
			.from("oa_companies")
			.select("id")
			.eq("slug", companySlug)
			.single();
		if (!company) return res.status(404).json({ error: "Company not found" });

		const { data: question } = await supabase
			.from("oa_questions")
			.select("id")
			.eq("slug", questionSlug)
			.single();
		if (!question) return res.status(404).json({ error: "Question not found — add slug to oa_questions first" });

		const { data, error } = await supabase
			.from("oa_question_occurrences")
			.insert({
				company_id: company.id,
				question_id: question.id,
				year,
				season: season ?? null,
				confidence_tier: confidenceTier,
				source_notes: sourceNotes,
				source_url: sourceUrl ?? null,
				round_type: "oa",
			})
			.select("id")
			.single();

		if (error) throw error;
		return res.status(200).json({ id: data.id, ok: true });
	} catch (err) {
		console.error(err);
		return res.status(500).json({ error: "Failed to ingest occurrence" });
	}
}
