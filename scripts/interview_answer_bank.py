#!/usr/bin/env python3
"""Comprehensive spoken-answer resolver for Ojas Srivastava interview prep."""

from __future__ import annotations

from collections.abc import Callable, Iterable

from generate_brutal_interview_prep import (
    COMPANIES as GEN_COMPANIES,
    CS_FUNDAMENTALS as GEN_CS_FUNDAMENTALS,
    MOCK_SCRIPTS as GEN_MOCK_SCRIPTS,
    PROJECT_QUESTIONS as GEN_PROJECT_QUESTIONS,
    UNIVERSAL_BEHAVIORAL as GEN_UNIVERSAL_BEHAVIORAL,
)
from interview_questions_shared import (
    CODING_PROBLEMS,
    COMPANY_EXTRA,
    EXTRA_BEHAVIORAL,
    HR_LOGISTICS,
    HR_SCREEN,
    INTERNET_BY_COMPANY,
    LEADERSHIP,
    MOCK_SCRIPTS,
    PANEL_STRESS,
    QUESTIONS_TO_ASK,
    RAPID_FIRE,
    RED_TEAM,
    RESUME_LINES,
    TRAP_QUESTIONS,
    UNIVERSAL_BEHAVIORAL,
    CS_FUNDAMENTALS,
    PROJECT_QUESTIONS,
)


CANON: dict[str, str] = {
    "intro_90s": (
        "I am Ojas Srivastava, a B.Tech Artificial Intelligence student at SVNIT Surat with a CGPA of 9.20, graduating in May 2028. "
        "In June and July 2025, I interned at IFFCO in Prayagraj, where I shipped production Node and Express services over MySQL, "
        "automated more than 50 daily workflows, and built over 10 REST APIs with JWT auth, Docker, and CI/CD. "
        "My flagship project is LogiFlow, a Google Solution Challenge Top 106 project, where I co-led backend work on Cloud Run and Redis, "
        "served corridor reads in roughly 100 to 400 milliseconds across 580+ corridors and 9,526 stations, and supported an XGBoost delay model at MAE 22.7 minutes on 15,650 train-days. "
        "I also built Community Hero solo and reached Global Top 20 in Vibe2Ship. I enjoy shipping code that survives review and real constraints, "
        "which is why I am targeting a software internship where I can own production-ready components."
    ),
    "iffco_star": (
        "At IFFCO, operations teams had repetitive daily processes and frequent data inconsistencies. "
        "My task was to own specific workflow and API slices, not the whole platform. "
        "I implemented Node/Express endpoints on MySQL, added input validation and JWT-protected routes, containerized services with Docker, "
        "and integrated checks into CI/CD. I worked closely with my mentor through PR reviews and fixed a validation issue that was creating inconsistent farmer records. "
        "The result was stable automation for 50+ workflows and cleaner, more predictable API behavior for downstream users."
    ),
    "logiflow_pitch": (
        "LogiFlow solves freight planning by comparing rail and road routes with both cost and delay perspective. "
        "I co-led backend and owned the railway pipeline plus caching contract. "
        "The stack was Cloud Run services, Redis for hot route cache, and relational storage for stations and corridors. "
        "We modeled more than 580 corridors over 9,526 stations, and used 15,650 train-days for delay learning. "
        "Our XGBoost model reached MAE 22.7 minutes, and our API reads were generally 100 to 400 milliseconds on warm paths. "
        "We also maintained strict test discipline with 100/100 pytest checks for business rules."
    ),
    "collab_redis": (
        "In LogiFlow, we had a disagreement: one teammate wanted to keep everything in-process while I advocated Redis for predictable latency. "
        "I avoided opinion battles and proposed a short benchmark spike with agreed success criteria. "
        "The data showed Redis gave more stable read latency, so we split ownership cleanly: I handled key design and invalidation behavior while my teammate focused on comparator logic. "
        "That compromise helped us ship on time and explain our trade-offs clearly during judging."
    ),
    "collab_iffco": (
        "At IFFCO, a mentor review pointed out that my first API version lacked robust server-side validation. "
        "I accepted the feedback, added validation middleware and clearer 400 error contracts, expanded tests, and re-opened for review quickly. "
        "That changed my default engineering behavior: now I treat validation as first-class design, not an afterthought."
    ),
    "weakness": (
        "A real weakness I have worked on is over-explaining when I am excited about a technical system. "
        "In interviews this can look unfocused, so I now use a strict structure: one-line context, two key decisions, one measurable result, then stop and invite follow-up."
    ),
    "why_intern_now": (
        "I do competitive programming for problem-solving speed, but internships are where I build production judgment. "
        "I want to learn team code review standards, release discipline, and reliability habits in real engineering environments, "
        "which is different from contest performance."
    ),
    "first_30_days": (
        "In my first 30 days I would prioritize onboarding and reliability over flashy changes: understand service ownership, deployment and alerting flows, "
        "pick one scoped bug or latency pain point, ship a tested improvement, and document trade-offs so the team can maintain it."
    ),
    "ge_workday_mapping": (
        "For GE, if Workday shows B.S. and CS field labels, that is ATS mapping. "
        "My actual degree is B.Tech in Artificial Intelligence at SVNIT Surat. "
        "I am transparent about that and I map my coursework to core CS topics I actively apply: DSA, DBMS, OS, networking, and backend systems."
    ),
    "availability": (
        "I am available full-time in Summer 2027 and can relocate. "
        "My preference is Bengaluru, but I am open to other major hubs if the role fit and team scope are strong."
    ),
    "ethics_oa_forge": (
        "OA Forge was built for personal learning and interview simulation, not for violating platform policies. "
        "I keep ethics boundaries clear: respect terms of service, avoid abusive scraping, and prioritize legal and compliance guidance in any real company context."
    ),
    "coding_framework": (
        "My coding approach is: clarify inputs and constraints, state brute force and optimized options, pick data structures with complexity targets, "
        "write clean code with edge-case checks, and close with test cases plus time and space analysis."
    ),
}


