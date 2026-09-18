#!/usr/bin/env python3
"""
Build Kavya PM-round pack from public scrape:
- Surekha Sailesh findings (Edison Program Manager — confirmed)
- GEHC Bengaluru Program Manager roster
- Full GFG managerial Q bank
- Mock 1 (Surekha / Edison PM personality check)
- Mock 2 (Campus Sr Manager filter + off-campus Sr Manager depth)
"""

from __future__ import annotations

from pathlib import Path

from playwright.sync_api import sync_playwright

DIR = Path(__file__).resolve().parent

CSS = """
@page { size: A4; margin: 10mm 11mm 12mm; }
* { box-sizing: border-box; }
html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body {
  font-family: "Segoe UI", "Helvetica Neue", Helvetica, Arial, sans-serif;
  font-size: 9.6pt; line-height: 1.38; color: #1f2937; margin: 0;
}
h1 { font-size: 16pt; color: #0b4f6c; margin: 0 0 2px; }
h2 {
  font-size: 10.5pt; margin: 10px 0 5px; padding: 4px 8px;
  background: #0b4f6c; color: #fff; border-radius: 5px; page-break-after: avoid;
}
h3 { font-size: 10pt; color: #0b4f6c; margin: 8px 0 3px; page-break-after: avoid; }
p, li { margin: 0 0 3px; }
ul, ol { padding-left: 1.1em; margin: 3px 0 7px; }
.hero {
  background: linear-gradient(135deg, #0b4f6c, #147a9b);
  color: #fff; padding: 14px 16px; border-radius: 10px; margin-bottom: 10px;
}
.hero h1 { color: #fff; margin: 0 0 3px; font-size: 17pt; }
.meta { opacity: 0.92; font-size: 9pt; margin: 0 0 7px; }
.badges { display: flex; flex-wrap: wrap; gap: 5px; }
.badge {
  display: inline-block; background: rgba(255,255,255,0.18);
  padding: 2px 9px; border-radius: 999px; font-size: 8.2pt; font-weight: 700;
}
.note {
  background: #f0f9ff; border-left: 4px solid #0b4f6c;
  padding: 7px 9px; border-radius: 0 6px 6px 0; margin: 6px 0 8px; font-size: 9pt;
}
.warn {
  background: #fff7ed; border-left: 4px solid #ea580c;
  padding: 7px 9px; border-radius: 0 6px 6px 0; margin: 6px 0 8px; font-size: 9pt;
}
.ok {
  background: #ecfdf5; border-left: 4px solid #059669;
  padding: 7px 9px; border-radius: 0 6px 6px 0; margin: 6px 0 8px; font-size: 9pt;
}
table {
  width: 100%; border-collapse: collapse; margin: 5px 0 10px; font-size: 8.8pt;
}
th, td {
  border: 1px solid #d1d5db; padding: 4px 6px; text-align: left; vertical-align: top;
}
th { background: #0b4f6c; color: #fff; font-weight: 700; }
tr:nth-child(even) td { background: #f8fafc; }
.iv {
  background: #fce7f3; border-left: 4px solid #be185d;
  padding: 6px 9px; border-radius: 0 6px 6px 0; margin: 7px 0 3px;
  font-size: 9.2pt; page-break-inside: avoid;
}
.iv strong { color: #9d174d; }
.you {
  background: #ecfdf5; border-left: 4px solid #059669;
  padding: 7px 9px; border-radius: 0 6px 6px 0; margin: 3px 0 7px;
  font-size: 9.2pt; page-break-inside: avoid;
}
.you strong { color: #047857; }
.src {
  background: #fef3c7; border-left: 4px solid #d97706;
  padding: 4px 8px; border-radius: 0 6px 6px 0; margin: 2px 0 5px;
  font-size: 8.4pt; color: #92400e;
}
.probe {
  background: #eff6ff; border: 1px solid #bfdbfe;
  padding: 5px 8px; border-radius: 6px; margin: 3px 0 7px; font-size: 8.8pt;
}
.score {
  background: #fafafa; border: 1px solid #e5e7eb;
  padding: 7px 9px; border-radius: 6px; margin: 6px 0 8px; font-size: 8.9pt;
}
.kpi {
  display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 7px; margin: 6px 0 10px;
}
.kpi div {
  background: #f0f9ff; border: 1px solid #bae6fd; border-radius: 7px;
  padding: 7px 8px; font-size: 8.7pt;
}
.kpi b { display: block; color: #0b4f6c; font-size: 11pt; margin-bottom: 1px; }
.tag {
  display: inline-block; font-size: 7.8pt; font-weight: 700; padding: 1px 6px;
  border-radius: 999px; margin-right: 4px;
}
.tag-hot { background: #fee2e2; color: #991b1b; }
.tag-ed { background: #dbeafe; color: #1e40af; }
.tag-ai { background: #ede9fe; color: #5b21b6; }
.tag-ops { background: #d1fae5; color: #065f46; }
.footer {
  margin-top: 10px; padding-top: 6px; border-top: 1px solid #e5e7eb;
  font-size: 8pt; color: #6b7280;
}
.page-break { page-break-before: always; }
"""


