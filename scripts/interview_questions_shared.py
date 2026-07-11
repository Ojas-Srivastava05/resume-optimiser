"""Shared interview question banks for prep + answer-key generators."""

from generate_brutal_interview_prep import (
    COMPANIES,
    CS_FUNDAMENTALS,
    PROJECT_QUESTIONS,
    UNIVERSAL_BEHAVIORAL,
)

COMPANY_EXTRA = {
    "Stripe": [
        ("Why Stripe and not a Indian fintech?", [
            "How does Stripe differ from Razorpay/Cashfree architecturally?",
            "Name a Stripe product you'd want to work on.",
        ]),
        ("Tell us about you + fit at Stripe (application essay live).", [
            "Cut your answer to 30 seconds.",
            "Remove all hackathon buzzwords.",
            "Add one failure story.",
        ]),
        ("Design: make Checkout errors understandable to merchants.", [
            "API vs UI ownership?",
            "Internationalization?",
            "Observability metrics?",
        ]),
        ("Coding: implement idempotent POST /v1/charges retry handler.", [
            "DB schema?",
            "Duplicate webhook delivery?",
        ]),
        ("Read a pull request diff and critique it.", [
            "What tests are missing?",
            "Naming?",
            "Security?",
        ]),
    ],
    "GE HealthCare": [
        ("Why digital healthcare / visualization platform?", [
            "Regulated environment mindset?",
            "Patient safety analogy in software?",
        ]),
        ("SDLC walkthrough for a feature you shipped.", [
            "Unit vs integration vs validation?",
            "Traceability for QA?",
        ]),
        ("On-site Bengaluru 100%---constraints?", [
            "Relocation from Surat?",
            "Semester conflicts?",
        ]),
        ("Testing philosophy for medical-adjacent software.", [
            "You didn't work on PHI---how do you reason about risk anyway?",
        ]),
    ],
    "Cisco": [
        ("Explain TCP handshake using your project's HTTP calls.", [
            "Where does TLS fit?",
            "What causes tail latency on mobile networks?",
        ]),
        ("Secure coding at IFFCO---JWT, validation.", [
            "STRIDE threat model quick pass.",
            "Common Cisco CVE classes?",
        ]),
        ("Design microservice for device telemetry ingestion.", [
            "Scale to 1M devices?",
            "Backpressure?",
        ]),
    ],
    "Wells Fargo": [
        ("Why banking? Why Wells Fargo program structure?", [
            "Compliance comfort?",
            "Example of following process under pressure?",
        ]),
        ("SQL: write query for top-N workflows by daily volume.", [
            "Index?",
            "Explain plan?",
        ]),
        ("Situational: teammate shortcuts security review.", [
            "What do you do Monday morning?",
        ]),
        ("Java vs Node---which for enterprise banking services?", [
            "Transaction boundaries?",
        ]),
    ],
    "Google": [
        ("GOC prep: arrays, strings, greedy, graphs medium.", [
            "Optimize from O(n^2) to O(n log n) with proof sketch.",
        ]),
        ("LogiFlow OAuth + Cloud Run cold starts---deep dive.", [
            "SLO definition?",
            "Error budget?",
        ]),
        ("Googleyness: disagreement with authority.", [
            "Data you brought?",
            "Outcome?",
        ]),
        ("Estimate: storage for 9,526 stations x daily events.", [
            "Fermi decomposition live.",
        ]),
    ],
    "Microsoft": [
        ("OOP design: parking lot / LRU / logger.", [
            "SOLID violation example from your code?",
        ]),
        ("Azure vs GCP---what did you choose and why?", [
            "Vendor lock-in concerns?",
        ]),
        ("Team conflict in hackathon team.", [
            "Role clarity?",
        ]),
    ],
    "Electronic Arts (EADP)": [
        ("Design load test for game login spike.", [
            "Metrics: p95, error rate, saturation.",
            "Tools you'd use?",
        ]),
        ("Career Automation Stack---map components to test infra.", [
            "Schedulers, artifacts, flaky tests.",
        ]),
        ("Debug: WebSocket drops at 80 concurrent users.", [
            "Profiling steps ordered.",
        ]),
        ("Why systest instead of feature dev?", [
            "Trap: don't sound like you want EA only for games.",
        ]),
    ],
    "Honeywell": [
        ("Industrial automation interest---beyond buzzwords.", [
            "IIoT example from your work?",
        ]),
        ("Data analysis story from LogiFlow model.", [
            "Business decision informed by model?",
        ]),
        ("Reliability in cooperative enterprise (IFFCO).", [
            "Stakeholder communication?",
        ]),
    ],
    "AlphaGrep (Core SWE)": [
        ("Implement fast parsing of market data feed (toy).", [
            "Memory allocations?",
            "Branch prediction?",
        ]),
        ("C++: vector growth, iterator invalidation.", [
            "Real bug you avoided?",
        ]),
        ("Linux: strace/ltrace usage on judge binary.", [
            "Syscalls allowed in sandbox?",
        ]),
    ],
    "AlphaGrep (Quant)": [
        ("Explain gradient boosting to a trader.", [
            "Overfitting on 15,650 train-days?",
            "Feature importance?",
        ]),
        ("Probability: expected rolls until double six.", [
            "Markov chain version?",
        ]),
        ("Personal equities experience---specific thesis you tested.", [
            "How did you falsify yourself?",
        ]),
    ],
    "Amazon ML Summer School": [
        ("Bias-variance on LogiFlow delay model.", [
            "Cross-val strategy?",
            "Leakage sources?",
        ]),
        ("Why MLSS over self-study?", [
            "What gap will Amazon scientists fill?",
        ]),
        ("Derive gradient descent update for linear regression.", [
            "Learning rate sensitivity?",
        ]),
    ],
    "Flipkart Grid 8.0": [
        ("Design flash sale inventory system.", [
            "Overselling prevention?",
            "Cache coherency?",
        ]),
        ("LogiFlow as supply chain---draw architecture.", [
            "Bottleneck at 10x traffic?",
        ]),
    ],
    "Goldman Sachs": [
        ("Probability + mental math warm-up.", [
            "Options intuition (even if basic).",
        ]),
        ("Engineering rigor in CI/CD.", [
            "Rollback strategy?",
        ]),
        ("Why finance + engineering hybrid?", [
            "GS culture fit?",
            "Risk vs reward in engineering?",
        ]),
    ],
    "Angel One": [
        ("Build rate-limited market data API.", [
            "Auth?",
            "Audit logs?",
        ]),
        ("Fintech compliance awareness (India).", [
            "SEBI basics you actually read?",
        ]),
    ],
}

