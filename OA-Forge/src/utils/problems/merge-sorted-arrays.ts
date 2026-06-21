import assert from "assert";
import { Problem } from "../types/problem";

const starterCode = `function merge(nums1, m, nums2, n){
  // Write your code here
};`;

const handler = (fn: (a: number[], m: number, b: number[], n: number) => void) => {
	const nums1 = [1, 2, 3, 0, 0, 0];
	fn(nums1, 3, [2, 5, 6], 3);
	assert.deepStrictEqual(nums1.slice(0, 6), [1, 2, 2, 3, 5, 6]);

	const nums2 = [1];
	fn(nums2, 1, [], 0);
	assert.deepStrictEqual(nums2, [1]);

	const nums3 = [0];
	fn(nums3, 0, [1], 1);
	assert.deepStrictEqual(nums3, [1]);
	return true;
};

export const mergeSortedArrays: Problem = {
	id: "merge-sorted-arrays",
	title: "Merge Sorted Array",
	problemStatement: `<p>You are given two integer arrays <code>nums1</code> and <code>nums2</code>, sorted in non-decreasing order, and integers <code>m</code> and <code>n</code>. Merge <code>nums2</code> into <code>nums1</code> as one sorted array in-place.</p>`,
	examples: [
		{
			id: 1,
			inputText: "nums1 = [1,2,3,0,0,0], m = 3, nums2 = [2,5,6], n = 3",
			outputText: "[1,2,2,3,5,6]",
		},
	],
	constraints: `<li><code>nums1.length == m + n</code></li>
<li><code>0 ≤ m, n ≤ 200</code></li>`,
	handlerFunction: handler,
	starterCode,
	order: 7,
	starterFunctionName: "function merge",
};