RAPID_FIRE_ANSWERS: dict[str, str] = {
    "Big-O of your favorite LogiFlow endpoint.": "For route compare reads with cache hit, it is effectively O(1) lookup plus serialization overhead; on cache miss, cost depends on indexed DB query but designed to stay near logarithmic index access.",
    "CAP theorem---where does Redis sit?": "Redis in our setup is primarily a CP-leaning cache component under partition trade-offs; we prefer consistency on key correctness over serving stale critical route data.",
    "Normalize vs denormalize in one sentence with example.": "Normalize for correctness and update safety in base station/corridor tables, denormalize selectively for read-heavy response speed like precomputed route summary views.",
    "HTTP 401 vs 403 in IFFCO auth.": "401 means authentication missing or invalid token; 403 means token is valid but access is not allowed for that role or resource.",
    "Difference between JWT and session cookie.": "JWT is self-contained token validation at the service edge, while session cookies rely on server-side session state; JWT scales statelessly but needs careful expiry and revocation strategy.",
    "What is connection pooling in MySQL?": "It reuses DB connections across requests so we avoid expensive connect/disconnect overhead and stabilize latency under concurrent traffic.",
    "Docker layer caching---practical tip.": "Copy dependency manifests first, install deps, then copy app code so unchanged dependencies stay cached between builds.",
    "CI fails on lint but not tests---ship or block?": "Block by default; style failures often hide maintainability drift and should be fixed before merge unless there is a declared emergency exception path.",
    "Git rebase vs merge for intern PRs.": "I rebase locally for clean history and merge via team policy so review context stays intact.",
    "When is gradient boosting better than linear regression for delays?": "When delay behavior is nonlinear with feature interactions and threshold effects, boosting captures patterns linear models miss.",
    "Precision vs recall for delay alerts.": "Precision avoids false alarms; recall avoids missing true delays. For operations, we tune based on the cost of missed delay versus alert fatigue.",
    "ChromaDB vs Pinecone---why you chose Chroma.": "Chroma was enough for hackathon scope, fast local iteration, and lower operational complexity; I would revisit managed options at larger scale.",
    "WebSocket close codes you actually know.": "1000 normal closure, 1001 going away, 1006 abnormal closure observed client-side, and 1011 for internal server error conditions.",
    "A* heuristic admissibility in AirHelp graph.": "Admissibility means the heuristic never overestimates true remaining cost, so A* still guarantees optimality.",
    "C++17 feature you used in OA Forge.": "I used structured bindings and `std::optional` patterns to keep parsing and judge-result handling clearer.",
    "Undefined behavior example in C++.": "Accessing an out-of-bounds vector index or using an invalidated iterator after reallocation are classic UB examples.",
    "Python GIL---does it affect your FastAPI app?": "Yes for CPU-bound threads; for I/O-bound APIs with async it is less limiting, and CPU-heavy work should move to worker processes.",
    "async/await vs threads for I/O bound work.": "I prefer async/await for high-concurrency I/O with lower overhead; threads are useful for blocking libraries and simpler migration paths.",
    "Supabase vs raw Postgres---trade-off.": "Supabase accelerates auth, storage, and ops speed; raw Postgres gives finer control and potentially tighter performance tuning.",
    "Cloud Run concurrency setting you tuned.": "I tuned concurrency to balance latency and cost, avoiding overpacking when p95 latency started rising.",
    "Cold start mitigation list (3 items).": "Keep image small, minimize startup initialization, and use warm traffic patterns with sensible min instances when budget allows.",
    "OAuth2 authorization code flow steps.": "User authenticates at provider, app gets auth code, backend exchanges code for tokens, and then uses access token for API calls.",
    "Rate limiting: token bucket vs leaky bucket.": "Token bucket allows bursts with average control; leaky bucket smooths output rate more strictly.",
    "Idempotency key placement in Stripe-like API.": "Place it in request headers and persist key plus result hash server-side for safe retry deduplication.",
    "SAGA vs 2PC---one-line intern answer.": "Use SAGA for scalable distributed compensation patterns, 2PC only when strict atomicity and coordinator cost are acceptable.",
    "Load balancer layer 4 vs layer 7.": "L4 routes by transport details and is faster/simpler; L7 routes with HTTP-aware logic like paths and headers.",
    "CDN cache hit ratio---what's good enough?": "Context-dependent, but for static assets I target very high hit rates and investigate quickly if it drops materially.",
    "Selenium vs Playwright for scrapers.": "Playwright generally gives better reliability and modern async ergonomics; Selenium has broader legacy ecosystem familiarity.",
    "Ethics of scraping job boards.": "Respect robots and terms, avoid abusive rates, and never collect or use data in ways users did not consent to.",
    "How you validate an OA question match.": "I compare normalized statement structure, constraints, and canonical test signatures before accepting a match.",
    "Explain CAP theorem using LogiFlow Redis + MySQL.": "On partition, we prefer correct durable source in MySQL and degrade cache behavior rather than serving risky stale data as truth.",
    "What is the thundering herd problem and your LogiFlow fix?": "Many clients miss cache together and stampede DB; we use jittered TTLs and single-flight style key rebuild control.",
    "Difference between IaaS, PaaS, SaaS with your stack examples.": "Cloud Run is PaaS-like for app deployment, VM-level control is IaaS, and tools like hosted collaboration products are SaaS.",
    "Stripe idempotency key --- where stored and for how long?": "Store it in a durable request ledger keyed by endpoint and merchant context, retained for the retry safety window defined by business policy.",
    "GE Workday B.S. mapping --- 15-second honest answer.": "That is ATS field mapping; my official degree is B.Tech AI at SVNIT, and I am explicit about that.",
    "Community Hero Firestore security rules --- one rule you wrote.": "I enforced that only authenticated users can write reports and only privileged roles can update moderation status fields.",
    "OA Forge memory limit --- how enforced in judge?": "Per-submission process limits with sandbox constraints and kill-on-threshold to prevent runaway memory usage.",
    "When would you pick Postgres over MySQL for LogiFlow?": "If we needed richer analytical SQL patterns, stronger extension ecosystem, or geospatial-heavy querying at scale.",
    "Explain your cold-start mitigation on Cloud Run (3 bullets).": "Lean container, lazy-load heavy components, and traffic-aware warm strategy with careful cost guardrails.",
}


