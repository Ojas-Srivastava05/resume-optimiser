import { createClient } from "@supabase/supabase-js";
import fs from "node:fs";
import path from "node:path";

const root = "/Users/ojas/Desktop/Resume Optimiser/OA-Forge";
const envPath = path.join(root, ".env.local");
if (fs.existsSync(envPath)) {
	for (const line of fs.readFileSync(envPath, "utf8").split(/\r?\n/)) {
		const match = line.match(/^([A-Za-z0-9_]+)=(.*)$/);
		if (match && !process.env[match[1]]) process.env[match[1]] = match[2];
	}
}

const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
const key = process.env.SUPABASE_SERVICE_ROLE_KEY;
if (!url || !key) {
	throw new Error("Missing Supabase credentials in .env.local.");
}

const supabase = createClient(url, key);

function parseCsvContent(text) {
	const rows = [];
	let row = [];
	let cell = "";
	let quoted = false;
	for (let i = 0; i < text.length; i++) {
		const ch = text[i];
		const next = text[i + 1];
		if (quoted && ch === '"' && next === '"') {
			cell += '"';
			i++;
		} else if (ch === '"') quoted = !quoted;
		else if (!quoted && ch === ",") {
			row.push(cell);
			cell = "";
		} else if (!quoted && (ch === "\n" || ch === "\r")) {
			if (ch === "\r" && next === "\n") i++;
			row.push(cell);
			rows.push(row);
			row = [];
			cell = "";
		} else cell += ch;
	}
	row.push(cell);
	rows.push(row);
	const [headers, ...body] = rows;
	if (!headers) return [];
	const cleanHeaders = headers.map(h => h.trim().replace(/^"/, "").replace(/"$/, ""));
	return body
		.filter(r => r.length > 0 && r.some(c => c.trim() !== ""))
		.map((r) => Object.fromEntries(cleanHeaders.map((h, i) => [h, r[i] ?? ""])));
}

async function clean() {
	console.log("Loading allowed companies from data/companies.csv...");
	const allowedText = fs.readFileSync(path.join(root, "data", "companies.csv"), "utf8");
	const allowed = parseCsvContent(allowedText);
	const allowedSlugs = new Set(allowed.map((c) => c.slug.trim()));
	console.log(`Loaded ${allowedSlugs.size} allowed slugs.`);

	console.log("Fetching all existing companies from Supabase (with pagination)...");
	let dbCompanies = [];
	let page = 0;
	const pageSize = 1000;
	while (true) {
		const { data, error } = await supabase
			.from("oa_companies")
			.select("id, slug, name")
			.range(page * pageSize, (page + 1) * pageSize - 1);
		if (error) throw error;
		if (!data || data.length === 0) break;
		dbCompanies = dbCompanies.concat(data);
		page++;
	}

	console.log(`Supabase currently has ${dbCompanies.length} companies.`);

	const toDelete = dbCompanies.filter((c) => !allowedSlugs.has(c.slug));
	console.log(`Found ${toDelete.length} companies to delete (not in companies.csv):`);
	for (const c of toDelete) {
		console.log(`  - ${c.name} (${c.slug})`);
	}

	if (toDelete.length > 0) {
		const deleteSlugs = toDelete.map((c) => c.slug);
		console.log(`Deleting ${deleteSlugs.length} companies...`);
		
		// Delete in chunks of 100 to be safe
		const chunkSize = 100;
		for (let i = 0; i < deleteSlugs.length; i += chunkSize) {
			const chunk = deleteSlugs.slice(i, i + chunkSize);
			const { error: delErr } = await supabase.from("oa_companies").delete().in("slug", chunk);
			if (delErr) {
				console.error("Error during deletion:", delErr);
				throw delErr;
			}
		}
		console.log("Deletion complete!");
	} else {
		console.log("No companies need to be deleted.");
	}

	// Refetch after deletion to check missing ones
	console.log("Refetching existing companies...");
	let refetchedCompanies = [];
	page = 0;
	while (true) {
		const { data, error } = await supabase
			.from("oa_companies")
			.select("id, slug, name")
			.range(page * pageSize, (page + 1) * pageSize - 1);
		if (error) throw error;
		if (!data || data.length === 0) break;
		refetchedCompanies = refetchedCompanies.concat(data);
		page++;
	}

	const dbSlugs = new Set(refetchedCompanies.map((c) => c.slug));
	const missing = allowed.filter((c) => !dbSlugs.has(c.slug));
	if (missing.length > 0) {
		console.log(`Inserting ${missing.length} missing allowed companies...`);
		const chunks = [];
		const insertBatchSize = 100;
		for (let i = 0; i < missing.length; i += insertBatchSize) {
			chunks.push(missing.slice(i, i + insertBatchSize));
		}
		
		for (const chunk of chunks) {
			const { error: insErr } = await supabase.from("oa_companies").insert(
				chunk.map((c) => ({ slug: c.slug, name: c.name }))
			);
			if (insErr) {
				console.error("Error during insertion:", insErr);
				throw insErr;
			}
		}
		console.log("Insertion complete!");
	} else {
		console.log("All allowed companies are present in Supabase.");
	}
}

clean().catch((err) => {
	console.error("Fatal error during cleanup:", err);
	process.exit(1);
});