HR_SCREEN = [
    ("Walk me through your background and what you have been working on recently.", [
        "Cut your answer to 90 seconds. Lead with degree + IFFCO + one flagship project.",
        "Do NOT open with hackathon rankings before establishing engineering work.",
        "If you mention Vibe2Ship, say outcome (Top 20) in one clause only.",
    ]),
    ("Clarify IFFCO timing and what you actually built there.", [
        "One month after first year vs last summer---get dates right.",
        "Tech stack must match resume (Node/Express/MySQL vs HTML/Bootstrap).",
        "What did YOU own vs mentor? Name 2 APIs or 2 bugs with outcomes.",
    ]),
    ("Walk through debugging when websites had broken parts / errors.", [
        "Reproduce -> DevTools -> isolate FE vs BE -> logs -> fix -> PR.",
        "Give one farmer data-inconsistency example with validation fix.",
        "How did you test before merge?",
    ]),
    ("LogiFlow: your specific role and backend architecture?", [
        "Answer in 2 min: problem, your railways pipeline, stack, metrics.",
        "Comparator vs hybrid engines---who built what?",
        "Do not narrate entire Indian logistics industry first.",
    ]),
    ("Where did railway data come from? How stored and queried?", [
        "2017 base CSV + scraping + 3 APIs---be honest about frugality.",
        "Schema: stations, trains, corridors---high level ER diagram.",
        "N-squared station pairing---complexity and why acceptable.",
    ]),
    ("XGBoost / delay model: features, validation, accuracy metric?", [
        "Say MAE 22.7 min consistently (not mixed 80% / 65% without defining metric).",
        "5-fold CV purpose in one sentence.",
        "Train/test leakage risks in time-series delay data?",
    ]),
    ("Redis + GCP: what was cached, async workers, API response shape?", [
        "Cache key design: origin, dest, weight bucket.",
        "Return cost fast; run ML delay async; update when ready.",
        "Draw JSON response---do NOT say random words like SLM.",
    ]),
    ("Collaboration: code review, feedback, teamwork examples.", [
        "STAR: LogiFlow pipeline split + Redis compromise with teammate.",
        "STAR: IFFCO PR feedback on validation layer.",
        "How do you disagree on technical decisions?",
    ]),
]