def _norm(text: str) -> str:
    return " ".join(text.lower().strip().split())


def _has_any(text: str, keys: Iterable[str]) -> bool:
    lowered = _norm(text)
    return any(k in lowered for k in keys)


def _company_name(company: str | None, question: str) -> str:
    if company:
        return company
    for c in COMPANY_EXTRA:
        if c.lower() in question.lower():
            return c
    return "this company"


def _rapid_or_short(question: str) -> bool:
    q = _norm(question)
    return question in RAPID_FIRE_ANSWERS or question in RAPID_FIRE or _has_any(
        q,
        [
            "one sentence",
            "15-second",
            "30 seconds",
            "difference between",
            "what is",
            "big-o",
        ],
    )


def _answer_universal_behavioral(question: str, company: str | None = None) -> str:
    q = _norm(question)
    if "walk me through your resume" in q or "tell me about yourself" in q:
        return CANON["intro_90s"]
    if "harsh critical feedback" in q:
        return (
            "A strong feedback moment was at IFFCO when my mentor said my initial endpoint was functionally correct but not production-safe because input validation was too weak. "
            "I first felt defensive, then I asked for concrete failure cases. I added validation middleware, clearer error codes, and tests for malformed inputs. "
            "That changed my workflow: now I design failure paths before happy paths. If I redid it, I would ship that validation contract from day one and avoid rework. "
            "The key lesson is to treat criticism as free architecture review, not personal judgment."
        )
    if "production bug" in q:
        return (
            "At IFFCO we found inconsistent records coming through one workflow path. I traced it by reproducing with known bad payloads, checking request logs, and isolating the endpoint missing server-side validation. "
            "I added schema validation, explicit 400 responses, and tests that replayed the bad payload set. I confirmed the fix in staging before merge and monitored error rates after deploy. "
            "A better monitoring setup would have been contract-level input anomaly alerts to catch it earlier."
        )
    if "pure cse degree" in q or "ai degree but swe role" in q:
        return (
            "I respect that concern. My degree title is AI, but my day-to-day work has been software engineering: Node/Express/MySQL APIs at IFFCO, Cloud Run backend and Redis in LogiFlow, and reliability-focused design decisions. "
            "I bring core CS fundamentals with applied systems execution. I do not claim an advantage from labels; I show value through shipped components, measurable latency improvements, and collaborative code reviews."
        )
    if "biggest weakness" in q:
        return CANON["weakness"]
    if "one month at iffco" in q:
        return (
            "It was one month, and I present it exactly that way. The reason it still matters is that it was production work, not shadowing. "
            "I owned specific API and workflow slices end-to-end with mentor review, used Node/Express/MySQL, implemented JWT-protected endpoints, and worked through real bug fixes. "
            "So the duration was short, but the engineering cycle was complete: requirements, implementation, testing, review, deployment, and post-fix validation."
        )
    if "not the leader" in q:
        return (
            "In LogiFlow I was not the only leader; I co-led backend in a team setting. One technical disagreement was around caching strategy. "
            "I proposed a benchmark-driven decision instead of arguing from preference. We time-boxed a spike, compared latencies, and then split responsibilities cleanly. "
            "That experience taught me that influence comes from reproducible evidence and respectful compromise, not title."
        )
    return (
        "My approach is to answer with clear scope, personal ownership, and measurable outcomes. "
        "For my profile that usually means one concise IFFCO production story, one LogiFlow architecture decision, and one collaboration lesson with specific numbers."
    )


