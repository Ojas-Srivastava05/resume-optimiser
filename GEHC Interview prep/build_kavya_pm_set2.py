#!/usr/bin/env python3
"""EID Intern PM/HR Set 2 — new review-backed mocks 7–12 + remaster pack."""

from __future__ import annotations

from pathlib import Path

from playwright.sync_api import sync_playwright
from pypdf import PdfReader, PdfWriter

DIR = Path(__file__).resolve().parent

CSS = """
@page { size: A4; margin: 10mm 11mm 12mm; }
* { box-sizing: border-box; }
html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body {
  font-family: "Segoe UI", "Helvetica Neue", Helvetica, Arial, sans-serif;
  font-size: 9.5pt; line-height: 1.38; color: #1f2937; margin: 0;
}
h1 { font-size: 15.5pt; color: #0b4f6c; margin: 0 0 2px; }
h2 {
  font-size: 10.2pt; margin: 9px 0 5px; padding: 4px 8px;
  background: #0b4f6c; color: #fff; border-radius: 5px; page-break-after: avoid;
}
p, li { margin: 0 0 3px; }
ul { padding-left: 1.1em; margin: 3px 0 7px; }
.hero {
  background: linear-gradient(135deg, #0b4f6c, #147a9b);
  color: #fff; padding: 13px 15px; border-radius: 10px; margin-bottom: 9px;
}
.hero h1 { color: #fff; margin: 0 0 3px; font-size: 16pt; }
.meta { opacity: 0.92; font-size: 8.8pt; margin: 0 0 6px; }
.badge {
  display: inline-block; background: rgba(255,255,255,0.18);
  padding: 2px 8px; border-radius: 999px; font-size: 8pt; font-weight: 700; margin: 1px 3px 0 0;
}
.note, .warn, .ok, .iv, .you, .src, .probe, .score {
  padding: 6px 9px; border-radius: 0 6px 6px 0; margin: 5px 0 6px; font-size: 9pt;
  page-break-inside: avoid;
}
.note { background: #f0f9ff; border-left: 4px solid #0b4f6c; }
.warn { background: #fff7ed; border-left: 4px solid #ea580c; }
.ok { background: #ecfdf5; border-left: 4px solid #059669; }
.iv { background: #fce7f3; border-left: 4px solid #be185d; }
.you { background: #ecfdf5; border-left: 4px solid #059669; }
.src { background: #fef3c7; border-left: 4px solid #d97706; color: #92400e; font-size: 8.3pt; }
.probe { background: #eff6ff; border: 1px solid #bfdbfe; border-radius: 6px; font-size: 8.7pt; }
.score { background: #fafafa; border: 1px solid #e5e7eb; border-radius: 6px; font-size: 8.7pt; }
table { width: 100%; border-collapse: collapse; margin: 4px 0 8px; font-size: 8.5pt; }
th, td { border: 1px solid #d1d5db; padding: 4px 6px; text-align: left; vertical-align: top; }
th { background: #0b4f6c; color: #fff; }
tr:nth-child(even) td { background: #f8fafc; }
.footer { margin-top: 8px; padding-top: 5px; border-top: 1px solid #e5e7eb; font-size: 7.8pt; color: #6b7280; }
.page-break { page-break-before: always; }
"""


def wrap(title: str, body: str) -> str:
    return f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"/>
<title>{title}</title><style>{CSS}</style></head><body>
{body}
<div class="footer">Set 2 · public GFG / PCON / Freshers Dunia / AmbitionBox · EID Intern · Kavya prep · not affiliated with GEHC</div>
</body></html>"""


BANK2 = wrap(
    "Set 2 Review Q Bank — new sources",
    """
<div class="hero">
  <h1>Set 2 — New review questions (not in Mocks 1–6)</h1>
  <p class="meta">Fresh scrape after you finished Set 1 · EID Intern / campus managerial + HR gate · PPO USP still SKIP</p>
  <span class="badge">GE Intern 2022</span>
  <span class="badge">GFG Intern 2021</span>
  <span class="badge">IIT BHU HR</span>
  <span class="badge">SVNIT 2024 kill-shot</span>
  <span class="badge">PCON EID</span>
  <span class="badge">Freshers Dunia 2026</span>
