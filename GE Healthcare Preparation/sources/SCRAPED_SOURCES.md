# GE HealthCare — Scraped sources & extracted patterns

**Last updated:** Sep 2026  
**Method:** GFG interview experiences, PCON EID write-up, InterviewSense (US + MRI), repo brutal-sim intel, senior SVNIT WhatsApp, job postings.  
**Labels:** **Confirmed** = multiple independent reports · **Repeated** = 2+ reports · **One-off** = single post (useful, not guaranteed)

---

## Primary sources (read these)

| Source | URL | What it adds |
|--------|-----|--------------|
| **PCON — EID Intern 2024** | https://pcon-app.vercel.app/blogs/cltfdffwe0003k1a1zpsw2i5g | **Highest EID-named signal:** 90 min OA (reasoning + CS MCQ + 2 Med–Hard trees/graphs/DP); tech: **Two Sum + Sum of Leaf Nodes via OOP classes**; HR strengths/weaknesses |
| GFG — SDE Intern SVNIT Aug 2024 | https://www.geeksforgeeks.org/interview-experiences/ge-healthcare-interview-experience-sde-internship-on-campus/ | **Confirmed** SVNIT OA: 2hr test; unique coding per student; OOP grill; HR on competitors/products |
| GFG — On-Campus (SVNIT) | https://www.geeksforgeeks.org/interview-experiences/ge-healthcare-interview-experience-on-campus-3/ | Math + DSA MCQ + English + 2 coding (1 easy, 1 DP); matrix diagonals; LL insert/delete; ACID/OOP |
| GFG — EEDP FTE On-Campus | https://www.geeksforgeeks.org/interview-experiences/ge-healthcare-interview-experience-for-fte-eedp-on-campus/ | **Confirmed** 5 rounds incl. pymetrics; 50 MCQ + 2 code; runtime polymorphism live; OSI in-depth |
| GFG — Intern On-Campus 2024 | https://www.geeksforgeeks.org/interview-experiences/ge-healthcare-interview-experience-for-internship-on-campus-2024/ | 50 Q aptitude/reasoning/English; PI 40–45 min; OOP + 2 coding Qs; 11/30 selected |
| GFG — Internship (older campus) | https://www.geeksforgeeks.org/interview-experiences/ge-healthcare-interview-experience-internship/ | 2 code / 45m + 30 tech MCQ / 30m + 50 aptitude / 50m; Tower of Hanoi, BST insert/delete, OOP grill |
| GFG — Intern 2021 | https://www.geeksforgeeks.org/interview-experiences/ge-healthcare-internship-interview-experience-2021/ | Coin change greedy + subtree-sum tree; CS MCQ DSA/DBMS/OS/CN |
| GFG — Off-Campus 2021 | https://www.geeksforgeeks.org/interview-experiences/ge-healthcare-interview-experience-off-campus-2021/ | Cocubes 3 sections; array reverse; prefix/postfix; 3-tier arch; SQL third-highest; DevOps scenario |
| GFG — On-Campus (general) | https://www.geeksforgeeks.org/interview-experiences/ge-healthcare-interview-experience-on-campus/ | Sieve primes <100; OOP live coding; HR medical-device interest |
| GFG — SW Engineer (FTE-ish) | https://www.geeksforgeeks.org/interview-experiences/ge-healthcare-interview-experience-for-software-engineer/ | Climbing stairs OA; sort LL + factorial; e-commerce design; puzzles |
| InterviewSense — SE Intern Summer 2026 | https://www.interviewsense.org/opportunities/ge-healthcare-software-engineering-intern-summer-2026-salt-lake-city-ut/ | US loop: 2 LC-medium / 70m; longest substring; group anagrams; merge intervals; light SD (rate limiter / notifications) |
| InterviewSense — MRI intern | https://www.interviewsense.org/opportunities/ge-healthcare-mri-systems-engineering-intern-waukesha/ | 2 LC-medium OA 70 min; sliding window; system design light |
| InterviewSense — EEDP | https://www.interviewsense.org/opportunities/ge-healthcare-engineering-development-program-full-time-aurora-t9yr9/ | Verbal tradeoffs; ramp on codebase; behavioral depth |
| Freshers Dunia — SW Intern 2026 | https://freshersdunia.in/ge-healthcare-internship-2026-hiring/ | Resume → OA → Tech → Manager → HR |
| Jobdexo — Intern 2026 | https://jobdexo.com/job/C165-J074/intern-ge-healthcare-2026 | C++/Python/Java; testing; CI/CD; healthcare platform |
| Extern — GE internship guide 2027–28 | https://www.extern.com/post/ge-healthcare-internship-guide | EEDP Software req language: Java/C++/Python, OOP, algorithms, ML preferred; regulated-device vocabulary tip |
| SVNIT CDC LinkedIn (2024 selections) | https://www.linkedin.com/posts/career-development-cell-tnp-section-svnit-surat-8711b087_svnit-cdc-ppo-activity-7244939422301904898-JJm8 | Confirms GE HealthCare 2-month summer interns from SVNIT |
| **Senior SVNIT intel (2025)** | `interview/SENIOR_SVNIT_INTEL.md` | **Highest signal for your batch:** 5 rounds, HireVue, personality games |