def _answer_cs(question: str) -> str:
    q = _norm(question)
    if "go deeper" in q:
        return (
            "Going deeper, I would formalize assumptions, specify complexity bounds, and discuss real failure modes I have seen in my projects. "
            "For example in LogiFlow, simple cache talk is not enough: key cardinality, invalidation triggers, and Redis-down behavior are what matter at scale."
        )
    if "give a number" in q:
        return (
            "A concrete number from my projects: LogiFlow warm read paths were typically around 100 to 400 milliseconds, and the delay model MAE was 22.7 minutes on 15,650 train-days. "
            "At IFFCO, I worked on 50+ workflow automations and 10+ REST APIs."
        )
    if "what breaks at scale" in q:
        return (
            "At scale, hidden assumptions break first: cache stampedes, hot partitions, connection-pool exhaustion, and noisy-neighbor effects. "
            "My default mitigation is measured load testing, defensive timeouts, graceful degradation, and instrumentation before feature expansion."
        )
    if "process and thread" in q:
        return "A process has isolated memory and heavier context overhead; threads share process memory and are lighter but need synchronization. For I/O-heavy backend tasks, threads or async models improve concurrency; for strong isolation, processes are safer."
    if "acid" in q:
        return "In IFFCO-style transaction flows, atomicity ensures all related updates commit together, consistency preserves schema and business rules, isolation prevents concurrent write anomalies, and durability guarantees committed data survives crashes."
    if "tcp" in q and "udp" in q:
        return "TCP gives ordered reliable delivery, which fits API and most WebSocket transports; UDP is lower overhead but needs app-level reliability logic and is better for specific latency-sensitive streaming patterns."
    if "lru cache" in q:
        return "I would use a hash map plus doubly linked list for O(1) get/put and eviction, then choose capacity based on hot corridor set size and memory budget observed from traffic distribution."
    return (
        "I would answer this by defining the concept, mapping it to one of my project decisions, and then giving a scale failure scenario with mitigation and complexity."
    )


def _answer_project(question: str, parent: str | None = None) -> str:
    q = _norm(question)
    root = _norm(parent or "")
    merged = f"{root} {q}".strip()

    if "iffco" in merged:
        if "jwt" in merged or "auth" in merged:
            return "Login validates credentials, issues a signed JWT with expiry, and protected routes verify signature and claims before business logic. For revocation, I would maintain deny-list strategy or short token life plus refresh controls, and harden against XSS by secure handling on clients."
        if "docker" in merged or "ci/cd" in merged or "pipeline" in merged:
            return "My IFFCO pipeline was commit to PR, lint and tests on CI, container build, and controlled deployment after review approval. If I improve it now, I add contract tests, migration checks, and rollback playbooks."
        return CANON["iffco_star"]

    if "logiflow" in merged:
        if "redis" in merged or "thundering herd" in merged:
            return (
                "We cached corridor reads using keys built from origin, destination, and weight bucket. "
                "To control thundering herd, we used staggered TTL behavior and recomputation discipline on misses. "
                "If Redis fails, we degrade to DB with higher latency and keep correctness over speed."
            )
        if "xgboost" in merged or "mae" in merged or "delay model" in merged:
            return (
                "The model used route and schedule context and was validated with cross-validation discipline, yielding MAE 22.7 minutes with about 81% within 30 minutes. "
                "The critical caution was leakage: time-aware split and feature hygiene mattered more than model complexity."
            )
        if "100--400" in merged or "latency" in merged:
            return (
                "That latency range was for cache-warm read paths, not every edge case. "
                "Time budget was request parsing, cache lookup or indexed DB fallback, response assembly, and network overhead. "
                "Cold starts and cache misses were slower, and I present that honestly."
            )
        return CANON["logiflow_pitch"]

    if "community hero" in merged or "vibe2ship" in merged:
        return (
            "Community Hero was a solo PWA build where I focused on practical reliability over polish. "
            "I used Firebase-backed flows, Cloud Run integration, and Gemini-assisted categorization with guardrails. "
            "The hard part was balancing low-connectivity UX, moderation safety, and response latency within hackathon time."
        )

    if "airhelp" in merged:
        return (
            "AirHelp combined FastAPI, WebSockets, and a retrieval layer using ChromaDB. "
            "I designed for roughly 50 to 100 concurrent sessions with 1 to 3 second end-to-end responsiveness, and route guidance with A* behavior above 95% accuracy on our test setup. "
            "At larger scale I would split stateful connections and retrieval workload across dedicated components."
        )

    if "oa forge" in merged:
        return (
            "OA Forge is a C++-centric judge and question-matching system with around 14K question occurrences and 5.5K test cases. "
            "The core engineering concern is safe execution: strict limits, sandbox controls, and deterministic evaluation contracts. "
            "I frame it as personal learning infrastructure, with clear ethics and compliance boundaries."
        )

    if "career automation" in merged or "internship scout" in merged:
        return (
            "Career Automation focused on scalable discovery and maintenance across 965+ companies, with deduplication, scheduling, and resilient retries as primary design concerns. "
            "I treat this as pipeline engineering: failure visibility, legality boundaries, and maintainability over one-off scraping scripts."
        )

    return (
        "For this project question I would answer in three parts: problem and ownership scope, architecture and trade-offs, then one measurable outcome and one honest limitation."
    )


