export const cppStarters: Record<string, string> = {
	"two-sum": `#include <bits/stdc++.h>
using namespace std;
class Solution {
public:
    vector<int> twoSum(vector<int>& nums, int target) { return {}; }
};`,
	"maximum-subarray": `#include <bits/stdc++.h>
using namespace std;
class Solution {
public:
    int maxSubArray(vector<int>& nums) { return 0; }
};`,
	"merge-sorted-arrays": `#include <bits/stdc++.h>
using namespace std;
class Solution {
public:
    void merge(vector<int>& nums1, int m, vector<int>& nums2, int n) {}
};`,
	"jump-game": `#include <bits/stdc++.h>
using namespace std;
class Solution {
public:
    bool canJump(vector<int>& nums) { return false; }
};`,
	"valid-parentheses": `#include <bits/stdc++.h>
using namespace std;
class Solution {
public:
    bool isValid(string s) { return false; }
};`,
	"search-a-2d-matrix": `#include <bits/stdc++.h>
using namespace std;
class Solution {
public:
    bool searchMatrix(vector<vector<int>>& matrix, int target) { return false; }
};`,
	"number-of-islands": `#include <bits/stdc++.h>
using namespace std;
class Solution {
public:
    int numIslands(vector<vector<char>>& grid) { return 0; }
};`,
	"reverse-linked-list": `#include <bits/stdc++.h>
using namespace std;
struct ListNode { int val; ListNode* next; ListNode(int x): val(x), next(nullptr) {} };
class Solution {
public:
    ListNode* reverseList(ListNode* head) { return nullptr; }
};`,
	"best-time-to-buy-sell-stock": `#include <bits/stdc++.h>
using namespace std;
class Solution {
public:
    int maxProfit(vector<int>& prices) { return 0; }
};`,
	"contains-duplicate": `#include <bits/stdc++.h>
using namespace std;
class Solution {
public:
    bool containsDuplicate(vector<int>& nums) { return false; }
};`,
	"climbing-stairs": `#include <bits/stdc++.h>
using namespace std;
class Solution {
public:
    int climbStairs(int n) { return 0; }
};`,
	"house-robber": `#include <bits/stdc++.h>
using namespace std;
class Solution {
public:
    int rob(vector<int>& nums) { return 0; }
};`,
	"longest-substring-without-repeating": `#include <bits/stdc++.h>
using namespace std;
class Solution {
public:
    int lengthOfLongestSubstring(string s) { return 0; }
};`,
	"single-number": `#include <bits/stdc++.h>
using namespace std;
class Solution {
public:
    int singleNumber(vector<int>& nums) { return 0; }
};`,
	"move-zeroes": `#include <bits/stdc++.h>
using namespace std;
class Solution {
public:
    void moveZeroes(vector<int>& nums) {}
};`,
	"binary-search": `#include <bits/stdc++.h>
using namespace std;
class Solution {
public:
    int search(vector<int>& nums, int target) { return -1; }
};`,
	"product-of-array-except-self": `#include <bits/stdc++.h>
using namespace std;
class Solution {
public:
    vector<int> productExceptSelf(vector<int>& nums) { return {}; }
};`,
	"rotate-array": `#include <bits/stdc++.h>
using namespace std;
class Solution {
public:
    void rotate(vector<int>& nums, int k) {}
};`,
	"intersection-of-two-arrays-ii": `#include <bits/stdc++.h>
using namespace std;
class Solution {
public:
    vector<int> intersect(vector<int>& nums1, vector<int>& nums2) { return {}; }
};`,
	"palindrome-number": `#include <bits/stdc++.h>
using namespace std;
class Solution {
public:
    bool isPalindrome(int x) { return false; }
};`,
};

function lit(value: unknown) {
	return JSON.stringify(value);
}

function vector(nums: number[]) {
	return `{${nums.join(",")}}`;
}

function matrix(rows: number[][]) {
	return `{${rows.map(vector).join(",")}}`;
}

function charMatrix(rows: string[][]) {
	return `{${rows.map((row) => `{${row.map((v) => `'${v}'`).join(",")}}`).join(",")}}`;
}

function sortedVector(nums: number[]) {
	return `sortVec(${vector(nums)})`;
}

type HarnessBuilder = (input: Record<string, unknown>, expected: unknown, index: number) => string;