---

## Consolidated round map

### Round 1 — Online Assessment

| Report | Format |
|--------|--------|
| **Senior 2025** | 2 DSA + 20 CS fundamentals MCQs |
| **PCON EID Intern 2024** | **90 min**, 3 sections: reasoning + CS MCQ (OOP/CN/OS) + **2 Med–Hard** (trees / graphs / DP) |
| EEDP FTE GFG | 50 MCQs (OOP, DBMS, OS, CN, aptitude) in 50 min + 2 coding in 45 min |
| SVNIT SDE 2024 | 2 hr: coding + English + logical + aptitude |
| SVNIT on-campus-3 | Math + DSA MCQ + English + 2 coding (easy + DP) |
| Older campus internship GFG | 2 coding / 45m + 30 tech MCQ / 30m + 50 aptitude / 50m |
| Off-campus 2021 | Cocubes: aptitude → technical MCQ → 2 coding (sequential sections) |
| Intern 2024 GFG | 50 Q: quant + analytical reasoning + English |
| InterviewSense SE Intern 2026 (US) | 2 LC-medium in ~70 min (sliding window / strings / hashing) |
| Repo brutal-sim | Cocubes-style: OS/DBMS/DSA MCQ + 1–2 coding |

**Confirmed OA topics:**
- **Coding:** Easy–Medium DSA — arrays, strings, hashing, trees, graphs, DP (**Repeated**)
- **MCQ:** OOP, OS, DBMS, CN, DSA theory (**Confirmed**)
- **Also possible:** Aptitude, English, logical reasoning (**Repeated**)
- **Platform:** Cocubes / HirePro / custom — varies by year (**One-off**)

**Reported coding problems (one-off — do NOT memorize as “the” question):**

| Problem | Source | Pattern |
|---------|--------|---------|
| Count numbers with equal nonzero freq of digits 2,4,8 in [1,n] | SVNIT SDE 2024 | Digit DP / counting |
| Min pencil height after cut operations | SVNIT SDE 2024 | Greedy / simulation |
| Zig-zag level traversal | SVNIT SDE 2024 peers | Tree BFS |
| Euler cycle in graph | SVNIT SDE 2024 peers | Graph |
| Matrix diagonals N×N | SVNIT on-campus-3 | Matrix traversal |
| LL insert + delete | SVNIT on-campus-3 | Linked list |
| **Two Sum — implement with OOP classes** | **PCON EID 2024** | Hashing + class design |
| **Sum of leaf nodes — implement with OOP** | **PCON EID 2024** | Tree recursion + OOP |
| Trees / Graphs / DP (OA Med–Hard pair) | PCON EID 2024 | Medium–Hard |
| Tower of Hanoi (code + explain) | GFG internship | Recursion |
| BST insert + delete | GFG internship | Trees |
| Coin change (denominations ≤ 100) | Intern 2021 | Greedy |
| Check subtree; if yes return subtree node sum else −1 | Intern 2021 | Trees |
| Climbing stairs (count ways) | GFG SW Engineer | Easy DP |
| Sort linked list; factorial | GFG SW Engineer | LL / math |
| Longest substring without repeating chars (+ streaming follow-up) | InterviewSense SE 2026 | Sliding window |
| Group anagrams (+ complexity tradeoffs) | InterviewSense SE 2026 | Hashing |
| Merge overlapping intervals (+ streaming OOO) | InterviewSense SE 2026 | Intervals / sorting |
| Sum of 2nd/4th/6th array elements | Repo intel | Array indexing |
| Two Sum (hash map) | Repo intel | Hashing |
| Level-order tree / print level-wise | Repo intel | BFS |
| Array reverse | Off-campus 2021 | Two pointers / in-place |
| Sieve — primes < 100 | GFG on-campus | Sieve of Eratosthenes |

