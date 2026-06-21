import { Problem } from "../types/problem";
import { jumpGame } from "./jump-game";
import { maximumSubarray } from "./maximum-subarray";
import { mergeSortedArrays } from "./merge-sorted-arrays";
import { numberOfIslands } from "./number-of-islands";
import { reverseLinkedList } from "./reverse-linked-list";
import { search2DMatrix } from "./search-a-2d-matrix";
import { twoSum } from "./two-sum";
import { validParentheses } from "./valid-parentheses";
import {
	bestTimeToBuySellStock,
	binarySearch,
	climbingStairs,
	containsDuplicate,
	houseRobber,
	intersectionArrays,
	longestSubstring,
	moveZeroes,
	palindromeNumber,
	productExceptSelf,
	rotateArray,
	singleNumber,
} from "./oa-classics";

interface ProblemMap {
	[key: string]: Problem;
}

export const problems: ProblemMap = {
	"two-sum": twoSum,
	"reverse-linked-list": reverseLinkedList,
	"jump-game": jumpGame,
	"search-a-2d-matrix": search2DMatrix,
	"valid-parentheses": validParentheses,
	"maximum-subarray": maximumSubarray,
	"merge-sorted-arrays": mergeSortedArrays,
	"number-of-islands": numberOfIslands,
	"best-time-to-buy-sell-stock": bestTimeToBuySellStock,
	"contains-duplicate": containsDuplicate,
	"climbing-stairs": climbingStairs,
	"house-robber": houseRobber,
	"longest-substring-without-repeating": longestSubstring,
	"single-number": singleNumber,
	"move-zeroes": moveZeroes,
	"binary-search": binarySearch,
	"product-of-array-except-self": productExceptSelf,
	"rotate-array": rotateArray,
	"intersection-of-two-arrays-ii": intersectionArrays,
	"palindrome-number": palindromeNumber,
};