</div>

<div class="warn">
  <strong>Still SKIP (PPO):</strong> “project you’re on + USP for the organisation” · “learning in the internship to date.”
</div>

<h2>New sources → new Q themes</h2>
<table>
  <tr><th>Source</th><th>New theme for EID Intern</th><th>Mock</th></tr>
  <tr><td>GFG GE Intern On-Campus 2022</td><td>Managerial = <strong>resume roasting</strong> + many situational Qs · Why GE from PPT · 42 min</td><td>7</td></tr>
  <tr><td>Same · HR 15–18 min</td><td>Challenges in projects · <strong>how will this internship help you?</strong></td><td>8</td></tr>
  <tr><td>GFG GEHC Intern 2021 HR</td><td>Healthcare vs product/service · <strong>why only GEHC</strong> · what do you know about GE · role flexibility Q</td><td>8</td></tr>
  <tr><td>GFG GEHC On-Campus (IIT BHU)</td><td><strong>What do you expect from this intern?</strong> · interest in medical field · instruments/ideas for health problems</td><td>9</td></tr>
  <tr><td>GFG SVNIT Aug 2024 HR (reject)</td><td><strong>Products · competitors · relocate</strong> — tech clear ≠ offer</td><td>10</td></tr>
  <tr><td>PCON EID Intern 2024</td><td>Strength/weakness with reason · <strong>semester challenges</strong></td><td>11</td></tr>
  <tr><td>GFG SVNIT selected + senior</td><td>Availability · org understanding · challenge STAR · hobbies/clubs</td><td>11</td></tr>
  <tr><td>GFG PPO HR one-off (adapted)</td><td>Humble: changes to org? · if we call a professor/mentor feedback?</td><td>12</td></tr>
  <tr><td>Freshers Dunia SW Intern 2026</td><td>Process confirms Managerial Discussion then HR — both matter</td><td>all</td></tr>
  <tr><td>AmbitionBox PM (light)</td><td>Underperforming teammate / influence without authority — intern-scaled</td><td>7</td></tr>
</table>

<div class="ok">
  <strong>Set 2 rule:</strong> New stories where possible — SMSRF/NSGA-II, Web Wonders/Echelon, semester load, professor feedback — not only the LogiFlow recall STAR from Set 1.
</div>
""",
)


MOCK7 = wrap(
    "Mock 7 — Resume roast + situational",
    """
<div class="hero">
  <h1>Mock 7 — Resume roast + situational barrage</h1>
  <p class="meta">GFG GE Intern 2022 managerial · ~40 min pattern compressed to 25 · EID Intern</p>
  <span class="badge">25 min</span>
  <span class="badge">Resume roast</span>
  <span class="badge">Situational</span>
</div>
<div class="src">Source: Managerial round described as “basically resume roasting” + many situational Qs + Why GE?</div>

<table>
  <tr><th>Time</th><th>Block</th></tr>
  <tr><td>0–2</td><td>Intro (≤90s)</td></tr>
  <tr><td>2–10</td><td>Line-by-line resume: LogiFlow → SMSRF → LC → competitions</td></tr>
  <tr><td>10–18</td><td>Situational rapid fire</td></tr>
  <tr><td>18–22</td><td>Why GEHC (use real reasons, not vague brand)</td></tr>
  <tr><td>22–25</td><td>Bengaluru + your Q</td></tr>
</table>

<div class="iv"><strong>INTERVIEWER</strong> Introduce yourself — under 90 seconds.</div>
<div class="you"><strong>YOU SAY</strong><br/>
Kavya Bhatiya, B.Tech AI, SVNIT Surat, CGPA 9.05. Cleared tech. I build measurable systems — LogiFlow Top 106 GSC 2026; multi-objective research with NSGA-II; 470+ LeetCode. Here for EID Intern in Bengaluru.</div>

