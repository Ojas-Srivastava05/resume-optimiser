#!/usr/bin/env python3
"""Generate Adobe University Hackathon 2026 Round 2 Case Study prep PDF."""

from pathlib import Path

from fpdf import FPDF

OUT = (
    Path(__file__).resolve().parents[1]
    / "Adobe University Hackathon 2026"
    / "Adobe_Round2_Brand_Visibility_Case_Study_Prep.pdf"
)


class Brief(FPDF):
    def footer(self):
        self.set_y(-12)
        self.set_font("Helvetica", "", 8)
        self.set_text_color(100, 100, 100)
        self.cell(
            0,
            8,
            "Adobe University Hackathon 2026  |  Round 2 Prep  |  Ojas Srivastava",
            align="C",
        )


def h1(pdf: FPDF, text: str):
    pdf.set_x(pdf.l_margin)
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(20, 20, 20)
    pdf.multi_cell(0, 8, text, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)


def h2(pdf: FPDF, text: str):
    pdf.ln(3)
    pdf.set_x(pdf.l_margin)
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(30, 30, 30)
    pdf.multi_cell(0, 7, text, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)


def h3(pdf: FPDF, text: str):
    pdf.ln(2)
    pdf.set_x(pdf.l_margin)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(40, 40, 40)
    pdf.multi_cell(0, 6, text, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(0.5)


def meta(pdf: FPDF, text: str):
    pdf.set_x(pdf.l_margin)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(80, 80, 80)
    pdf.multi_cell(0, 5, text, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)


def para(pdf: FPDF, text: str):
    pdf.set_x(pdf.l_margin)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(25, 25, 25)
    pdf.multi_cell(0, 5.5, text, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1.5)


def bullet(pdf: FPDF, text: str, indent: float = 4):
    pdf.set_x(pdf.l_margin + indent)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(25, 25, 25)
    pdf.multi_cell(pdf.epw - indent, 5.5, f"- {text}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(0.4)


def note(pdf: FPDF, text: str):
    pdf.set_x(pdf.l_margin)
    pdf.set_font("Helvetica", "I", 9)
    pdf.set_text_color(70, 70, 70)
    pdf.multi_cell(0, 5, text, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)


def table_row(pdf: FPDF, left: str, right: str, bold_left: bool = False):
    pdf.set_x(pdf.l_margin)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(25, 25, 25)
    label = f"{left}: "
    # Measure label width then print label + value on one wrapped block
    label_w = pdf.get_string_width(label) + 1
    y = pdf.get_y()
    pdf.cell(label_w, 5.5, label)
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(pdf.epw - label_w, 5.5, right, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(0.6)


def build():
    pdf = Brief()
    pdf.set_auto_page_break(auto=True, margin=16)
    pdf.add_page()

    h1(pdf, "Adobe University Hackathon 2026")
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(40, 40, 40)
    pdf.set_x(pdf.l_margin)
    pdf.multi_cell(0, 7, "Round 2 Prep: Case Study on Brand Visibility", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)
    meta(
        pdf,
        "Theme: Speak to Agents - The New Language of Brand Visibility\n"
        "Source: Unstop listing + Adobe Brand Visibility product docs  |  Prep date: 15 Aug 2026\n"
        "Unstop: https://unstop.com/hackathons/crp-adobe-university-hackathon-2026-adobe-1715333",
    )

    note(
        pdf,
        "Exact Round 2 questions are not public yet. This brief consolidates confirmed format "
        "details and high-probability content based on the official theme and Adobe Brand Visibility (GEO).",
    )

    # --- Section 1 ---
    h2(pdf, "1. What Round 2 Officially Is")
    for left, right in [
        ("Name", "Round 2 - Case Study on Brand Visibility"),
        ("Date", "16 August 2026"),
        ("Who", "Shortlisted participants from Round 1 (Online Assessment)"),
        ("Format", "Analyse a real-world brand visibility scenario + answer questions"),
        ("Time", "45 minutes, one sitting (timer expires = done)"),
        ("Attempts", "One only"),
        ("Judged on", "Analytical thinking, strategic approach, actionable insights"),
    ]:
        table_row(pdf, left, right, bold_left=True)

    para(
        pdf,
        "Note on numbering: Older Internshala/LinkedIn posts call Development Round 2. "
        "On the live Unstop page, Round 2 is the case study; Development is Round 3.",
    )

    # --- Section 2 ---
    h2(pdf, "2. What Will Almost Certainly Be Inside")
    para(
        pdf,
        "Adobe recently launched Adobe Brand Visibility (GEO / AI-search visibility). "
        "The case will almost certainly sit in that product world - not generic marketing fluff.",
    )
    h3(pdf, "Expected scenario shape")
    para(
        pdf,
        "Brand X is strong on Google SEO but weak, invisible, or misrepresented when users ask "
        "ChatGPT, Perplexity, Gemini, Copilot, or Google AI Mode questions like "
        "'best CRM for startups' or 'best travel insurance'. Competitors get recommended. "
        "Your job: diagnose and fix visibility in the agent era.",
    )
    para(
        pdf,
        "You will likely get a short brief (maybe fake metrics, competitor table, or sample prompts) "
        "plus open-ended written questions.",
    )

    h3(pdf, "Likely question themes (~4 questions)")
    themes = [
        (
            "1. Diagnose the problem",
            "Why is the brand invisible or wrongly described in AI answers? SEO vs GEO gaps, "
            "crawl blocks, stale content, weak third-party mentions, JS-heavy pages AI cannot read.",
        ),
        (
            "2. Metrics and analysis",
            "What would you measure? Mentions, citations, sentiment, position in the answer, "
            "visibility score, share of voice vs competitors, agentic traffic, referral traffic from AI.",
        ),
        (
            "3. Strategy / recommendations",
            "Onsite: robots/CDN for AI bots, natural-language FAQs, structured content, freshness. "
            "Offsite: Wikipedia, Reddit/Quora, PR, reviews, YouTube. Prioritize: Analyze -> Plan -> Act -> Adapt.",
        ),
        (
            "4. Product / tech angle (Adobe-flavored)",
            "How would you use Brand Visibility / agents to monitor prompts, close citation gaps, "
            "deploy fixes fast, prove ROI in analytics - or how a tool/agent could help marketers "
            "speak to agents.",
        ),
    ]
    for title, body in themes:
        pdf.set_x(pdf.l_margin)
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(25, 25, 25)
        pdf.multi_cell(0, 5.5, title, new_x="LMARGIN", new_y="NEXT")
        para(pdf, body)

    para(
        pdf,
        "They score structure + insight + concrete actions - not buzzwords.",
    )

    # --- Section 3 ---
    h2(pdf, "3. Concepts to Lock Before 16 Aug")
    para(
        pdf,
        "From Adobe Brand Visibility best practices (Experience League):",
    )
    concepts = [
        "GEO / AEO / AIO = win citations inside AI answers, not only blue-link SEO.",
        "Core metrics: Mentions, Citations, Sentiment, Position -> Visibility score.",
        "Agentic traffic = AI bots crawling your site (often deep pages, not the homepage).",
        "Zero-click = user gets the answer in chat without visiting you; influence is not equal to clicks.",
        "SEO vs LLM: links vs brand mentions; limited JS rendering for agents; freshness + earned media matter more.",
        "Optimization loop: onsite + offsite; Analyze -> Plan -> Act -> Adapt.",
        "Platforms to name: ChatGPT, Perplexity, Gemini, Copilot, Google AI Mode.",
    ]
    for c in concepts:
        bullet(pdf, c)

    h3(pdf, "Read these (official)")
    links = [
        "Unstop hackathon page (format + timelines)",
        "business.adobe.com/products/brand-visibility.html",
        "experienceleague.adobe.com - Brand Visibility best practices",
        "business.adobe.com/blog/introducing-adobe-brand-visibility",
    ]
    for link in links:
        bullet(pdf, link)

    # --- Section 4 ---
    h2(pdf, "4. How to Answer in 45 Minutes")
    para(pdf, "For each question, use this tight frame:")
    steps = [
        "Restate the goal in one line.",
        "List 2-3 root causes.",
        "Give prioritized actions (quick wins vs long-term).",
        "Say how you would measure success.",
        "Add one Adobe / agent angle if it fits.",
    ]
    for i, s in enumerate(steps, 1):
        bullet(pdf, f"{i}. {s}")

    para(
        pdf,
        "Write clear, bullet-friendly paragraphs. Sound like a PM/analyst, not a thesaurus. "
        "Aim for structured answers you can finish under time pressure.",
    )

    # --- Section 5 ---
    h2(pdf, "5. Cheat Sheet: SEO vs LLM / GEO")
    rows = [
        ("SEO", "LLM / GEO"),
        ("Index-based", "Token-based + RAG for freshness"),
        ("Link authority matters", "Brand mentions matter more"),
        ("JS rendering supported", "Very limited client-side JS for agents"),
        ("Win page-one rankings", "Win AI citations and answer presence"),
        ("Traffic via clicks", "Often zero-click influence + agentic crawl"),
    ]
    for left, right in rows:
        table_row(pdf, left, right, bold_left=(left == "SEO"))

    # --- Section 6 ---
    h2(pdf, "6. Onsite vs Offsite Actions (Quick Recall)")
    h3(pdf, "Onsite")
    for item in [
        "Allow AI agents in robots.txt / CDN settings; fix blocked URLs.",
        "Refresh 10-15% of content regularly; use clear H1/H2/H3 structure.",
        "Add conversational FAQs mapped to real user prompts.",
        "Track visibility score, sentiment, citation frequency; iterate.",
    ]:
        bullet(pdf, item)

    h3(pdf, "Offsite")
    for item in [
        "Keep Wikipedia accurate, sourced, and neutral.",
        "Earn mentions via Reddit/Quora, reviews, affiliates, news/PR, YouTube.",
        "Diversify footprint; monitor citations and competitor share of voice.",
        "Coordinate PR + social so third-party sources LLMs trust mention you.",
    ]:
        bullet(pdf, item)

    # --- Section 7 ---
    h2(pdf, "7. Bottom Line")
    para(
        pdf,
        "Nobody online has the real Round 2 paper yet - it goes live for shortlisted people on "
        "16 Aug 2026. What is confirmed: 45-minute, one-shot brand-visibility case under the "
        "Speak to Agents theme, graded on analysis + strategy + actionable insights, tightly "
        "aligned with Adobe Brand Visibility / GEO.",
    )
    para(
        pdf,
        "Prep goal: walk in able to diagnose AI-visibility gaps, pick the right metrics, "
        "propose prioritized onsite/offsite fixes, and sound product-aware about agents and Adobe.",
    )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(OUT)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    build()