def wrap(title: str, body: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"/>
<title>{title}</title>
<style>{CSS}</style>
</head><body>
{body}
<div class="footer">Public LinkedIn / GFG / company posts only · Kavya Bhatiya prep · not affiliated with GE HealthCare · do not name-drop LinkedIn in the interview</div>
</body></html>"""


FINDINGS = wrap(
    "Surekha Sailesh — Findings",
    """
<div class="hero">
  <h1>Surekha Sailesh — Findings</h1>
  <p class="meta">Public-web only · Edison Program Manager (confirmed by GEHC TA posts) · Kavya Edison Intern PM round</p>
  <div class="badges">
    <span class="badge">Spelling: Sailesh (not Shailesh)</span>
    <span class="badge">Bengaluru</span>
    <span class="badge">Sr. Manager — Strategic Programs</span>
    <span class="badge">Highest-likelihood PM panelist</span>
  </div>
</div>

<div class="ok">
  <strong>Why she matters for you.</strong> Multiple GE HealthCare India / TA posts for the 2025 Edison intern cohort
  explicitly thank <em>Edison Program Manager Surekha Sailesh</em> alongside APAC TA Head Annu Mathew and HR partners.
  A GE HealthCare India “Desk Diaries” post notes photos of her <em>Edison batches</em> on her desk — early-talent is core to her work.
  For a post-tech “Program Manager” round on Edison Intern, she is the highest-probability named interviewer from public sources.
</div>

<div class="warn">
  <strong>Inference vs fact.</strong> Role + Edison Program Manager title = CONFIRMED. Exact Saturday panel assignment is NOT public.
  Everything about “how she interviews” is INFERENCE from role + campus EID Intern managerial patterns. Do not say “I saw your LinkedIn.”
</div>

<div class="warn">
  <strong>EID Intern ≠ PPO.</strong> GFG “project you are on / USP for the organisation” and “learning in the internship to date” are for people <em>already interning</em> converting to FTE.
  Kavya is a <strong>campus EID Intern</strong> candidate — ask about <em>her</em> projects (LogiFlow), why GEHC/EID, ownership, Bengaluru — not GE project USP.
</div>

<div class="kpi">
  <div><b>CONFIRMED</b>Edison Program Manager (TA posts)</div>
  <div><b>Apr 2023→</b>Sr. Manager, Strategic Programs &amp; Initiatives</div>
  <div><b>EID Intern</b>campus fit · not PPO</div>
</div>

<h2>1. Confirmed public facts</h2>
<table>
  <tr><th>Item</th><th>Detail</th></tr>
  <tr><td>Current title</td><td>Sr. Manager — Strategic Programs &amp; Initiatives, GE HealthCare (India)</td></tr>
  <tr><td>Edison role</td><td>Named <strong>Edison Program Manager</strong> on GEHC intern onboarding posts (May 2025 cohort of 35; SVNIT Surat listed among colleges)</td></tr>
  <tr><td>Prior GEHC</td><td>India Healthcare Technology Center — Strategic Programs and Initiatives Lead (Nov 2021 → Apr 2023), Bengaluru</td></tr>
  <tr><td>Before GEHC</td><td>Cisco — Program Manager, Enterprise PMO &amp; Operations; Business Operations / site strategies</td></tr>
  <tr><td>Public themes</td><td>University relations, early talent, partner/program ops, employee engagement, cross-functional interlock</td></tr>
  <tr><td>Culture signal</td><td>Desk Diaries: Edison batch photos + art/painting — values young talent energy, not only delivery metrics</td></tr>
  <tr><td>Public AI pride</td><td>Reposted GEHC topping USFDA AI-enabled medical device authorizations list — cares about healthcare AI impact narrative</td></tr>
</table>

<h2>2. What she is likely screening for — EID Intern (INFERENCE)</h2>
<ul>
  <li><strong>Why EID / why healthcare / why GEHC</strong> — genuine, not “any internship.”</li>
  <li><strong>Ownership on <em>your</em> projects</strong> — LogiFlow: what you built, what was hard, honest metrics — not “USP for GE.”</li>
  <li><strong>Will you show up</strong> — Bengaluru full duration; no-show = withdrawal.</li>
  <li><strong>Coachability</strong> — feedback, ambiguity, conflict without ego.</li>
  <li><strong>Curiosity</strong> — what a strong EID intern looks like; how interns are staffed.</li>
</ul>
<div class="note">She is a <strong>program / strategic ops</strong> leader, not an architect. Expect fit + ownership storytelling, not live coding. Skip PPO phrasing.</div>

<h2>3. How to play 20–25 minutes with her</h2>
<table>
  <tr><th>Do</th><th>Don’t</th></tr>
  <tr>
    <td>45s intro → LogiFlow you owned → why healthcare / EID → why GEHC → Bengaluru yes → 1–2 intern questions</td>
    <td>PPO “project I’m on at GE” answers · name-drop LinkedIn · invent SKUs · “maybe” on relocate · accuracy-only metrics</td>
  </tr>
</table>
<div class="you">
  <strong>One line she should hear.</strong><br/>
  “I want my first engineering bar to be reliability under clinical-adjacent standards — LogiFlow taught me to defend metrics honestly; EID is where I want to grow that under mentorship.”
</div>
""",
)


ROSTER = wrap(
    "GEHC Bengaluru — Program Manager Roster",
    """
<div class="hero">
  <h1>GEHC Bengaluru — Program Manager Roster</h1>
  <p class="meta">Public LinkedIn / company posts · who could sit a “Program Manager” / managerial round · ranked by Edison-intern relevance</p>
  <div class="badges">
    <span class="badge">14 people mapped</span>
    <span class="badge">Edison-linked first</span>
    <span class="badge">Then AI/Edison platform PMs</span>
    <span class="badge">Then product / TPM</span>
  </div>
</div>

<div class="warn">
  Panel assignment is never public. Treat Tier A as primary prep; Tier B/C as “if the calendar name is different, adapt tone.”
  Do not contact these people. Do not mention scraping this list in interview.
</div>

<h2>Tier A — Edison / early-talent program (prep first)</h2>
<table>
  <tr><th>Person</th><th>Public role</th><th>Why relevant</th></tr>
  <tr>
    <td><span class="tag tag-hot">HOT</span><strong>Surekha Sailesh</strong></td>
    <td>Sr. Manager, Strategic Programs &amp; Initiatives; named <strong>Edison Program Manager</strong></td>
    <td>Thanked on 2025 Edison intern onboarding (35 interns; SVNIT listed). Desk has Edison batch photos. Highest-likelihood PM round.</td>
  </tr>
  <tr>
    <td><span class="tag tag-ed">ED</span><strong>Uma Parameswaran</strong></td>
    <td>Lean Six Sigma MBB · <strong>Edison Program Manager</strong> · Talent Competency Leader (since ~2013)</td>
    <td>Long-standing Edison Program Manager; issues Edison impact awards / graduation support. Alternate or senior Edison voice.</td>
  </tr>
  <tr>
    <td><strong>Annu Mathew</strong></td>
    <td>TA Leader — APAC / Global IT Segment</td>
    <td>Leads campus / Edison talent posts; more TA/HR than PM, but co-appears with Surekha on Edison intern wins.</td>
  </tr>
  <tr>
    <td><strong>HR partners (cohort posts)</strong></td>
    <td>Monika Suryawanshi · Amrita Mishra · Shreya Kumar · Sarvesh Sharma · Siren Sivan</td>
    <td>Delivery / HR side of Edison intern process — more likely HR round than PM, but know the names if calendar shows them.</td>
  </tr>
</table>

<h2>Tier B — Edison platform / AI program delivery (if named)</h2>
<table>
  <tr><th>Person</th><th>Public role</th><th>Tone shift if they interview</th></tr>
  <tr>
    <td><span class="tag tag-ai">AI</span><strong>Gajanana Kamath</strong></td>
    <td>Sr. Program Manager — AVS Digital; ex Staff TPM — <strong>Edison AI</strong></td>
    <td>Regulated software / SaMD / AI-ML delivery language. Lean into metric honesty, risk, reliability — not only soft fit.</td>
  </tr>
  <tr>
    <td><span class="tag tag-ai">AI</span><strong>Hitesh Boda</strong></td>
    <td>Sr. PM AI/ML (STO); ex Sr. PM <strong>Edison Data Platform</strong></td>
    <td>Data platform, governance, clinical data lake. Speak pipelines, validation, “advisory not verdict” for ML.</td>
  </tr>
  <tr>
    <td><span class="tag tag-ai">AI</span><strong>Shubha Shirsat</strong></td>
    <td>Product Program Leader — AI/ML Strategic Partnerships</td>
    <td>Partnerships / AI programs. Why healthcare AI + honest impact story.</td>
  </tr>
  <tr>
    <td><span class="tag tag-ai">AI</span><strong>Ashwin TV</strong></td>
    <td>AI Transformation Program Manager (PCS)</td>
    <td>Portfolio / governance of AI initiatives. Prioritisation and measurable outcomes.</td>
  </tr>
</table>

<h2>Tier C — Product / TPM / ops PMs (Bengaluru)</h2>
<table>
  <tr><th>Person</th><th>Public role</th><th>Note</th></tr>
  <tr><td><strong>Rajee Kukreja</strong></td><td>Sr. PM — Advanced Visualization Solutions Digital; ex PCS Data Platform TPM</td><td>Imaging / AVS digital + data-as-product.</td></tr>
  <tr><td><strong>Abhilash G</strong></td><td>Program Manager (Agile/SAFe, embedded SW background)</td><td>Classic delivery PM — ownership, milestones, conflict.</td></tr>
  <tr><td><strong>Sheeja Shetty</strong></td><td>Program Manager; ex NASSCOM Digital Innovation / Novo Nordisk</td><td>Innovation ecosystem background.</td></tr>
  <tr><td><strong>Preethi Kandavel</strong></td><td>Sr. Staff Technical Program Manager</td><td>Agile coaching + TPM depth.</td></tr>
  <tr><td><strong>Keshava J</strong></td><td>Staff Technical Program Manager</td><td>Scrum / PI planning / stakeholder reporting.</td></tr>
  <tr><td><strong>Rajesh Roshan</strong></td><td>TPM / Staff Software Architect; PACS performance &amp; reliability</td><td>Reliability programs — metric honesty lands well.</td></tr>
  <tr><td><strong>Sandeep MB</strong></td><td>Senior Staff TPM; LPI Digital Cloud (AWS)</td><td>Cloud migration / cross-functional governance.</td></tr>
  <tr><td><strong>Sravan Vasireddy</strong></td><td>Strategic Initiatives Leader — Enterprise Applications</td><td>Enterprise release / transformation — less Edison-intern specific.</td></tr>
</table>

<div class="note">
  <strong>Practical rule (EID Intern).</strong> Calendar “Program Manager” → Mock 1 (Surekha-style fit).
  Tier B/C name → Mock 2. Never use PPO “project you’re on / USP for the organisation.”
</div>
""",
)


GFG_BANK = wrap(
    "GFG Managerial Scrape — EID Intern filter",
    """
<div class="hero">
  <h1>GFG Managerial Scrape — Filtered for EID Intern</h1>
  <p class="meta">Kavya is campus EID Intern (pre-start) · PPO / “already at GE” questions marked SKIP</p>
  <div class="badges">
    <span class="badge">EID Intern only</span>
    <span class="badge">SKIP = PPO junk</span>
    <span class="badge">USE = campus / fit</span>
  </div>
</div>

<div class="warn">
  <strong>Skip these for EID Intern.</strong> From GFG Internship+PPO “EEDP Manager” round — written for someone <em>already interning</em>:
  “What project are you on and what USP does it create for the organisation?” · “Learning experience in the internship to date?”
  Do not rehearse those phrasings. Translate to: tell me about <em>your</em> strongest project / what you owned.
</div>

<h2>1. USE for EID Intern PM round</h2>
<table>
  <tr><th>Ask this way</th><th>Why</th><th>Source cue</th></tr>
  <tr><td>Introduce yourself — why EID Intern?</td><td>Opener</td><td>Every campus write-up</td></tr>
  <tr><td>Walk me through your strongest project — what did <em>you</em> own?</td><td>Ownership (not GE USP)</td><td>FTE managerial · Off-campus 2021 · campus</td></tr>
  <tr><td>What was hard / what did you learn?</td><td>Coachability</td><td>GE 2019 · Extern</td></tr>
  <tr><td>Why GE HealthCare / why healthcare?</td><td>Motivation</td><td>FTE · EEDP campus · PPO overlap OK</td></tr>
  <tr><td>What do you know about us? (website)</td><td>Research</td><td>GFG FTE managerial</td></tr>
  <tr><td>Why are you a good fit — tech + projects?</td><td>Fit map</td><td>FTE · EEDP campus</td></tr>
  <tr><td>Disagreement / ambiguity / feedback?</td><td>Intern delivery</td><td>AmbitionBox · campus prep</td></tr>
  <tr><td>Hobbies? Strength / weakness with proof?</td><td>Human</td><td>FTE · GE 2019</td></tr>
  <tr><td>Bengaluru full duration?</td><td>Logistics</td><td>SVNIT 2024 · GE 2019</td></tr>
  <tr><td>Questions for me?</td><td>Curiosity</td><td>Every write-up</td></tr>
</table>

<h2>2. SKIP for EID Intern (PPO / already-employed)</h2>
<table>
  <tr><th>Irrelevant question</th><th>Why skip</th></tr>
  <tr><td>“What project are you on and USP for the organisation?”</td><td>Assumes you are already on a GE project</td></tr>
  <tr><td>“Learning experience in the internship to date?”</td><td>Assumes internship already started</td></tr>
  <tr><td>Deep “rate the EEDP program structure” as primary</td><td>EID Intern first; EEDP is a later path if earned — one calm line is enough</td></tr>
  <tr><td>Managerial puzzles as core prep</td><td>Rare one-off; don’t centre mocks on them</td></tr>
</table>

<div class="ok">
  <strong>GFG tip still useful:</strong> prepare key points; honesty beats spontaneous fluff. Just use EID Intern wording.
</div>
""",
)


MOCK1 = wrap(
    "PM Mock 1 — EID Intern · Surekha / Edison PM",
    """
<div class="hero">
  <h1>PM Mock 1 — EID Intern · Surekha / Edison PM</h1>
  <p class="meta">Kavya Bhatiya · campus EID Intern · post-tech · no PPO / “project you’re on at GE” questions</p>
  <div class="badges">
    <span class="badge">20–25 min</span>
    <span class="badge">EID Intern</span>
    <span class="badge">Ownership · fit · Bengaluru</span>
    <span class="badge">Do not name-drop</span>
  </div>
</div>

<div class="warn">
  <strong>Removed as irrelevant for EID Intern:</strong> “What project are you on, and what USP does it create for an organisation?”
  That is PPO/EEDP Manager language for current interns. Here we ask about <em>your</em> college / GSC project.
</div>

<div class="note">
  <strong>How to use.</strong> Friend reads pink only. 25-min timer. Green = debrief. She screens: will this intern show up, own a slice, take feedback, care about healthcare — not GE product USP.
</div>

<div class="kpi">
  <div><b>Your project</b>LogiFlow · what you owned</div>
  <div><b>Why EID</b>healthcare bar + mentorship</div>
  <div><b>Logistics</b>Bengaluru full yes</div>
</div>

<h2>Clock</h2>
<table>
  <tr><th>Time</th><th>Block</th><th>Goal</th></tr>
  <tr><td>0:00–2:00</td><td>Intro</td><td>45–60s; why EID Intern; stop.</td></tr>
  <tr><td>2:00–8:00</td><td>Your project</td><td>LogiFlow ownership + hard part + metrics.</td></tr>
  <tr><td>8:00–13:00</td><td>Why GEHC / healthcare</td><td>Motivation; no Amazon-bash.</td></tr>
  <tr><td>13:00–17:00</td><td>Learning / ambiguity</td><td>Metric honesty or thin-slice STAR.</td></tr>
  <tr><td>17:00–20:00</td><td>After internship</td><td>Ship + learn; EEDP only if earned — light.</td></tr>
  <tr><td>20:00–25:00</td><td>Bengaluru + questions</td><td>Full yes; intern success criteria.</td></tr>
</table>

<h2>Script</h2>
<div class="iv"><strong>INTERVIEWER</strong> Good morning. Please introduce yourself — and why the EID / Edison Intern role.</div>
<div class="you"><strong>YOU SAY</strong><br/>
Good morning. I am Kavya Bhatiya, B.Tech Artificial Intelligence at SVNIT Surat, CGPA 9.05. I cleared technical.
Strongest work: LogiFlow — multimodal logistics on FastAPI, PostgreSQL, Next.js with delay-risk ML — Top 106 Google Solution Challenge 2026.
I am here for EID Intern because I want to contribute on a live healthcare software team, take feedback from seniors, and learn GEHC engineering practices on-site in Bengaluru.</div>

<div class="iv"><strong>INTERVIEWER</strong> Tell me about your strongest project — what did you personally own, and what was hard?</div>
<div class="src">EID Intern framing · NOT “USP for the organisation” / PPO</div>
<div class="you"><strong>YOU SAY (~75s)</strong><br/>
LogiFlow ranks road/rail/air/sea on time, reliability, cost, and sustainability. Most tools optimise only speed or cost; we put delay risk in the ranking.
I owned the FastAPI ranking pipelines and the HistGradientBoosting delay-risk model — 73.0% accuracy, 68.0% delayed recall, 78.3% ROC-AUC — tuned for recall because missing a delay costs more than a false alarm.
Hard part: early accuracy looked fine while we were missing real delays. I moved the team to recall and ROC-AUC and treated the model as an advisory risk signal, not a verdict. Outcome: Top 106 global. That habit — measure what the user feels — is what I want to bring as an EID intern.</div>

<div class="iv"><strong>INTERVIEWER</strong> Why healthcare — and why GE HealthCare — for this internship?</div>
<div class="you"><strong>YOU SAY (~60s)</strong><br/>
I want my first real engineering bar to be reliability under clinical-adjacent standards. In LogiFlow a wrong risk signal costs money; here it can cost trust.
GE HealthCare builds imaging and monitoring plus a software/AI layer (Edison) clinicians rely on. EID gives live project work under review — how I learn fastest. Money matters, but early on the problem shape matters more; I’m not Amazon-bashing, I’m choosing this bar.</div>

<div class="iv"><strong>INTERVIEWER</strong> Tell me about a time something was unfamiliar or you had to change approach under pressure.</div>
<div class="you"><strong>YOU SAY — STAR</strong><br/>
Delay model looked fine on accuracy, weak on real delays. Unfamiliar: defending a “bad looking” metric choice. Switched focus to recall/ROC-AUC; kept the model advisory inside ranking. Learned to pick the metric the user feels — same loop I’ll use on a new codebase here.</div>

<div class="iv"><strong>INTERVIEWER</strong> Where do you see yourself after this internship?</div>
<div class="you"><strong>YOU SAY (~40s)</strong><br/>
Short term: contribute a tested slice on a real backlog and learn GEHC practices. If performance is strong, I’m interested in growing further here — including an EEDP-style path later if I earn it. I’m not claiming a title; I want to compound in healthcare software.</div>

<div class="iv"><strong>INTERVIEWER</strong> Bengaluru, full duration — any constraints?</div>
<div class="you"><strong>YOU SAY</strong><br/>Yes — full duration, on-site Bengaluru, no constraints. Every scheduled slot is mandatory; no-shows are not an option for me.</div>

<div class="iv"><strong>INTERVIEWER</strong> Questions for me?</div>
<div class="you"><strong>YOU SAY (pick 1–2)</strong><br/>
What does a strong EID intern look like in week 2 versus week 6?<br/>
How are interns staffed — one-team ownership or rotating support?<br/>
Avoid: stipend, PPO odds, WFH, “how did I do?”, LinkedIn name-drops.</div>

<h2>Rapid probes</h2>
<div class="probe">
• Explain LogiFlow to a non-coder → risk score for routes, not a black-box “fastest.”<br/>
• Strength with proof → ownership + metric honesty.<br/>
• Weakness → early over-scoping; now ship thin slices.<br/>
• Higher studies? (if asked) → industry first this internship; master’s later only if a problem needs research depth.
</div>

<div class="score">
Score 1–5: Structure · Project ownership · Why EID/GEHC · Learning STAR · Bengaluru · Questions.<br/>
<strong>Fail:</strong> answering as if already on a GE project · inventing SKUs · “maybe” relocate · no questions.
</div>
""",
)


MOCK2 = wrap(
    "PM Mock 2 — EID Intern · Campus filter",
    """
<div class="hero">
  <h1>PM Mock 2 — EID Intern · Campus / Sr Manager filter</h1>
  <p class="meta">Alternate PM name or classic campus managerial · still EID Intern · no PPO USP phrasing</p>
  <div class="badges">
    <span class="badge">20–25 min</span>
    <span class="badge">Website + fit</span>
    <span class="badge">Ownership drill</span>
    <span class="badge">Conflict + hobbies</span>
  </div>
</div>

<div class="note">
  <strong>vs Mock 1.</strong> Same EID Intern audience. Mock 1 leans Surekha / program fit. Mock 2 leans website research, cross-questions on LogiFlow, conflict, hobbies.
</div>

<h2>Clock</h2>
<table>
  <tr><th>Time</th><th>Block</th><th>Goal</th></tr>
  <tr><td>0:00–2:00</td><td>Intro</td><td>Why EID Intern.</td></tr>
  <tr><td>2:00–7:00</td><td>GEHC website / why GE</td><td>Accurate; no invented SKUs.</td></tr>
  <tr><td>7:00–13:00</td><td>Your project drill</td><td>What you built; X-factor; metrics.</td></tr>
  <tr><td>13:00–18:00</td><td>Conflict / ambiguity</td><td>STAR maturity.</td></tr>
  <tr><td>18:00–21:00</td><td>Hobbies + strength/weakness</td><td>Short + proof.</td></tr>
  <tr><td>21:00–25:00</td><td>Bengaluru + close</td><td>Yes + intern questions.</td></tr>
</table>

<h2>Script</h2>
<div class="iv"><strong>INTERVIEWER</strong> Introduce yourself.</div>
<div class="you"><strong>YOU SAY</strong><br/>
Kavya Bhatiya, B.Tech AI, SVNIT Surat, CGPA 9.05. Backend + applied ML. LogiFlow (FastAPI/Postgres/Next.js/delay-risk) — Top 106 GSC 2026. 470+ LeetCode. Here for EID Intern to ship on a live healthcare team in Bengaluru.</div>

<div class="iv"><strong>INTERVIEWER</strong> What do you know about GE HealthCare?</div>
<div class="src">GFG FTE managerial — website · USE for EID</div>
<div class="you"><strong>YOU SAY</strong><br/>
Standalone med-tech: imaging (MRI/CT/X-ray/ultrasound), patient monitoring, plus software/digital turning device data into clinical insight. Edison = AI/analytics layer. Customers: hospitals, imaging centres, clinicians. I want to build reliable software in that stack — not invent model numbers.</div>

<div class="iv"><strong>INTERVIEWER</strong> Why are you a good fit for EID Intern — technologies and projects?</div>
<div class="you"><strong>YOU SAY</strong><br/>
I ship systems: FastAPI, Postgres, Docker, Next.js, HistGB/CatBoost. LogiFlow end-to-end ownership with defendable metrics 73/68/78.3. Fit is ownership + measuring what I ship + taking feedback. Domain I’ll learn fast on the team.</div>

<div class="iv"><strong>INTERVIEWER</strong> Walk me through what you personally built on LogiFlow. What was the X-factor?</div>
<div class="you"><strong>YOU SAY</strong><br/>
Mine: ranking pipelines, delay-risk model, Docker packaging with the team. X-factor: multi-objective ranking with delay risk first-class — plus honest metrics. Hard: accuracy hid missed delays; I moved us to recall/ROC-AUC.</div>

<div class="iv"><strong>INTERVIEWER</strong> Disagreement on the team?</div>
<div class="you"><strong>YOU SAY — STAR</strong><br/>
UI polish vs harden metrics under GSC deadline. Argued defendable metrics &gt; polish; time-boxed UI; locked three metrics. Compromise on polish, not on numbers I cannot explain.</div>

<div class="iv"><strong>INTERVIEWER</strong> Ambiguous requirements?</div>
<div class="you"><strong>YOU SAY</strong><br/>Smallest acceptance check → confirm in one message → thin slice → show early. LogiFlow: rank schema before more modes.</div>

<div class="iv"><strong>INTERVIEWER</strong> Hobbies? Strength and weakness with examples?</div>
<div class="you"><strong>YOU SAY</strong><br/>
Hobbies: DSA, Web Wonders/Echelon, healthcare-tech reading — short.<br/>
Strength: ownership + metric honesty.<br/>
Weakness: early over-scoping; now cut to shippable core.</div>

<div class="iv"><strong>INTERVIEWER</strong> Bengaluru full duration? Questions?</div>
<div class="you"><strong>YOU SAY</strong><br/>
Yes — full, on-site, no constraints.<br/>
Q: What does success look like for an EID intern by week 6? Optional: communication cadence you expect?</div>

<div class="page-break"></div>
<h2>EID Intern — what we dropped</h2>
<table>
  <tr><th>Dropped (PPO)</th><th>Use instead (EID)</th></tr>
  <tr><td>Project you’re on + USP for the organisation</td><td>Strongest project you owned + what was hard</td></tr>
  <tr><td>Learning in the internship to date</td><td>Learning from LogiFlow / GSC / unfamiliar situation</td></tr>
  <tr><td>Deep EEDP program quiz as centrepiece</td><td>Why EID Intern now; EEDP only as optional later path</td></tr>
</table>

<div class="ok">
  <strong>Day-of.</strong> Surekha / Edison PM → Mock 1. Other name → Mock 2. Same EID Intern answers either way.
</div>
""",
)


MOCK3 = wrap(
    "PM Mock 3 — EID Intern · STAR pressure",
    """
<div class="hero">
  <h1>PM Mock 3 — EID Intern · STAR pressure tape</h1>
  <p class="meta">Back-to-back behavioural · conflict · failure · feedback · prioritisation · 20 min</p>
  <div class="badges">
    <span class="badge">20 min</span>
    <span class="badge">STAR only</span>
    <span class="badge">Interruptions OK</span>
    <span class="badge">EID Intern</span>
  </div>
</div>

<div class="note">
  Friend fires pink lines fast. Keep each answer 45–60s. If they interrupt with “so what?” land the Result in one sentence.
</div>

<h2>Clock</h2>
<table>
  <tr><th>Time</th><th>Probe</th></tr>
  <tr><td>0:00–2:00</td><td>30s intro + why EID</td></tr>
  <tr><td>2:00–5:00</td><td>Conflict STAR</td></tr>
  <tr><td>5:00–8:00</td><td>Something you owned that broke / failed</td></tr>
  <tr><td>8:00–11:00</td><td>Critical feedback</td></tr>
  <tr><td>11:00–14:00</td><td>Deadline — what did you cut?</td></tr>
  <tr><td>14:00–17:00</td><td>Ambiguous task from a senior</td></tr>
  <tr><td>17:00–20:00</td><td>Bengaluru yes + one question</td></tr>
</table>

<div class="iv"><strong>INTERVIEWER</strong> 30 seconds — who are you and why EID Intern?</div>
<div class="you"><strong>YOU SAY</strong><br/>
Kavya Bhatiya, B.Tech AI, SVNIT, CGPA 9.05. LogiFlow — Top 106 GSC 2026. I want EID to ship on a live healthcare software team in Bengaluru under review.</div>

<div class="iv"><strong>INTERVIEWER</strong> Disagreement with a teammate. STAR. Go.</div>
<div class="you"><strong>YOU SAY</strong><br/>
S: GSC deadline; teammate wanted UI polish, I wanted harden delay-risk metrics.<br/>
T: Keep a demo we could defend.<br/>
A: Time-boxed polish; locked 73/68/78.3; Gemini off critical path; made it a data conversation.<br/>
R: Cleaner demos. I compromise on polish, not on numbers I cannot explain.</div>

<div class="iv"><strong>INTERVIEWER</strong> Something you owned broke. What did you do?</div>
<div class="you"><strong>YOU SAY</strong><br/>
S: FastAPI ranking endpoint returned inconsistent results under load near a demo — my slice.<br/>
T: Fix without hiding it.<br/>
A: Flagged the team immediately; reproduced; fixed non-deterministic handling; added a check for that class of bug.<br/>
R: Demo held. Owning breaks out loud beats a quiet patch.</div>

<div class="iv"><strong>INTERVIEWER</strong> Hard feedback that stung?</div>
<div class="you"><strong>YOU SAY</strong><br/>
Mentor said leading with accuracy on an imbalanced delay problem was misleading. It stung; he was right. I switched to recall + ROC-AUC together and closed the loop. Default: assume they’ve seen something I haven’t.</div>

<div class="iv"><strong>INTERVIEWER</strong> Under a hard deadline — what did you cut and why?</div>
<div class="you"><strong>YOU SAY</strong><br/>
Cut scope on extra modes / polish; kept ranking schema + delay-risk metrics. Saying no to good ideas so the core ships is how we hit Top 106.</div>

<div class="iv"><strong>INTERVIEWER</strong> Senior gives a vague ticket. First three moves?</div>
<div class="you"><strong>YOU SAY</strong><br/>
1) Write smallest acceptance check — input, output, failure case.<br/>
2) Confirm in one message.<br/>
3) Ship a thin slice, show early, iterate. Same as fixing LogiFlow rank schema before more modes.</div>