const harnessBuilders: Record<string, HarnessBuilder> = {
	"two-sum": (input, expected, i) => `{
    vector<int> nums = ${vector(input.nums as number[])};
    vector<int> expected = ${vector(expected as number[])};
    auto got = sol.twoSum(nums, ${input.target});
    if (got != expected) fail(${i + 1});
}`,
	"maximum-subarray": (input, expected, i) => `{
    vector<int> nums = ${vector(input.nums as number[])};
    if (sol.maxSubArray(nums) != ${expected}) fail(${i + 1});
}`,
	"merge-sorted-arrays": (input, expected, i) => `{
    vector<int> nums1 = ${vector(input.nums1 as number[])};
    vector<int> nums2 = ${vector(input.nums2 as number[])};
    vector<int> expected = ${vector(expected as number[])};
    sol.merge(nums1, ${input.m}, nums2, ${input.n});
    if (nums1 != expected) fail(${i + 1});
}`,
	"jump-game": (input, expected, i) => `{
    vector<int> nums = ${vector(input.nums as number[])};
    if (sol.canJump(nums) != ${expected ? "true" : "false"}) fail(${i + 1});
}`,
	"valid-parentheses": (input, expected, i) => `{
    if (sol.isValid(${lit(input.s)}) != ${expected ? "true" : "false"}) fail(${i + 1});
}`,
	"search-a-2d-matrix": (input, expected, i) => `{
    vector<vector<int>> matrix = ${matrix(input.matrix as number[][])};
    if (sol.searchMatrix(matrix, ${input.target}) != ${expected ? "true" : "false"}) fail(${i + 1});
}`,
	"number-of-islands": (input, expected, i) => `{
    vector<vector<char>> grid = ${charMatrix(input.grid as string[][])};
    if (sol.numIslands(grid) != ${expected}) fail(${i + 1});
}`,
	"reverse-linked-list": (input, expected, i) => `{
    vector<int> vals = ${vector(input.vals as number[])};
    ListNode* head = buildList(vals);
    ListNode* rev = sol.reverseList(head);
    vector<int> got = listToVec(rev);
    vector<int> expected = ${vector(expected as number[])};
    if (got != expected) fail(${i + 1});
}`,
	"best-time-to-buy-sell-stock": (input, expected, i) => `{
    vector<int> prices = ${vector(input.prices as number[])};
    if (sol.maxProfit(prices) != ${expected}) fail(${i + 1});
}`,
	"contains-duplicate": (input, expected, i) => `{
    vector<int> nums = ${vector(input.nums as number[])};
    if (sol.containsDuplicate(nums) != ${expected ? "true" : "false"}) fail(${i + 1});
}`,
	"climbing-stairs": (input, expected, i) => `{
    if (sol.climbStairs(${input.n}) != ${expected}) fail(${i + 1});
}`,
	"house-robber": (input, expected, i) => `{
    vector<int> nums = ${vector(input.nums as number[])};
    if (sol.rob(nums) != ${expected}) fail(${i + 1});
}`,
	"longest-substring-without-repeating": (input, expected, i) => `{
    if (sol.lengthOfLongestSubstring(${lit(input.s)}) != ${expected}) fail(${i + 1});
}`,
	"single-number": (input, expected, i) => `{
    vector<int> nums = ${vector(input.nums as number[])};
    if (sol.singleNumber(nums) != ${expected}) fail(${i + 1});
}`,
	"move-zeroes": (input, expected, i) => `{
    vector<int> nums = ${vector(input.nums as number[])};
    vector<int> expected = ${vector(expected as number[])};
    sol.moveZeroes(nums);
    if (nums != expected) fail(${i + 1});
}`,
	"binary-search": (input, expected, i) => `{
    vector<int> nums = ${vector(input.nums as number[])};
    if (sol.search(nums, ${input.target}) != ${expected}) fail(${i + 1});
}`,
	"product-of-array-except-self": (input, expected, i) => `{
    vector<int> nums = ${vector(input.nums as number[])};
    vector<int> expected = ${vector(expected as number[])};
    auto got = sol.productExceptSelf(nums);
    if (got != expected) fail(${i + 1});
}`,
	"rotate-array": (input, expected, i) => `{
    vector<int> nums = ${vector(input.nums as number[])};
    vector<int> expected = ${vector(expected as number[])};
    sol.rotate(nums, ${input.k});
    if (nums != expected) fail(${i + 1});
}`,
	"intersection-of-two-arrays-ii": (input, expected, i) => `{
    vector<int> nums1 = ${vector(input.nums1 as number[])};
    vector<int> nums2 = ${vector(input.nums2 as number[])};
    auto got = sortVec(sol.intersect(nums1, nums2));
    auto expected = ${sortedVector(expected as number[])};
    if (got != expected) fail(${i + 1});
}`,
	"palindrome-number": (input, expected, i) => `{
    if (sol.isPalindrome(${input.x}) != ${expected ? "true" : "false"}) fail(${i + 1});
}`,
};

const sortVecHelper = `vector<int> sortVec(vector<int> v) { sort(v.begin(), v.end()); return v; }`;

const listHelpers = `
ListNode* buildList(const vector<int>& vals) {
    ListNode dummy(0);
    ListNode* tail = &dummy;
    for (int v : vals) { tail->next = new ListNode(v); tail = tail->next; }
    return dummy.next;
}
vector<int> listToVec(ListNode* head) {
    vector<int> out;
    while (head) { out.push_back(head->val); head = head->next; }
    return out;
}`;

function helperBlock(slug: string) {
	if (slug === "reverse-linked-list") return listHelpers;
	if (slug === "intersection-of-two-arrays-ii") return sortVecHelper;
	return "";
}

export function buildCppHarness(slug: string, userCode: string, tests: { input_text: string; expected_output: string }[]) {
	const builder = harnessBuilders[slug];
	if (!builder) throw new Error(`No C++ harness for ${slug}`);

	const assertions = tests
		.map((test, index) => {
			const input = JSON.parse(test.input_text) as Record<string, unknown>;
			const expected = JSON.parse(test.expected_output);
			return builder(input, expected, index);
		})
		.join("\n");

	return `${userCode}
${helperBlock(slug)}

void fail(int caseNo) {
    cout << "WA case " << caseNo << endl;
    exit(1);
}

int main() {
    Solution sol;
${assertions}
    cout << "AC" << endl;
    return 0;
}`;
}