EXTRA_BEHAVIORAL = [
    ("Tell me about yourself --- 30s / 90s / 3min versions.", [
        "Which version for a bar raiser?",
        "Remove all awards---still compelling?",
    ]),
    ("Why intern now vs focusing on CP?", [
        "Is internship just resume padding?",
        "What if you fail to convert?",
    ]),
    ("Conflict with a teammate who wouldn't review your PR.", [
        "Exact Slack message you'd send.",
        "When do you involve the mentor?",
    ]),
    ("Time you shipped something you knew was wrong.", [
        "Technical debt accepted?",
        "How did you document it?",
    ]),
    ("Most embarrassing bug in front of users.", [
        "Hotfix process?",
        "Communication to stakeholders?",
    ]),
    ("Describe LogiFlow team dynamics. Who argued with you?", [
        "What did you lose on?",
        "What did you win on?",
    ]),
    ("Community Hero solo---prove you didn't outsource work.", [
        "Hardest integration point?",
        "Git history story?",
    ]),
    ("Why SVNIT and not IIT?", [
        "Defensive answer trap---stay factual.",
    ]),
    ("CGPA 9.20---why not higher?", [
        "Which course pulled you down?",
        "Learning vs grades?",
    ]),
    ("McKinsey Forward Fellow---what did it change in you?", [
        "Not name-dropping---substance?",
    ]),
    ("Mentoring at Nexus---tell about a junior who struggled.", [
        "How do you measure mentor success?",
    ]),
    ("ACM events you organized---numbers, outcomes.", [
        "Budget? Sponsors? Failures?",
    ]),
    ("RangRiti Technical Lead---what broke on demo day?", [
        "Rollback plan?",
    ]),
    ("If we Google your GitHub right now, what will we critique?", [
        "Open issues?",
        "Test coverage gaps?",
    ]),
    ("What are you building this week?", [
        "Not vaporware---show commit cadence.",
    ]),
]

HR_LOGISTICS = [
    ("Summer 2027 availability: exact dates.", [
        "May--Aug full-time?",
        "Exam conflicts in SVNIT calendar?",
    ]),
    ("Bengaluru relocation from Surat.", [
        "Housing plan?",
        "Budget?",
        "Family constraints?",
    ]),
    ("Will you accept hybrid in Hyderabad if Bengaluru fails?", [
        "Preference ranking of cities?",
    ]),
    ("Stipend expectations.", [
        "Trap: don't anchor too high for intern; show flexibility.",
    ]),
    ("Other offers / pipelines in flight.", [
        "Honesty without sounding desperate.",
    ]),
    ("Security clearance / background check issues?", [
        "Any legal incidents? Default no.",
    ]),
    ("Need academic credit for internship?", [
        "SVNIT internship policy awareness?",
    ]),
    ("Rejoin as PPO goal---explicit or exploratory?", [
        "Company-specific honesty.",
    ]),
]