<div class="iv"><strong>INTERVIEWER</strong> Bengaluru full duration? One question for me.</div>
<div class="you"><strong>YOU SAY</strong><br/>
Yes — full, on-site, no constraints. Question: what does a strong EID intern look like by week 6?</div>

<div class="score">Fail flags: long stories with no Result · blaming teammates · “maybe” on Bengaluru · PPO USP phrasing.</div>
""",
)


MOCK4 = wrap(
    "PM Mock 4 — EID Intern · Non-coder + GEHC",
    """
<div class="hero">
  <h1>PM Mock 4 — EID Intern · Explain + company research</h1>
  <p class="meta">Program manager who is not deep-coding · communication + why GEHC · 20 min</p>
  <div class="badges">
    <span class="badge">20 min</span>
    <span class="badge">Layman English</span>
    <span class="badge">Website check</span>
    <span class="badge">EID Intern</span>
  </div>
</div>

<div class="warn">If you drown them in FastAPI jargon, you fail this mock even if tech was right.</div>

<h2>Clock</h2>
<table>
  <tr><th>Time</th><th>Block</th></tr>
  <tr><td>0:00–2:00</td><td>Intro</td></tr>
  <tr><td>2:00–7:00</td><td>Explain LogiFlow to a non-engineer</td></tr>
  <tr><td>7:00–11:00</td><td>What do you know about GEHC?</td></tr>
  <tr><td>11:00–15:00</td><td>Why healthcare / why EID for you</td></tr>
  <tr><td>15:00–18:00</td><td>How will you ramp in week 1–2?</td></tr>
  <tr><td>18:00–20:00</td><td>Bengaluru + questions</td></tr>
