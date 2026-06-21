import { Problem } from "../types/problem";

function p(
	id: string,
	title: string,
	order: number,
	statement: string,
	examples: Problem["examples"],
	constraints: string
): Problem {
	return {
		id,
		title,
		order,
		problemStatement: statement,
		examples,
		constraints,
		starterCode: `// ${title}`,
		starterFunctionName: "function solution(",
		handlerFunction: () => true,
	};
}

export const bestTimeToBuySellStock = p(
	"best-time-to-buy-sell-stock",
	"9. Best Time to Buy and Sell Stock",
	9,
	`<p>Given an array <code>prices</code> where <code>prices[i]</code> is the price on day <code>i</code>, return the maximum profit from one buy and one sell.</p>`,
	[
		{ id: 1, inputText: "prices = [7,1,5,3,6,4]", outputText: "5", explanation: "Buy day 2, sell day 5." },
		{ id: 2, inputText: "prices = [7,6,4,3,1]", outputText: "0" },
	],
	`<li><code>1 ≤ prices.length ≤ 10^5</code></li>`
);

export const containsDuplicate = p(
	"contains-duplicate",
	"10. Contains Duplicate",
	10,
	`<p>Return <code>true</code> if any value appears at least twice in <code>nums</code>.</p>`,
	[
		{ id: 1, inputText: "nums = [1,2,3,1]", outputText: "true" },
		{ id: 2, inputText: "nums = [1,2,3,4]", outputText: "false" },
	],
	`<li><code>1 ≤ nums.length ≤ 10^5</code></li>`
);

export const climbingStairs = p(
	"climbing-stairs",
	"11. Climbing Stairs",
	11,
	`<p>Climb <code>n</code> stairs. Each time climb 1 or 2 steps. Return distinct ways.</p>`,
	[
		{ id: 1, inputText: "n = 2", outputText: "2" },
		{ id: 2, inputText: "n = 3", outputText: "3" },
	],
	`<li><code>1 ≤ n ≤ 45</code></li>`
);

export const houseRobber = p(
	"house-robber",
	"12. House Robber",
	12,
	`<p>Return max money robbing non-adjacent houses in <code>nums</code>.</p>`,
	[
		{ id: 1, inputText: "nums = [1,2,3,1]", outputText: "4" },
		{ id: 2, inputText: "nums = [2,7,9,3,1]", outputText: "12" },
	],
	`<li><code>1 ≤ nums.length ≤ 100</code></li>`
);

export const longestSubstring = p(
	"longest-substring-without-repeating",
	"13. Longest Substring Without Repeating Characters",
	13,
	`<p>Return length of longest substring without repeating characters.</p>`,
	[
		{ id: 1, inputText: 's = "abcabcbb"', outputText: "3" },
		{ id: 2, inputText: 's = "bbbbb"', outputText: "1" },
	],
	`<li><code>0 ≤ s.length ≤ 5 * 10^4</code></li>`
);

export const singleNumber = p(
	"single-number",
	"14. Single Number",
	14,
	`<p>Every element appears twice except one. Find it.</p>`,
	[
		{ id: 1, inputText: "nums = [2,2,1]", outputText: "1" },
		{ id: 2, inputText: "nums = [4,1,2,1,2]", outputText: "4" },
	],
	`<li><code>1 ≤ nums.length ≤ 3 * 10^4</code></li>`
);

export const moveZeroes = p(
	"move-zeroes",
	"15. Move Zeroes",
	15,
	`<p>Move all zeros to end while maintaining relative order of non-zero elements.</p>`,
	[
		{ id: 1, inputText: "nums = [0,1,0,3,12]", outputText: "[1,3,12,0,0]" },
		{ id: 2, inputText: "nums = [0]", outputText: "[0]" },
	],
	`<li><code>1 ≤ nums.length ≤ 10^4</code></li>`
);

export const binarySearch = p(
	"binary-search",
	"16. Binary Search",
	16,
	`<p>Search <code>target</code> in sorted <code>nums</code>. Return index or -1.</p>`,
	[
		{ id: 1, inputText: "nums = [-1,0,3,5,9,12], target = 9", outputText: "4" },
		{ id: 2, inputText: "nums = [-1,0,3,5,9,12], target = 2", outputText: "-1" },
	],
	`<li><code>1 ≤ nums.length ≤ 10^4</code></li>`
);

export const productExceptSelf = p(
	"product-of-array-except-self",
	"17. Product of Array Except Self",
	17,
	`<p>Return array <code>answer</code> where answer[i] is product of all elements except nums[i].</p>`,
	[
		{ id: 1, inputText: "nums = [1,2,3,4]", outputText: "[24,12,8,6]" },
		{ id: 2, inputText: "nums = [-1,1,0,-3,3]", outputText: "[0,0,9,0,0]" },
	],
	`<li><code>2 ≤ nums.length ≤ 10^5</code></li>`
);

export const rotateArray = p(
	"rotate-array",
	"18. Rotate Array",
	18,
	`<p>Rotate <code>nums</code> to the right by <code>k</code> steps.</p>`,
	[
		{ id: 1, inputText: "nums = [1,2,3,4,5,6,7], k = 3", outputText: "[5,6,7,1,2,3,4]" },
		{ id: 2, inputText: "nums = [-1,-100,3,99], k = 2", outputText: "[3,99,-1,-100]" },
	],
	`<li><code>1 ≤ nums.length ≤ 10^5</code></li>`
);

export const intersectionArrays = p(
	"intersection-of-two-arrays-ii",
	"19. Intersection of Two Arrays II",
	19,
	`<p>Return intersection of two arrays with multiplicity.</p>`,
	[
		{ id: 1, inputText: "nums1 = [1,2,2,1], nums2 = [2,2]", outputText: "[2,2]" },
		{ id: 2, inputText: "nums1 = [4,9,5], nums2 = [9,4,8,9,5]", outputText: "[4,9]" },
	],
	`<li>Result may be in any order.</li>`
);

export const palindromeNumber = p(
	"palindrome-number",
	"20. Palindrome Number",
	20,
	`<p>Return <code>true</code> if integer <code>x</code> is a palindrome.</p>`,
	[
		{ id: 1, inputText: "x = 121", outputText: "true" },
		{ id: 2, inputText: "x = -121", outputText: "false" },
	],
	`<li><code>-2^31 ≤ x ≤ 2^31 - 1</code></li>`
);
