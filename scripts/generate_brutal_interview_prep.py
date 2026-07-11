#!/usr/bin/env python3
"""Generate brutal-but-realistic interview prep PDF for Ojas Srivastava."""

from pathlib import Path
from datetime import date

OUT_TEX = Path(__file__).resolve().parents[1] / "Reference Collection" / "Planning" / "ojas_brutal_interview_simulation.tex"

COMPANIES = [
    {
        "name": "Stripe",
        "role": "Software Engineer, Intern",
        "loc": "Bengaluru (100% in-office)",
        "status": "Applied",
        "oa": "HackerRank / CodeSignal-style DSA (2--3 mediums) + strong behavioral writing round",
        "focus": "production shipping, code review culture, systems + user-facing, financial infra curiosity, clarity of writing",
    },
    {
        "name": "GE HealthCare",
        "role": "Software Intern (R4043319)",
        "loc": "Bengaluru on-site",
        "status": "Applied",
        "oa": "Aptitude + technical MCQ + coding (DSA medium) + HR",
        "focus": "SDLC, testing, healthcare/regulated mindset, cross-functional work, visualization/compute platform",
    },
    {
        "name": "Cisco",
        "role": "Software Engineer Summer Intern",
        "loc": "Bengaluru",
        "status": "Applied / pipeline",
        "oa": "Cisco OA: DSA + networking fundamentals MCQs possible",
        "focus": "networking-aware software, secure coding, cloud scale, agile SDLC",
    },
    {
        "name": "Wells Fargo",
        "role": "Technology Program Intern 2027 (R-557386)",
        "loc": "Bengaluru / Hyderabad",
        "status": "Applied / pipeline",
        "oa": "Codility/HackerRank + Java-heavy MCQ + situational judgment",
        "focus": "enterprise discipline, security, SQL, teamwork, regulated banking environment",
    },
    {
        "name": "Google",
        "role": "Software Engineering Intern 2027",
        "loc": "Bengaluru / Hyderabad / Pune",
        "status": "Applied / pipeline",
        "oa": "Google Online Challenge (GOC) + 4--5 onsite-style rounds if shortlisted",
        "focus": "algorithms, systems, scalability, ambiguity tolerance, Googleyness",
    },
    {
        "name": "Microsoft",
        "role": "Software Engineer Intern",
        "loc": "India hubs",
        "status": "Resume ready",
        "oa": "Codility + AA (automated assessment) + interview loop",
        "focus": "OOP, DSA, collaboration, Azure familiarity bonus",
    },
    {
        "name": "Electronic Arts (EADP)",
        "role": "SWE Intern --- Systest Engineer (214959)",
        "loc": "Hyderabad hybrid",
        "status": "Applied / pipeline",
        "oa": "Automation + scripting + testing scenarios + DSA easy-medium",
        "focus": "test automation, load simulation, performance debugging, pipelines",
    },
    {
        "name": "Honeywell",
        "role": "Intern",
        "loc": "India",
        "status": "Applied / pipeline",
        "oa": "Aptitude + technical + HR",
        "focus": "industrial software, data analysis, automation, reliability",
    },
    {
        "name": "AlphaGrep (Core SWE)",
        "role": "Software Development Intern --- Core Engineering",
        "loc": "Mumbai / Bengaluru",
        "status": "Applied / pipeline",
        "oa": "Heavy DSA (CF Div2 level) + C++ systems questions",
        "focus": "C++ performance, low latency, Linux, memory, I/O",
    },
    {
        "name": "AlphaGrep (Quant)",
        "role": "Quantitative Developer Intern",
        "loc": "Mumbai",
        "status": "Applied / pipeline",
        "oa": "Math + probability + Python/C++ + puzzles",
        "focus": "ML features, market data pipelines, statistics, coding speed",
    },
    {
        "name": "Amazon ML Summer School",
        "role": "MLSS 2026 cohort",
        "loc": "Virtual / selective",
        "status": "Applied",
        "oa": "ML fundamentals test + selection interview",
        "focus": "ML theory, generalization, probability, coding in Python",
    },
    {
        "name": "Flipkart Grid 8.0",
        "role": "Engineering track",
        "loc": "India",
        "status": "Resume ready",
        "oa": "Grid-specific challenges + DSA + ML optional",
        "focus": "scale, e-commerce, latency, distributed systems",
    },
    {
        "name": "Goldman Sachs",
        "role": "Engineering Intern",
        "loc": "India",
        "status": "Resume + cover letter ready",
        "oa": "HackerRank (math + DSA) + HireVue + superday",
        "focus": "engineering rigor, probability, systems, finance curiosity",
    },
    {
        "name": "Angel One",
        "role": "SDE Intern",
        "loc": "India fintech",
        "status": "Resume ready",
        "oa": "DSA + backend + fintech aptitude",
        "focus": "trading-adjacent systems, APIs, reliability",
    },
]

PROJECTS = [
    "IFFCO Internship (Jun--Jul 2025)",
    "LogiFlow (GSC 2026 Global Top 106)",
    "Community Hero (Vibe2Ship 2026 Global Top 20)",
    "AirHelp (PowerMind Hackathon 2026)",
    "OA Forge / Career Automation Stack",
    "RangRiti (Web Wonders 2025 --- Technical Lead)",
]

UNIVERSAL_BEHAVIORAL = [
    ("Walk me through your resume in 90 seconds.", [
        "You listed 50+ workflows at IFFCO---name three specifically. Who used them?",
        "Why does a Knight on LeetCode matter for this job?",
        "You have many hackathon projects. Which one would you put in production at our company tomorrow, and which would you delete?",
    ]),
    ("Tell me about a time you received harsh critical feedback.", [
        "What did you disagree with in that feedback?",
        "If you had to redo the project, what would you cut to ship two weeks earlier?",
    ]),
    ("Describe a production bug you caused or found.", [
        "How did you know it was your change?",
        "What monitoring would have caught it faster?",
        "Write the postmortem title in one sentence.",
    ]),
    ("Why should we hire you over someone with a pure CSE degree from the same college?", [
        "What do CSE students know that you don't?",
        "Convince me AI isn't just a buzzword on your degree.",
    ]),
    ("What is your biggest weakness---and don't say 'perfectionism'.", [
        "Give an example from the last 30 days.",
        "How would that weakness hurt our team in week one?",
    ]),
    ("You only interned for one month at IFFCO. Was that real experience?", [
        "What did you own end-to-end vs. what did your mentor do?",
        "Why not return for a longer stint?",
    ]),
    ("Explain a project where you were NOT the leader.", [
        "What did you disagree with technically?",
        "How did you escalate without being toxic?",
    ]),
]

CS_FUNDAMENTALS = [
    ("OS", [
        "Difference between process and thread; when would you prefer threads in your LogiFlow backend?",
        "Explain deadlock with a scenario from a database + cache system.",
        "What happens when you fork a process that holds a mutex?",
        "Virtual memory: why can a 4GB RAM machine run LogiFlow with large datasets?",
        "Context switch cost---why does high concurrency hurt if work is CPU-bound?",
    ]),
    ("DBMS", [
        "Explain ACID using your IFFCO MySQL schema.",
        "When would you denormalize in LogiFlow's 9,526 station dataset?",
        "Index types you used; why did a query get faster after indexing?",
        "Serializable vs Read Committed---which for financial reporting?",
        "Explain a slow JOIN you fixed and the EXPLAIN output you saw.",
    ]),
    ("Networks", [
        "Walk through what happens when a user hits your Cloud Run LogiFlow endpoint.",
        "TCP vs UDP---which for WebSockets in AirHelp and why?",
        "How does TLS termination work on Cloud Run?",
        "HTTP/1.1 vs HTTP/2 impact on your progressive streaming design.",
        "What is a CDN and would you add one to Community Hero?",
    ]),
    ("DSA / Coding", [
        "Implement LRU cache---then defend cache size for LogiFlow corridors.",
        "Detect cycle in linked list---variant: dependency graph in CI pipeline.",
        "Top K frequent elements---apply to OA Forge question frequency.",
        "Binary search on answer---rate limiter design.",
        "Graph shortest path---justify A* vs Dijkstra in AirHelp.",
    ]),
]

