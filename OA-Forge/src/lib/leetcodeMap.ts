/** Maps LeetCode problem URL slugs → OA Forge question slugs */
const LC_TO_FORGE: Record<string, string> = {
	"two-sum": "two-sum",
	"valid-parentheses": "valid-parentheses",
	"merge-sorted-array": "merge-sorted-arrays",
	"maximum-subarray": "maximum-subarray",
	"jump-game": "jump-game",
	"search-a-2d-matrix": "search-a-2d-matrix",
	"number-of-islands": "number-of-islands",
	"reverse-linked-list": "reverse-linked-list",
	"best-time-to-buy-and-sell-stock": "best-time-to-buy-sell-stock",
	"contains-duplicate": "contains-duplicate",
	"climbing-stairs": "climbing-stairs",
	"house-robber": "house-robber",
	"longest-substring-without-repeating-characters": "longest-substring-without-repeating",
	"single-number": "single-number",
	"move-zeroes": "move-zeroes",
	"binary-search": "binary-search",
	"product-of-array-except-self": "product-of-array-except-self",
	"rotate-array": "rotate-array",
	"intersection-of-two-arrays-ii": "intersection-of-two-arrays-ii",
	"palindrome-number": "palindrome-number",
};

export function extractLeetcodeSlug(url: string): string | null {
	const match = url.match(/leetcode\.com\/problems\/([a-z0-9-]+)/i);
	return match?.[1]?.toLowerCase() ?? null;
}

export function mapUrlToForgeSlug(url: string): string | null {
	const lc = extractLeetcodeSlug(url);
	if (!lc) return null;
	return LC_TO_FORGE[lc] ?? null;
}

export function mapTitleToForgeSlug(title: string): string | null {
	const lower = title.toLowerCase();
	for (const [lc, forge] of Object.entries(LC_TO_FORGE)) {
		const name = lc.replace(/-/g, " ");
		if (lower.includes(name)) return forge;
	}
	return null;
}
