import assert from "assert";
import { OATestCase } from "./types/oa";

type UserFn = (...args: unknown[]) => unknown;

function parseJson<T>(text: string): T {
	return JSON.parse(text) as T;
}

function runSlugTests(slug: string, fn: UserFn, tests: OATestCase[]): boolean {
	for (const t of tests) {
		const expected = parseJson<unknown>(t.expected_output);
		const input = parseJson<Record<string, unknown>>(t.input_text);

		switch (slug) {
			case "two-sum": {
				assert.deepStrictEqual(fn(input.nums, input.target), expected);
				break;
			}
			case "maximum-subarray":
			case "best-time-to-buy-sell-stock":
			case "house-robber":
			case "single-number": {
				assert.strictEqual(fn(input.nums ?? input.prices), expected);
				break;
			}
			case "climbing-stairs":
			case "binary-search":
			case "palindrome-number": {
				if (slug === "binary-search") assert.strictEqual(fn(input.nums, input.target), expected);
				else if (slug === "climbing-stairs") assert.strictEqual(fn(input.n), expected);
				else assert.strictEqual(fn(input.x), expected);
				break;
			}
			case "merge-sorted-arrays":
			case "move-zeroes":
			case "rotate-array": {
				const nums = [...(input.nums as number[])];
				if (slug === "merge-sorted-arrays") {
					fn(nums, input.m, input.nums2, input.n);
				} else if (slug === "rotate-array") {
					fn(nums, input.k);
				} else {
					fn(nums);
				}
				assert.deepStrictEqual(nums, expected);
				break;
			}
			case "number-of-islands": {
				const { grid } = input as { grid: string[][] };
				assert.strictEqual(fn(grid.map((r) => [...r])), expected);
				break;
			}
			case "jump-game":
			case "contains-duplicate":
			case "valid-parentheses": {
				const arg = input.nums ?? input.s;
				assert.strictEqual(fn(arg), expected);
				break;
			}
			case "search-a-2d-matrix": {
				assert.strictEqual(fn(input.matrix, input.target), expected);
				break;
			}
			case "longest-substring-without-repeating": {
				assert.strictEqual(fn(input.s), expected);
				break;
			}
			case "product-of-array-except-self":
			case "intersection-of-two-arrays-ii": {
				const got = fn(input.nums1 ?? input.nums, input.nums2) as number[];
				const sorted = [...got].sort((a, b) => a - b);
				const exp = [...(expected as number[])].sort((a, b) => a - b);
				assert.deepStrictEqual(sorted, exp);
				break;
			}
			default:
				throw new Error(`No DB test runner for slug: ${slug}`);
		}
	}
	return true;
}

export function runDbTests(slug: string, fn: UserFn, tests: OATestCase[]): boolean {
	if (tests.length === 0) return false;
	return runSlugTests(slug, fn, tests);
}
