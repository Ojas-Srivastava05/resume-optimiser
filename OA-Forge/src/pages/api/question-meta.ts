import type { NextApiRequest, NextApiResponse } from "next";
import { getQuestionMeta } from "@/lib/db";

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
	if (req.method !== "GET") return res.status(405).json({ error: "Method not allowed" });

	const slug = req.query.slug as string;
	if (!slug) return res.status(400).json({ error: "slug required" });

	try {
		const meta = await getQuestionMeta(slug);
		return res.status(200).json(meta);
	} catch (err) {
		console.error(err);
		return res.status(500).json({ error: "Failed to load question metadata" });
	}
}
