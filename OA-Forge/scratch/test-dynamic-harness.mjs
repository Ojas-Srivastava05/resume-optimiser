import { getOrIngestDynamicQuestion } from "../src/lib/dynamicQuestions.js";
import { buildCppHarness } from "../src/lib/cppTemplates.js";

// Mock env variables so imports don't crash
process.env.NEXT_PUBLIC_SUPABASE_URL = "https://mwvohdvtxwltzkyuboaz.supabase.co";
process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9";

async function run() {
	const slug = "container-with-most-water";
	console.log(`Fetching dynamic question: ${slug}...`);
	const problem = await getOrIngestDynamicQuestion(slug);
	if (!problem) {
		console.error("Failed to fetch problem");
		return;
	}

	console.log("\nFetched Problem Successfully:");
	console.log(`Title: ${problem.title}`);
	console.log(`Category: ${problem.category}`);
	console.log(`Starter Function: ${problem.starterFunctionName}`);
	console.log(`Starter Code:\n${problem.starterCode}`);

	console.log("\nParsing sample test cases:");
	const tests = problem.examples.map(ex => ({
		input_text: ex.inputText,
		expected_output: ex.outputText
	}));
	console.log(JSON.stringify(tests, null, 2));

	console.log("\nBuilding C++ Harness...");
	const userCppCode = `
#include <bits/stdc++.h>
using namespace std;
class Solution {
public:
    int maxArea(vector<int>& height) {
        int left = 0, right = height.size() - 1;
        int max_val = 0;
        while (left < right) {
            int h = min(height[left], height[right]);
            max_val = max(max_val, h * (right - left));
            if (height[left] < height[right]) left++;
            else right--;
        }
        return max_val;
    }
};
`;

	const harness = buildCppHarness(slug, userCppCode, tests);
	console.log("\nGenerated C++ Harness:\n");
	console.log(harness);
}

run().catch(console.error);
