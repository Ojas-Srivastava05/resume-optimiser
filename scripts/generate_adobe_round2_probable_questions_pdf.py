#!/usr/bin/env python3
"""Generate probable Adobe Round 2 Brand Visibility case study questions PDF."""

from pathlib import Path

from fpdf import FPDF

OUT = (
    Path(__file__).resolve().parents[1]
    / "Adobe University Hackathon 2026"
    / "Adobe_Round2_Probable_Questions.pdf"
)


class Doc(FPDF):
    def footer(self):
        self.set_y(-12)
        self.set_font("Helvetica", "", 8)
        self.set_text_color(100, 100, 100)
        self.cell(
            0,
            8,
            "Adobe University Hackathon 2026  |  Probable Round 2 Questions  |  Practice Only",
            align="C",
        )


def sx(pdf: FPDF):
    pdf.set_x(pdf.l_margin)


def h1(pdf: FPDF, text: str):
    sx(pdf)
    pdf.set_font("Helvetica", "B", 15)
    pdf.set_text_color(20, 20, 20)
    pdf.multi_cell(0, 8, text, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)


def h2(pdf: FPDF, text: str):
    pdf.ln(3)
    sx(pdf)
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(30, 30, 30)
    pdf.multi_cell(0, 6.5, text, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)


def h3(pdf: FPDF, text: str):
    pdf.ln(2)
    sx(pdf)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(35, 35, 35)
    pdf.multi_cell(0, 5.5, text, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(0.5)


def meta(pdf: FPDF, text: str):
    sx(pdf)
    pdf.set_font("Helvetica", "I", 9)
    pdf.set_text_color(80, 80, 80)
    pdf.multi_cell(0, 5, text, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)


def para(pdf: FPDF, text: str):
    sx(pdf)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(25, 25, 25)
    pdf.multi_cell(0, 5.4, text, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1.2)


def bullet(pdf: FPDF, text: str, indent: float = 3):
    sx(pdf)
    pdf.set_x(pdf.l_margin + indent)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(25, 25, 25)
    pdf.multi_cell(pdf.epw - indent, 5.3, f"- {text}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(0.3)


def qbox(pdf: FPDF, qnum: str, text: str, hints: list[str] | None = None):
    h3(pdf, qnum)
    para(pdf, text)
    if hints:
        sx(pdf)
        pdf.set_font("Helvetica", "I", 9)
        pdf.set_text_color(90, 90, 90)
        pdf.multi_cell(0, 5, "Think about:", new_x="LMARGIN", new_y="NEXT")
        for h in hints:
            sx(pdf)
            pdf.set_x(pdf.l_margin + 3)
            pdf.set_font("Helvetica", "I", 9)
            pdf.set_text_color(90, 90, 90)
            pdf.multi_cell(pdf.epw - 3, 5, f"- {h}", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(1)


def build():
    pdf = Doc()
    pdf.set_auto_page_break(auto=True, margin=16)
    pdf.add_page()

    h1(pdf, "Adobe University Hackathon 2026")
    sx(pdf)
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(40, 40, 40)
    pdf.multi_cell(
        0,
        6.5,
        "Round 2 Practice Pack: Probable Case Study Questions",
        new_x="LMARGIN",
        new_y="NEXT",
    )
    pdf.ln(1)
    meta(
        pdf,
        "Theme: Speak to Agents - The New Language of Brand Visibility\n"
        "Format mirror: 45 minutes, one sitting, one attempt  |  Practice only (not official)\n"
        "Use this under a timer. Draft answers like the real round: analysis + strategy + actions.",
    )

    # -------- CASE A --------
    h2(pdf, "CASE A  |  AuraWear (DTC Apparel) loses AI recommendations")
    para(
        pdf,
        "AuraWear is a mid-size Indian D2C apparel brand. Classic SEO is fine: many category "
        "pages rank on page 1 for 'organic cotton tees', 'workwear shirts women', etc. Monthly "
        "organic sessions are stable.",
    )
    para(
        pdf,
        "But when shoppers ask AI assistants things like 'best sustainable everyday wear brands "
        "in India under 2000 INR' or 'good formal shirts for college placements', ChatGPT / "
        "Perplexity / Gemini often recommend 3-4 competitors and never mention AuraWear. When "
        "AuraWear does appear, the answer misstates pricing and calls it a 'premium luxury' brand.",
    )
    para(pdf, "Internal notes from the growth team:")
    for b in [
        "robots.txt blocks several AI crawlers; CDN returns 403 to unknown bots on /collections/*.",
        "Product pages are heavily client-rendered (JS). Key specs sit behind tabs.",
        "Blog last major refresh: 11 months ago. Few FAQ blocks in natural Q&A form.",
        "Wikipedia page is a stub. Reddit / Quora mentions are rare vs Competitor NovaKnit.",
        "Sample prompt board (20 prompts): AuraWear mention rate 15%, citation rate 5%, "
        "avg sentiment mixed/negative on price. NovaKnit mention rate 60%, citation 35%.",
        "Analytics shows almost no agentic bot hits on PDP URLs; a few hits on old blog posts.",
    ]:
        bullet(pdf, b)

    qbox(
        pdf,
        "Q1. Diagnose (8-10 min)",
        "What are the top 3 reasons AuraWear is invisible or misrepresented in AI-generated "
        "answers despite decent SEO? Separate technical, content, and offsite/earned-media causes.",
        [
            "SEO vs GEO differences",
            "crawlability / JS / freshness",
            "third-party mention gaps and wrong brand narrative",
        ],
    )
    qbox(
        pdf,
        "Q2. Metrics (6-8 min)",
        "Design a simple measurement plan for the next 8 weeks. Which metrics would you track "
        "across AI platforms, how often, and how would you know if the brand is actually winning "
        "visibility (not just traffic)?",
        [
            "mentions, citations, sentiment, position, share of voice",
            "agentic traffic vs referral / zero-click",
            "prompt clusters, not vanity homepage hits",
        ],
    )
    qbox(
        pdf,
        "Q3. Strategy (10-12 min)",
        "Propose a prioritized 30-day action plan (quick wins vs deeper work) for onsite and "
        "offsite GEO. Be specific. Tie each action to the diagnosis in Q1.",
        [
            "robots/CDN, FAQs, content refresh",
            "Wikipedia / reviews / PR / community mentions",
            "what NOT to do first",
        ],
    )
    qbox(
        pdf,
        "Q4. Product / agent angle (8-10 min)",
        "Imagine AuraWear's growth lead wants an 'agent-era brand visibility' workflow (monitor "
        "prompts -> find gaps -> fix content -> prove impact). Outline the workflow and what a "
        "tool like Adobe Brand Visibility (or a student-built agent) should automate vs leave to humans.",
        [
            "prompt library + competitor bench",
            "opportunities queue + deploy/rollback thinking",
            "how you'd prove ROI to leadership",
        ],
    )

    # -------- CASE B --------
    pdf.add_page()
    h2(pdf, "CASE B  |  FinClear (fintech) - trust, YMYL, and wrong AI answers")
    para(
        pdf,
        "FinClear offers a student credit-builder card and a basic savings vault in India. "
        "Compliance is strict. The website ranks okay for branded queries, but AI answers often:",
    )
    for b in [
        "Confuse FinClear with a failed 2022 neo-bank with a similar name.",
        "Quote outdated fees from an old Moneycontrol article.",
        "Skip FinClear entirely for 'best student credit builder India 2026'.",
        "Cite a Reddit thread where an angry user alleged 'hidden charges' (later resolved).",
    ]:
        bullet(pdf, b)
    para(
        pdf,
        "Legal will not approve aggressive marketing claims. Product pages exist but are dense "
        "and legalistic. Help Center is good but buried. Competitor PulseCard dominates AI answers "
        "via review-site roundups and a strong Wikipedia page.",
    )

    qbox(
        pdf,
        "Q1.",
        "In a YMYL (Your Money or Your Life) category, why can negative or outdated third-party "
        "content hurt FinClear more in LLM answers than in classic Google search? What does that "
        "imply for brand safety in the agent era?",
    )
    qbox(
        pdf,
        "Q2.",
        "List the highest-leverage offsite and onsite fixes FinClear should pursue in order. "
        "Explain what 'authoritative, neutral, updatable' content means for AI citations.",
    )
    qbox(
        pdf,
        "Q3.",
        "Propose 5 prompt clusters FinClear should monitor weekly (example format: intent + sample "
        "prompt). For each, say what 'winning' looks like (mention only vs preferred recommendation "
        "vs accurate fee citation).",
    )
    qbox(
        pdf,
        "Q4.",
        "Leadership asks: 'If AI answers reduce clicks (zero-click), why invest in GEO at all?' "
        "Write a concise business case linking visibility, trust, and downstream conversion "
        "for a fintech brand.",
    )

    # -------- CASE C --------
    h2(pdf, "CASE C  |  Quick prompts bank (speed drill)")
    para(
        pdf,
        "Answer any 3 in 15 minutes total. Keep each answer under 160 words. Bottom line first.",
    )
    drills = [
        "A brand blocks GPTBot 'for security'. Traffic from ChatGPT referrals is near zero and "
        "mentions are falling. Do you unblock? What safeguards would you add?",
        "Competitor is cited more because of one evergreen 'best of' listicle from 2024. Your "
        "product changed. What is your 2-week counter-plan?",
        "Agentic traffic hits /blog/old-guide.html but never PDPs. What does that tell you, and "
        "what would you change on-site?",
        "Mention rate is high but sentiment is negative on price. Is that a GEO win? What would "
        "you optimize next?",
        "You can only ship one thing this sprint: schema+FAQ on top 10 URLs, OR a PR push for "
        "3 review sites. Pick one and defend it for a fashion D2C brand.",
        "Explain SEO vs GEO to a non-technical founder in 6 bullets without jargon overload.",
        "Design a 'prompt war room' for a 3-person student team building a hackathon prototype "
        "around brand visibility agents. What screens/features are must-have for Round 3/4?",
    ]
    for i, d in enumerate(drills, 1):
        h3(pdf, f"Drill {i}")
        para(pdf, d)

    # -------- CASE D --------
    pdf.add_page()
    h2(pdf, "CASE D  |  Full mock paper (closest to real format)")
    meta(
        pdf,
        "Timebox: 45:00  |  Suggested split: read 5 | Q1 10 | Q2 8 | Q3 12 | Q4 8 | buffer 2\n"
        "Do not use the internet. Write as if this is the Unstop attempt.",
    )
    para(
        pdf,
        "NovaHost is a cloud hosting company targeting Indian startups. SEO is strong for "
        "'cheap VPS India' and docs are solid. In AI assistants, NovaHost appears in ~25% of "
        "relevant prompts, but usually in position 3-4 with neutral-to-weak sentiment "
        "('okay for beginners'). Competitor OrbitCloud appears first with phrases like "
        "'best developer experience' and gets cited from GitHub READMEs, Hashnode posts, and "
        "a popular comparison table.",
    )
    para(pdf, "Data snapshot (last 30 days, 50 tracked prompts across ChatGPT + Perplexity + Gemini):")
    for b in [
        "NovaHost: mention 25%, citation 8%, avg position 3.4, sentiment 0.1 (near neutral)",
        "OrbitCloud: mention 70%, citation 42%, avg position 1.6, sentiment 0.6",
        "Agentic bot success rate on NovaHost docs: 61% (many 404s on old /v1/ API paths)",
        "Top losing prompt cluster: 'best hosting for student hackathon projects India'",
        "Top winning prompt cluster (rare): 'NovaHost pricing' (branded)",
    ]:
        bullet(pdf, b)

    qbox(
        pdf,
        "Question 1",
        "Analyse NovaHost's brand visibility problem. What does the data imply about discovery, "
        "authority, and technical readiness for AI agents?",
    )
    qbox(
        pdf,
        "Question 2",
        "Recommend a strategy to improve NovaHost's presence specifically for the losing "
        "hackathon/student prompt cluster within 4 weeks. Include onsite and offsite moves.",
    )
    qbox(
        pdf,
        "Question 3",
        "Which 4 metrics would you put on an executive dashboard, and what decision would each "
        "metric drive? Avoid vanity metrics.",
    )
    qbox(
        pdf,
        "Question 4",
        "Propose a lightweight 'Speak to Agents' solution idea (feature set + user flow) that "
        "helps brands like NovaHost monitor and improve AI answer visibility. Keep it realistic "
        "for a student hackathon build.",
    )

    # -------- Answer frame --------
    h2(pdf, "Answer frame (use on every question)")
    for b in [
        "1) One-line bottom line",
        "2) 2-3 causes tied to case facts",
        "3) Prioritized actions (quick vs later)",
        "4) How you measure success",
        "5) Optional one-line Adobe/agent angle",
    ]:
        bullet(pdf, b)
    para(
        pdf,
        "Judging lens from Unstop: analytical thinking, strategic approach, actionable insights. "
        "Sound like a sharp student analyst - specific, not buzzwordy.",
    )
    meta(
        pdf,
        "Disclaimer: Unofficial practice set inferred from the public theme and Adobe Brand "
        "Visibility / GEO materials. Official Round 2 content may differ.",
    )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(OUT)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    build()
