import assert from "assert";
import { Problem } from "../types/problem";

const starterCode = `function maxSubArray(nums){
  // Write your code here
};`;

const handler = (fn: (nums: number[]) => number) => {
	const cases = [
		{ nums: [-2, 1, -3, 4, -1, 2, 1, -5, 4], out: 6 },
		{ nums: [1], out: 1 },
		{ nums: [5, 4, -1, 7, 8], out: 23 },
	];
	for (const c of cases) {
		assert.strictEqual(fn(c.nums), c.out);
	}
	return true;
};

export const maximumSubarray: Problem = {
	id: "maximum-subarray",
	title: "Maximum Subarray",
	problemStatement: `<p>Given an integer array <code>nums</code>, find the contiguous subarray with the largest sum and return its sum.</p>`,
	examples: [
		{
			id: 1,
			inputText: "nums = [-2,1,-3,4,-1,2,1,-5,4]",
			outputText: "6",
			explanation: "The subarray [4,-1,2,1] has the largest sum 6.",
		},
		{
			id: 2,
			inputText: "nums = [1]",
			outputText: "1",
		},
	],
	constraints: `<li><code>1 ≤ nums.length ≤ 10<sup>5</sup></code></li>
<li><code>-10<sup>4</sup> ≤ nums[i] ≤ 10<sup>4</sup></code></li>`,
	handlerFunction: handler,
	starterCode,
	order: 6,
	starterFunctionName: "function maxSubArray",
};