<div class="iv"><strong>INTERVIEWER</strong> CGPA 9.05 — what does that say about how you work under load?</div>
<div class="you"><strong>YOU SAY</strong><br/>
Consistency over spikes. I plan weekly: academics + project slices + DSA. When GSC collided with semesters I cut project scope instead of letting grades or the core demo slip.</div>

<div class="iv"><strong>INTERVIEWER</strong> SMSRF / NSGA-II on the resume — one minute, no jargon dump.</div>
<div class="you"><strong>YOU SAY</strong><br/>
Multi-objective recommender research — optimising conflicting goals (e.g. novelty vs serenity) with NSGA-II. Reported gains vs a baseline on MovieLens. Habit: when goals conflict, measure trade-offs explicitly — same habit as LogiFlow’s four objectives.</div>

<div class="iv"><strong>INTERVIEWER</strong> Teammate misses a deadline two days before a demo. What do you do?</div>
<div class="you"><strong>YOU SAY</strong><br/>
Check blockers without blame → re-scope their slice to a minimum → take a parallel critical path if I can → tell the team early what’s at risk. Never surprise the demo with silence.</div>

<div class="iv"><strong>INTERVIEWER</strong> Senior asks for a feature that would break your metric honesty. Response?</div>
<div class="you"><strong>YOU SAY</strong><br/>
Explain the failure mode in one sentence + offer a safer alternative (flag as experimental / behind a toggle). I won’t ship a number I can’t defend — especially near clinical-adjacent software.</div>

<div class="iv"><strong>INTERVIEWER</strong> Why GE HealthCare — and don’t say “brand.”</div>
<div class="you"><strong>YOU SAY</strong><br/>
Imaging + monitoring + Edison AI layer = software that must earn trust. I want that reliability bar as my first internship. Bengaluru engineering + EID mentorship is the learning environment I chose — not any logo.</div>

<div class="iv"><strong>INTERVIEWER</strong> Relocate? Question?</div>
<div class="you"><strong>YOU SAY</strong><br/>Yes, full Bengaluru. Q: In managerial check-ins, what signal tells you an intern is on track by week 3?</div>
""",
)


MOCK8 = wrap(
    "Mock 8 — HR-leaning + why only GEHC",
    """
<div class="hero">
  <h1>Mock 8 — HR-leaning gate (still post-tech)</h1>
  <p class="meta">GFG Intern 2021 HR + GE Intern 2022 HR · ~15–20 min · own answers not internet scripts</p>
  <span class="badge">20 min</span>
  <span class="badge">Why only GEHC</span>
  <span class="badge">Internship help you?</span>
</div>
<div class="src">Tips from selected Intern 2021: give your own answers — don’t paste standard internet HR lines.</div>

<div class="iv"><strong>INTERVIEWER</strong> Tell me about yourself — person, not only resume.</div>
<div class="you"><strong>YOU SAY</strong><br/>
From Vadodara; AI at SVNIT. I like building things I can measure. Outside class: DSA, campus finals (Web Wonders, Echelon). Cleared tech; excited for EID Intern.</div>

<div class="iv"><strong>INTERVIEWER</strong> Why healthcare instead of a service or pure product company?</div>
<div class="you"><strong>YOU SAY</strong><br/>
Service/product often optimises delivery speed or engagement. Healthcare raises the cost of being wrong. I want to learn that bar early — LogiFlow already pushed me toward honest risk metrics.</div>

<div class="iv"><strong>INTERVIEWER</strong> In healthcare — why only GE HealthCare?</div>
<div class="src">GFG Intern 2021 — explicit “why only GE Healthcare?”</div>
<div class="you"><strong>YOU SAY</strong><br/>
Because of the stack I want to grow in: devices plus Edison AI/analytics, Bengaluru engineering depth, and an EID path with real mentorship. I’m not applying “healthcare anywhere” — this is the specific engineering culture I researched.</div>

