import fs from "fs";
import path from "path";

export type CsvRow = Record<string, string>;

export function parseCsvText(text: string): CsvRow[] {
	const clean = text.trim();
	if (!clean) return [];
	const rows: string[][] = [];
	let row: string[] = [];
	let cell = "";
	let quoted = false;

	for (let i = 0; i < clean.length; i++) {
		const ch = clean[i];
		const next = clean[i + 1];
		if (quoted && ch === '"' && next === '"') {
			cell += '"';
			i++;
		} else if (ch === '"') {
			quoted = !quoted;
		} else if (!quoted && ch === ",") {
			row.push(cell);
			cell = "";
		} else if (!quoted && (ch === "\n" || ch === "\r")) {
			if (ch === "\r" && next === "\n") i++;
			row.push(cell);
			rows.push(row);
			row = [];
			cell = "";
		} else {
			cell += ch;
		}
	}
	row.push(cell);
	rows.push(row);

	const [headers, ...body] = rows;
	return body.map((r) => Object.fromEntries(headers.map((h, i) => [h, r[i] ?? ""])));
}

export function readCsvFile(filePath: string): CsvRow[] {
	if (!fs.existsSync(filePath)) return [];
	return parseCsvText(fs.readFileSync(filePath, "utf8"));
}

export function readDataCsv(file: string): CsvRow[] {
	return readCsvFile(path.join(process.cwd(), "data", file));
}

export function slugifyCompany(name: string) {
	return name
		.toLowerCase()
		.replace(/&/g, " and ")
		.replace(/[^a-z0-9]+/g, "-")
		.replace(/^-+|-+$/g, "")
		.slice(0, 80);
}