def _answer_company(question: str, company: str | None) -> str:
    q = _norm(question)
    target = _company_name(company, question)

    if "why" in q and ("stripe" in q or "ge healthcare" in q or "wells fargo" in q or "cisco" in q or "google" in q or "microsoft" in q or "honeywell" in q or "alpha" in q or "amazon" in q or "flipkart" in q or "goldman" in q or "angel one" in q):
        return (
            f"My interest in {target} is role-fit first: strong engineering rigor, reviewed production work, and high learning density. "
            "I can contribute quickly with backend/API ownership, testing discipline, and measurable performance focus from IFFCO and LogiFlow. "
            "I am not applying for logo value; I am applying for environments where intern code quality standards are real."
        )
    if "first 30 days" in q:
        return CANON["first_30_days"]
    if "logiflow in 2 minutes" in q:
        return CANON["logiflow_pitch"]
    if "workday" in q or "b.s." in q:
        return CANON["ge_workday_mapping"]
    if "stipend expectations" in q:
        return (
            "I am flexible and focused on learning scope, mentorship quality, and role impact. "
            "I am comfortable aligning with your internship compensation band."
        )
    if "availability" in q or "relocation" in q or "bengaluru" in q or "hyderabad" in q:
        return CANON["availability"]
    if "other offers" in q:
        return (
            "I have active pipelines, but I keep communication transparent and timeline-respectful. "
            "My decision priority is team quality, project ownership, and growth fit."
        )
    return (
        f"For {target}, I would tie my answer to your role focus and show exactly how my IFFCO production experience plus LogiFlow backend ownership translates to intern impact."
    )


def _answer_trap(question: str) -> str:
    q = _norm(question)
    if "chatgpt code" in q:
        return (
            "I do use AI tools for acceleration, but ownership means I can explain architecture, defend trade-offs, and debug failures live. "
            "At IFFCO and in LogiFlow, the value was not copied code; it was end-to-end decisions, testing, and integration under constraints."
        )
    if "top 106" in q:
        return (
            "That ranking is one credential, not my whole claim. "
            "The stronger evidence is what I personally owned in backend architecture and measured outcomes like latency range, model error, and test discipline."
        )
    if "optimize for internships" in q:
        return (
            "OA Forge began as interview prep tooling, but I deliberately turned it into systems practice: sandbox safety, deterministic judging, and data pipeline quality. "
            "So it improved both interview readiness and engineering maturity."
        )
    if "ai degree but swe" in q:
        return _answer_universal_behavioral("AI degree but SWE role?")
    if "leave for higher cp" in q or "quant" in q:
        return (
            "I am intentional about role commitment. Competitive programming helps my problem-solving speed, but I am looking for sustained team-based software engineering growth, not short-term hopping."
        )
    return (
        "I would acknowledge the concern directly, give factual evidence, and avoid defensive language."
    )


def _answer_questions_to_ask(question: str) -> str:
    return (
        "I would ask this near the end because it helps me align expectations. "
        "For me, the answer should clarify intern ownership boundaries, review cadence, and what success looks like by the end of the internship."
    )


def _answer_coding_problem(question: str) -> str:
    return (
        f"For '{question}', I would first restate constraints and target complexity, then propose a brute-force baseline and optimized approach. "
        "I code while narrating invariants, handle edge cases early, and close with time-space analysis plus two concrete tests. "
        "If asked for follow-up, I discuss trade-offs for readability versus performance."
    )


def _answer_red_team(question: str) -> str:
    q = _norm(question)
    if "stack swap trap" in q:
        return "I would correct once with confidence: IFFCO stack was Node/Express/MySQL in Jun-Jul 2025, then continue with ownership details and outcomes."
    if "ownership shrink" in q:
        return "I would immediately name my owned slices: specific APIs, validation logic, deployment participation, and measurable results."
    if "metric challenge" in q:
        return "I would explain benchmark setup, traffic shape, warm versus cold behavior, and which percentile I am quoting."
    if "ethics ambush" in q:
        return CANON["ethics_oa_forge"]
    if "prestige bait" in q:
        return "I would stay factual: SVNIT gave me a strong base, and I focus on demonstrable engineering outcomes rather than institute comparisons."
    if "negative sell" in q:
        return (
            "A fair reason not to hire me would be if you need someone already experienced in your exact production stack from day zero. "
            "What I bring is fast ramp, disciplined execution, and evidence-backed ownership."
        )
    return "I would treat this as a pressure test: stay calm, answer with facts, and avoid overclaiming."