<div class="iv"><strong>INTERVIEWER</strong> What do you know about GE / GE HealthCare?</div>
<div class="you"><strong>YOU SAY</strong><br/>
GE HealthCare is standalone med-tech. Imaging (MRI, CT, ultrasound, X-ray), patient monitoring, software/AI (Edison). Roots tie to Edison’s industrial legacy — I won’t invent founder trivia beyond what’s solid. Customers: hospitals and clinicians.</div>

<div class="iv"><strong>INTERVIEWER</strong> How will this internship help you?</div>
<div class="src">GE Intern 2022 HR</div>
<div class="you"><strong>YOU SAY</strong><br/>
Code review on a live backlog, healthcare quality habits, and working with seniors who’ve shipped regulated software. I’ll contribute ownership; I’ll leave with sharper engineering judgment.</div>

<div class="iv"><strong>INTERVIEWER</strong> Challenge in a project — how did you overcome it?</div>
<div class="you"><strong>YOU SAY</strong><br/>
GSC + academics: early over-scope. Cut to core ranking + delay-risk; time-boxed polish. Landed Top 106. Fix was prioritisation, not working longer blindly.</div>

<div class="iv"><strong>INTERVIEWER</strong> Any questions? (roles flexibility / tech stack OK)</div>
<div class="you"><strong>YOU SAY</strong><br/>
How flexible is intern staffing across teams if skills fit? What languages/stacks do EID interns commonly touch in the first month?</div>
""",
)


MOCK9 = wrap(
    "Mock 9 — Expectations + medical interest",
    """
<div class="hero">
  <h1>Mock 9 — Expectations + medical-field interest</h1>
  <p class="meta">GFG GEHC On-Campus IIT BHU HR pattern · “put your views forward clearly”</p>
  <span class="badge">20 min</span>
  <span class="badge">Expect from intern?</span>
  <span class="badge">Health problems ideas</span>
</div>

<div class="iv"><strong>INTERVIEWER</strong> Tell me about yourself. Hobbies?</div>
<div class="you"><strong>YOU SAY</strong><br/>
Kavya, AI at SVNIT, CGPA 9.05. LogiFlow Top 106. Hobbies: DSA practice, campus competitions, reading healthcare-tech explainers — short.</div>

<div class="iv"><strong>INTERVIEWER</strong> What are you expecting from this internship?</div>
<div class="src">IIT BHU HR — CONFIRMED theme</div>
<div class="you"><strong>YOU SAY</strong><br/>
A real ticket on a backlog, weekly feedback, and the chance to ship a tested slice. I expect to be useful by week 3–4, not only “learning by watching.” Mentorship + ownership.</div>

<div class="iv"><strong>INTERVIEWER</strong> Are you interested in the medical field — or only coding?</div>
<div class="you"><strong>YOU SAY</strong><br/>
I’m an engineer first — but I’m drawn to medical tech because the users are clinicians and patients. I don’t claim clinical training; I claim respect for reliability and clear communication of uncertainty (same as our delay-risk as advisory, not verdict).</div>

<div class="iv"><strong>INTERVIEWER</strong> What more instruments or machines / software could help health problems?</div>
<div class="src">IIT BHU — wanted to see genuine interest, not memorised product list</div>
<div class="you"><strong>YOU SAY</strong><br/>
Stay humble and concrete: better workflow software that reduces missed follow-ups; decision-support that surfaces risk without replacing the clinician; monitoring alerts that cut false alarms so nurses don’t ignore them.
I care about false negatives and alert fatigue — that’s an engineering problem I already felt on delay recall vs accuracy.</div>

<div class="iv"><strong>INTERVIEWER</strong> Prefer building devices or software?</div>
<div class="you"><strong>YOU SAY</strong><br/>
Software — backends, data pipelines, ML in systems. Devices matter; my skill path is the software layer that makes device data trustworthy.</div>

