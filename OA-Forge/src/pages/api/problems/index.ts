import type { NextApiRequest, NextApiResponse } from "next";
import { getQuestionsByCompany } from "@/lib/db";

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
	if (req.method !== "GET") return res.status(405).json({ error: "Method not allowed" });

	const company = req.query.company as string;
	const strict = req.query.strict === "true";

	if (!company || company === "all") {
		return res.status(400).json({ error: "company query param required" });
	}

	try {
		const questions = await getQuestionsByCompany(company, strict);
		return res.status(200).json({ questions });
	} catch (err) {
		console.error(err);
		return res.status(500).json({ error: "Failed to fetch questions" });
	}
}