def _answer_panel_stress(question: str) -> str:
    return (
        "In a panel-stress setup, my strategy is structured composure: answer the active interviewer in 30 to 60 seconds, confirm understanding before switching, "
        "and keep claims auditable with project numbers. If challenged, I separate facts from assumptions and acknowledge unknowns quickly."
    )


def _answer_mock_brutal(question: str) -> str:
    return (
        "I treat this as a deliberate interruption scenario. "
        "My response is short and concrete: ownership slice, one metric, one trade-off, one next step. "
        "If I detect drift, I summarize in 20 seconds and ask whether they want architecture depth or implementation depth next."
    )


def _answer_internet_probe(question: str) -> str:
    if "60-min hackerrank" in _norm(question):
        return (
            "For that Stripe-style format, I would design Part 1 as reusable parser primitives so Part 2 and Part 3 are extensions, not rewrites. "
            "I would prioritize malformed-line handling, deterministic test helpers, and clear complexity notes."
        )
    return (
        "For internet-reported patterns, my preparation approach is to practice realistic constraints: timed implementation, follow-up optimization, and clear explanation quality."
    )


def _fallback_answer(question: str, company: str | None = None) -> str:
    if _rapid_or_short(question):
        return (
            "I would answer this in one crisp definition, then attach one concrete example from IFFCO or LogiFlow."
        )
    target = _company_name(company, question)
    return (
        f"My short answer is that I map this to real examples from IFFCO and LogiFlow: clear ownership, measured outcomes, and honest trade-offs. "
        f"If relevant to {target}, I also align my response to your intern success criteria and first-month execution expectations."
    )


RuleMatcher = Callable[[str, str | None, bool, str | None], bool]
RuleAnswer = Callable[[str, str | None, bool, str | None], str]


RULES: list[tuple[RuleMatcher, RuleAnswer]] = [
    (
        lambda q, c, f, p: q in RAPID_FIRE_ANSWERS,
        lambda q, c, f, p: RAPID_FIRE_ANSWERS[q],
    ),
    (
        lambda q, c, f, p: q in QUESTIONS_TO_ASK,
        lambda q, c, f, p: _answer_questions_to_ask(q),
    ),
    (
        lambda q, c, f, p: any(q == item[0] for item in TRAP_QUESTIONS),
        lambda q, c, f, p: _answer_trap(q),
    ),
    (
        lambda q, c, f, p: q in PANEL_STRESS,
        lambda q, c, f, p: _answer_panel_stress(q),
    ),
    (
        lambda q, c, f, p: any(q == title or q == desc for title, desc in RED_TEAM),
        lambda q, c, f, p: _answer_red_team(q),
    ),
    (
        lambda q, c, f, p: any(q in script.get("brutal_moments", []) for script in MOCK_SCRIPTS),
        lambda q, c, f, p: _answer_mock_brutal(q),
    ),
    (
        lambda q, c, f, p: _has_any(q, ["go deeper", "give a number", "what breaks at scale"]),
        lambda q, c, f, p: _answer_cs(q),
    ),
    (
        lambda q, c, f, p: any(q in probs for _, probs in CODING_PROBLEMS),
        lambda q, c, f, p: _answer_coding_problem(q),
    ),
    (
        lambda q, c, f, p: (
            _has_any(q, ["iffco", "logiflow", "community hero", "airhelp", "oa forge", "career automation"])
            and not _has_any(q, ["you listed", "which one would you put", "why does a knight", "many hackathon"])
        ),
        lambda q, c, f, p: _answer_project(q, p),
    ),
    (
        lambda q, c, f, p: any(name.lower() in q.lower() for name in COMPANY_EXTRA) or _has_any(q, ["why ", "first 30 days", "workday", "relocation", "stipend"]),
        lambda q, c, f, p: _answer_company(q, c),
    ),
    (
        lambda q, c, f, p: _has_any(q, ["walk me through your resume", "tell me about yourself", "weakness", "critical feedback", "production bug"]),
        lambda q, c, f, p: _answer_universal_behavioral(q, c),
    ),
    (
        lambda q, c, f, p: _has_any(q, ["oa", "hackerrank", "integration round", "public reports"]),
        lambda q, c, f, p: _answer_internet_probe(q),
    ),
]


def _iter_question_pairs(bank: Iterable[tuple[str, list[str]]]) -> Iterable[str]:
    for question, followups in bank:
        yield question
        for fu in followups:
            yield fu