RESUME_LINES = [
    ("Bullet: 50+ daily workflows --- quantify users and frequency.", [
        "Per workflow runtime?",
        "Manual time saved?",
    ]),
    ("Bullet: 10+ REST APIs --- pick 3 methods + status codes.", [
        "429 handling?",
        "Pagination?",
    ]),
    ("Bullet: 100--400 ms read paths --- measurement harness.", [
        "wrk/k6?",
        "Synthetic vs real?",
    ]),
    ("Bullet: 580+ corridors --- data source provenance.", [
        "Government open data?",
        "Cleaning pipeline?",
    ]),
    ("Bullet: 9,526 stations --- schema normalization.", [
        "Duplicates across zones?",
    ]),
    ("Bullet: 15,650 train-days --- label definition.", [
        "What counts as a train-day?",
    ]),
    ("Bullet: MAE 22.7 min --- baseline comparison.", [
        "Naive baseline?",
        "Business acceptable error?",
    ]),
    ("Bullet: 100/100 pytest --- are tests too brittle?", [
        "Mutation testing awareness?",
    ]),
    ("Bullet: 14K+ question occurrences --- legal/ethical sourcing.", [
        "DMCA concern?",
    ]),
    ("Bullet: 5.5K+ test cases --- generation vs manual.", [
        "False AC risk?",
    ]),
    ("Bullet: 965+ companies scout --- maintenance burden.", [
        "Broken scrapers weekly?",
    ]),
    ("Bullet: LeetCode Knight 2048 --- contest vs practice split.", [
        "When did you peak?",
        "Trend last 6 months?",
    ]),
    ("Bullet: Vibe2Ship Top 20 --- team size vs solo claim.", [
        "What did judges score?",
    ]),
    ("Bullet: GSC Top 106 --- how many teams globally?", [
        "Your rank within team?",
    ]),
]

LEADERSHIP = [
    ("ACM Executive Member---conflict with faculty advisor.", [
        "Budget overrun story?",
    ]),
    ("Nexus DSA Mentor---curriculum you designed.", [
        "Beginner failure modes?",
        "How many mentees?",
    ]),
    ("Organizing contest---cheating detection.", [
        "Plagiarism tools?",
        "Appeals process?",
    ]),
    ("Balancing mentorship vs your own CP grind.", [
        "Time audit weekly?",
    ]),
]

RAPID_FIRE = [
    "Big-O of your favorite LogiFlow endpoint.",
    "CAP theorem---where does Redis sit?",
    "Normalize vs denormalize in one sentence with example.",
    "HTTP 401 vs 403 in IFFCO auth.",
    "Difference between JWT and session cookie.",
    "What is connection pooling in MySQL?",
    "Docker layer caching---practical tip.",
    "CI fails on lint but not tests---ship or block?",
    "Git rebase vs merge for intern PRs.",
    "When is gradient boosting better than linear regression for delays?",
    "Precision vs recall for delay alerts.",
    "ChromaDB vs Pinecone---why you chose Chroma.",
    "WebSocket close codes you actually know.",
    "A* heuristic admissibility in AirHelp graph.",
    "C++17 feature you used in OA Forge.",
    "Undefined behavior example in C++.",
    "Python GIL---does it affect your FastAPI app?",
    "async/await vs threads for I/O bound work.",
    "Supabase vs raw Postgres---trade-off.",
    "Cloud Run concurrency setting you tuned.",
    "Cold start mitigation list (3 items).",
    "OAuth2 authorization code flow steps.",
    "Rate limiting: token bucket vs leaky bucket.",
    "Idempotency key placement in Stripe-like API.",
    "SAGA vs 2PC---one-line intern answer.",
    "Load balancer layer 4 vs layer 7.",
    "CDN cache hit ratio---what's good enough?",
    "Selenium vs Playwright for scrapers.",
    "Ethics of scraping job boards.",
    "How you validate an OA question match.",
    "Explain CAP theorem using LogiFlow Redis + MySQL.",
    "What is the thundering herd problem and your LogiFlow fix?",
    "Difference between IaaS, PaaS, SaaS with your stack examples.",
    "Stripe idempotency key --- where stored and for how long?",
    "GE Workday B.S. mapping --- 15-second honest answer.",
    "Community Hero Firestore security rules --- one rule you wrote.",
    "OA Forge memory limit --- how enforced in judge?",
    "When would you pick Postgres over MySQL for LogiFlow?",
    "Explain your cold-start mitigation on Cloud Run (3 bullets).",
]