### EID-specific tip (PCON 2024 — **Confirmed useful**)
> For coding in the **technical interview**, practice implementing Easy DSA **inside OOP wrappers** (classes/methods), not just bare functions. Interviewer explicitly required Two Sum + Sum of Leaf Nodes **using OOPs concepts**.

---

### Round 2 — HireVue (video)

**Source:** Senior 2025 only — treat as **Repeated** for SVNIT EID/EEDP pipeline.

- ~5 questions, 30–60 sec to think, **3 recording attempts** each
- Typical: intro, why GE, why healthcare, strengths, motivation
- Prep: bullet scripts, speak to camera, calm pace

---

### Round 3 — Technical interview

**Duration:** 30 min typical; senior reported **75 min** (**One-off** but prepare for long)

| Theme | Frequency | Examples |
|-------|-----------|----------|
| **Resume / projects** | **Confirmed** | Workflow, auth, architecture, accuracy (AI projects), improvements |
| **OOP** | **Confirmed** | Encapsulation, inheritance, polymorphism; copy ctor; virtual functions; **live implement polymorphism** |
| **DSA** | **Confirmed** | Logic on whiteboard/notepad — **mostly not full IDE** (senior); **EID 2024:** Two Sum + Sum of Leaf Nodes **via OOP classes** |
| **OS** | **Repeated** | Process vs thread, deadlock, OSI layers, race conditions, locks |
| **DBMS** | **Repeated** | ACID, normalization, SQL queries (3rd highest salary) |
| **CN** | **Repeated** | TCP/IP, DHCP, OSI |
| **System design light** | **One-off** | Testing software design (senior); 3-tier architecture; token system |
| **ML basics** | **One-off** | “ChatGPT uses which type of ML?” (supervised/generative) |

**Senior tips:**
- Panel **completely depends on interviewer**
- They may **not** ask you to open live project — but know demo flow anyway
- **Drive interview** toward your strengths (mention auth, Django, team lead)
- If stuck on design, **ask for hints** — senior’s interviewer helped

---

### Round 4 — HR (~15 min)

**Confirmed topics:** hobbies, clubs, teamwork, why GE, relocation, competitors, GE products, strengths/weaknesses, challenge STAR story.

**SVNIT 2024 note:** Candidate cleared tech but **rejected at HR** — take HR seriously, not a formality.

---

### Round 5 — Personality assessment

**Source:** Senior 2025 + EEDP FTE pymetrics

- **100 situational questions** (untimed) — be consistent, don’t overthink
- **3 timed puzzle games** — score as high as possible; described as simple
- EEDP FTE also mentions **pymetrics** personality games — similar intent

---

## CS fundamentals checklist (OA + interview)

### OOP (must know + code)
- 4 pillars with **your project example**
- Compile-time vs runtime polymorphism
- Copy constructor, virtual functions, overriding vs overloading
- Access specifiers; encapsulation vs data hiding

### OS
- Process vs thread; context switch
- Deadlock (4 conditions), mutex vs semaphore
- Paging; scheduling basics
- Race condition + locks (EEDP FTE report)

