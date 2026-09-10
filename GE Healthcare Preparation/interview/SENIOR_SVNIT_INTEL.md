# Senior SVNIT intel — GE HealthCare (WhatsApp, Aug 2026)

**Source:** Senior who went through GE HealthCare campus process last year.  
**Audience:** Vansh / SVNIT AI batch · EID Software track.

---

## Process overview — 5 rounds

```
OA → HireVue → Technical → HR → Personality assessment
```

---

## Round 1 — Online Assessment

- **2 DSA questions**
- **20 MCQs** on CS fundamentals (OS, DBMS, CN, OOP-style core CS)

**Prep:**
- Striver sheet for DSA (Easy + Medium)
- GFG for OS / DBMS / CN MCQs

---

## Round 2 — HireVue (recorded video)

- **~5 questions**
- **30–60 seconds** to think before each answer
- **3 attempts** to record each answer
- Questions like: **introduction**, **why you want to join**, etc.

**Prep:**
- Search “HireVue questions” and prepare bullet points
- Record yourself on phone — check lighting, audio, eye contact
- Keep answers **structured** (Situation → Action → Result for behavioral)

---

## Round 3 — Technical interview

- **Panel-dependent** — different interviewers ask completely different things
- Duration: **~75 minutes** (senior’s experience; others report 30–40 min)

**Prepare all of:**
- DSA (approach + logic)
- CS fundamentals (OS, DBMS, CN, SQL)
- **Every project on resume** — deeply

**What senior was asked (AI-heavy project):**
- How accuracy was achieved
- Architecture used
- How results could be improved

**Also reported:** asked to **design a testing software** — senior said they weren’t fully aware of architecture; **interviewer gave hints**. OK to think aloud and collaborate.

**Hardcoding vs logic:**
> “They'll mostly just ask logic” — **not always live coding in IDE**, but **depends on interviewer**. Some panels may ask implement runtime polymorphism in online compiler (EEDP FTE report).

**Live demo / open project?**
> Not guaranteed. Prepare workflow anyway; don’t assume they’ll ask to screen-share.

**Drive the interview:**
> Mention strengths (auth, Django, team lead) so conversation goes where you’re strong.

---

## Round 4 — HR (~15 min)

- Hobbies
- Clubs / extracurriculars
- How you work in a team

Also seen in other reports: why GE, competitors, relocation, GE products knowledge.

---

## Round 5 — Personality assessment

- **100 situational questions** — **untimed**
- **3 games** — **timed**, score as high as possible
- Games = **simple puzzles**

**Strategy:**
- Situational: pick answers that are **consistent** (don’t flip personality mid-test)
- Games: stay calm, read instructions once, speed matters

---

## Senior’s prep stack

| Area | Resource |
|------|----------|
| CS fundamentals | **GeeksforGeeks** |
| DSA | **Striver’s sheet** |
| Projects | Self-prep — workflow, backend, auth, architecture |

---

## Project depth — what to prepare

If they ask about a project, be ready for **any** of:

| Topic | Prepare |
|-------|---------|
| **Workflow** | User journey step-by-step |
| **Backend logic** | Request → validation → DB → response |
| **Auth** | Login, session/token, protected routes |
| **Authorization** | Who can access what (admin vs user) |
| **Architecture** | Client → server → database; 3-tier mental model |
| **AI projects** | How accuracy/metrics; how to improve; fallback if model fails |
| **Trade-offs** | Why Django/Firestore/SQL; what you’d change at scale |

**For Vansh specifically (EduAce + Beneath The Blue):**
- Django auth + session flow
- Quiz generation + score tracking logic
- Team lead decisions on Web Wonder
- What you’d add for **testing** (unit tests, edge cases) — ties to senior’s design question

---

## Questions senior couldn’t fully answer (learn from this)

- Full **testing software architecture** — prep a simple answer:
  - Test pyramid: unit → integration → E2E
  - For Django: pytest, test client, mock DB
  - For healthcare mindset: regression tests before release, traceability

---

## Raw WhatsApp excerpts (verbatim themes)

> “Last year they had 5 rounds”

> “First one is OA which had 2 dsa questions and 20 mcqs on cs fundamentals”

> “Then there was a hireview round… 5 questions… 30-60 sec to think… 3 attempts”

> “Then there was technical interview… different panels asked different types of questions”

> “Prepare dsa, cs fundamentals and all projects mentioned in your resume thoroughly”

> “They'll mostly just ask logic… again it completely depends on the interviewer”

> “Cs fundamentals ke liye i used gfg… Dsa ke liye striver's sheet”

> “It's better you prepare all this… you can drive the interview in the direction of your strength”
