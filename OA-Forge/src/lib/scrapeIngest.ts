import fs from "fs";
import path from "path";
import { createClient } from "@supabase/supabase-js";
import { readDataCsv } from "./csv";

export type ScrapeLead = {
	title: string;
	url: string;
	snippet: string;
	source_type: string;
	leetcode_slug?: string;
	mapped_question_slug?: string;
};

import { getOrIngestDynamicQuestion } from "./dynamicQuestions";

function extractLeetcodeSlug(url: string) {
	const m = url.match(/leetcode\.com\/problems\/([a-z0-9-]+)/i);
	return m?.[1]?.toLowerCase();
}

function inferSource(url: string) {
	const lower = url.toLowerCase();
	if (lower.includes("leetcode.com/problems")) return "leetcode";
	if (lower.includes("leetcode.com/discuss")) return "lc_discuss";
	if (lower.includes("geeksforgeeks.org")) return "gfg";
	if (lower.includes("reddit.com")) return "reddit";
	return "web";
}

function isRelevant(title: string, snippet: string, url: string) {
	const text = `${title} ${snippet} ${url}`.toLowerCase();
	return (
		/interview|assessment|oa\b|coding|leetcode|problem|question/.test(text) &&
		!/job posting|apply now|salary|resume|career page/.test(text)
	);
}

async function firecrawlSearch(query: string, limit = 8) {
	const key = process.env.FIRECRAWL_API_KEY;
	if (!key) {
		console.warn("No FIRECRAWL_API_KEY found in environment.");
		return [];
	}

	try {
		const res = await fetch("https://api.firecrawl.dev/v1/search", {
			method: "POST",
			headers: {
				"Authorization": `Bearer ${key}`,
				"Content-Type": "application/json"
			},
			body: JSON.stringify({
				query,
				limit
			}),
			signal: AbortSignal.timeout(15000),
		});

		if (!res.ok) {
			const resV2 = await fetch("https://api.firecrawl.dev/v2/search", {
				method: "POST",
				headers: {
					"Authorization": `Bearer ${key}`,
					"Content-Type": "application/json"
				},
				body: JSON.stringify({
					query,
					limit
				}),
				signal: AbortSignal.timeout(15000),
			});
			if (!resV2.ok) {
				console.error(`Firecrawl search failed: ${resV2.statusText}`);
				return [];
			}
			const json = await resV2.json();
			return (json.data ?? []).map((r: any) => ({
				title: r.title ?? "",
				url: r.url ?? "",
				snippet: r.description ?? r.markdown ?? ""
			}));
		}

		const json = await res.json();
		return (json.data ?? []).map((r: any) => ({
			title: r.title ?? "",
			url: r.url ?? "",
			snippet: r.description ?? r.markdown ?? ""
		}));
	} catch (err) {
		console.error("Firecrawl search error:", err);
		return [];
	}
}

export async function scrapeCompanyLeads(companyName: string, companySlug: string, max = 5): Promise<ScrapeLead[]> {
	const year = new Date().getFullYear();
	const queries = [
		`${companyName} online assessment coding questions ${year}`,
		`${companyName} OA leetcode intern`,
	];
	const leads: ScrapeLead[] = [];
	const seen = new Set<string>();

	for (const query of queries) {
		if (leads.length >= max) break;
		const results = await firecrawlSearch(query, 8);
		for (const r of results) {
			if (leads.length >= max || seen.has(r.url) || !isRelevant(r.title, r.snippet, r.url)) continue;
			seen.add(r.url);
			const lc = extractLeetcodeSlug(r.url);
			leads.push({
				...r,
				source_type: inferSource(r.url),
				leetcode_slug: lc,
				mapped_question_slug: lc || undefined,
			});
		}
		await new Promise((r) => setTimeout(r, 1100));
	}

	appendScrapedCsv(companySlug, companyName, leads);
	return leads;
}

function appendScrapedCsv(companySlug: string, companyName: string, leads: ScrapeLead[]) {
	const outPath = path.join(process.cwd(), "data", "scraped-questions.csv");
	const headers =
		"company_slug,company_name,title,url,source_type,leetcode_slug,mapped_question_slug,scraped_at\n";
	if (!fs.existsSync(outPath)) fs.writeFileSync(outPath, headers);

	const rows = leads.map((l) =>
		[companySlug, companyName, l.title, l.url, l.source_type, l.leetcode_slug ?? "", l.mapped_question_slug ?? "", new Date().toISOString()]
			.map((v) => `"${String(v).replace(/"/g, '""')}"`)
			.join(",")
	);
	if (rows.length) fs.appendFileSync(outPath, rows.join("\n") + "\n");
}

function appendLocalOccurrence(companySlug: string, questionSlug: string, sourceUrl: string) {
	const occPath = path.join(process.cwd(), "data", "occurrences.csv");
	const text = fs.readFileSync(occPath, "utf8");
	if (text.includes(`${companySlug},${questionSlug},`)) return false;

	const year = new Date().getFullYear();
	const row = `${companySlug},${questionSlug},${year},Intern,oa,B,"Scraped from ${sourceUrl}",${sourceUrl}`;
	fs.appendFileSync(occPath, row + "\n");
	return true;
}

export async function ingestScrapeResults(companySlug: string, leads: ScrapeLead[]) {
	let ingested = 0;
	const mapped = leads.filter((l) => l.mapped_question_slug);

	for (const lead of mapped) {
		await getOrIngestDynamicQuestion(lead.mapped_question_slug!);
		if (appendLocalOccurrence(companySlug, lead.mapped_question_slug!, lead.url)) ingested++;
	}

	const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
	const key = process.env.SUPABASE_SERVICE_ROLE_KEY;
	if (!url || !key || mapped.length === 0) return ingested;

	const supabase = createClient(url, key);
	const { data: company } = await supabase.from("oa_companies").select("id").eq("slug", companySlug).maybeSingle();
	if (!company) return ingested;

	const { data: questions } = await supabase.from("oa_questions").select("id, slug").in(
		"slug",
		mapped.map((m) => m.mapped_question_slug!)
	);
	const qBySlug = new Map((questions ?? []).map((q) => [q.slug, q.id]));
	const year = new Date().getFullYear();

	for (const lead of mapped) {
		const qid = qBySlug.get(lead.mapped_question_slug!);
		if (!qid) continue;
		const { error } = await supabase.from("oa_question_occurrences").upsert(
			{
				company_id: company.id,
				question_id: qid,
				year,
				season: "Intern",
				round_type: "oa",
				confidence_tier: "B",
				source_notes: `Scraped: ${lead.title}`,
				source_url: lead.url,
			},
			{ onConflict: "question_id,company_id,year,season,round_type", ignoreDuplicates: true }
		);
		if (!error) ingested++;
	}

	return ingested;
}

export async function refreshLeadsForCompanies(limit = 10) {
	const companies = readDataCsv("companies.csv").slice(0, limit);
	let total = 0;
	for (const c of companies) {
		const leads = await scrapeCompanyLeads(c.name, c.slug, 3);
		total += await ingestScrapeResults(c.slug, leads);
		await new Promise((r) => setTimeout(r, 1100));
	}
	return total;
}
