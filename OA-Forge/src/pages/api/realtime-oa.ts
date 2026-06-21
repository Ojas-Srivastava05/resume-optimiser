import type { NextApiRequest, NextApiResponse } from "next";
import { getLocalCompanyReadiness } from "@/lib/localBank";
import { getRealtimeOALeads } from "@/lib/oaResearch";

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
	if (req.method !== "GET") return res.status(405).json({ error: "Method not allowed" });
	const companySlug = String(req.query.companySlug ?? "");
	const company = getLocalCompanyReadiness().find((row) => row.slug === companySlug);
	if (!company) return res.status(404).json({ error: "Company not found" });

	try {
		const leads = await getRealtimeOALeads(company.name, company.slug);
		return res.status(200).json({
			company: { slug: company.slug, name: company.name },
			leads: leads.slice(0, 12),
			mode: company.total_questions > 0 ? "curated-plus-live" : "research-only",
		});
	} catch (error) {
		return res.status(200).json({
			company: { slug: company.slug, name: company.name },
			leads: [],
			mode: "research-only",
			error: error instanceof Error ? error.message : "Live scrape failed",
		});
	}
}