</table>

<div class="iv"><strong>INTERVIEWER</strong> Introduce yourself — keep it human.</div>
<div class="you"><strong>YOU SAY</strong><br/>
I’m Kavya, AI undergrad at SVNIT Surat. I like building systems that make trade-offs visible — my team’s LogiFlow project reached Top 106 in Google Solution Challenge. I’m interviewing for EID Intern to do that kind of careful engineering on healthcare software in Bengaluru.</div>

<div class="iv"><strong>INTERVIEWER</strong> Explain your project as if I’m a hospital ops person, not a coder.</div>
<div class="you"><strong>YOU SAY</strong><br/>
Imagine choosing how to move a shipment — cheap, fast, and reliable pull in different directions. LogiFlow shows options side by side and flags which ones are more likely to arrive late — like a weather risk score for logistics. It doesn’t make the final call; it gives a clearer picture so people don’t pick “cheap and fast” that often fails. I built the scoring backend and the delay-risk model, and I insisted we report the metrics that matter — catching real delays — not only a flattering accuracy number.</div>

<div class="iv"><strong>INTERVIEWER</strong> What do you actually know about GE HealthCare?</div>
<div class="you"><strong>YOU SAY</strong><br/>
Major med-tech company, now standalone. Imaging — MRI, CT, X-ray, ultrasound — plus patient monitoring, and a growing software/AI layer that turns device data into clinical insight. Edison sits in that software layer. Customers are hospitals and clinicians. I’m not inventing product model numbers; I care about the reliability bar those products need.</div>