<div class="iv"><strong>INTERVIEWER</strong> Bengaluru? Questions?</div>
<div class="you"><strong>YOU SAY</strong><br/>Yes. Q: How do interns get exposure to the clinical/context side without being clinicians?</div>
""",
)


MOCK10 = wrap(
    "Mock 10 — SVNIT HR kill-shot pack",
    """
<div class="hero">
  <h1>Mock 10 — SVNIT HR kill-shot pack</h1>
  <p class="meta">GFG SVNIT Aug 2024 · cleared tech · rejected at HR on products / competitors / relocate</p>
  <span class="badge">15–20 min</span>
  <span class="badge">Must not fail</span>
  <span class="badge">Cold answers</span>
</div>
<div class="warn">This mock is non-negotiable. Tech clear ≠ offer. Drill until answers are automatic.</div>

<div class="iv"><strong>INTERVIEWER</strong> Name GE HealthCare products you know.</div>
<div class="you"><strong>YOU SAY</strong><br/>
Imaging: MRI, CT, ultrasound, X-ray. Patient monitoring. Software/AI layer — Edison — analytics on device data. I’m not inventing model numbers or SKUs.</div>

<div class="iv"><strong>INTERVIEWER</strong> Competitors?</div>
<div class="you"><strong>YOU SAY</strong><br/>
At a high level: Siemens Healthineers and Philips in imaging/monitoring. I chose GEHC for Edison/EID and the engineering path I want — not because I claim a full market analysis.</div>

<div class="iv"><strong>INTERVIEWER</strong> Willing to relocate to Bengaluru for the full duration?</div>
<div class="you"><strong>YOU SAY</strong><br/>
Yes — on-site Bengaluru, full internship, no constraints. Family is aligned. No-shows aren’t an option.</div>

<div class="iv"><strong>INTERVIEWER</strong> Any hesitation — hostel, family, exams?</div>
<div class="you"><strong>YOU SAY</strong><br/>
I’ve planned around the internship dates. Academics won’t block attendance. If something extreme happened I’d communicate early — but I’m committing fully now.</div>

<div class="iv"><strong>INTERVIEWER</strong> Why should we take you over someone with a similar CGPA?</div>
<div class="you"><strong>YOU SAY</strong><br/>
Ownership with honest metrics — Top 106 LogiFlow, clear “I” contribution, and I’ve prepared company basics so HR isn’t a surprise after tech.</div>

<div class="iv"><strong>INTERVIEWER</strong> Other offers?</div>
<div class="you"><strong>YOU SAY</strong><br/>
Be factual. If none: “No competing offer I’m weighing; GE HealthCare EID is my priority.” Never invent offers.</div>

<div class="score">Pass = products + competitors + relocate in &lt;45s each, calm tone. Fail = “I’ll check with family” · blank on Siemens/Philips · inventing CT model names.</div>
""",
)


MOCK11 = wrap(
    "Mock 11 — Semester pressure + proof adjectives",
    """
<div class="hero">
  <h1>Mock 11 — Semester challenges + prove every adjective</h1>
  <p class="meta">PCON EID 2024 · FTE HR “good at teamwork — give example” · SVNIT challenge STAR</p>
  <span class="badge">20 min</span>
  <span class="badge">Proof required</span>
</div>

<div class="iv"><strong>INTERVIEWER</strong> Strength — and why do you say that?</div>
<div class="you"><strong>YOU SAY</strong><br/>
Ownership under deadlines. Proof: GSC — I owned delay-risk + pipelines and pushed recall/ROC-AUC when accuracy looked nicer so the team’s story was defendable. Top 106.</div>

<div class="iv"><strong>INTERVIEWER</strong> Weakness — with a fix, not a humblebrag.</div>
<div class="you"><strong>YOU SAY</strong><br/>
Over-scoping early. Fix: force a thin slice + time-box. Still watch myself when a shiny feature appears.</div>

