#!/usr/bin/env python3
"""Practice-first OA topic mastery PDF - HackerRank problems only."""

from pathlib import Path

from fpdf import FPDF

OUT = Path(__file__).resolve().parents[1] / "OA-Topic-Mastery-HackerRank.pdf"


class PDF(FPDF):
    def footer(self):
        self.set_y(-12)
        self.set_font("Helvetica", "", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 8, f"Page {self.page_no()}", align="C")


def cell(pdf, text, h=5):
    pdf.multi_cell(0, h, text, new_x="LMARGIN", new_y="NEXT")


def h1(pdf, text):
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(20, 20, 20)
    cell(pdf, text, 8)
    pdf.ln(2)


def h2(pdf, text):
    pdf.ln(2)
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(20, 20, 20)
    cell(pdf, text, 6)
    pdf.ln(1)


def h3(pdf, text):
    pdf.ln(1)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(40, 40, 40)
    cell(pdf, text, 5)


def body(pdf, text):
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(30, 30, 30)
    cell(pdf, text, 5)


def bullet(pdf, text):
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(30, 30, 30)
    cell(pdf, f"  - {text}", 5)


def code(pdf, text):
    pdf.set_font("Courier", "", 8)
    pdf.set_text_color(20, 20, 20)
    pdf.set_fill_color(245, 245, 245)
    pdf.multi_cell(0, 4.2, text, fill=True, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)


def rule(pdf):
    pdf.ln(1)
    y = pdf.get_y()
    pdf.set_draw_color(200, 200, 200)
    pdf.line(pdf.l_margin, y, pdf.w - pdf.r_margin, y)
    pdf.ln(3)


