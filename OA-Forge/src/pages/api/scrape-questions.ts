import type { NextApiRequest, NextApiResponse } from "next";
import { getRealtimeOALeads } from "@/lib/oaResearch";
import { slugifyCompany, readDataCsv } from "@/lib/csv";

function extractLeetcodeSlug(url: string): string | null {
	const m = url.match(/leetcode\.com\/problems\/([a-z0-9-]+)/i);
	return m?.[1]?.toLowerCase() ?? null;
}

async function enrichCompany(name: string, slug: string, maxQuestions: number) {
	const leads = await getRealtimeOALeads(name, slug);
	const mapped: { forgeSlug: string; title: string; url: string; source: string }[] = [];
	const seen = new Set<string>();

	for (const lead of leads) {
		const forgeSlug = extractLeetcodeSlug(lead.url);
		if (!forgeSlug || seen.has(forgeSlug)) continue;
		seen.add(forgeSlug);
		mapped.push({ forgeSlug, title: lead.title, url: lead.url, source: lead.source_type });
		if (mapped.length >= maxQuestions) break;
	}

	return { companySlug: slug, leadsFound: leads.length, mappedQuestions: mapped.length, mapped };
}

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
	if (req.method !== "POST") return res.status(405).json({ error: "Method not allowed" });

	const body = req.body as {
		companySlug?: string;
		companyName?: string;
		maxQuestions?: number;
		batch?: boolean;
		limit?: number;
	};

	const maxQuestions = body.maxQuestions ?? 10;

	try {
		if (body.batch) {
			const limit = body.limit ?? 5;
			const targets = readDataCsv("companies.csv").slice(0, limit);
			const results = [];
			for (const c of targets) {
				try {
					results.push(await enrichCompany(c.name, c.slug, maxQuestions));
				} catch {
					results.push({ companySlug: c.slug, leadsFound: 0, mappedQuestions: 0, mapped: [] });
				}
			}
			return res.status(200).json({ success: true, batch: true, results });
		}

		if (!body.companySlug && !body.companyName) {
			return res.status(400).json({ error: "companySlug or companyName required" });
		}

		const slug = body.companySlug ?? slugifyCompany(body.companyName!);
		const name = body.companyName ?? slug.replace(/-/g, " ");
		const result = await enrichCompany(name, slug, maxQuestions);
		return res.status(200).json({ success: true, ...result });
	} catch (err) {
		console.error(err);
		return res.status(500).json({ error: err instanceof Error ? err.message : "Enrichment failed" });
	}
}