<div class="iv"><strong>INTERVIEWER</strong> Why this internship — why not a pure product company?</div>
<div class="you"><strong>YOU SAY</strong><br/>
Money matters, but early career the multiplier is the problem. I want reliability under clinical-adjacent standards. LogiFlow taught me wrong signals have a cost; healthcare raises that cost. EID is live work under seniors — how I learn.</div>

<div class="iv"><strong>INTERVIEWER</strong> First two weeks here — how do you ramp without wasting the team?</div>
<div class="you"><strong>YOU SAY</strong><br/>
Read the smallest ticket end-to-end; write acceptance checks; ask one clarifying question early; ship a thin visible slice; update in writing. I’d rather show a small correct piece than disappear for a week.</div>

<div class="iv"><strong>INTERVIEWER</strong> Relocate? Questions?</div>
<div class="you"><strong>YOU SAY</strong><br/>
Yes — full duration Bengaluru. Q: How do you expect interns to communicate progress — standup, chat, or short written updates?</div>
""",
)


MOCK5 = wrap(
    "PM Mock 5 — EID Intern · Interrupt & probe",
    """
<div class="hero">
  <h1>PM Mock 5 — EID Intern · Interrupt &amp; probe</h1>
  <p class="meta">Manager cuts you off · “prove it” · ownership language · 20 min</p>
  <div class="badges">
    <span class="badge">20 min</span>
    <span class="badge">Pressure</span>
    <span class="badge">I not we</span>
    <span class="badge">EID Intern</span>
  </div>