### DBMS
- ACID; 1NF–3NF; PK/FK
- INNER vs LEFT JOIN; GROUP BY / HAVING
- Index trade-offs
- Normalization (when / why)

### CN
- OSI 7 layers (EEDP FTE went **in-depth**)
- TCP vs UDP; TCP handshake (3-way)
- DHCP, DNS basics

### DSA (Striver sheet alignment — senior recommendation)
- Arrays: Kadane, Two Sum, prefix sum, sliding window, merge intervals
- Strings: first unique char, anagram, valid parens, longest substring no repeat, group anagrams
- Linked list: reverse, insert/delete, cycle detection, sort LL (one-off)
- Trees: BFS level-order, zig-zag, BST insert/delete, **sum of leaf nodes**, subtree check
- Graphs: BFS/DFS, islands
- DP: climbing stairs, coin change (easy variants)
- Recursion: Tower of Hanoi (explain + code)
- Math: sieve, Fibonacci in range
- **OOP + DSA:** wrap Two Sum / tree problems in classes (EID 2024)

---

## HireVue / behavioral bank

1. Tell me about yourself (60–90 sec)
2. Why GE HealthCare?
3. Why healthcare / medical technology?
4. Why software engineering at GE vs pure IT services?
5. Strength + example (teamwork from Web Wonder / Nexus)
6. Weakness + how you improve
7. Tell me about a challenge you overcame (STAR)
8. Where do you see yourself in 5 years? (EEDP pathway)

---

## Why GE HealthCare (30 sec template)

> “GE HealthCare builds software and devices that touch real clinical workflows — not just consumer apps. I want an internship where code quality, testing, and reliability matter because outcomes affect patients. EID is attractive because it’s a live engineering project with a pathway to EEDP, and I can grow on C++/Python-style product teams while contributing from day one on something I’ve built end-to-end in my own projects.”

---

## Prep resources (senior + standard)

| Area | Resource |
|------|----------|
| CS fundamentals MCQ | GeeksforGeeks OS, DBMS, CN, OOP articles |
| DSA | Striver A2Z / SDE sheet (Easy + selected Medium) |
| OA practice | OA Forge → **GEP Worldwide** bank (similar Easy string/hash patterns) |
| HireVue | Search “HireVue GE Healthcare” + rehearse out loud |
| Projects | `interview/GE_Project_Drill.pdf` in this folder |
| Company research | gehealthcare.com — products (MRI, ultrasound, monitoring), mission |

---

## LeetCode Discuss

No dedicated high-traffic **“GE Healthcare OA 2026”** LeetCode Discuss thread was found in search (Sep 2026 refresh). Closest public signals:
- **India campus / EID:** GFG SVNIT + [PCON EID Intern 2024](https://pcon-app.vercel.app/blogs/cltfdffwe0003k1a1zpsw2i5g)
- **US SE Intern 2026:** InterviewSense Salt Lake City write-ups (sliding window / hashing / light SD)

Patterns still match: **2 coding + CS MCQ** (India) or **2 LC-medium** (US). Prefer India campus sources for SVNIT EID.

---

## What changed in Sep 2026 refresh

1. Added **EID Intern 2024 (PCON)** — named EID role; OOP-wrapped DSA in tech round  
2. Added InterviewSense **SE Intern Summer 2026** problem names  
3. Added older GFG internship OA structure (2+30+50 timing) and Tower of Hanoi / BST  
4. Cross-linked Extern EEDP Software req vocabulary for resume/HireVue language  

---

## Internal repo cross-refs

- `Reference Collection/Planning/ojas_brutal_interview_simulation.tex` — GE HealthCare section (OA Cocubes, OOP grill, SDLC)
- `Peers Resume Collection/vansh_rawat_ge_healthcare_eid_software.pdf` / `vansh_rawat_final.pdf` — Vansh EID resume
- `Peers Resume Collection/karan_bheda_ge_healthcare_eid_software.pdf` — Karan EID resume
- `Latex Collection/ojas_srivastava_ge_healthcare_*.tex` — Ojas GE prep (Bengaluru SW intern — different req ID but similar CS bar)