<div class="iv"><strong>INTERVIEWER</strong> Challenge during college semesters?</div>
<div class="src">PCON EID Intern 2024 HR</div>
<div class="you"><strong>YOU SAY</strong><br/>
Balancing GSC build with coursework and DSA. Hard part was energy, not intelligence. System: calendar blocks, cut project scope, protect sleep before exams. Grades held (9.05) and project shipped.</div>

<div class="iv"><strong>INTERVIEWER</strong> You’re good at teamwork — prove it.</div>
<div class="src">GFG FTE EEDP HR — adjective needs example</div>
<div class="you"><strong>YOU SAY</strong><br/>
Clear interfaces + no fake metrics. Example: disagreement on UI vs metrics — I didn’t override; I showed the confusion matrix and we aligned. Teammates could trust the demo narrative.</div>

<div class="iv"><strong>INTERVIEWER</strong> Tell me about Web Wonders / Echelon — what did you actually do?</div>
<div class="you"><strong>YOU SAY</strong><br/>
Keep truthful to resume: finalist-level campus competitions — prep under time pressure, ship a working demo, take jury feedback. Transferable: calm under timed evaluation, same as interview day.</div>

<div class="iv"><strong>INTERVIEWER</strong> How do you handle a teammate who is underperforming?</div>
<div class="src">AmbitionBox PM theme — scaled to intern/peer</div>
<div class="you"><strong>YOU SAY</strong><br/>
Private check-in first (blocker vs skill vs load) → offer a smaller clear task → escalate early if demo risk rises. Don’t gossip; don’t carry silently until failure.</div>

<div class="iv"><strong>INTERVIEWER</strong> Bengaluru? One question.</div>
<div class="you"><strong>YOU SAY</strong><br/>Yes. Q: How do you want interns to flag when they’re stuck — same day or in standup only?</div>
""",
)


MOCK12 = wrap(
    "Mock 12 — Curveballs + close",
    """
<div class="hero">
  <h1>Mock 12 — Curveballs + clean close</h1>
  <p class="meta">Odd one-offs from scrapes · stay humble · 15–20 min</p>
  <span class="badge">20 min</span>
  <span class="badge">Curveballs</span>
  <span class="badge">Day-before</span>
</div>

<div class="iv"><strong>INTERVIEWER</strong> If I call one of your professors or a project mentor — what would they say about you?</div>
<div class="src">Adapted from GFG “ex-employer feedback” HR probe</div>
<div class="you"><strong>YOU SAY</strong><br/>
That I deliver what I promise, ask precise questions, and don’t hide bad news. They’d also say I can over-invest in polish — I’ve been fixing that with time-boxes.</div>

<div class="iv"><strong>INTERVIEWER</strong> What changes should GE HealthCare incorporate?</div>
<div class="src">GFG PPO HR one-off — dangerous if arrogant</div>
<div class="you"><strong>YOU SAY</strong><br/>
As an outsider I won’t prescribe. I’d ask what slows new-intern onboarding and help there. Curiosity beats criticism.</div>

<div class="iv"><strong>INTERVIEWER</strong> Where do you see yourself in 5 years?</div>
<div class="you"><strong>YOU SAY</strong><br/>
A strong backend/applied-ML engineer who owns reliability-critical components in healthcare software. Prefer compounding here if I earn it — not hopping for titles.</div>

<div class="iv"><strong>INTERVIEWER</strong> Will you pursue a master’s next year?</div>
<div class="you"><strong>YOU SAY</strong><br/>
Near term: industry. This internship isn’t a placeholder. Master’s later only if a specific problem needs research depth.</div>

<div class="iv"><strong>INTERVIEWER</strong> Online/hybrid classes — how did you stay disciplined?</div>
<div class="src">GFG Intern 2021 HR asked about online education</div>
<div class="you"><strong>YOU SAY</strong><br/>
Fixed schedule, camera-on when required, weekly goals for DSA + projects. Treat remote like on-site — same for a Bengaluru internship day.</div>