</div>

<div class="note">Friend should interrupt mid-answer with the pink follow-ups. Train landing a crisp close.</div>

<div class="iv"><strong>INTERVIEWER</strong> Tell me about LogiFlow.</div>
<div class="probe"><strong>Interrupt at 20s:</strong> “Stop. What did <em>you</em> build — not the team?”</div>
<div class="you"><strong>YOU SAY</strong><br/>
I owned FastAPI ranking pipelines and the delay-risk model (HistGB) — 73.0 / 68.0 delayed recall / 78.3 ROC-AUC — and Docker packaging with the team. Ranking UI was shared; the risk model and serving path were mine.</div>

<div class="iv"><strong>INTERVIEWER</strong> Those numbers look modest. Why should I trust you?</div>
<div class="you"><strong>YOU SAY</strong><br/>
Because I won’t inflate them. Accuracy alone hid missed delays; I moved the story to recall on purpose. I’d rather bring honest metrics a clinician-adjacent team can challenge than a vanity score.</div>

<div class="iv"><strong>INTERVIEWER</strong> So you’re an ML person. Can you take a boring backend ticket?</div>
<div class="you"><strong>YOU SAY</strong><br/>
Yes. Most of LogiFlow ownership was pipelines, APIs, data shape, Docker — the model was one slice. As an EID intern I’ll take whatever backlog slice helps the team; I care about shipping tested work.</div>

