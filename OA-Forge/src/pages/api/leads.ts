import type { NextApiRequest, NextApiResponse } from "next";
import { readDataCsv } from "@/lib/csv";

export default function handler(req: NextApiRequest, res: NextApiResponse) {
	if (req.method !== "GET") return res.status(405).json({ error: "Method not allowed" });
	const company = String(req.query.company ?? "");
	const rows = readDataCsv("oa-source-leads.csv")
		.filter((row) => !company || row.company_slug === company)
		.filter((row) => row.title !== "FETCH_ERROR")
		.slice(0, 12);
	return res.status(200).json({ leads: rows });
}