def _iter_all_questions() -> list[str]:
    questions: list[str] = []
    seen: set[str] = set()

    def add(text: str) -> None:
        stripped = text.strip()
        if stripped and stripped not in seen:
            seen.add(stripped)
            questions.append(stripped)

    for q in _iter_question_pairs(UNIVERSAL_BEHAVIORAL):
        add(q)
    for q in _iter_question_pairs(GEN_UNIVERSAL_BEHAVIORAL):
        add(q)

    for _, qs in CS_FUNDAMENTALS:
        for q in qs:
            add(q)
            add("Go deeper.")
            add("Give a number from your project.")
            add("What breaks at scale?")
    for _, qs in GEN_CS_FUNDAMENTALS:
        for q in qs:
            add(q)

    for proj_banks in (PROJECT_QUESTIONS, GEN_PROJECT_QUESTIONS):
        for entries in proj_banks.values():
            for q, fus in entries:
                add(q)
                for fu in fus:
                    add(fu)

    for entries in COMPANY_EXTRA.values():
        for q, fus in entries:
            add(q)
            for fu in fus:
                add(fu)

    for bank in (HR_SCREEN, EXTRA_BEHAVIORAL, HR_LOGISTICS, RESUME_LINES, LEADERSHIP):
        for q in _iter_question_pairs(bank):
            add(q)

    for q in RAPID_FIRE:
        add(q)
    for q, _ in TRAP_QUESTIONS:
        add(q)
    for q in QUESTIONS_TO_ASK:
        add(q)
    for _, probs in CODING_PROBLEMS:
        for p in probs:
            add(p)

    for title, desc in RED_TEAM:
        add(title)
        add(desc)
    for q in PANEL_STRESS:
        add(q)

    for script in MOCK_SCRIPTS:
        add(script.get("title", ""))
        add(script.get("interviewer", ""))
        for slot, action in script.get("flow", []):
            add(slot)
            add(action)
        for moment in script.get("brutal_moments", []):
            add(moment)
    for script in GEN_MOCK_SCRIPTS:
        add(script.get("title", ""))
        add(script.get("interviewer", ""))
        for slot, action in script.get("flow", []):
            add(slot)
            add(action)
        for moment in script.get("brutal_moments", []):
            add(moment)

    for entries in INTERNET_BY_COMPANY.values():
        for q, fus in entries:
            add(q)
            for fu in fus:
                add(fu)

    for c in COMPANY_EXTRA:
        add(f"Why {c}?")
        add(f"What would you build in your first 30 days at {c}?")
        add("Tell me about LogiFlow in 2 minutes.")
    for c in GEN_COMPANIES:
        name = c.get("name")
        if name:
            add(f"Why {name}?")
            add(f"What would you build in your first 30 days at {name}?")

    return questions


def _default_exact_answer(question: str) -> str:
    for matcher, answer in RULES:
        if matcher(question, None, False, None):
            return answer(question, None, False, None)
    return _fallback_answer(question, None)


def resolve_answer(
    question: str,
    *,
    company: str | None = None,
    is_followup: bool = False,
    parent: str | None = None,
) -> str:
    q = question.strip()
    if not q:
        return "Please ask a concrete interview question and I will answer it in spoken format."

    if q in EXACT_ANSWERS:
        base = EXACT_ANSWERS[q]
        if company and "this company" in base:
            return base.replace("this company", company)
        return base

    for matcher, answer in RULES:
        if matcher(q, company, is_followup, parent):
            return answer(q, company, is_followup, parent)

    if is_followup and parent:
        parent_answer = EXACT_ANSWERS.get(parent, _default_exact_answer(parent))
        follow = _default_exact_answer(q)
        if _rapid_or_short(q):
            return follow
        return (
            f"Building on my previous answer: {parent_answer} "
            f"For your follow-up specifically: {follow}"
        )

    return _fallback_answer(q, company)


def build_exact_index() -> dict[str, str]:
    """Programmatically register answers for every imported question string."""
    index: dict[str, str] = {}
    for q in _iter_all_questions():
        index[q] = _default_exact_answer(q)
    index.update(EXACT_OVERRIDES)
    return index