<div class="iv"><strong>INTERVIEWER</strong> Why GEHC — one minute, then I’ll cut you.</div>
<div class="probe"><strong>At 40s:</strong> “So it’s just brand?”</div>
<div class="you"><strong>YOU SAY</strong><br/>
No — brand isn’t enough. I want the reliability bar of software near clinical workflows, and EID gives mentorship on a live team. If it were only brand I’d apply anywhere.</div>

<div class="iv"><strong>INTERVIEWER</strong> Offer from a product company mid-internship — what do you do?</div>
<div class="you"><strong>YOU SAY</strong><br/>
I finish commitments. I chose EID for the problem and learning; I don’t ghost a team. Any decision after the internship would be after I’ve delivered here.</div>

<div class="iv"><strong>INTERVIEWER</strong> Weakness — don’t give me a humblebrag.</div>
<div class="you"><strong>YOU SAY</strong><br/>
Early GSC: I over-scoped. We were drowning. I learned to cut to a shippable core. Still watch myself when a cool feature appears — I time-box or park it.</div>

<div class="iv"><strong>INTERVIEWER</strong> Bengaluru. Any family “maybe”?</div>
<div class="you"><strong>YOU SAY</strong><br/>
No maybe — full duration, on-site, ready on your timeline.</div>

<div class="iv"><strong>INTERVIEWER</strong> Ask me something that isn’t stipend or PPO.</div>
<div class="you"><strong>YOU SAY</strong><br/>
When an EID intern is struggling silently, how do you want them to surface that — and how early?</div>

<div class="score">Pass = short answers, “I” ownership, honest metrics, Bengaluru certainty. Fail = we-we-we, vanity accuracy, PPO USP, stipend questions.</div>
""",
)


MOCK6 = wrap(
    "PM Mock 6 — EID Intern · Day-of cold run",
    """
<div class="hero">
  <h1>PM Mock 6 — EID Intern · Day-of cold run</h1>
  <p class="meta">Shortest full loop · morning-of rehearsal · 15 min · no notes</p>
  <div class="badges">
    <span class="badge">15 min</span>
    <span class="badge">Cold</span>
    <span class="badge">Must land</span>
    <span class="badge">EID Intern</span>
  </div>
</div>

<div class="ok">Run once the morning of. Then stop rehearsing. If you blank, use the order below as a mental checklist.</div>

<table>
  <tr><th>Min</th><th>They ask</th><th>You must land</th></tr>
  <tr><td>0–1</td><td>Intro</td><td>Name · SVNIT · 9.05 · LogiFlow Top 106 · EID Intern</td></tr>
  <tr><td>1–5</td><td>Project</td><td>What you owned · 73/68/78.3 · hard = recall not vanity accuracy</td></tr>
  <tr><td>5–8</td><td>Why GEHC / EID</td><td>Reliability bar · live team · not any internship</td></tr>
  <tr><td>8–11</td><td>One STAR</td><td>Conflict or feedback — Result in one line</td></tr>
  <tr><td>11–13</td><td>Bengaluru</td><td>Full yes · no constraints</td></tr>
  <tr><td>13–15</td><td>Your Q</td><td>Strong EID intern week 2 vs 6</td></tr>
</table>

<div class="iv"><strong>INTERVIEWER</strong> Intro.</div>
<div class="you"><strong>YOU SAY (~45s)</strong><br/>
Good morning. Kavya Bhatiya, B.Tech AI, SVNIT Surat, CGPA 9.05. Cleared technical. Strongest work LogiFlow — FastAPI, PostgreSQL, Next.js, delay-risk ML — Top 106 GSC 2026. Here for EID Intern to contribute on a live healthcare software team in Bengaluru.</div>

<div class="iv"><strong>INTERVIEWER</strong> Project — what did you own?</div>
<div class="you"><strong>YOU SAY (~60s)</strong><br/>
Ranking pipelines + delay-risk model. Tuned for 68% delayed recall / 78.3% ROC-AUC because missing delays mattered more than flattering accuracy. Hard part was changing the metric story under deadline. Outcome Top 106.</div>

<div class="iv"><strong>INTERVIEWER</strong> Why us?</div>
<div class="you"><strong>YOU SAY (~40s)</strong><br/>
GEHC: imaging, monitoring, software/AI (Edison) clinicians rely on. I want that reliability bar. EID = ship under seniors. That’s the internship I want.</div>

<div class="iv"><strong>INTERVIEWER</strong> One teamwork example.</div>
<div class="you"><strong>YOU SAY (~40s)</strong><br/>
Metrics vs UI polish — time-boxed polish, locked defendable metrics. Compromise on polish, not on numbers.</div>

<div class="iv"><strong>INTERVIEWER</strong> Location? Questions?</div>
<div class="you"><strong>YOU SAY</strong><br/>
Bengaluru full duration — yes. Question: what does a strong EID intern look like in week 2 versus week 6?</div>

<div class="warn">Do <strong>not</strong> say: USP for the organisation · internship learning to date · Cloud Run · invent SKUs · ask PPO odds.</div>
""",
)


def html_to_pdf(html_path: Path, pdf_path: Path) -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(html_path.resolve().as_uri(), wait_until="networkidle")
        page.pdf(
            path=str(pdf_path),
            format="A4",
            print_background=True,
            margin={"top": "0", "bottom": "0", "left": "0", "right": "0"},
        )
        browser.close()


def merge_master(parts: list[tuple[str, str]]) -> None:
    from pypdf import PdfReader, PdfWriter

    rows = "".join(
        f"<tr><td>{i}</td><td>{label}</td><td>{PdfReader(str(DIR / p)).get_num_pages()} pp</td></tr>"
        for i, (p, label) in enumerate(parts, 1)
    )
    cover_html = DIR / "_pm_master_cover.html"
    cover_html.write_text(
        f"""<!DOCTYPE html><html><head><meta charset="utf-8"/>