TRAP_QUESTIONS = [
    ("Isn't this just ChatGPT code?", None),
    ("Global Top 106 sounds like marketing.", None),
    ("You optimize for internships (OA Forge) more than engineering.", None),
    ("AI degree but SWE role?", None),
    ("Will you leave for higher CP / quant?", None),
]

QUESTIONS_TO_ASK = [
    "What does a successful intern project look like at handoff?",
    "How are interns paired with mentors weekly?",
    "What is the code review culture for intern PRs?",
    "Biggest technical debt the team wants help with this summer?",
    "How is on-call / production responsibility handled for interns (usually: none---verify)?",
]

CODING_PROBLEMS = [
    ("Stripe/Google", [
        "Two Sum / 3Sum",
        "Valid Parentheses",
        "Merge Intervals",
        "LRU Cache",
        "Rate Limiter",
        "Serialize BT",
        "Word Break",
        "Course Schedule",
        "K Closest Points",
    ]),
    ("GE/Honeywell", [
        "SQL: second highest salary",
        "Find duplicate emails",
        "Running total",
        "Array rotation",
        "String anagram groups",
        "BST validation",
    ]),
    ("Wells Fargo/GS", [
        "Expected dice rolls",
        "Stock span",
        "Max subarray",
        "Matrix islands",
        "Coin change",
        "Probability: birthday paradox sketch",
    ]),
    ("AlphaGrep", [
        "Fast stdin sum",
        "Custom sort with comparator",
        "Segment tree range sum (conceptual)",
        "Greedy scheduling",
        "Binary search on answer",
    ]),
    ("EA Systest", [
        "Parse nginx log top IPs",
        "Flaky test reproduction plan",
        "pytest fixture design",
        "Load test scenario doc",
    ]),
    ("Amazon MLSS", [
        "Logistic regression grad",
        "Train/test leakage spotting",
        "Vectorized mean in numpy",
        "Bias-variance tradeoff MCQ",
    ]),
    ("Cisco", [
        "Prefix trie insert/search",
        "TCP handshake ordering quiz",
        "HTTP status code scenarios",
    ]),
    ("Flipkart", [
        "Inventory decrement race",
        "Cache stampede mitigation",
        "Cart merge concurrency",
    ]),
    ("General", [
        "Detect cycle in LL",
        "Topo sort",
        "Dijkstra",
        "Union Find",
        "Heap merge K lists",
        "DP knapsack",
        "Sliding window max",
    ]),
]

INTERNET_BY_COMPANY = {
    "Stripe": [
        ("OA: 60-min HackerRank --- 1 problem, 3 sequential sub-parts (unlock Part 2 after Part 1).", [
            "Log parsing / transaction metrics / average latency / success rate---not classic DP.",
            "Modular code so Part 2 reuses Part 1; edge cases on malformed lines.",
            "Practice: parse logs, filter error codes, aggregate by merchant ID.",
        ]),
        ("Technical screen: 2 medium LC-style + code quality discussion.", [
            "Arrays, maps, strings; clean naming and tests.",
            "Explain time/space before coding; handle follow-up optimization.",
        ]),
        ("Integration round (90 min): real API docs, HTTP errors, pagination, idempotency.", [
            "Authenticate -> basic GET -> paginate -> retry failed events.",
            "Read docs out loud; debug 4xx/5xx live.",
            "Why idempotency keys matter for payment retries?",
        ]),
        ("Behavioral: ownership under ambiguous requirements.", [
            "Task decomposition when spec changes mid-internship.",
            "What do you do when integration test fails at 11pm?",
        ]),
    ],
    "GE HealthCare": [
        ("OA (Cocubes-style): Aptitude + Technical MCQ (OS, DBMS, DSA) + 1--2 coding.", [
            "MCQ: TCP/IP, OOP, normalization, indexing.",
            "Coding: array manipulation (e.g. sum of 2nd/4th/6th elements); Two Sum with hash map.",
            "Tree: level-order traversal / print level-wise string.",
        ]),
        ("PI: Deep project walkthrough + HTTP 404 on live resume links.", [
            "Interviewer clicks your demo---what if link broken?",
            "Error handling, status codes, monitoring.",
        ]),
        ("OOP grill: encapsulation, inheritance, polymorphism, constructor types.", [
            "Virtual functions with examples in C++ or Java.",
            "Practical OOP in your IFFCO or LogiFlow code.",
        ]),
        ("Manager: Why healthcare? Early release under compliance pressure?", [
            "DevOps/CI-CD answer for faster safe release.",
            "Why GE over pharma IT services firms?",
        ]),
    ],
}