EXACT_OVERRIDES: dict[str, str] = {
    # Universal behavioral follow-ups
    "You listed 50+ workflows at IFFCO---name three specifically. Who used them?": (
        "Three examples: daily farmer registration sync, inventory reconciliation for dispatch planning, and internal reporting exports for operations supervisors. "
        "Primary users were IFFCO operations staff at Phulpur who previously ran these manually in spreadsheets. "
        "My automation reduced repetitive entry and validation errors in those daily paths."
    ),
    "Why does a Knight on LeetCode matter for this job?": (
        "Knight rating reflects sustained problem-solving practice---711+ problems and 32 contests---which helps me debug faster, reason about edge cases in code review, and estimate complexity under time pressure. "
        "It is not a substitute for shipping: my IFFCO and LogiFlow work matter more. CP is a tool for engineering speed, not the job itself."
    ),
    "You have many hackathon projects. Which one would you put in production at our company tomorrow, and which would you delete?": (
        "Ship tomorrow: LogiFlow backend patterns---caching, API contracts, pytest discipline---because they are production-shaped. "
        "I would not delete Community Hero; I would harden it first---auth rules, rate limits, and test coverage need more enterprise polish before I'd call it production-ready at your scale."
    ),
    "What did you disagree with in that feedback?": (
        "Initially I felt the validation critique was too strict for a one-month intern scope. "
        "After reproducing bad payloads, I agreed the mentor was right: client-side checks are not enough. "
        "I now default to server-side validation on every endpoint."
    ),
    "If you had to redo the project, what would you cut to ship two weeks earlier?": (
        "I would cut nice-to-have UI polish and defer one non-critical analytics endpoint. "
        "I would not cut validation, tests, or API documentation---those prevented rework."
    ),
    "How did you know it was your change?": (
        "Git blame on the merged PR, timestamp alignment with the regression window, and reproducing the bug on my branch but not on the prior commit."
    ),
    "What monitoring would have caught it faster?": (
        "Structured 4xx/5xx rate alerts per endpoint plus input-schema violation counters would have flagged the validation gap within hours instead of after user reports."
    ),
    "Write the postmortem title in one sentence.": (
        "Missing server-side validation on farmer ID field caused inconsistent records until middleware and tests were added."
    ),
    "What do CSE students know that you don't?": (
        "Some peers have deeper traditional OS or compiler exposure from electives I have not taken yet. "
        "I close that gap by reading docs, building projects, and asking targeted questions in review---my applied backend work compensates where theory gaps remain."
    ),
    "Convince me AI isn't just a buzzword on your degree.": (
        "My degree title says AI, but my proof is systems work: XGBoost delay model with MAE 22.7 on 15,650 train-days, RAG in AirHelp, and feature-pipeline discipline---not buzzwords. "
        "I can explain train/test leakage risks and when not to deploy a model."
    ),
    "Give an example from the last 30 days.": (
        "In a recent mock interview I talked three minutes before stating my ownership slice. "
        "I now use a timer and STAR structure---that is the behavior I am actively fixing."
    ),
    "How would that weakness hurt our team in week one?": (
        "I might over-explain in standups and burn meeting time. "
        "My mitigation is a 60-second cap, then 'happy to go deeper on architecture or implementation' and let the interviewer choose."
    ),
    "What did you own end-to-end vs. what did your mentor do?": (
        "I owned: requirements for two workflows, three REST endpoints, validation middleware, tests, and Docker deploy steps for my slices. "
        "Mentor owned: architecture sign-off, production access policies, and final merge approval on sensitive tables."
    ),
    "Why not return for a longer stint?": (
        "The program was structured as a one-month summer slot after my first year. "
        "I maximized ownership in that window; a longer return was not offered, but I left documentation so the next intern could extend the APIs."
    ),
    "What did you disagree with technically?": (
        "On LogiFlow, a teammate wanted in-process caching only; I advocated Redis for stable p99 under load. "
        "We resolved it with a timed benchmark spike, not opinion."
    ),
    "How did you escalate without being toxic?": (
        "I wrote a one-page comparison with metrics, shared it async, proposed a 2-hour spike, and agreed upfront to accept data-driven outcome regardless of who was right."
    ),
    # Questions to ask (speak these aloud)
    "What does a successful intern project look like at handoff?": (
        "What does a successful intern project look like at handoff, and how do you measure whether it was a win for the team?"
    ),
    "How are interns paired with mentors weekly?": (
        "How are interns paired with mentors week to week, and what does a good mentor relationship look like in your team?"
    ),
    "What is the code review culture for intern PRs?": (
        "What is the code review culture for intern PRs---how much coaching versus autonomy do you expect in the first month?"
    ),
    "Biggest technical debt the team wants help with this summer?": (
        "What is the biggest technical debt or reliability pain point where an intern could make a real dent this summer?"
    ),
    "How is on-call / production responsibility handled for interns (usually: none---verify)?": (
        "How is on-call or production responsibility handled for interns---typically I assume none, but I want to understand escalation paths if something I ship breaks."
    ),
    # Trap questions (exact titles from simulation)
    "Isn't this just ChatGPT code?": (
        "I use AI tools for drafting speed, but I own architecture, tests, and debugging. "
        "At IFFCO I can walk through JWT flow, validation middleware, and the exact PR that fixed farmer-record inconsistencies. "
        "In LogiFlow I can explain Redis key design and why our MAE is 22.7 minutes. Copied code cannot survive that depth of questioning."
    ),
    "Global Top 106 sounds like marketing.": (
        "Fair pushback. The ranking reflects Google Solution Challenge judging among global teams; my stronger claim is personal: I co-led backend, owned the railway pipeline and cache contract, and we measured 100--400 ms reads with 100/100 pytest business rules."
    ),
    "You optimize for internships (OA Forge) more than engineering.": (
        "OA Forge started for interview prep, but building it taught real engineering: C++ sandbox limits, deterministic judging, 14K+ question normalization, and CI for test harnesses. "
        "That is the same discipline I want in a production team."
    ),
    "AI degree but SWE role?": (
        "My coursework includes DSA, OS, DBMS, and networks; my projects are backend-heavy---Node/Express/MySQL at IFFCO, Cloud Run and Redis at LogiFlow. "
        "The degree title says AI; the work profile is software engineering with ML where it adds measurable value."
    ),
    "Will you leave for higher CP / quant?": (
        "Competitive programming is practice for problem-solving speed; my goal this summer is team-based production engineering. "
        "I am applying for SWE intern roles with intent to learn release discipline and code review culture, not to treat the internship as a short stop toward something else."
    ),
}

EXACT_ANSWERS: dict[str, str] = build_exact_index()