<style>
@page {{ size: A4; margin: 16mm; }}
body {{ font-family: Segoe UI, Helvetica, Arial, sans-serif; color: #1f2937; font-size: 10.5pt; }}
.hero {{ background: linear-gradient(135deg,#0b4f6c,#147a9b); color:#fff; padding:22px 20px; border-radius:12px; margin-bottom:16px; }}
h1 {{ margin:0 0 4px; font-size:20pt; }}
.meta {{ opacity:.92; margin:0 0 10px; font-size:10pt; }}
.badge {{ display:inline-block; background:rgba(255,255,255,.18); padding:3px 10px; border-radius:999px; font-size:8.5pt; font-weight:700; margin:2px 4px 0 0; }}
table {{ width:100%; border-collapse:collapse; font-size:9.5pt; }}
th,td {{ border:1px solid #d1d5db; padding:6px 8px; text-align:left; }}
th {{ background:#0b4f6c; color:#fff; }}
.warn {{ margin-top:12px; background:#fff7ed; border-left:4px solid #ea580c; padding:10px 12px; border-radius:0 8px 8px 0; font-size:9.5pt; }}
.ok {{ margin-top:10px; background:#ecfdf5; border-left:4px solid #059669; padding:10px 12px; border-radius:0 8px 8px 0; font-size:9.5pt; }}
</style></head><body>
<div class="hero">
  <h1>Kavya · GEHC EID Intern · PM Master Pack</h1>
  <p class="meta">Campus EID Intern · Program Manager round · 6 timed mocks · PPO questions removed</p>
  <span class="badge">EID Intern</span>
  <span class="badge">6 mocks</span>
  <span class="badge">Surekha Sailesh</span>
  <span class="badge">Not PPO</span>
</div>
<table><tr><th>#</th><th>Section</th><th>Pages</th></tr>{rows}</table>
<div class="ok"><strong>Practice order:</strong> Mock 1 → 2 → 3 (STAR) → 4 (layman) → 5 (pressure) → morning-of Mock 6 only.</div>
<div class="warn"><strong>Never rehearse as live Q:</strong> “What project are you on, and what USP does it create for an organisation?”</div>
</body></html>""",
        encoding="utf-8",
    )
    cover_pdf = DIR / "_pm_master_cover.pdf"
    html_to_pdf(cover_html, cover_pdf)

    writer = PdfWriter()
    for page in PdfReader(str(cover_pdf)).pages:
        writer.add_page(page)
    for pdf_name, _ in parts:
        for page in PdfReader(str(DIR / pdf_name)).pages:
            writer.add_page(page)
    out = DIR / "Kavya_GEHC_PM_Master_Pack.pdf"
    with out.open("wb") as f:
        writer.write(f)
    cover_html.unlink(missing_ok=True)
    cover_pdf.unlink(missing_ok=True)
    print(f"Merged {out.name} — {len(PdfReader(str(out)).pages)} pages — {out.stat().st_size:,} bytes")


def main() -> None:
    specs = [
        ("Surekha_Sailesh_Findings.html", "Surekha_Sailesh_Findings.pdf", FINDINGS),
        ("Kavya_GEHC_PM_People_Roster.html", "Kavya_GEHC_PM_People_Roster.pdf", ROSTER),
        ("Kavya_GEHC_PM_GFG_Managerial_Bank.html", "Kavya_GEHC_PM_GFG_Managerial_Bank.pdf", GFG_BANK),
        ("Kavya_GEHC_Mock1_PM_Personality_Check.html", "Kavya_GEHC_Mock1_PM_Personality_Check.pdf", MOCK1),
        ("Kavya_GEHC_Mock2_PM_Campus_Filter.html", "Kavya_GEHC_Mock2_PM_Campus_Filter.pdf", MOCK2),
        ("Kavya_GEHC_Mock3_PM_STAR_Pressure.html", "Kavya_GEHC_Mock3_PM_STAR_Pressure.pdf", MOCK3),
        ("Kavya_GEHC_Mock4_PM_Layman_GEHC.html", "Kavya_GEHC_Mock4_PM_Layman_GEHC.pdf", MOCK4),
        ("Kavya_GEHC_Mock5_PM_Interrupt_Probe.html", "Kavya_GEHC_Mock5_PM_Interrupt_Probe.pdf", MOCK5),
        ("Kavya_GEHC_Mock6_PM_DayOf_Cold.html", "Kavya_GEHC_Mock6_PM_DayOf_Cold.pdf", MOCK6),
    ]
    for html_name, pdf_name, content in specs:
        html_path = DIR / html_name
        pdf_path = DIR / pdf_name
        html_path.write_text(content, encoding="utf-8")
        html_to_pdf(html_path, pdf_path)
        print(f"Wrote {pdf_path.name} ({pdf_path.stat().st_size:,} bytes)")

    # Reviews one-pager kept for master
    reviews = DIR / "Kavya_GEHC_Program_Manager_Reviews.pdf"
    if not reviews.exists():
        print("WARN: reviews PDF missing")

    merge_master(
        [
            ("Surekha_Sailesh_Findings.pdf", "Surekha Sailesh — EID angle"),
            ("Kavya_GEHC_PM_People_Roster.pdf", "GEHC Bengaluru PM roster"),
            ("Kavya_GEHC_PM_GFG_Managerial_Bank.pdf", "GFG bank filtered for EID"),
            ("Kavya_GEHC_Program_Manager_Reviews.pdf", "PM reviews — EID filter"),
            ("Kavya_GEHC_Mock1_PM_Personality_Check.pdf", "Mock 1 — Surekha / fit"),
            ("Kavya_GEHC_Mock2_PM_Campus_Filter.pdf", "Mock 2 — campus filter"),
            ("Kavya_GEHC_Mock3_PM_STAR_Pressure.pdf", "Mock 3 — STAR pressure"),
            ("Kavya_GEHC_Mock4_PM_Layman_GEHC.pdf", "Mock 4 — layman + GEHC"),
            ("Kavya_GEHC_Mock5_PM_Interrupt_Probe.pdf", "Mock 5 — interrupt & probe"),
            ("Kavya_GEHC_Mock6_PM_DayOf_Cold.pdf", "Mock 6 — day-of cold run"),
        ]
    )


if __name__ == "__main__":
    main()