# Format: Name (diff) | slug
# URL: https://www.hackerrank.com/challenges/{slug}/problem
TOPICS = [
    {
        "title": "1. Warm-up (do first, timed)",
        "spot": "Build platform comfort. Still use the no-AI rule.",
        "template": "Read constraints. Write brute if tiny n. Else O(n)/O(n log n).",
        "do": [
            "Sock Merchant (E) | sock-merchant",
            "Counting Valleys (E) | counting-valleys",
            "Jumping on the Clouds (E) | jumping-on-the-clouds",
            "Repeated String (E) | repeated-string",
        ],
        "more": "Interview Preparation Kit -> Warm-up Challenges",
        "done": "All 4 AC in one sitting under 60 min total.",
    },
    {
        "title": "2. Arrays & Hashing",
        "spot": "Counts, lookups, frequency maps, two-sum style.",
        "template": "Use dict/Counter/set.\nfor x in a:\n    if need in seen: ...\n    seen[x] = ...",
        "do": [
            "Hash Tables: Ransom Note (E) | ctci-ransom-note",
            "Two Strings (E) | two-strings",
            "Hash Tables: Ice Cream Parlor (M) | ctci-ice-cream-parlor",
            "Sherlock and Anagrams (M) | sherlock-and-anagrams",
            "Frequency Queries (M) | frequency-queries",
            "Count Triplets (M) | count-triplets-1",
            "Strings: Making Anagrams (E) | ctci-making-anagrams",
        ],
        "more": "IPK -> Dictionaries and Hashmaps",
        "done": "Ice Cream Parlor + Sherlock and Anagrams without peeking.",
    },
    {
        "title": "3. Arrays (manipulation / simulation)",
        "spot": "In-place ops, bribes, swaps, difference array.",
        "template": "Simulate carefully. Prefer O(n). Difference array for range updates.",
        "do": [
            "2D Array - DS (E) | 2d-array",
            "Arrays: Left Rotation (E) | ctci-array-left-rotation",
            "New Year Chaos (M) | new-year-chaos",
            "Minimum Swaps 2 (M) | minimum-swaps-2",
            "Array Manipulation (H) | crush",
        ],
        "more": "IPK -> Arrays",
        "done": "New Year Chaos + Array Manipulation AC (crush = difference array).",
    },
    {
        "title": "4. Two Pointers / Sliding Window (PRIORITY)",
        "spot": "Contiguous segment, pairs with difference k, min unfairness window.",
        "template": "l = 0\nfor r in range(n):\n    add a[r]\n    while INVALID:\n        remove a[l]; l += 1\n    update ans\n# or sort then window of size k",
        "do": [
            "Subarray Division (E) | the-birthday-bar",
            "Picking Numbers (E) | picking-numbers",
            "Pairs (M) | pairs",
            "Max Min (M) | angry-children",
            "Minimum Absolute Difference (E) | minimum-absolute-difference-in-an-array",
            "Sherlock and Array (E) | sherlock-and-array",
            "Special String Again (M) | special-palindrome-again",
            "Beautiful Triplets (E) | beautiful-triplets",
        ],
        "more": "Search Algorithms domain for 'subarray' / IPK Search + Greedy Max Min",
        "done": "Pairs + Max Min + Subarray Division cold. State expand/shrink rule each time.",
    },
    {
        "title": "5. Binary Search / Search",
        "spot": "Sorted search, rank queries, min unfairness after sort.",
        "template": "lo, hi = ...\nwhile lo < hi:\n    mid = (lo+hi)//2\n    if check(mid): hi = mid\n    else: lo = mid + 1",
        "do": [
            "Pairs (M) | pairs",
            "Ice Cream Parlor (M) | ctci-ice-cream-parlor",
            "Climbing the Leaderboard (M) | climbing-the-leaderboard",
            "Hackerland Radio Transmitters (M) | hackerland-radio-transmitters",
            "Maximum Subarray Sum (H) | maximum-subarray-sum (stretch)",
        ],
        "more": "Algorithms -> Search",
        "done": "Climbing the Leaderboard with binary search, not O(n^2).",
    },
    {
        "title": "6. Stack / Queue",
        "spot": "Brackets, queue via stacks, histogram rectangle.",
        "template": "st = []\nfor x in s:\n    if match(st, x): st.pop()\n    else: st.append(x)",
        "do": [
            "Balanced Brackets (M) | balanced-brackets",
            "Queues: A Tale of Two Stacks (M) | ctci-queue-using-two-stacks",
            "Equal Stacks (E) | equal-stacks",
            "Largest Rectangle (M) | largest-rectangle",
            "Castle on the Grid (M) | castle-on-the-grid",
            "Poisonous Plants (H) | poisonous-plants (stretch)",
        ],
        "more": "IPK -> Stacks and Queues",
        "done": "Balanced Brackets + Largest Rectangle attempted; brackets AC cold.",
    },
    {
        "title": "7. Sorting + Greedy",
        "spot": "Sort then one pass. Local choice optimal.",
        "template": "a.sort()\n# one pass / window / two pointers",
        "do": [
            "Mark and Toys (E) | mark-and-toys",
            "Sorting: Bubble Sort (E) | ctci-bubble-sort",
            "Luck Balance (E) | luck-balance",
            "Greedy Florist (M) | greedy-florist",
            "Max Min (M) | angry-children",
            "Minimum Absolute Difference (E) | minimum-absolute-difference-in-an-array",
            "Sorting: Comparator (M) | ctci-comparator-sorting",
            "Merge Sort: Counting Inversions (H) | ctci-merge-sort",
        ],
        "more": "IPK -> Sorting + Greedy Algorithms",
        "done": "Greedy Florist + Max Min without editorial.",
    },
    {
        "title": "8. Strings",
        "spot": "Frequency, anagrams, consecutive deletes, validity.",
        "template": "Counter / two-pointer on chars / DP for LCS-style.",
        "do": [
            "Alternating Characters (E) | alternating-characters",
            "Making Anagrams (E) | ctci-making-anagrams",
            "Sherlock and the Valid String (M) | sherlock-and-valid-string",
            "Special String Again (M) | special-palindrome-again",
            "Common Child (M) | common-child",
            "Sherlock and Anagrams (M) | sherlock-and-anagrams",
            "String Construction (E) | string-construction",
        ],
        "more": "IPK -> String Manipulation",
        "done": "Valid String + Common Child (LCS) AC.",
    },
    {
        "title": "9. Linked Lists",
        "spot": "Pointer rewiring. Draw first.",
        "template": "prev, cur = None, head\nwhile cur:\n    nxt = cur.next\n    cur.next = prev\n    prev, cur = cur, nxt",
        "do": [
            "Detect a Cycle (E) | ctci-linked-list-cycle",
            "Insert a node at a specific position (E) | insert-a-node-at-a-specific-position-in-a-linked-list",
            "Insert into Sorted Doubly Linked List (E) | insert-a-node-into-a-sorted-doubly-linked-list",
            "Reverse a Doubly Linked List (E) | reverse-a-doubly-linked-list",
            "Find Merge Point of Two Lists (E) | find-the-merge-point-of-two-joined-linked-lists",
        ],
        "more": "IPK -> Linked Lists",
        "done": "Cycle + Merge Point cold.",
    },
    {
        "title": "10. Trees",
        "spot": "Height, BST check, LCA.",
        "template": "def dfs(node):\n    if not node: return base\n    L, R = dfs(node.left), dfs(node.right)\n    return combine(node, L, R)",
        "do": [
            "Tree: Height of a Binary Tree (E) | tree-height-of-a-binary-tree",
            "Tree: Huffman Decoding (M) | tree-huffman-decoding",
            "Is This a Binary Search Tree? (M) | ctci-is-binary-search-tree",
            "BST: Lowest Common Ancestor (E) | binary-search-tree-lowest-common-ancestor",
            "Tree: Level Order Traversal (E) | tree-level-order-traversal",
            "Tree: Top View (E) | tree-top-view",
        ],
        "more": "IPK -> Trees / Data Structures -> Trees",
        "done": "BST check + LCA without looking.",
    },
    {
        "title": "11. Graphs (BFS / DFS)",
        "spot": "Shortest unweighted, connected components, grid flood fill.",
        "template": "q = deque([s]); dist[s]=0\nwhile q:\n    u = q.popleft()\n    for v in g[u]:\n        if v not in dist:\n            dist[v]=dist[u]+1; q.append(v)",
        "do": [
            "BFS: Shortest Reach in a Graph (H) | ctci-bfs-shortest-reach",
            "DFS: Connected Cell in a Grid (H) | ctci-connected-cell-in-a-grid",
            "Roads and Libraries (M) | torque-and-development",
            "Journey to the Moon (M) | journey-to-the-moon",
            "Find the Nearest Clone (M) | find-the-nearest-clone",
            "Even Tree (M) | even-tree",
            "Castle on the Grid (M) | castle-on-the-grid",
        ],
        "more": "IPK -> Graphs",
        "done": "BFS Shortest Reach + Connected Cell AC.",
    },
    {
        "title": "12. Recursion / Backtracking / DP",
        "spot": "Ways to climb, optimal subsequence, candies distribution.",
        "template": "dp[i] = best over previous states\n# or recurse + memo",
        "do": [
            "Recursion: Fibonacci Numbers (E) | ctci-fibonacci-numbers",
            "Recursion: Davis' Staircase (M) | ctci-recursive-staircase",
            "Max Array Sum (M) | max-array-sum",
            "Candies (M) | candies",
            "Abbreviation (M) | abbr",
            "Common Child (M) | common-child",
            "The Coin Change Problem (M) | coin-change",
            "Equal (M) | equal",
        ],
        "more": "IPK -> Recursion and Backtracking + Dynamic Programming",
        "done": "Davis Staircase + Candies + Max Array Sum: write state before code.",
    },
    {
        "title": "13. Heap / Priority Queue",
        "spot": "Running median, kth, merge by cost.",
        "template": "import heapq\nheapq.heappush(h, x)\nheapq.heappop(h)",
        "do": [
            "QHEAP1 (E) | qheap1",
            "Jesse and Cookies (E) | jesse-and-cookies",
            "Find the Running Median (H) | find-the-running-median",
            "Minimum Average Waiting Time (H) | minimum-average-waiting-time (stretch)",
        ],
        "more": "Data Structures -> Heap",
        "done": "Jesse and Cookies + Running Median attempted.",
    },
]


