import type { NextApiRequest, NextApiResponse } from "next";
import { getCompanyReadiness } from "@/lib/db";
import { getLocalCompanyReadiness } from "@/lib/localBank";

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
	if (req.method !== "GET") return res.status(405).json({ error: "Method not allowed" });

	try {
		const companies = await getCompanyReadiness();
		const localCompanies = getLocalCompanyReadiness();
		const merged = new Map(localCompanies.map((company) => [company.slug, company]));
		for (const company of companies) {
			const local = merged.get(company.slug);
			// Prefer whichever source has more questions (local CSV is usually fuller)
			if (!local || company.total_questions > local.total_questions) {
				merged.set(company.slug, company);
			}
		}
		return res
			.status(200)
			.json({ companies: Array.from(merged.values()).sort((a, b) => a.name.localeCompare(b.name)) });
	} catch (err) {
		console.error(err);
		return res.status(200).json({ companies: getLocalCompanyReadiness(), source: "local-csv" });
	}
}