RED_TEAM = [
    ("Resume click-through", "Opens your live demo mid-call."),
    ("Stack swap trap", "You said Bootstrap at IFFCO vs resume Node."),
    ("Ownership shrink", "So your mentor did the real work?"),
    ("Metric challenge", "Prove 100--400 ms."),
    ("Ambiguity freeze", "Long silence after vague answer."),
    ("Ethics ambush", "OA Forge scraping, cold email."),
    ("Prestige bait", "Why not IIT?"),
    ("Overclaim interrupt", "Stop---what did you write?"),
    ("Negative sell", "Why shouldn't we hire you?"),
    ("City trap", "Bengaluru only vs Hyderabad offer."),
]

PANEL_STRESS = [
    "Engineer A attacks LogiFlow architecture for 15 min straight.",
    "Engineer B asks OS/DBMS/CN rapid fire; no pauses > 5 sec.",
    "HR C asks ethics of scraping, cold email, OA Forge legality.",
    "All three: Where do you rank yourself in your batch? Prove it.",
    "Closing: each gives one reason to reject you---you respond without defensiveness.",
]

# Import base mocks A--C; extended D--I appended for answer-key completeness
from generate_brutal_interview_prep import MOCK_SCRIPTS as _BASE_MOCKS

MOCK_SCRIPTS = list(_BASE_MOCKS) + [
    {
        "title": "Mock Round D --- Google SWE Intern (60 min)",
        "interviewer": "L3/L4 Engineer, Core Infrastructure",
        "flow": [
            ("0--5 min", "Warm-up: favorite data structure and non-coding use."),
            ("5--15 min", "Coding #1: medium array/graph with follow-up optimization."),
            ("15--25 min", "Coding #2: strings + hash map twist."),
            ("25--40 min", "System: design global key-value cache for LogiFlow reads."),
            ("40--50 min", "Behavioral: failed hypothesis in project."),
            ("50--60 min", "Reverse: questions + What Google product would you remove?"),
        ],
        "brutal_moments": [
            "Your second solution is still not optimal---try again.",
            "How would this work at Google scale with multi-region?",
            "Tell me about a time you had no idea what to do for 2 days.",
        ],
    },
    {
        "title": "Mock Round H --- HackerRank AI Screen Replay (30 min)",
        "interviewer": "AI Recruiter + Automated Rubric (Collaboration weighted)",
        "flow": [
            ("0--2 min", "90-second intro --- friend stops you at 90s."),
            ("2--8 min", "IFFCO STAR + stack alignment (Node/Express/MySQL only)."),
            ("8--14 min", "LogiFlow 2-min pitch + JSON response whiteboard."),
            ("14--20 min", "ML metrics: MAE 22.7, CV, leakage --- no mixed percentages."),
            ("20--26 min", "Collaboration STAR x2 --- Redis split + IFFCO PR review."),
            ("26--30 min", "Your questions; debrief score 1--5."),
        ],
        "brutal_moments": [
            "You mentioned Bootstrap---resume says Express. Which is true?",
            "Pause. Summarize LogiFlow in 30 seconds.",
            "No teamwork example yet---Weak Fit on collaboration.",
        ],
    },
]