<div class="iv"><strong>INTERVIEWER</strong> Sell me on hiring you in 45 seconds.</div>
<div class="you"><strong>YOU SAY</strong><br/>
I ship and measure. LogiFlow Top 106 with honest metrics I can defend. I’ve prepared GEHC basics so I’m ready for PM and HR. Bengaluru full yes. I’ll take feedback and make the team’s life easier, not harder.</div>

<div class="iv"><strong>INTERVIEWER</strong> Questions?</div>
<div class="you"><strong>YOU SAY</strong><br/>
What does a strong EID intern look like in week 2 vs week 6?</div>

<div class="ok">After Mock 12: stop inventing new stories. Sleep. Morning-of = Set 1 Mock 6 cold run only.</div>
""",
)


def html_to_pdf(html: Path, pdf: Path) -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(html.resolve().as_uri(), wait_until="networkidle")
        page.pdf(
            path=str(pdf),
            format="A4",
            print_background=True,
            margin={"top": "0", "bottom": "0", "left": "0", "right": "0"},
        )
        browser.close()


def main() -> None:
    specs = [
        ("Kavya_GEHC_PM_Set2_Review_Bank.html", "Kavya_GEHC_PM_Set2_Review_Bank.pdf", BANK2),
        ("Kavya_GEHC_Mock7_PM_Resume_Roast.html", "Kavya_GEHC_Mock7_PM_Resume_Roast.pdf", MOCK7),
        ("Kavya_GEHC_Mock8_PM_HR_WhyOnlyGEHC.html", "Kavya_GEHC_Mock8_PM_HR_WhyOnlyGEHC.pdf", MOCK8),
        ("Kavya_GEHC_Mock9_PM_Expectations_Medical.html", "Kavya_GEHC_Mock9_PM_Expectations_Medical.pdf", MOCK9),
        ("Kavya_GEHC_Mock10_PM_HR_Killshot.html", "Kavya_GEHC_Mock10_PM_HR_Killshot.pdf", MOCK10),
        ("Kavya_GEHC_Mock11_PM_Semester_Proof.html", "Kavya_GEHC_Mock11_PM_Semester_Proof.pdf", MOCK11),
        ("Kavya_GEHC_Mock12_PM_Curveballs.html", "Kavya_GEHC_Mock12_PM_Curveballs.pdf", MOCK12),
    ]
    for h, p, body in specs:
        hp, pp = DIR / h, DIR / p
        hp.write_text(body, encoding="utf-8")
        html_to_pdf(hp, pp)
        print(f"Wrote {pp.name}")

    parts = [
        ("Surekha_Sailesh_Findings.pdf", "Surekha Sailesh — EID angle"),
        ("Kavya_GEHC_PM_People_Roster.pdf", "GEHC Bengaluru PM roster"),
        ("Kavya_GEHC_PM_GFG_Managerial_Bank.pdf", "Set 1 GFG bank (EID filter)"),
        ("Kavya_GEHC_Program_Manager_Reviews.pdf", "PM reviews — EID filter"),
        ("Kavya_GEHC_PM_Set2_Review_Bank.pdf", "Set 2 — new review Q bank"),
        ("Kavya_GEHC_Mock1_PM_Personality_Check.pdf", "Mock 1 — Surekha / fit"),
        ("Kavya_GEHC_Mock2_PM_Campus_Filter.pdf", "Mock 2 — campus filter"),
        ("Kavya_GEHC_Mock3_PM_STAR_Pressure.pdf", "Mock 3 — STAR pressure"),
        ("Kavya_GEHC_Mock4_PM_Layman_GEHC.pdf", "Mock 4 — layman + GEHC"),
        ("Kavya_GEHC_Mock5_PM_Interrupt_Probe.pdf", "Mock 5 — interrupt & probe"),
        ("Kavya_GEHC_Mock6_PM_DayOf_Cold.pdf", "Mock 6 — day-of cold"),
        ("Kavya_GEHC_Mock7_PM_Resume_Roast.pdf", "Mock 7 — resume roast"),
        ("Kavya_GEHC_Mock8_PM_HR_WhyOnlyGEHC.pdf", "Mock 8 — why only GEHC"),
        ("Kavya_GEHC_Mock9_PM_Expectations_Medical.pdf", "Mock 9 — expectations + medical"),
        ("Kavya_GEHC_Mock10_PM_HR_Killshot.pdf", "Mock 10 — products/competitors/relocate"),
        ("Kavya_GEHC_Mock11_PM_Semester_Proof.pdf", "Mock 11 — semester + proof"),
        ("Kavya_GEHC_Mock12_PM_Curveballs.pdf", "Mock 12 — curveballs"),
    ]
    for p, _ in parts:
        if not (DIR / p).exists():
            raise SystemExit(f"Missing {p}")

    rows = "".join(
        f"<tr><td>{i}</td><td>{label}</td><td>{PdfReader(str(DIR/p)).get_num_pages()} pp</td></tr>"
        for i, (p, label) in enumerate(parts, 1)
    )
    cover = DIR / "_pm_master_cover.html"
    cover.write_text(
        f"""<!DOCTYPE html><html><head><meta charset="utf-8"/><style>