PROJECT_QUESTIONS = {
    "IFFCO": [
        ("What exactly were the 50+ workflows?", ["Name one workflow's input/output.", "How did you validate correctness with users?", "What broke in production?"]),
        ("Why Node.js and not Java/Spring for an enterprise coop?", ["Would you choose differently today?", "How did you structure the Express app?"]),
        ("JWT auth---walk through login to protected API.", ["Where do you store refresh tokens?", "How do you revoke access?", "Threat model: XSS vs CSRF here."]),
        ("10+ REST APIs---pick one and design the OpenAPI spec live.", ["Versioning strategy?", "Idempotency for POST retries?"]),
        ("Docker + CI/CD---draw the pipeline.", ["What ran on every PR?", "What tests were missing that you'd add now?"]),
    ],
    "LogiFlow": [
        ("Why 100--400 ms and not sub-50 ms?", ["Show where time is spent.", "What is your p99?", "Cold start impact on Cloud Run?"]),
        ("Explain progressive HTTP streaming.", ["Why not WebSockets?", "Backpressure handling?", "Client disconnect mid-stream?"]),
        ("Redis caching---cache key design and invalidation.", ["Thundering herd on expiry?", "Redis down---what happens?"]),
        ("Gradient Boosting delay model: features, leakage, MAE 22.7 min.", ["Train/test split by time?", "Would you deploy this model to prod?"]),
        ("100/100 pytest rules---give 3 example rules.", ["Are these unit or integration tests?", "How do you test ML outputs?"]),
        ("580 corridors, 9,526 stations---data pipeline architecture.", ["Storage format?", "Ingestion failures?", "Duplicate station IDs?"]),
    ],
    "Community Hero": [
        ("Solo-built in a hackathon---what is the scariest technical debt?", ["Auth model?", "Firestore rules?", "Rate limiting on Gemini calls?"]),
        ("SLA routing logic---pseudo-code it.", ["Edge case: duplicate reports same GPS?", "Admin override?"]),
        ("Map-based UX---how do you handle low connectivity?", ["Offline PWA strategy?", "Service worker scope?"]),
        ("Gemini categorization---prompt design and failure modes.", ["Hallucinated category?", "Cost per 1K reports?"]),
    ],
    "AirHelp": [
        ("RAG pipeline architecture.", ["Chunk size?", "Embedding model?", "When does RAG fail at an airport?"]),
        ("WebSockets at 50--100 concurrent---bottleneck?", ["Single process limit?", "Horizontal scaling plan?"]),
        ("A* navigation 95%+ accuracy---how measured?", ["What is the other 5%?", "Graph construction from floor plans?"]),
        ("1--3s latency budget breakdown.", ["Which component to optimize first?"]),
    ],
    "OA Forge": [
        ("C++ judge sandbox---how do you prevent fork bombs / file system escape?", ["seccomp? namespaces? timeouts?", "What about infinite loops?"]),
        ("g++ -O2 vs -O0 for judging fairness.", ["Floating point nondeterminism?", "Memory limit enforcement?"]),
        ("14K+ occurrences vs 5.5K test cases---explain the data model.", ["Copyright / scraping ethics?", "False positives in question matching?"]),
        ("Why build this instead of just using LeetCode?", ["Does this make you a better engineer or a better test-taker?"]),
    ],
    "Career Automation Stack": [
        ("Internship Scout across 965+ companies---architecture.", ["Dedup logic?", "Rate limits?", "Legal/ToS concerns?"]),
        ("Hiring Scout cold outreach---ethics and deliverability.", ["Would you do this at scale for a real company?"]),
        ("Four pipelines---which is production-grade vs hacky?", ["Single point of failure?", "Observability?"]),
    ],
}

MOCK_SCRIPTS = [
    {
        "title": "Mock Round A --- Stripe-style (45 min)",
        "interviewer": "Senior Engineer, Payments Infrastructure",
        "flow": [
            ("0--5 min", "Intro + 'Tell me about a time you shipped under ambiguity.'"),
            ("5--20 min", "Resume deep-dive on LogiFlow + OA Forge with interrupting follow-ups."),
            ("20--35 min", "Coding: implement rate limiter (token bucket) + unit tests."),
            ("35--42 min", "Design lite: idempotent payment retry API---components only."),
            ("42--45 min", "Your questions + 'Why Stripe over Razorpay?'"),
        ],
        "brutal_moments": [
            "'You said production---how many daily active users?'",
            "'Your cache numbers sound benchmarked. Show me methodology.'",
            "'What happens if Redis and DB disagree on corridor status?'",
        ],
    },
    {
        "title": "Mock Round B --- GE HealthCare / Enterprise (45 min)",
        "interviewer": "Engineering Manager, Digital Technology",
        "flow": [
            ("0--5 min", "Why healthcare? Why GE? Why Bengaluru on-site?"),
            ("5--15 min", "IFFCO: requirements, testing, documentation for auditors."),
            ("15--25 min", "LogiFlow reliability + pytest culture."),
            ("25--35 min", "MCQ rapid fire: SQL, OOP, testing definitions."),
            ("35--40 min", "Behavioral: conflict with teammate on design."),
            ("40--45 min", "Logistics: dates, backlog status, degree clarification."),
        ],
        "brutal_moments": [
            "'Workday says B.S. Computer Science; resume says B.Tech AI---explain.'",
            "'One-month internship---how is that sufficient?'",
            "'Healthcare is regulated. Where did you validate PHI/PII handling?' (trap: you didn't---answer honestly)",
        ],
    },
    {
        "title": "Mock Round C --- AlphaGrep / HFT-flavored (60 min)",
        "interviewer": "Core Engineering Lead",
        "flow": [
            ("0--10 min", "C++ trivia: move semantics, STL complexity, memory alignment basics."),
            ("10--25 min", "Live coding: parse streaming integers from stdin under time limit."),
            ("25--40 min", "OA Forge judge design whiteboard."),
            ("40--50 min", "LogiFlow latency story---skeptical probing."),
            ("50--60 min", "Probability warm-up + 'Why trading?'"),
        ],
        "brutal_moments": [
            "'CF 1419 is Specialist, not expert---why should we trust your systems skills?'",
            "'Judge in C++---how many microseconds per test case?'",
        ],
    },
]


