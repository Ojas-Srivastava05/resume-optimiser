const STORAGE_KEY = "oa-crucible-solved";

export function getSolvedSlugs(): string[] {
	if (typeof window === "undefined") return [];
	try {
		const raw = localStorage.getItem(STORAGE_KEY);
		return raw ? (JSON.parse(raw) as string[]) : [];
	} catch {
		return [];
	}
}

export function markSolved(slug: string): void {
	if (typeof window === "undefined") return;
	const set = new Set(getSolvedSlugs());
	set.add(slug);
	localStorage.setItem(STORAGE_KEY, JSON.stringify(Array.from(set)));
}

export function isSolved(slug: string): boolean {
	return getSolvedSlugs().includes(slug);
}
