import assert from "assert";
import { Problem } from "../types/problem";

const starterCode = `function numIslands(grid){
  // Write your code here
};`;

const handler = (fn: (grid: string[][]) => number) => {
	const g1 = [
		["1", "1", "1", "1", "0"],
		["1", "1", "0", "1", "0"],
		["1", "1", "0", "0", "0"],
		["0", "0", "0", "0", "0"],
	];
	assert.strictEqual(fn(g1.map((r) => [...r])), 1);

	const g2 = [
		["1", "1", "0", "0", "0"],
		["1", "1", "0", "0", "0"],
		["0", "0", "1", "0", "0"],
		["0", "0", "0", "1", "1"],
	];
	assert.strictEqual(fn(g2.map((r) => [...r])), 3);
	return true;
};

export const numberOfIslands: Problem = {
	id: "number-of-islands",
	title: "Number of Islands",
	problemStatement: `<p>Given an <code>m × n</code> 2D binary grid which represents a map of <code>'1'</code>s (land) and <code>'0'</code>s (water), return the number of islands.</p>
<p>An island is surrounded by water and is formed by connecting adjacent lands horizontally or vertically.</p>`,
	examples: [
		{
			id: 1,
			inputText: `grid = [
  ["1","1","1","1","0"],
  ["1","1","0","1","0"],
  ["1","1","0","0","0"],
  ["0","0","0","0","0"]
]`,
			outputText: "1",
		},
	],
	constraints: `<li><code>m == grid.length</code></li>
<li><code>n == grid[i].length</code></li>
<li><code>1 ≤ m, n ≤ 300</code></li>`,
	handlerFunction: handler,
	starterCode,
	order: 8,
	starterFunctionName: "function numIslands",
};