@page {{ size: A4; margin: 15mm; }}
body {{ font-family: Segoe UI, Helvetica, Arial, sans-serif; color:#1f2937; font-size:10pt; }}
.hero {{ background:linear-gradient(135deg,#0b4f6c,#147a9b); color:#fff; padding:20px; border-radius:12px; margin-bottom:14px; }}
h1 {{ margin:0 0 4px; font-size:19pt; }}
.badge {{ display:inline-block; background:rgba(255,255,255,.18); padding:3px 9px; border-radius:999px; font-size:8pt; font-weight:700; margin:2px 3px 0 0; }}
table {{ width:100%; border-collapse:collapse; font-size:8.8pt; }}
th,td {{ border:1px solid #d1d5db; padding:5px 7px; text-align:left; }}
th {{ background:#0b4f6c; color:#fff; }}
.ok {{ margin-top:10px; background:#ecfdf5; border-left:4px solid #059669; padding:9px 11px; border-radius:0 8px 8px 0; font-size:9pt; }}
.warn {{ margin-top:8px; background:#fff7ed; border-left:4px solid #ea580c; padding:9px 11px; border-radius:0 8px 8px 0; font-size:9pt; }}
</style></head><body>
<div class="hero">
  <h1>Kavya · GEHC EID Intern · PM Master Pack</h1>
  <p style="opacity:.92;margin:0 0 8px">Set 1 (Mocks 1–6) + Set 2 new reviews (Mocks 7–12)</p>
  <span class="badge">12 mocks</span>
  <span class="badge">EID Intern</span>
  <span class="badge">PM + HR gate</span>
  <span class="badge">Not PPO USP</span>
</div>
<table><tr><th>#</th><th>Section</th><th>Pages</th></tr>{rows}</table>
<div class="ok"><strong>After Set 1 done:</strong> run Set 2 in order 7→12. Morning-of: Mock 6 only. Prioritise Mock 10 (SVNIT HR kill-shot) before Saturday.</div>
<div class="warn">Skip PPO “project you’re on / USP for the organisation.”</div>
</body></html>""",
        encoding="utf-8",
    )
    cover_pdf = DIR / "_pm_master_cover.pdf"
    html_to_pdf(cover, cover_pdf)
    w = PdfWriter()
    for page in PdfReader(str(cover_pdf)).pages:
        w.add_page(page)
    for name, _ in parts:
        for page in PdfReader(str(DIR / name)).pages:
            w.add_page(page)
    out = DIR / "Kavya_GEHC_PM_Master_Pack.pdf"
    with out.open("wb") as f:
        w.write(f)
    cover.unlink(missing_ok=True)
    cover_pdf.unlink(missing_ok=True)
    print(f"Merged {out.name}: {len(PdfReader(str(out)).pages)} pages, {out.stat().st_size:,} bytes")


if __name__ == "__main__":
    main()