def topic_block(pdf, t):
    h2(pdf, t["title"])
    h3(pdf, "Spot it")
    body(pdf, t["spot"])
    h3(pdf, "Template")
    code(pdf, t["template"])
    h3(pdf, "Do these (HackerRank)")
    for p in t["do"]:
        bullet(pdf, p)
    h3(pdf, "More")
    body(pdf, t["more"])
    h3(pdf, "Topic done when")
    body(pdf, t["done"])
    rule(pdf)


def build():
    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=16)
    pdf.add_page()

    h1(pdf, "OA Topic Mastery - HackerRank Practice")
    body(
        pdf,
        "Topic-wise HackerRank list for OA practice. Mostly Interview Preparation Kit + "
        "Algorithms classics. Practice beats planning. Check off. No fluff.",
    )
    pdf.ln(2)

    h2(pdf, "How to open a problem")
    code(
        pdf,
        "slug -> https://www.hackerrank.com/challenges/{slug}/problem\n"
        "Example: pairs -> https://www.hackerrank.com/challenges/pairs/problem\n"
        "IPK hub: https://www.hackerrank.com/interview/interview-preparation-kit",
    )

    h2(pdf, "Rules")
    bullet(pdf, "No AI until AFTER you submit (or timebox ends).")
    bullet(pdf, "Timer: Easy 20-30 min. Medium 35-50. Hard 60-75.")
    bullet(pdf, "Before code: name the pattern + write invariant in one line.")
    bullet(pdf, "Stuck 20 min: brute force, then optimize. Editorial only after attempt.")
    bullet(pdf, "Failed = re-solve in 2-3 days blank. Need help again = does not count.")
    bullet(pdf, "Finish topic list before skipping. Sliding window / pairs is priority.")
    rule(pdf)

    h2(pdf, "Order")
    body(
        pdf,
        "1 Warm-up -> 2 Hashing -> 3 Arrays -> 4 Two Pointers/Window -> "
        "5 Binary Search -> 6 Stack/Queue -> 7 Greedy/Sort -> 8 Strings -> "
        "9 Linked Lists -> 10 Trees -> 11 Graphs -> 12 DP -> 13 Heap",
    )
    body(
        pdf,
        "Short on time: finish 1-5 + 6 + 11 + 12. Many company OAs use HackerRank UI - "
        "practice here so the platform is not foreign.",
    )
    rule(pdf)

    h2(pdf, "One problem flow")
    code(
        pdf,
        "1. Classify pattern (2 min)\n"
        "2. Invariant / what you track (2 min)\n"
        "3. Dry-run sample input by hand (3 min)\n"
        "4. Code + edge cases from constraints\n"
        "5. Submit. Only then read discussions for gaps\n"
        "6. Log: pattern | trigger | bug type",
    )
    rule(pdf)

    for t in TOPICS:
        if pdf.get_y() > 245:
            pdf.add_page()
        topic_block(pdf, t)

    h2(pdf, "Weekly volume")
    bullet(pdf, "Weekdays: 1-2 timed HR problems from current topic.")
    bullet(pdf, "Weekend: full IPK section timed, or 3 mediums / 2 hours, no AI.")
    bullet(pdf, "After IPK core: Algorithms domain filter by topic for extras.")
    rule(pdf)

    h2(pdf, "Sources")
    bullet(pdf, "HackerRank Interview Preparation Kit (official company OA-style set).")
    bullet(pdf, "Algorithms / Data Structures domain classics (Pairs, Max Min, Candies...).")
    bullet(pdf, "Same topic order as the Codeforces practice sheet for parallel drilling.")
    pdf.ln(3)
    body(pdf, "Open HackerRank IPK. Start topic 4 if window/pairs is the hole. Submit.")

    pdf.output(str(OUT))
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    build()