def latex_escape(s: str) -> str:
    repl = {
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    for a, b in repl.items():
        s = s.replace(a, b)
    return s


def qblock(title: str, questions: list[tuple[str, list[str]]]) -> str:
    parts = ["\\subsection{" + latex_escape(title) + "}\n"]
    parts.append("\\begin{enumerate}[label=\\textbf{Q\\arabic*:}, leftmargin=*]\n")
    for q, followups in questions:
        parts.append("  \\item " + latex_escape(q) + "\n")
        parts.append("  \\begin{enumerate}[label=\\textit{FU\\arabic*:}, leftmargin=2em]\n")
        for fu in followups:
            parts.append("    \\item " + latex_escape(fu) + "\n")
        parts.append("  \\end{enumerate}\n")
    parts.append("\\end{enumerate}\n")
    return "".join(parts)


def main() -> None:
    lines: list[str] = []
    a = lines.append

    a(r"""\documentclass[9pt,a4paper]{article}
\usepackage[margin=1.8cm]{geometry}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage{enumitem}
\usepackage{booktabs}
\usepackage{longtable}
\usepackage{array}
\usepackage{hyperref}
\usepackage{fancyhdr}
\usepackage{titlesec}
\usepackage{xcolor}
\usepackage{tabularx}
\usepackage{multicol}

\definecolor{brutal}{RGB}{120,0,0}
\definecolor{hint}{RGB}{0,80,120}
\definecolor{goodbg}{RGB}{230,245,230}
\definecolor{badbg}{RGB}{255,235,235}
\definecolor{scriptbg}{RGB}{245,248,255}

\newcommand{\goodans}[1]{\par\noindent\textbf{\textcolor{green!50!black}{Strong:}} #1\par\vspace{1mm}}
\newcommand{\badans}[1]{\par\noindent\textbf{\textcolor{red!70!black}{Weak:}} #1\par\vspace{1mm}}
\newcommand{\diffLone}{\textcolor{green!50!black}{\textbf{[L1]}}}
\newcommand{\diffLtwo}{\textcolor{orange!90!black}{\textbf{[L2]}}}
\newcommand{\diffLthree}{\textcolor{brutal}{\textbf{[L3]}}}

\pagestyle{fancy}
\fancyhf{}
\fancyhead[L]{\small Ojas Srivastava --- Brutal Interview Simulation}
\fancyhead[R]{\small """ + date.today().strftime("%d %b %Y") + r"""}
\fancyfoot[C]{\thepage}

\titleformat{\section}{\large\bfseries\color{brutal}}{}{0em}{}[\titlerule]
\titleformat{\subsection}{\normalsize\bfseries}{}{0em}{}

\setlist{nosep}

\begin{document}
""")

    a(r"""
\begin{center}
{\LARGE\bfseries Brutal Interview Simulation Playbook}\\[4pt]
{\large Ojas Srivastava --- B.Tech Artificial Intelligence, SVNIT Surat}\\[2pt]
{\small CGPA 9.20/10 \textbar{} Graduating May 2028 \textbar{} LeetCode Knight 2048 (711+ solved) \textbar{} Codeforces Specialist 1419 (252+ solved)}\\[6pt]
{\color{hint}\textit{Purpose: simulate real interview pressure across every role in your pipeline. Answer out loud. Time yourself. No bullet-point mumbling.}}\\[4pt]
{\small \textbf{Edition 2} --- internet-sourced banks, canonical scripts, red-team tactics, 30-day schedule \textbar{} Difficulty: \diffLone warm-up \diffLtwo bar-raiser \diffLthree kill-shot}
\end{center}

\tableofcontents
\newpage

\section{How to Use This Document (Read First)}
\textbf{This is not a cheat sheet of answers.} It is an adversarial question bank modeled on how real interviewers probe interns in India (Bengaluru/Hyderabad/Mumbai) for 2027 summer roles.

\subsection{Difficulty legend}
\begin{itemize}
  \item \diffLone \textbf{Warm-up} --- HR, logistics, ``tell me about yourself''; aim 60--90s crisp.
  \item \diffLtwo \textbf{Bar-raiser} --- architecture, metrics, follow-up chains; aim 2 min then FUs.
  \item \diffLthree \textbf{Kill-shot} --- resume contradiction, ethics trap, live coding under interrupt; no notes.
\end{itemize}

\subsection{Self-score after every session (1--5)}
\begin{tabularx}{\textwidth}{@{}lX@{}}
\toprule
\textbf{Score} & \textbf{Meaning} \\
\midrule
5 & Answered all FUs; numbers consistent; asked one smart question back. \\
4 & Main story clear; one FU wobbled but recovered. \\
3 & Moderate Fit zone --- right content, too long or vague metrics. \\
2 & Weak Fit --- contradicted resume or no STAR structure. \\
1 & Fail --- could not explain own architecture; restart prep. \\
\bottomrule
\end{tabularx}

\subsection{Simulation protocol}
\begin{enumerate}
  \item Pick one company section + one mock script.
  \item Set a 45--60 minute timer. No IDE for behavioral rounds; IDE only when marked coding.
  \item For each question: answer in 60--90 seconds, then attempt \textbf{every follow-up (FU)} without looking at notes.
  \item Record yourself once per week. If you say ``we used AI/ML'' without specifics, restart.
  \item After each session, write a 5-line ``what I failed to prove'' debrief.
\end{enumerate}

\subsection{Your canonical facts (keep consistent)}
\begin{itemize}
  \item \textbf{Degree:} B.Tech Artificial Intelligence, SVNIT (not ``AI/ML''; not Robotics-heavy).
  \item \textbf{Internship:} IFFCO, Jun--Jul 2025, Prayagraj, 1 month, production Node/Express/MySQL.
  \item \textbf{Flagship projects:} LogiFlow (GSC Top \textbf{106}), Community Hero (Vibe2Ship Top \textbf{20}), AirHelp, OA Forge.
  \item \textbf{Locations willing:} Bengaluru on-site (Stripe, GE, Cisco); Hyderabad (Wells Fargo, EA); Mumbai (AlphaGrep).
\end{itemize}

\subsection{Known resume attack surfaces (prepare defenses)}
\begin{enumerate}
  \item \textbf{One-month IFFCO} --- emphasize ownership slices, production usage, metrics, mentor validation.
  \item \textbf{B.Tech AI vs Computer Science} --- emphasize coursework overlap (DSA, OS, DBMS, CN, Distributed Systems).
  \item \textbf{Hackathon $\rightarrow$ production claims} --- cite live URLs, tests, user flows, known limitations honestly.
  \item \textbf{Workday B.S. + CS field (GE)} --- explain ATS mapping; actual degree is B.Tech AI at NIT.
  \item \textbf{Career Automation / cold outreach} --- frame as personal tooling; acknowledge ethics boundaries.
  \item \textbf{High CP stats but intern bar} --- connect CP to debugging speed, not bragging rights.
\end{enumerate}

\newpage
\section{Application Portfolio Snapshot}
\begin{longtable}{@{}p{2.2cm}p{3.5cm}p{2cm}p{1.5cm}p{5cm}@{}}
\toprule
\textbf{Company} & \textbf{Role} & \textbf{Location} & \textbf{Status} & \textbf{Likely OA / Focus} \\
\midrule
\endhead
""")

    for c in COMPANIES:
        a(f"{latex_escape(c['name'])} & {latex_escape(c['role'])} & {latex_escape(c['loc'])} & {latex_escape(c['status'])} & {latex_escape(c['oa'])} --- {latex_escape(c['focus'])} \\\\\n")

    a(r"""\bottomrule
\end{longtable}

\newpage
\section{Universal Brutal Round (Every Company Will Touch This)}
\textit{Interviewers cross-check consistency. If LogiFlow numbers change between answers, you lose trust.}

""")
    a(qblock("Behavioral + Resume Integrity", UNIVERSAL_BEHAVIORAL))

    a(r"\newpage" + "\n")
    a(r"\section{Computer Science Fundamentals --- Rapid Fire + Follow-ups}" + "\n")
    for area, qs in CS_FUNDAMENTALS:
        items = [(q, ["Go deeper.", "Give a number from your project.", "What breaks at scale?"]) for q in qs]
        a(qblock(area, items))

    a(r"\newpage" + "\n")
    a(r"\section{Project Deep-Dive Banks (Exhaustive)}" + "\n")
    for proj, qs in PROJECT_QUESTIONS.items():
        a(qblock(proj, qs))

    a(r"\newpage" + "\n")
    a(r"\section{Company-Specific Question Banks}" + "\n")

    company_extra = {
        "Stripe": [
            ("Why Stripe and not a Indian fintech?", ["How does Stripe differ from Razorpay/Cashfree architecturally?", "Name a Stripe product you'd want to work on."]),
            ("Tell us about you + fit at Stripe (application essay live).", ["Cut your answer to 30 seconds.", "Remove all hackathon buzzwords.", "Add one failure story."]),
            ("Design: make Checkout errors understandable to merchants.", ["API vs UI ownership?", "Internationalization?", "Observability metrics?"]),
            ("Coding: implement idempotent POST /v1/charges retry handler.", ["DB schema?", "Duplicate webhook delivery?"]),
            ("Read a pull request diff and critique it.", ["What tests are missing?", "Naming?", "Security?"]),
        ],
        "GE HealthCare": [
            ("Why digital healthcare / visualization platform?", ["Regulated environment mindset?", "Patient safety analogy in software?"]),
            ("SDLC walkthrough for a feature you shipped.", ["Unit vs integration vs validation?", "Traceability for QA?"]),
            ("On-site Bengaluru 100%---constraints?", ["Relocation from Surat?", "Semester conflicts?"]),
            ("Testing philosophy for medical-adjacent software.", ["You didn't work on PHI---how do you reason about risk anyway?"]),
        ],
        "Cisco": [
            ("Explain TCP handshake using your project's HTTP calls.", ["Where does TLS fit?", "What causes tail latency on mobile networks?"]),
            ("Secure coding at IFFCO---JWT, validation.", ["STRIDE threat model quick pass.", "Common Cisco CVE classes?"]),
            ("Design microservice for device telemetry ingestion.", ["Scale to 1M devices?", "Backpressure?"]),
        ],
        "Wells Fargo": [
            ("Why banking? Why Wells Fargo program structure?", ["Compliance comfort?", "Example of following process under pressure?"]),
            ("SQL: write query for top-N workflows by daily volume.", ["Index?", "Explain plan?"]),
            ("Situational: teammate shortcuts security review.", ["What do you do Monday morning?"]),
            ("Java vs Node---which for enterprise banking services?", ["Transaction boundaries?"]),
        ],
        "Google": [
            ("GOC prep: arrays, strings, greedy, graphs medium.", ["Optimize from O(n^2) to O(n log n) with proof sketch."]),
            ("LogiFlow OAuth + Cloud Run cold starts---deep dive.", ["SLO definition?", "Error budget?"]),
            ("Googleyness: disagreement with authority.", ["Data you brought?", "Outcome?"]),
            ("Estimate: storage for 9,526 stations x daily events.", ["Fermi decomposition live."]),
        ],
        "Microsoft": [
            ("OOP design: parking lot / LRU / logger.", ["SOLID violation example from your code?"]),
            ("Azure vs GCP---what did you choose and why?", ["Vendor lock-in concerns?"]),
            ("Team conflict in hackathon team.", ["Role clarity?"]),
        ],
        "Electronic Arts (EADP)": [
            ("Design load test for game login spike.", ["Metrics: p95, error rate, saturation.", "Tools you'd use?"]),
            ("Career Automation Stack---map components to test infra.", ["Schedulers, artifacts, flaky tests."]),
            ("Debug: WebSocket drops at 80 concurrent users.", ["Profiling steps ordered."]),
            ("Why systest instead of feature dev?", ["Trap: don't sound like you want EA only for games."]),
        ],
        "Honeywell": [
            ("Industrial automation interest---beyond buzzwords.", ["IIoT example from your work?"]),
            ("Data analysis story from LogiFlow model.", ["Business decision informed by model?"]),
            ("Reliability in cooperative enterprise (IFFCO).", ["Stakeholder communication?"]),
        ],
        "AlphaGrep (Core SWE)": [
            ("Implement fast parsing of market data feed (toy).", ["Memory allocations?", "Branch prediction?"]),
            ("C++: vector growth, iterator invalidation.", ["Real bug you avoided?"]),
            ("Linux: strace/ltrace usage on judge binary.", ["Syscalls allowed in sandbox?"]),
        ],
        "AlphaGrep (Quant)": [
            ("Explain gradient boosting to a trader.", ["Overfitting on 15,650 train-days?", "Feature importance?"]),
            ("Probability: expected rolls until double six.", ["Markov chain version?"]),
            ("Personal equities experience---specific thesis you tested.", ["How did you falsify yourself?"]),
        ],
        "Amazon ML Summer School": [
            ("Bias-variance on LogiFlow delay model.", ["Cross-val strategy?", "Leakage sources?"]),
            ("Why MLSS over self-study?", ["What gap will Amazon scientists fill?"]),
            ("Derive gradient descent update for linear regression.", ["Learning rate sensitivity?"]),
        ],
        "Flipkart Grid 8.0": [
            ("Design flash sale inventory system.", ["Overselling prevention?", "Cache coherency?"]),
            ("LogiFlow as supply chain---draw architecture.", ["Bottleneck at 10x traffic?"]),
        ],
        "Goldman Sachs": [
            ("Probability + mental math warm-up.", ["Options intuition (even if basic)."]),
            ("Engineering rigor in CI/CD.", ["Rollback strategy?"]),
            ("Why finance + engineering hybrid?", ["GS culture fit?", "Risk vs reward in engineering?"]),
        ],
        "Angel One": [
            ("Build rate-limited market data API.", ["Auth?", "Audit logs?"]),
            ("Fintech compliance awareness (India).", ["SEBI basics you actually read?"]),
        ],
    }

    for c in COMPANIES:
        name = c["name"]
        a(f"\\subsection{{{latex_escape(name)} --- {latex_escape(c['role'])}}}\n")
        a(f"\\textbf{{Location:}} {latex_escape(c['loc'])} \\quad ")
        a(f"\\textbf{{OA expectation:}} {latex_escape(c['oa'])}\n\n")
        a("\\textbf{Primary probes:}\n")
        a("\\begin{itemize}\n")
        for point in c["focus"].split(", "):
            a(f"  \\item {latex_escape(point)}\n")
        a("\\end{itemize}\n\n")
        extras = company_extra.get(name, [])
        if extras:
            a(qblock(f"{name} targeted questions", extras))
        # generic company questions
        generic = [
            (f"Why {name}?", [f"Why not a competitor of {name}?", "What did you read about our stack last week?"]),
            (f"What would you build in your first 30 days at {name}?", ["How is that not arrogant for an intern?", "Dependencies on onboarding?"]),
            ("Tell me about LogiFlow in 2 minutes.", ["Interrupt at 60s: get to YOUR contribution only.", "What would you rebuild?"]),
        ]
        a(qblock(f"{name} standard intern probes", generic))
        a("\\newpage\n")

    append_internet_sourced_banks(a)
    append_refined_content(a)
    append_extensive_banks(a)
    append_mega_content(a)

    a(r"\section{Full Mock Interview Scripts (Timed)}" + "\n")
    for mock in MOCK_SCRIPTS:
        a(f"\\subsection{{{latex_escape(mock['title'])}}}\n")
        a(f"\\textbf{{Interviewer persona:}} {latex_escape(mock['interviewer'])}\n\n")
        a("\\textbf{Flow:}\n\\begin{enumerate}\n")
        for slot, action in mock["flow"]:
            a(f"  \\item \\textbf{{{latex_escape(slot)}}}: {latex_escape(action)}\n")
        a("\\end{enumerate}\n\n")
        a("\\textbf{Brutal interruption bank (use randomly):}\n\\begin{itemize}\n")
        for m in mock["brutal_moments"]:
            a(f"  \\item {latex_escape(m)}\n")
        a("\\end{itemize}\n\n")

    a(r"""
\section{OA / Coding Problem Bank (Aligned to Your Pipeline)}
\subsection{High-frequency patterns for your stats (Knight / Specialist)}
\begin{itemize}
  \item Arrays/strings: two pointers, sliding window, prefix sums
  \item Trees/graphs: BFS/DFS, shortest path, topological sort
  \item Heaps: top-K, merge K lists, scheduling
  \item DP: knapsack variants, LIS, grid paths
  \item System-ish: rate limiter, LRU, file tail, log aggregation
\end{itemize}

\subsection{Company-tagged practice set}
\begin{longtable}{@{}p{2.5cm}p{4cm}p{8cm}@{}}
\toprule
\textbf{Company} & \textbf{Format} & \textbf{Representative problems} \\
\midrule
Stripe / Google & 2--3 mediums OR 1x 3-part implementation (log parse) & Rate limiter; segment tree; merge intervals \\
GE / Honeywell & Aptitude + MCQ + 1--2 coding & Sum 2nd/4th/6th elems; Two Sum; HTTP/OOP MCQ \\
Wells Fargo / GS & AMCAT/Codility + aptitude & Token system DS; tree level-order; swap 3 ways \\
AlphaGrep & 5 CP / 90 min or 2--3 code + C++ MCQ & Order book design; fast I/O; bitmask \\
EA Systest & OOP + code reading + LC medium & Load test design; vector vs list; medal ranking \\
HackerRank Screen & AI 30-min behavioral-technical & Resume deep-dive; collaboration STAR required \\
Amazon MLSS & ML + code & Logistic regression derivation, numpy vectorization, train/test leakage MCQ \\
\bottomrule
\end{longtable}

\section{Trap Questions --- Honest Answer Frameworks}
\begin{enumerate}
  \item \textbf{``Isn't this just ChatGPT code?''} --- Point to commits, tests, architecture trade-offs YOU defended live.
  \item \textbf{``Global Top 106 sounds like marketing.''} --- Explain judging criteria, team size, your measurable contribution.
  \item \textbf{``You optimize for internships (OA Forge) more than engineering.''} --- Pivot to judge sandbox, CI, data pipelines as real engineering.
  \item \textbf{``AI degree but SWE role?''} --- Coursework map + projects that are backend/systems heavy.
  \item \textbf{``Will you leave for higher CP / quant?''} --- Commit to role scope; honesty without sounding flaky.
\end{enumerate}

\section{Questions YOU Should Ask (Don't End Passive)}
\begin{itemize}
  \item What does a successful intern project look like at handoff?
  \item How are interns paired with mentors weekly?
  \item What is the code review culture for intern PRs?
  \item Biggest technical debt the team wants help with this summer?
  \item How is on-call / production responsibility handled for interns (usually: none---verify)?
\end{itemize}

\section{7-Day Brutal Prep Schedule}
\begin{enumerate}
  \item \textbf{Day 1:} Canonical scripts (Section 6) + IFFCO deep-dive recorded.
  \item \textbf{Day 2:} LogiFlow + Community Hero whiteboard + DBMS/OS rapid fire.
  \item \textbf{Day 3:} Stripe/Google mock script A + 2 medium LeetCode timed.
  \item \textbf{Day 4:} AlphaGrep C++ + OA Forge security questions.
  \item \textbf{Day 5:} Wells Fargo SQL + situational + GE healthcare angle.
  \item \textbf{Day 6:} EA systest load testing narrative + AirHelp concurrency.
  \item \textbf{Day 7:} Full 3-hour loop: OA simulation + behavioral + one system lite.
\end{enumerate}

\section{30-Day Interview Camp (Recommended Rotation)}
\textit{Repeat the 7-day block 4 times; each week add one new mock script and re-record canonical answers.}

\begin{longtable}{@{}p{1.2cm}p{5.5cm}p{8cm}@{}}
\toprule
\textbf{Week} & \textbf{Focus} & \textbf{Daily minimum (weekdays)} \\
\midrule
\endhead
1 & Canon + HackerRank screen & Memorize 90s intro; 1 STAR/day; 1 timed medium LC \\
2 & Stripe + Google OAs & Log-parse 3-part mock; segment tree review; 2 mediums \\
3 & Enterprise (GE, WF, Cisco) & SQL + OOP MCQ drill; situational STAR; HTTP/CN rapid fire \\
4 & AlphaGrep + EA + MLSS & C++ MCQ; load-test narrative; bias-variance on LogiFlow \\
\bottomrule
\end{longtable}

\subsection{Weekend blocks (Sat--Sun)}
\begin{itemize}
  \item \textbf{Saturday:} Full mock script (45--60 min) with friend + brutal interruption bank.
  \item \textbf{Sunday:} OA simulation timetable + debrief 5 lines + update STAR worksheets.
\end{itemize}

\vfill
\begin{center}
\textit{Generated for Ojas Srivastava --- Resume Optimiser repo --- """ + date.today().strftime("%B %Y") + r"""}\\
\small Good luck. Brutal practice $\rightarrow$ calm interviews.
\end{center}

\end{document}
""")

    OUT_TEX.parent.mkdir(parents=True, exist_ok=True)
    OUT_TEX.write_text("".join(lines), encoding="utf-8")
    print(f"Wrote {OUT_TEX} ({len(lines)} chunks, {OUT_TEX.stat().st_size // 1024} KB)")


def append_internet_sourced_banks(a) -> None:
    """Questions synthesized from public interview experiences (GeeksforGeeks, Medium, Glassdoor, Taro, HackerRank docs)."""
    a(r"""
\newpage
\section{Internet-Sourced Real Questions (2024--2026 Reviews)}
\textit{Compiled from candidate writeups on GeeksforGeeks, Medium, LinkedIn, Jointaro, Exponent, and company hiring blogs. These are what people actually report---not generic LeetCode lists.}

\subsection{HackerRank Technical Screen (AI Recruiter) --- Your Exact Format}
\textbf{Reported structure:} Eligibility $\rightarrow$ Role Alignment $\rightarrow$ Core SWE $\rightarrow$ Collaboration \& Communication (30 min). \textbf{Your mock result:} Moderate Fit; Collaboration = Weak Fit.

""")
    hr_screen = [
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
            "Reproduce $\rightarrow$ DevTools $\rightarrow$ isolate FE vs BE $\rightarrow$ logs $\rightarrow$ fix $\rightarrow$ PR.",
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
    a(qblock("HackerRank Screen Question Bank (from your transcript + public reports)", hr_screen))

    internet_by_company = {
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
                "Authenticate $\rightarrow$ basic GET $\rightarrow$ paginate $\rightarrow$ retry failed events.",
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
        "Google": [
            ("OA: 60--90 min, 1--2 DSA on Codility/HackerRank/Google platform.", [
                "Arrays/strings ~85%; graphs BFS/DFS common in loops.",
                "Practice in plain text editor---no autocomplete.",
            ]),
            ("Phone/onsite: Range Sum Query with updates (Segment Tree / Fenwick).", [
                "Explain lazy propagation if asked follow-up.",
                "BQ: learned from failure; disagree with teammate---STAR only.",
            ]),
            ("Googleyness: intellectual humility, bias to action, ambiguity.", [
                "Admit wrong approach and how you corrected.",
                "Team matching: pick a Google product and say why concretely.",
            ]),
        ],
        "Cisco": [
            ("OA: 2 coding + 40+ MCQs on OS, CN, OOP (HackerRank).", [
                "Blind resume round---no college name/CGPA; candidate code only.",
                "CN: OSI layers, TCP/IP, DNS, DHCP.",
                "OS: deadlock, threads, memory management.",
            ]),
            ("Technical: Resume deep-dive + notepad coding (denominations / frequency sort).", [
                "Every project: what YOU built, scalability, deployment.",
                "Favorite subject = Networks $\rightarrow$ protocol application questions.",
            ]),
            ("Manager: Design Instagram competitor in 5 min + distributed delay follow-up.", [
                "Feed, storage, CDN, upload path.",
                "What breaks at global scale?",
            ]),
        ],
        "Wells Fargo": [
            ("OA: AMCAT/Codility --- English, aptitude, 2 medium coding (60 min).", [
                "Perfect squares in array; tree level-order string.",
                "Cannot revisit sections---time management.",
            ]),
            ("Technical: OOP live coding (implement what you explain).", [
                "Swap two numbers three different ways.",
                "Runtime polymorphism, virtual functions, Java vs C++.",
            ]),
            ("Design: Token generation system for a bank---which DS?", [
                "Deque $\rightarrow$ interviewer complicates $\rightarrow$ DFS traversal variant.",
                "Security vs speed in banking---your stance?",
            ]),
            ("Project grill + React/Node if on resume.", [
                "State vs props; lifecycle/hooks; normalization in DB.",
            ]),
        ],
        "AlphaGrep": [
            ("OA: 5 CP problems / 90 min OR 2--3 coding + 15--20 C++ MCQ.", [
                "Bitmask, interactive graph sink, priority queue + binary search.",
                "MCQ: C++ constructs, probability, statistics.",
            ]),
            ("Interview: Design order book (bid/ask) with evolving requirements.", [
                "Throughput vs memory footprint trade-offs.",
                "Follow-ups: new fields, faster top-of-book lookup.",
            ]),
            ("C++ deep: virtual functions, shared pointer implementation, sizeof tricks.", [
                "Memory management mapping to OS paging.",
                "Low-latency network programming (TCP/IP).",
            ]),
        ],
        "Electronic Arts (EADP Systest)": [
            ("Phone screen: Why EA? General background.", [
                "Why systest vs gameplay---positive framing.",
            ]),
            ("Technical: OOP, C++, STL --- what does this code do?", [
                "vector vs linked list trade-offs.",
                "Medal ranking / wiggle subsequence style LC mediums reported.",
            ]),
            ("Systest focus: load test game login spike; parse game logs.", [
                "Metrics: p95 latency, error rate, saturation.",
                "Automation tool you would build for flaky tests.",
            ]),
        ],
        "Honeywell / Flipkart / Goldman / Amazon MLSS": [
            ("Honeywell: aptitude + technical + industrial automation curiosity.", [
                "Data analysis story from LogiFlow model.",
                "Reporting and reliability in enterprise settings.",
            ]),
            ("Flipkart Grid: inventory race, flash sale, cache stampede.", [
                "E-commerce scale; supply chain tie to LogiFlow.",
            ]),
            ("Goldman: probability puzzles + HackerRank math + engineering rigor.", [
                "Mental math; options intuition basic.",
                "CI/CD rollback story.",
            ]),
            ("Amazon MLSS: ML theory test + logistic regression + leakage spotting.", [
                "Bias-variance; cross-val on your delay model honestly.",
            ]),
        ],
    }

    for company, blocks in internet_by_company.items():
        a(f"\\subsection{{Internet-Sourced: {latex_escape(company)}}}\n")
        for title, fus in blocks:
            a("\\textbf{" + latex_escape(title) + "}\n")
            a("\\begin{enumerate}[label=\\textit{Probe \\arabic*:}]\n")
            for fu in fus:
                a("  \\item " + latex_escape(fu) + "\n")
            a("\\end{enumerate}\n\\vspace{2mm}\n")

    a(r"""
\subsection{Post-Mock Fix List (Ojas --- July 2026)}
\begin{enumerate}
  \item \textbf{90-sec intro script} --- degree, IFFCO, LogiFlow, Community Hero, CP one line.
  \item \textbf{IFFCO resume alignment} --- single canonical stack story; no ChatGPT-debugging tangent.
  \item \textbf{LogiFlow 2-min pitch} --- railways pipeline, XGBoost MAE 22.7, Redis cache, 100--400 ms.
  \item \textbf{API JSON mock} --- comparator response with \texttt{ml\_status: pending|complete}.
  \item \textbf{2 STAR collaboration stories} --- memorize; deliver under 60 sec each.
  \item \textbf{Ban filler:} ``you know'', ``basically'', ``like uh'' --- record and count per answer.
\end{enumerate}

\subsection{Communication Rubric (What AI Screens Score)}
\begin{itemize}
  \item \textbf{Strong:} STAR in $<$90s; numbers first; admits unknowns; asks clarifying question.
  \item \textbf{Weak:} 3+ min monologue; contradicts resume; no teamwork example; vague metrics.
  \item \textbf{Fail:} Cannot explain own architecture; blames tools; no question back to interviewer.
\end{itemize}
\newpage
""")


def append_refined_content(a) -> None:
    """Edition 2: canonical scripts, weak/strong contrasts, red-team, whiteboards."""
    a(r"""
\newpage
\section{Canonical Model Answers (Memorize --- Resume-Aligned)}
\textit{These are not essays. Read aloud until you hit time targets without looking. Every number must match your resume.}

\subsection{90-Second Intro \diffLone (HackerRank / phone screen)}
\begin{quote}\small
\textbf{I'm Ojas Srivastava, B.Tech Artificial Intelligence at SVNIT Surat, CGPA 9.20, graduating May 2028.}

\textbf{Last summer I interned at IFFCO Prayagraj for one month, shipping production Node.js and Express services on MySQL---automating 50+ daily workflows and building 10+ REST APIs with JWT auth, Docker, and CI/CD. I owned API slices end-to-end under mentor review.}

\textbf{My flagship project is LogiFlow---Google Solution Challenge Global Top 106---where I co-led backend on GCP Cloud Run: Redis-cached reads at 100--400 ms across 580+ corridors, an XGBoost delay model with MAE 22.7 minutes on 15,650 train-days, and 100/100 pytest business-rule tests.}

\textbf{I also solo-built Community Hero, Vibe2Ship Global Top 20---a civic PWA on Cloud Run.}

\textbf{Competitively I am LeetCode Knight 2048 with 711+ problems solved; I use that for fast debugging, not as a substitute for shipping. I'm looking for an internship where I write reviewed production code---which is why [COMPANY] fits.}
\end{quote}

\subsection{IFFCO STAR (60 seconds) \diffLtwo}
\begin{quote}\small
\textbf{Situation:} At IFFCO Phulpur, operations teams ran 50+ manual daily workflows across farmer and inventory data---slow and error-prone.

\textbf{Task:} I was responsible for two workflow automations and three REST endpoints, not the whole platform.

\textbf{Action:} I gathered requirements from stakeholders, designed MySQL schemas with indexes for reporting queries, implemented Express routes with JWT-protected access and input validation, wrote unit tests for edge cases, and opened PRs for mentor review before Docker deploy.

\textbf{Result:} Those workflows ran in production daily; one validation fix stopped inconsistent farmer records. I documented APIs so the next intern could extend them.
\end{quote}

\subsection{LogiFlow 2-Minute Pitch \diffLtwo}
\begin{quote}\small
\textbf{Problem:} Indian logistics lacks a single place to compare rail vs road cost and delay for freight corridors.

\textbf{My role:} Railway pipeline owner and backend co-lead---not solo on ML or full frontend.

\textbf{Architecture:} Next.js frontend $\rightarrow$ FastAPI/Node services on GCP Cloud Run $\rightarrow$ MySQL/Postgres for 9,526 stations and 580+ corridors $\rightarrow$ Redis for hot route cache keys (origin, destination, weight bucket).

\textbf{Data:} 2017 base CSV plus public APIs and scraping---honest about frugality; 15,650 train-days for XGBoost delay model.

\textbf{Metrics:} MAE 22.7 min; 81\% within 30 min in 5-fold CV; read path 100--400 ms with cache warm.

\textbf{Async ML:} Comparator returns cost immediately; delay prediction runs async---client polls or receives \texttt{ml\_status} pending then complete.

\textbf{Quality:} 100/100 pytest business rules; live demo on Vercel. If I rebuilt: add CDN and stricter time-based train/test split.
\end{quote}

\subsection{Collaboration STAR \#1 --- LogiFlow Redis Split \diffLtwo}
\begin{quote}\small
\textbf{Situation:} During Solution Challenge crunch, teammate wanted all corridor data in-process; I pushed Redis to hit latency targets.

\textbf{Task:} Agree on architecture without blocking the railway pipeline merge.

\textbf{Action:} I wrote a one-page comparison---p99 with/without cache, invalidation on corridor update, fallback if Redis down. We time-boxed a spike; data showed 100--400 ms only with cache. We split: I owned cache keys + API contract; they owned comparator logic.

\textbf{Result:} Merged on schedule; demo held latency; judge questions on cache were answerable because we documented trade-offs in the PR description.
\end{quote}

\subsection{Collaboration STAR \#2 --- IFFCO PR Feedback \diffLtwo}
\begin{quote}\small
\textbf{Situation:} Mentor flagged my first API for missing server-side validation on farmer ID fields.

\textbf{Task:} Fix without breaking existing mobile clients.

\textbf{Action:} Added validation middleware, returned 400 with clear error codes, extended tests, asked mentor to re-review within 24 hours.

\textbf{Result:} Zero regression in production; I now default to validation layer before business logic on every endpoint.
\end{quote}

\subsection{API Response JSON (draw on whiteboard) \diffLthree}
\begin{quote}\small
\begin{verbatim}
GET /api/v1/compare?origin=NDLS&dest=BCT&weight_kg=5000

200 OK (cache hit, ML pending)
{
  "corridor_id": "NDLS-BCT-rail",
  "cost_inr": 84200,
  "distance_km": 1384,
  "mode": "rail",
  "latency_ms": 127,
  "ml_status": "pending",
  "delay_prediction_min": null
}

200 OK (ML complete)
{
  ...
  "ml_status": "complete",
  "delay_prediction_min": 34,
  "model_version": "xgb-v3"
}
\end{verbatim}
\end{quote}

\subsection{Redis Down / Degrade Path \diffLthree}
\begin{quote}\small
If Redis is unavailable: (1) circuit-breaker skips cache after N failures; (2) serve from DB with higher latency---acceptable for demo; (3) alert in logs; (4) never return stale corridor pricing---TTL enforced; (5) ML async queue retried with backoff. I would not claim sub-100 ms without cache in production.
\end{quote}

\newpage
\section{Weak vs Strong --- Fix Your HackerRank Mock Gaps}
\textit{Side-by-side from your July 2026 Moderate Fit / Weak Collaboration screen.}

\subsection{IFFCO story}
\badans{I built websites with HTML and Bootstrap and used ChatGPT to fix broken parts. It was mostly frontend debugging.}
\goodans{I shipped Node.js/Express/MySQL services---50+ automated workflows, 10+ REST APIs, JWT auth, Docker CI/CD. I owned specific endpoints and validation fixes reviewed by my mentor.}

\subsection{Opening pitch}
\badans{Three-minute tour of every hackathon, CP stats first, logistics industry essay before saying my role.}
\goodans{90 seconds: degree $\rightarrow$ IFFCO production $\rightarrow$ LogiFlow metrics $\rightarrow$ one line CP $\rightarrow$ why this company.}

\subsection{LogiFlow architecture}
\badans{``We used SLM models'' / vague ``AI'' without stack, numbers, or personal ownership.}
\goodans{Cloud Run + Redis + XGBoost; MAE 22.7 min; 100--400 ms reads; I owned railway pipeline and cache contract; async \texttt{ml\_status} field.}

\subsection{Collaboration}
\badans{``I'm a good team player'' / no named conflict / no PR review example.}
\goodans{Two STAR stories above---Redis disagreement and IFFCO validation PR---under 60 seconds each.}

\subsection{Metrics consistency}
\badans{Mixing ``80\% accuracy'' and ``65\%'' without defining the metric.}
\goodans{Always: MAE 22.7 minutes; 81\% of predictions within 30 minutes (5-fold CV); separate latency metric 100--400 ms on cached reads.}

\newpage
\section{Interviewer Red-Team Playbook}
\textit{Interviewers use these moves deliberately. Recognize and counter without getting defensive.}

\begin{enumerate}
  \item \textbf{Resume click-through} --- Opens your live demo mid-call. \textit{Counter:} know URL uptime; explain 404 handling; offer GitHub fallback.
  \item \textbf{Stack swap trap} --- ``You said Bootstrap at IFFCO'' vs resume Node. \textit{Counter:} ``Correction---Express/MySQL; Bootstrap was not my stack'' once, then move on.
  \item \textbf{Ownership shrink} --- ``So your mentor did the real work?'' \textit{Counter:} name 2 APIs, 1 schema change, 1 bug with before/after.
  \item \textbf{Metric challenge} --- ``Prove 100--400 ms.'' \textit{Counter:} tool (k6/curl loop), environment, p50 vs p99, cache warm vs cold.
  \item \textbf{Ambiguity freeze} --- long silence after vague answer. \textit{Counter:} ask clarifying question; structure answer STAR or architecture diagram.
  \item \textbf{Ethics ambush} --- OA Forge scraping, cold email. \textit{Counter:} personal learning scope; respect robots.txt; no automated spam; would follow legal at company.
  \item \textbf{Prestige bait} --- ``Why not IIT?'' \textit{Counter:} factual SVNIT + NIT system; outcomes via projects; no defensiveness.
  \item \textbf{Overclaim interrupt} --- ``Stop---what did \emph{you} write?'' \textit{Counter:} ``I co-led backend; teammate owned X; I owned railway pipeline and Redis layer.''
  \item \textbf{Negative sell} --- ``Why shouldn't we hire you?'' \textit{Counter:} real weakness (e.g., verbose under pressure) + mitigation (STAR practice, timers).
  \item \textbf{City trap} --- Bengaluru only vs Hyderabad offer. \textit{Counter:} honest ranking; flexibility where true.
\end{enumerate}

\newpage
\section{System Design Whiteboards (Lite --- Intern Bar)}
\textit{Draw these in 5 minutes; label bottlenecks and one scaling knob.}

\subsection{LogiFlow Read Path}
\begin{verbatim}
[Browser/PWA] --HTTPS--> [Cloud Run API]
                              |
                    +---------+---------+
                    |                   |
               [Redis cache]        [MySQL/Postgres]
               route quotes         stations, corridors
                    |
              cache miss -> DB + populate TTL
                    |
              [Async worker] -> XGBoost delay model
                    |
              update ml_status on result
\end{verbatim}
\textbf{Probe chain:} \diffLtwo Where is thundering herd? \diffLthree Multi-region? \diffLtwo Cache invalidation trigger?

\subsection{IFFCO Workflow Service}
\begin{verbatim}
[Ops UI] --JWT--> [Express API] --> [MySQL]
                       |
                 [Validation middleware]
                       |
                 [Workflow engine: 50+ jobs]
                       |
                 [Docker] <-- GitHub Actions CI
\end{verbatim}
\textbf{Probe chain:} \diffLtwo Idempotent workflow retry? \diffLthree Audit log for cooperative compliance?

\subsection{Wells Fargo Token System (reported OA)}
\begin{verbatim}
[Client] --> [Token Service] --> deque / queue of active tokens
                |                      |
           rate limit              expiry sweep
                |                      |
           [Auth DB]              DFS variant follow-up
\end{verbatim}
\textbf{Probe chain:} \diffLthree Why deque? Security vs latency in banking?

\newpage
\section{HackerRank AI Screen --- Full Mock Replay (30 min)}
\textit{Run with a friend reading \textbf{I:} lines; you answer \textbf{Y:} without notes.}

\subsection{Minute-by-minute script}
\begin{enumerate}
  \item \textbf{0--2 min} \diffLone Eligibility + role alignment --- use 90s intro; stop if friend raises hand at 90s.
  \item \textbf{2--8 min} \diffLtwo IFFCO deep-dive --- STAR above + name 2 APIs + JWT flow.
  \item \textbf{8--14 min} \diffLtwo LogiFlow --- 2-min pitch + whiteboard JSON response.
  \item \textbf{14--20 min} \diffLtwo Data/ML --- MAE 22.7, leakage risks, 5-fold CV purpose.
  \item \textbf{20--26 min} \diffLthree Collaboration --- both STAR stories; friend uses interruption bank below.
  \item \textbf{26--30 min} \diffLone Your questions + thank-you.
\end{enumerate}

\subsection{Interruption bank (friend reads randomly)}
\begin{itemize}
  \item ``You said one month---was that an internship or training?''
  \item ``Name the exact Express middleware you used for auth.''
  \item ``What if Redis and DB disagree on price?''
  \item ``Give me the SQL for your heaviest IFFCO query.''
  \item ``Community Hero---team of one. Who reviewed your code?''
  \item ``Pause---you've talked 3 minutes. Summarize in 30 seconds.''
\end{itemize}

\subsection{Pass criteria for this mock}
\begin{itemize}
  \item Intro $\leq$ 90s; IFFCO stack matches resume; LogiFlow numbers consistent.
  \item Both collaboration STARs delivered; no ``SLM'' or mystery acronyms.
  \item Self-score $\geq$ 4 on rubric in Section 1.
\end{itemize}

\newpage
\section{Company Priority Matrix (Your Pipeline)}
\begin{tabularx}{\textwidth}{@{}lccX@{}}
\toprule
\textbf{Company} & \textbf{Urgency} & \textbf{Prep depth} & \textbf{Why now} \\
\midrule
GE HealthCare & High & Full & Applied; PI + OA likely soon \\
Stripe & High & Full & Applied; 3-part OA + behavioral writing \\
HackerRank screens & High & Canon scripts & Any company using AI screen \\
Google & Medium & OA heavy & GOC segment trees + Googleyness \\
Wells Fargo / Cisco & Medium & SQL + CN/OOP & Enterprise MCQ patterns \\
AlphaGrep & Medium & C++ + CP & Hard OA; start early \\
EA Systest & Medium & Load test narrative & Systest framing critical \\
Amazon MLSS & Lower & ML theory & Selective cohort \\
Others & As scheduled & Mock script only & Flipkart Grid, GS, Honeywell \\
\bottomrule
\end{tabularx}

\section{Microsoft + Additional Internet Patterns (2024--2026)}
\begin{itemize}
  \item \textbf{Microsoft:} Codility 2 mediums (arrays, strings); AA (automated assessment) --- OOP design parking lot/LRU; Azure trivia bonus; ``tell me about a bug you fixed in a team''.
  \item \textbf{Stripe essay:} ``Tell us about you + fit'' --- 250 words: production IFFCO, LogiFlow metrics, curiosity about payments reliability; no CP flex.
  \item \textbf{GE PI:} Interviewer opens your portfolio link --- prepare 404 page story and monitoring.
  \item \textbf{Cisco blind:} Resume only round --- every bullet must survive without college name.
  \item \textbf{Goldman HireVue:} ``Why GS?'' + probability brain teaser recorded on camera.
\end{itemize}

\section{Live Coding Follow-Up Chains (Don't Stop at AC)}
\textit{After solving, interviewers stack these. Practice aloud.}

\begin{enumerate}
  \item \textbf{Two Sum} \diffLone $\rightarrow$ \diffLtwo 3Sum $\rightarrow$ \diffLthree 3Sum closest with proof of two-pointer move.
  \item \textbf{Valid parentheses} \diffLone $\rightarrow$ \diffLtwo Generate all valid $\rightarrow$ \diffLthree Longest valid substring.
  \item \textbf{LRU Cache} \diffLtwo $\rightarrow$ \diffLthree Thread-safe version / distributed cache invalidation story.
  \item \textbf{Rate limiter} \diffLtwo $\rightarrow$ \diffLthree Per-merchant limits + Redis atomicity.
  \item \textbf{Level-order traversal} \diffLone $\rightarrow$ \diffLtwo Zigzag $\rightarrow$ \diffLthree Serialize BT with null markers.
  \item \textbf{Merge intervals} \diffLtwo $\rightarrow$ \diffLthree Employee free time across calendars.
\end{enumerate}

\newpage
""")


def append_extensive_banks(a) -> None:
    """Additional exhaustive sections for realism."""
    extra_behavioral = [
        ("Tell me about yourself --- 30s / 90s / 3min versions.", ["Which version for a bar raiser?", "Remove all awards---still compelling?"]),
        ("Why intern now vs focusing on CP?", ["Is internship just resume padding?", "What if you fail to convert?"]),
        ("Conflict with a teammate who wouldn't review your PR.", ["Exact Slack message you'd send.", "When do you involve the mentor?"]),
        ("Time you shipped something you knew was wrong.", ["Technical debt accepted?", "How did you document it?"]),
        ("Most embarrassing bug in front of users.", ["Hotfix process?", "Communication to stakeholders?"]),
        ("Describe LogiFlow team dynamics. Who argued with you?", ["What did you lose on?", "What did you win on?"]),
        ("Community Hero solo---prove you didn't outsource work.", ["Hardest integration point?", "Git history story?"]),
        ("Why SVNIT and not IIT?", ["Defensive answer trap---stay factual."]),
        ("CGPA 9.20---why not higher?", ["Which course pulled you down?", "Learning vs grades?"]),
        ("McKinsey Forward Fellow---what did it change in you?", ["Not name-dropping---substance?"]),
        ("Mentoring at Nexus---tell about a junior who struggled.", ["How do you measure mentor success?"]),
        ("ACM events you organized---numbers, outcomes.", ["Budget? Sponsors? Failures?"]),
        ("RangRiti Technical Lead---what broke on demo day?", ["Rollback plan?"]),
        ("If we Google your GitHub right now, what will we critique?", ["Open issues?", "Test coverage gaps?"]),
        ("What are you building this week?", ["Not vaporware---show commit cadence."]),
    ]
    a(qblock("Extended Behavioral Bank (Round 2 HR + Hiring Manager)", extra_behavioral))

    hr_logistics = [
        ("Summer 2027 availability: exact dates.", ["May--Aug full-time?", "Exam conflicts in SVNIT calendar?"]),
        ("Bengaluru relocation from Surat.", ["Housing plan?", "Budget?", "Family constraints?"]),
        ("Will you accept hybrid in Hyderabad if Bengaluru fails?", ["Preference ranking of cities?"]),
        ("Stipend expectations.", ["Trap: don't anchor too high for intern; show flexibility."]),
        ("Other offers / pipelines in flight.", ["Honesty without sounding desperate."]),
        ("Security clearance / background check issues?", ["Any legal incidents? Default no."]),
        ("Need academic credit for internship?", ["SVNIT internship policy awareness?"]),
        ("Rejoin as PPO goal---explicit or exploratory?", ["Company-specific honesty."]),
    ]
    a(qblock("HR + Logistics (Often Dismissed --- Don't)", hr_logistics))

    resume_lines = [
        ("Bullet: 50+ daily workflows --- quantify users and frequency.", ["Per workflow runtime?", "Manual time saved?"]),
        ("Bullet: 10+ REST APIs --- pick 3 methods + status codes.", ["429 handling?", "Pagination?"]),
        ("Bullet: 100--400 ms read paths --- measurement harness.", ["wrk/k6?", "Synthetic vs real?"]),
        ("Bullet: 580+ corridors --- data source provenance.", ["Government open data?", "Cleaning pipeline?"]),
        ("Bullet: 9,526 stations --- schema normalization.", ["Duplicates across zones?"]),
        ("Bullet: 15,650 train-days --- label definition.", ["What counts as a train-day?"]),
        ("Bullet: MAE 22.7 min --- baseline comparison.", ["Naive baseline?", "Business acceptable error?"]),
        ("Bullet: 100/100 pytest --- are tests too brittle?", ["Mutation testing awareness?"]),
        ("Bullet: 14K+ question occurrences --- legal/ethical sourcing.", ["DMCA concern?"]),
        ("Bullet: 5.5K+ test cases --- generation vs manual.", ["False AC risk?"]),
        ("Bullet: 965+ companies scout --- maintenance burden.", ["Broken scrapers weekly?"]),
        ("Bullet: LeetCode Knight 2048 --- contest vs practice split.", ["When did you peak?", "Trend last 6 months?"]),
        ("Bullet: Vibe2Ship Top 20 --- team size vs solo claim.", ["What did judges score?"]),
        ("Bullet: GSC Top 106 --- how many teams globally?", ["Your rank within team?"]),
    ]
    a(qblock("Resume Line-by-Line Interrogation (Bring BATCH-6 PDF)", resume_lines))

    leadership = [
        ("ACM Executive Member---conflict with faculty advisor.", ["Budget overrun story?"]),
        ("Nexus DSA Mentor---curriculum you designed.", ["Beginner failure modes?", "How many mentees?"]),
        ("Organizing contest---cheating detection.", ["Plagiarism tools?", "Appeals process?"]),
        ("Balancing mentorship vs your own CP grind.", ["Time audit weekly?"]),
    ]
    a(qblock("Leadership + POR (ACM SVNIT / Nexus)", leadership))

    rapid_fire = [
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
    a("\\subsection{Rapid-Fire 30 (30 seconds each, no filler)}\n\\begin{enumerate}\n")
    for rf in rapid_fire:
        a("  \\item " + latex_escape(rf) + "\n")
    a("\\end{enumerate}\n\\newpage\n")

    more_mocks = [
        {
            "title": "Mock Round D --- Google SWE Intern (60 min)",
            "interviewer": "L3/L4 Engineer, Core Infrastructure",
            "flow": [
                ("0--5 min", "Warm-up: favorite data structure and non-coding use."),
                ("5--15 min", "Coding #1: medium array/graph with follow-up optimization."),
                ("15--25 min", "Coding #2: strings + hash map twist."),
                ("25--40 min", "System: design global key-value cache for LogiFlow reads."),
                ("40--50 min", "Behavioral: failed hypothesis in project."),
                ("50--60 min", "Reverse: questions + 'What Google product would you remove?' (trap: be thoughtful)."),
            ],
            "brutal_moments": [
                "'Your second solution is still not optimal---try again.'",
                "'How would this work at Google scale with multi-region?'",
                "'Tell me about a time you had no idea what to do for 2 days.'",
            ],
        },
        {
            "title": "Mock Round E --- Wells Fargo / Enterprise Bank (45 min)",
            "interviewer": "VP Technology + Campus Recruiter",
            "flow": [
                ("0--8 min", "Why banking; why not fintech startup?"),
                ("8--18 min", "SQL live + explain integrity constraints."),
                ("18--28 min", "Secure SDLC story from IFFCO."),
                ("28--38 min", "Situational judgment: data leak scare."),
                ("38--45 min", "Program fit + location preference."),
            ],
            "brutal_moments": [
                "'Banking is boring---convince me you'll stay engaged.'",
                "'Node in production at coop---would we allow that here?'",
            ],
        },
        {
            "title": "Mock Round F --- EA Systest / Games Platform (50 min)",
            "interviewer": "Senior SDET, EADP Hyderabad",
            "flow": [
                ("0--10 min", "Resume: Career Automation Stack only."),
                ("10--25 min", "Design load test for login API."),
                ("25--35 min", "Debug flaky test exercise."),
                ("35--45 min", "Coding: parse log file, top 10 error codes."),
                ("45--50 min", "Culture: crunch vs quality (navigate carefully)."),
            ],
            "brutal_moments": [
                "'Systest is unglamorous---why not gameplay engineering?'",
                "'Your WebSocket load numbers are tiny for games scale.'",
            ],
        },
        {
            "title": "Mock Round G --- Cisco Networking Flavor (45 min)",
            "interviewer": "Application Software Engineer",
            "flow": [
                ("0--10 min", "TCP/IP deep dive tied to your projects."),
                ("10--20 min", "Secure coding checklist for REST APIs."),
                ("20--30 min", "Coding: implement prefix trie for routing table toy."),
                ("30--40 min", "Agile ceremony participation proof."),
                ("40--45 min", "Device/cloud intersection curiosity."),
            ],
            "brutal_moments": [
                "'Name a Cisco product---if you can't, why Cisco?'",
                "'How does your PWA relate to networking?'",
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
                "'You mentioned Bootstrap---resume says Express. Which is true?'",
                "'Pause. Summarize LogiFlow in 30 seconds.'",
                "'No teamwork example yet---Weak Fit on collaboration.'",
            ],
        },
        {
            "title": "Mock Round I --- Stripe Essay + Integration (60 min)",
            "interviewer": "Recruiter + Engineer pair",
            "flow": [
                ("0--10 min", "Read aloud 250-word Stripe fit essay; cut fluff live."),
                ("10--25 min", "Log-parse 3-part OA simulation on paper."),
                ("25--40 min", "Integration: paginated API + idempotent retry design."),
                ("40--50 min", "Code review diff critique exercise."),
                ("50--60 min", "Why Stripe over Razorpay---specific product reference."),
            ],
            "brutal_moments": [
                "'Your essay mentions CP twice---remove and re-read.'",
                "'Part 2 fails if Part 1 parsing is brittle---show tests.'",
            ],
        },
    ]
    MOCK_SCRIPTS.extend(more_mocks)

    oa_sim = [
        ("Stripe/Google OA simulation (90 min)", [
            "0--15: warm-up easy array.",
            "15--45: medium #1 (intervals/heap).",
            "45--75: medium #2 (graphs/BFS).",
            "75--90: review complexity, edge cases, test cases.",
        ]),
        ("GE/Honeywell OA simulation (60 min)", [
            "20 MCQ OS/DBMS/CN.",
            "20 MCQ aptitude.",
            "1 coding medium.",
            "5 HR written responses.",
        ]),
        ("AlphaGrep OA simulation (120 min)", [
            "3 implementation-heavy problems.",
            "Fast I/O required.",
            "Partial scoring---attempt all.",
        ]),
    ]
    a("\\section{OA Full Simulation Timetables}\n")
    for title, steps in oa_sim:
        a("\\subsection{" + latex_escape(title) + "}\n\\begin{enumerate}\n")
        for s in steps:
            a("  \\item " + latex_escape(s) + "\n")
        a("\\end{enumerate}\n")

    a("\\newpage\n")


def append_mega_content(a) -> None:
    """Final expansion: transcripts, coding bank, STAR worksheets."""
    a(r"\section{Full Verbatim Mock Transcripts (Read Aloud with a Friend)}" + "\n")

    transcripts = [
        ("Stripe --- Round 1 (excerpt, 12 min)", r"""
\textbf{Interviewer (I):} Thanks for joining. I've got your resume---B.Tech AI, IFFCO, LogiFlow, OA Forge. Quick one: what happens when I click Pay on a Stripe Checkout page? Keep it under two minutes.

\textbf{You (Y):} [Answer: browser $\rightarrow$ merchant backend creates PaymentIntent $\rightarrow$ client secret $\rightarrow$ Stripe.js confirms $\rightarrow$ webhooks notify merchant $\rightarrow$ idempotent fulfillment.]

\textbf{I:} Good. You wrote production Node at IFFCO for one month. Skeptical---what did \emph{you} own?

\textbf{Y:} [Name 2--3 APIs, one schema change, one bug you fixed.]

\textbf{I:} LogiFlow---100 to 400 ms. Measured how?

\textbf{Y:} [Tool, environment, p50 vs p99, before/after.]

\textbf{I:} If Redis evaporates?

\textbf{Y:} [Degrade path, DB fallback, circuit breaker, alert.]

\textbf{I:} Coding: implement rate limiter, 10 req/sec per API key.

\textbf{Y:} [Token bucket; mention thread safety if asked.]

\textbf{I:} Why Stripe over building payments yourself?

\textbf{Y:} [Compliance, reliability, global rails, learning from best team.]
"""),
        ("GE HealthCare --- Hiring Manager (excerpt, 10 min)", r"""
\textbf{I:} Why healthcare software if your projects are logistics and civic apps?

\textbf{Y:} [Impact on clinicians, reliability culture, compute/visualization interest---honest pivot.]

\textbf{I:} Walk SDLC for one IFFCO feature.

\textbf{Y:} [Req $\rightarrow$ design $\rightarrow$ impl $\rightarrow$ test $\rightarrow$ deploy $\rightarrow$ feedback.]

\textbf{I:} Workday says B.S. Computer Science. Resume B.Tech AI. Explain.

\textbf{Y:} [ATS mapping; coursework is CS-core; official degree at NIT.]

\textbf{I:} How do you test software where mistakes hurt patients, even if you don't touch PHI?

\textbf{Y:} [Traceability, regression suites, documentation, escalation---no fake HIPAA claims.]

\textbf{I:} On-site Bengaluru entire summer?

\textbf{Y:} [Yes + logistics.]
"""),
        ("AlphaGrep --- Core SWE (excerpt, 15 min)", r"""
\textbf{I:} CF 1419 Specialist. Why not more contests before applying here?

\textbf{Y:} [Honest balance with shipping projects; trend improving.]

\textbf{I:} OA Forge judge---sandbox escape in 30 seconds.

\textbf{Y:} [Timeouts, syscall restrictions, resource limits, separate user, no network.]

\textbf{I:} std::vector reallocation---what invalidates?

\textbf{Y:} [Iterators/pointers/references; emplace vs push\_back trade-offs.]

\textbf{I:} Parse 10M integers from stdin fast---outline.

\textbf{Y:} [Fast I/O, avoid endl, reserve where possible, minimal allocations.]

\textbf{I:} Why trading?

\textbf{Y:} [Real systems constraints + personal markets interest---specific, not glam.]
"""),
        ("HackerRank AI Screen --- Full Replay (excerpt, 18 min)", r"""
\textbf{I:} Walk me through your background and recent work. Ninety seconds.

\textbf{Y:} [Use canonical 90s intro---stop at degree, IFFCO, LogiFlow, Community Hero, CP one line.]

\textbf{I:} IFFCO was one month. What did you actually build?

\textbf{Y:} [STAR: Node/Express/MySQL; 50+ workflows; 10+ APIs; JWT; name 2 endpoints.]

\textbf{I:} LogiFlow---your role and backend architecture. Two minutes.

\textbf{Y:} [2-min pitch: Cloud Run, Redis 100--400 ms, XGBoost MAE 22.7, async ml\_status.]

\textbf{I:} Redis and GCP---what is cached and what does the API return?

\textbf{Y:} [Draw JSON; cache keys; pending vs complete ML.]

\textbf{I:} Collaboration example---code review or disagreement.

\textbf{Y:} [Redis split STAR under 60s; IFFCO validation PR if time.]

\textbf{I:} [SILENCE 5 sec] You talked three minutes on logistics. Thirty-second summary.

\textbf{Y:} [``I owned railway pipeline and cache layer; MAE 22.7 min; 100--400 ms reads.'']

\textbf{I:} Any questions for us?

\textbf{Y:} [Intern project success criteria; mentor pairing; code review culture.]
"""),
    ]
    for title, body in transcripts:
        a("\\subsection{" + latex_escape(title) + "}\n")
        a(body + "\n\\newpage\n")

    a(r"\section{Coding Problem Bank --- 60 Problems (Company-Tagged)}" + "\n")
    problems = [
        ("Stripe/Google", "Two Sum / 3Sum", "Valid Parentheses", "Merge Intervals", "LRU Cache", "Rate Limiter", "Serialize BT", "Word Break", "Course Schedule", "K Closest Points"),
        ("GE/Honeywell", "SQL: second highest salary", "Find duplicate emails", "Running total", "Array rotation", "String anagram groups", "BST validation"),
        ("Wells Fargo/GS", "Expected dice rolls", "Stock span", "Max subarray", "Matrix islands", "Coin change", "Probability: birthday paradox sketch"),
        ("AlphaGrep", "Fast stdin sum", "Custom sort with comparator", "Segment tree range sum (conceptual)", "Greedy scheduling", "Binary search on answer"),
        ("EA Systest", "Parse nginx log top IPs", "Flaky test reproduction plan", "pytest fixture design", "Load test scenario doc"),
        ("Amazon MLSS", "Logistic regression grad", "Train/test leakage spotting", "Vectorized mean in numpy", "Bias-variance tradeoff MCQ"),
        ("Cisco", "Prefix trie insert/search", "TCP handshake ordering quiz", "HTTP status code scenarios"),
        ("Flipkart", "Inventory decrement race", "Cache stampede mitigation", "Cart merge concurrency"),
        ("General", "Detect cycle in LL", "Topo sort", "Dijkstra", "Union Find", "Heap merge K lists", "DP knapsack", "Sliding window max"),
    ]
    for tag, *probs in problems:
        a("\\subsection{" + latex_escape(tag) + "}\n\\begin{enumerate}\n")
        for p in probs:
            a("  \\item " + latex_escape(p) + " --- \\textit{Follow-up: time/space, edge cases, test cases.}\n")
        a("\\end{enumerate}\n")

    a(r"\section{STAR Story Worksheets (Fill Before Interview)}" + "\n")
    stories = [
        "IFFCO production delivery under mentor oversight",
        "LogiFlow latency crisis during Solution Challenge",
        "Community Hero solo ship under hackathon deadline",
        "OA Forge security/scoping decision",
        "ACM/Nexus mentoring breakthrough",
        "Code review conflict resolution",
        "Failed approach you pivoted from",
    ]
    for s in stories:
        a("\\subsection{" + latex_escape(s) + "}\n")
        a("\\begin{itemize}\n")
        for part in ["Situation (2 sentences)", "Task (your responsibility only)", "Action (technical verbs, metrics)", "Result (quantified)", "Brutal follow-up you fear"]:
            a("  \\item \\textbf{" + latex_escape(part) + "}: \\rule{0.65\\textwidth}{0.4pt}\n")
        a("\\end{itemize}\n")

    a(r"\section{Panel Stress Interview (3 Interviewers, 60 min)}" + "\n")
    a(r"""
\begin{enumerate}
  \item \textbf{Engineer A} attacks LogiFlow architecture for 15 min straight.
  \item \textbf{Engineer B} asks OS/DBMS/CN rapid fire; no pauses $>$ 5 sec.
  \item \textbf{HR C} asks ethics of scraping, cold email, OA Forge legality.
  \item \textbf{All three:} ``Where do you rank yourself in your batch? Prove it.''
  \item \textbf{Closing:} each gives one reason to reject you---you respond without defensiveness.
\end{enumerate}
""")


if __name__ == "__main__":
    main()
