#!/usr/bin/env python3
"""Generate 9 distinct Adobe Round 2 practice case-study PDFs for team distribution."""

from pathlib import Path

from fpdf import FPDF

OUT_DIR = Path(__file__).resolve().parents[1] / "Adobe University Hackathon 2026" / "Team Case Studies"


class Doc(FPDF):
    def __init__(self, short_name: str):
        super().__init__()
        self.short_name = short_name

    def footer(self):
        self.set_y(-12)
        self.set_font("Helvetica", "", 8)
        self.set_text_color(100, 100, 100)
        self.cell(
            0,
            8,
            f"Adobe UH 2026 Round 2 Practice  |  {self.short_name}  |  Unofficial",
            align="C",
        )


def sx(pdf: FPDF):
    pdf.set_x(pdf.l_margin)


def h1(pdf: FPDF, text: str):
    sx(pdf)
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(20, 20, 20)
    pdf.multi_cell(0, 7.5, text, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)


def h2(pdf: FPDF, text: str):
    pdf.ln(2.5)
    sx(pdf)
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(30, 30, 30)
    pdf.multi_cell(0, 6.2, text, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(0.8)


def h3(pdf: FPDF, text: str):
    pdf.ln(1.8)
    sx(pdf)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(35, 35, 35)
    pdf.multi_cell(0, 5.4, text, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(0.4)


def meta(pdf: FPDF, text: str):
    sx(pdf)
    pdf.set_font("Helvetica", "I", 9)
    pdf.set_text_color(80, 80, 80)
    pdf.multi_cell(0, 4.8, text, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1.5)


def para(pdf: FPDF, text: str):
    sx(pdf)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(25, 25, 25)
    pdf.multi_cell(0, 5.2, text, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1.0)


def bullet(pdf: FPDF, text: str, indent: float = 3):
    pdf.set_x(pdf.l_margin + indent)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(25, 25, 25)
    pdf.multi_cell(pdf.epw - indent, 5.1, f"- {text}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(0.25)


def question(pdf: FPDF, n: int, text: str, mins: str):
    h3(pdf, f"Question {n}  ({mins})")
    para(pdf, text)


CASES = [
    {
        "file": "01_LearnOrbit_EdTech.pdf",
        "short": "Case 01 LearnOrbit",
        "title": "Case 01  |  LearnOrbit (EdTech)",
        "subtitle": "Course marketplace invisible in AI study-assistant answers",
        "industry": "EdTech / Online learning",
        "scenario": [
            "LearnOrbit is an Indian online course marketplace (coding, design, aptitude). Google SEO is decent for branded + a few long-tail course pages. Monthly organic traffic is flat, not collapsing.",
            "Students increasingly ask ChatGPT / Gemini / Perplexity: 'best DSA course for placements India', 'affordable UI/UX certificate under 5k', 'how to prepare for product company OA in 8 weeks'. LearnOrbit rarely appears. When it does, AI often confuses it with a discontinued 2021 Udemy clone and quotes wrong course prices.",
            "Competitor SkillForge dominates AI answers via Quora threads, YouTube review roundups, and a well-maintained Wikipedia page.",
        ],
        "facts": [
            "Prompt board (40 prompts): LearnOrbit mention 18%, citation 4%, avg position 3.7, sentiment mixed (price skepticism).",
            "SkillForge mention 65%, citation 38%, avg position 1.5, sentiment positive.",
            "robots.txt allows Googlebot but disallows GPTBot and ClaudeBot 'temporarily'.",
            "Course pages are SPA-heavy; syllabus text loads after JS. Few natural-language FAQs.",
            "Help Center is strong but on a subdomain with weak internal linking.",
            "Agentic traffic mostly hits old /blog/placement-tips-2023.html; almost zero bot hits on live course PDPs.",
            "Top losing cluster: 'placement prep courses India'. Top rare win: branded 'LearnOrbit login' style prompts.",
        ],
        "questions": [
            (
                "8-10 min",
                "Diagnose why LearnOrbit loses AI answer share despite okay SEO. Give exactly 3 root causes spanning technical access, content shape, and offsite authority. Tie each cause to a fact above.",
            ),
            (
                "7-8 min",
                "Build an 8-week measurement plan. Which metrics, on which platforms, and what would count as a real win for the placement-prep prompt cluster (not vanity traffic)?",
            ),
            (
                "10-12 min",
                "Write a prioritized 30-day GEO plan (quick wins vs deeper bets). Be specific about onsite and offsite actions. Call out one thing you would deliberately NOT do first.",
            ),
            (
                "8-10 min",
                "Sketch a 'Speak to Agents' workflow for LearnOrbit's growth team (monitor -> gap -> fix -> prove). What should software/agents automate vs what should humans approve, especially for education claims?",
            ),
        ],
    },
    {
        "file": "02_TrailMuse_Travel.pdf",
        "short": "Case 02 TrailMuse",
        "title": "Case 02  |  TrailMuse (Travel)",
        "subtitle": "Experiential travel brand losing itinerary prompts to OTAs",
        "industry": "Travel / Experiences",
        "scenario": [
            "TrailMuse sells curated weekend treks and heritage city walks in India. Brand SEO is okay for 'meghalaya trek package' style queries. Booking conversions from Google are acceptable in peak season.",
            "Trip planners now ask AI: '7-day north india itinerary for couples under 40k', 'safe solo female trek near Bangalore', 'best operator for spiti circuit'. AI recommends MakeMyTrip-style OTAs or 2 viral Instagram operators. TrailMuse is almost never cited; one answer wrongly says TrailMuse only does Kerala backwaters.",
        ],
        "facts": [
            "Mention rate 12% on experiential prompts; citation 3%. Competitor PeakNomad mention 55%, citation 30%.",
            "CDN WAF challenges unknown bots; many AI crawlers get interstitial blocks on /trips/*.",
            "Itinerary pages are image-heavy carousels; day-wise text is thin. Cancellation policy is a PDF.",
            "No structured FAQ for safety, group size, difficulty grades.",
            "Strong Instagram, weak Wikipedia / review-site footprint. Reddit mentions are sparse and outdated.",
            "Agentic hits concentrate on a 2022 'best monsoon treks' blog, not current trip pages.",
            "Sentiment when mentioned: positive on guides, negative/uncertain on pricing transparency.",
        ],
        "questions": [
            (
                "8-10 min",
                "What makes travel a hard GEO problem (seasonality, safety, trust, zero-click itineraries)? How do those factors show up in TrailMuse's data?",
            ),
            (
                "8-10 min",
                "Propose a content architecture AI agents could actually parse for a trek PDP (sections, FAQs, freshness). Explain why image carousels alone fail.",
            ),
            (
                "10-12 min",
                "Design a competitive response to PeakNomad for the prompt 'safe solo female trek near Bangalore'. Include onsite fixes + offsite earned-media moves in priority order.",
            ),
            (
                "7-8 min",
                "Leadership fears GEO investment won't matter because users get full itineraries in chat (zero-click). Argue for or against investing anyway - with a practical metric that still proves value.",
            ),
        ],
    },
    {
        "file": "03_MediLink_Health.pdf",
        "short": "Case 03 MediLink",
        "title": "Case 03  |  MediLink (Telehealth)",
        "subtitle": "YMYL brand hurt by outdated medical pages in AI answers",
        "industry": "Healthcare / Telemedicine (YMYL)",
        "scenario": [
            "MediLink is a telehealth app for specialist consults in Tier-1/2 India. Compliance is strict. Branded search is healthy. Unbranded SEO for condition pages is mixed.",
            "AI assistants sometimes recommend MediLink, but frequently cite an old blog claiming MediLink 'does not offer psychiatry' (they launched psychiatry 9 months ago). Another answer invents a consultation fee. A third mixes MediLink with a different clinic chain.",
        ],
        "facts": [
            "Mention 28%, citation 11%, sentiment volatile (trust concerns).",
            "Competitor CareStack mention 50%, citation 33%, helped by Times of India explainers + doctor-authored Quora answers.",
            "Condition pages last medically reviewed dates are inconsistent; some show 2023.",
            "robots allow major AI bots, but /doctors/* profiles return soft-404 empty shells to non-JS clients.",
            "App-store listings are strong; website EEAT signals (author bios, review dates, citations) are weak.",
            "Legal forbids unverified 'best doctor' claims. PR team can pitch educational explainers only.",
            "Top risky prompt cluster: 'online psychiatrist India cost'. Top safe cluster: 'MediLink app download'.",
        ],
        "questions": [
            (
                "8-10 min",
                "In YMYL, why can a single outdated third-party page damage MediLink more inside LLMs than on classic Google SERPs? What brand-safety principle should guide GEO here?",
            ),
            (
                "8-10 min",
                "Prioritize 5 fixes (onsite + offsite) that improve accurate citations without making disallowed marketing claims. Rank by impact vs risk.",
            ),
            (
                "8-10 min",
                "Define 'winning' for the psychiatry cost prompt cluster. Is being mentioned enough, or must the answer be accurate on fees/services? How would you score answers weekly?",
            ),
            (
                "8-10 min",
                "Outline a human-in-the-loop agent workflow: AI proposes content updates, doctors/legal approve, CDN/edge publish, then re-measure citations. Where are the failure points?",
            ),
        ],
    },
    {
        "file": "04_StackPilot_SaaS.pdf",
        "short": "Case 04 StackPilot",
        "title": "Case 04  |  StackPilot (B2B SaaS)",
        "subtitle": "Devtools SaaS cited less than open-source alternatives",
        "industry": "B2B SaaS / Developer tools",
        "scenario": [
            "StackPilot is a paid workflow automation tool for engineering teams (CI helpers + release checklists). Docs SEO is good. PLG trials are okay from Google.",
            "When developers ask AI 'best CI release checklist tool', 'alternative to manual release notes', or 'automate PR release hygiene', answers push open-source GitHub Actions templates or Competitor Shiply. StackPilot appears late, described as 'enterprise-only' (false - they have a free tier).",
        ],
        "facts": [
            "Mention 22%, citation 9%, position ~3.2. Shiply mention 58%, citation 40%.",
            "Shiply wins via public comparison tables, GitHub READMEs, and Hashnode tutorials that LLMs cite.",
            "StackPilot docs are gated behind login for advanced pages; AI bots get redirect loops.",
            "Pricing page is accurate but FAQ is salesy. No neutral 'when NOT to use StackPilot' page.",
            "Agentic traffic strong on /docs/getting-started, weak on /docs/integrations/* (many 401s).",
            "G2/Capterra reviews exist but are sparse vs Shiply. Wikipedia: none.",
            "Losing cluster: 'open source vs paid release automation'. Winning cluster: branded troubleshooting prompts.",
        ],
        "questions": [
            (
                "8-10 min",
                "Why do LLMs currently prefer Shiply/open-source narratives over StackPilot? Separate crawl access issues from authority/earned-media issues.",
            ),
            (
                "8-10 min",
                "Propose a 'citation bait' content set developers (and agents) would trust - without sounding like ads. List 4 assets and the prompt each should win.",
            ),
            (
                "8-10 min",
                "Should StackPilot ungated advanced docs for AI bots only (edge variant) while keeping human login? Debate tradeoffs (security, SEO, GEO, support load) and recommend a decision.",
            ),
            (
                "8-10 min",
                "Design an executive dashboard with 4 metrics that connect AI visibility to pipeline (trials/SQLs). For each metric, state the decision it drives.",
            ),
        ],
    },
    {
        "file": "05_BiteBeam_Food.pdf",
        "short": "Case 05 BiteBeam",
        "title": "Case 05  |  BiteBeam (Food delivery)",
        "subtitle": "Regional food app missing from 'best places / late night' AI answers",
        "industry": "Food delivery / Local commerce",
        "scenario": [
            "BiteBeam is a regional food delivery app strong in 8 Indian cities. App rankings and paid UA are fine. Website SEO is mostly blog recipes and city landing pages.",
            "Users ask AI: 'best late night biryani near me Hyderabad', 'healthy meal subscription Hyderabad students', 'food delivery with student discounts'. AI names Swiggy/Zomato and a few cloud kitchens. BiteBeam is rarely mentioned; one answer claims BiteBeam shut operations in 2024 (false).",
        ],
        "facts": [
            "Mention 10% on local food prompts; citation 2%. National apps dominate.",
            "City pages are thin templates with little unique copy. Restaurant lists load via JS after geolocation.",
            "AI crawlers often see empty shells because content depends on location permission.",
            "PR rumor about shutdown still ranks on a random news aggregator; BiteBeam never issued a clear rebuttal page.",
            "Student discount exists in-app only; no indexable landing page explaining eligibility.",
            "Agentic traffic hits recipe blogs, not /hyderabad or partner restaurant pages.",
            "Sentiment when mentioned: positive on prices, confusion on availability cities.",
        ],
        "questions": [
            (
                "8-10 min",
                "Explain the GEO failure mode of geolocation-gated JS content for AI agents. What alternative onsite pattern would you ship for city discovery pages?",
            ),
            (
                "7-8 min",
                "How should BiteBeam handle the false 'shutdown' narrative across AI answers? Give a 14-day response plan (owned + earned media).",
            ),
            (
                "10-12 min",
                "Build a prompt strategy for 3 clusters (late night, healthy student meals, student discounts). For each: sample prompts, desired AI answer shape, and success metric.",
            ),
            (
                "8-10 min",
                "Can a regional app realistically beat national brands on AI answers? If yes, where (niche prompts)? If no, what 'win' should BiteBeam optimize for instead?",
            ),
        ],
    },
    {
        "file": "06_VoltRide_EV.pdf",
        "short": "Case 06 VoltRide",
        "title": "Case 06  |  VoltRide (EV scooters)",
        "subtitle": "EV brand wins SEO keywords but loses 'should I buy' AI advice prompts",
        "industry": "EV / Automotive retail",
        "scenario": [
            "VoltRide sells electric scooters online + via dealers. Category SEO is strong for 'best electric scooter under 1 lakh'. Spec sheets rank. Showroom footfall from Google is okay.",
            "However, advice-style prompts like 'is VoltRide good for daily 30km commute', 'VoltRide vs Ather for college students', 'real world range VoltRide monsoon' get answers that cite YouTube long-form reviews of competitors and a critical Reddit thread about VoltRide charger failures (old batch, fixed).",
        ],
        "facts": [
            "Mention 35% (decent) but citation 12% (weak). Position often mid-answer.",
            "Sentiment 0.05 overall; negative spike on battery/charger prompts.",
            "Official range claims are on PDPs; independent test data is not linked. Service center list is a PDF.",
            "Competitor citations come from detailed comparison blogs + owner forums.",
            "VoltRide YouTube exists but transcripts are sparse; no chaptered 'commute test' videos optimized as citable sources.",
            "Agentic bots successfully fetch PDPs (80% success) but rarely hit /support/charger-recall-faq (almost unknown URL).",
            "Dealer pages vary wildly in quality; many are thin and duplicate.",
        ],
        "questions": [
            (
                "8-10 min",
                "VoltRide is mentioned often but not trusted/cited. What does that pattern mean, and which 3 actions raise citation quality (not just mention count)?",
            ),
            (
                "8-10 min",
                "Design an onsite 'evidence pack' for the commute/range prompt cluster that LLMs can quote accurately (what pages, what proof, how often refreshed).",
            ),
            (
                "8-10 min",
                "How would you neutralize the outdated charger-failure narrative without deleting legitimate criticism? Include offsite and onsite steps.",
            ),
            (
                "8-10 min",
                "Propose a student-hackathon-friendly agent that monitors EV 'consideration' prompts weekly and opens tickets for content/PR owners. List must-have features for a prototype.",
            ),
        ],
    },
    {
        "file": "07_GlowTheory_Beauty.pdf",
        "short": "Case 07 GlowTheory",
        "title": "Case 07  |  GlowTheory (Beauty D2C)",
        "subtitle": "Clean beauty brand mislabeled by AI and losing ingredient prompts",
        "industry": "Beauty / Personal care D2C",
        "scenario": [
            "GlowTheory sells fragrance-free skincare for sensitive skin. Instagram and influencer SEO referrals are strong. Google ranks for a few ingredient terms.",
            "AI answers to 'niacinamide serum for sensitive skin India', 'fragrance free moisturizer fungal acne' often recommend 2 bigger D2C brands. GlowTheory sometimes appears with wrong claims ('contains essential oils' - it does not) or is labeled 'luxury' despite mid pricing.",
        ],
        "facts": [
            "Mention 20%, citation 6%, sentiment mixed; wrong-ingredient hallucinations in ~1 of 5 mentions.",
            "INCI / ingredient lists are in images on PDPs, not text. 'Free-from' claims are in a popup.",
            "Blog has good derm-interview content but no author credentials displayed.",
            "Competitor citations lean on dermatologist Instagram carousels transcribed elsewhere + Amazon A+ text.",
            "GPTBot allowed; however /products/* returns different content to bots vs users (incomplete bot view).",
            "No Wikipedia. Reddit skincare community mentions are rare; when present, positive on gentle formula.",
            "Losing cluster: fungal-acne-safe routines. Weak win: branded shade/serum names.",
        ],
        "questions": [
            (
                "8-10 min",
                "Why might AI invent wrong ingredients for GlowTheory? Connect hallucinations to onsite content format and offsite sparse authority.",
            ),
            (
                "8-10 min",
                "Write a 21-day plan to make ingredient truth machine-readable and citable. Include PDP changes, FAQ, and one earned-media play.",
            ),
            (
                "8-10 min",
                "Should GlowTheory chase broad 'best serum India' prompts or niche 'sensitive / fungal-acne-safe' prompts first? Defend with expected mention/citation ROI.",
            ),
            (
                "8-10 min",
                "Define an answer-quality rubric for beauty GEO (accuracy of ingredients, price band, suitable skin type, citation source). How would a weekly review work for a 3-person team?",
            ),
        ],
    },
    {
        "file": "08_ClaimWise_Insurance.pdf",
        "short": "Case 08 ClaimWise",
        "title": "Case 08  |  ClaimWise (Insurtech)",
        "subtitle": "Insurance aggregator accurate on Google, risky in AI advice answers",
        "industry": "Insurtech / Insurance aggregation (YMYL)",
        "scenario": [
            "ClaimWise compares health and term policies and earns referral commissions. Classic SEO comparison pages rank well. Compliance reviews every public page.",
            "Users ask AI 'best term insurance for 25 year old non smoker', 'does policy X cover maternity waiting', 'ClaimWise vs Policybazaar'. AI sometimes recommends ClaimWise, but also invents coverage details, mixes insurer names, or cites an old page with pre-IRDAI-update waiting periods.",
        ],
        "facts": [
            "Mention 30%, citation 14%, position ~2.8. Policybazaar mention 75%, citation 50%.",
            "Sentiment okay on UX, weak on 'trust / impartiality' prompts.",
            "Comparison tables are interactive widgets; static HTML fallback is incomplete for bots.",
            "Disclaimers exist but are footer-only; AI answers often omit them.",
            "Several high-authority affiliate blogs still scrape ClaimWise's 2023 waiting-period numbers.",
            "Agentic success rate 55% on comparison URLs (timeouts on widget endpoints).",
            "Legal wants fewer aggressive 'best policy' phrases; product wants more AI share of voice.",
        ],
        "questions": [
            (
                "8-10 min",
                "Map the conflict between growth (more AI recommendations) and compliance (no unsafe advice). What GEO strategy respects both?",
            ),
            (
                "8-10 min",
                "How do you stop outdated scraped numbers from poisoning LLM answers? Give onsite technical steps + offsite correction tactics.",
            ),
            (
                "8-10 min",
                "Propose a bot-safe version of a comparison page that still converts humans. What content must be in static HTML vs progressive enhancement?",
            ),
            (
                "8-10 min",
                "If ClaimWise can only monitor 25 prompts, how do you choose them? Give a selection framework and 6 example prompts spanning trust, comparison, and coverage FAQs.",
            ),
        ],
    },
    {
        "file": "09_AuraWear_DTC_Apparel.pdf",
        "short": "Case 09 AuraWear",
        "title": "Case 09  |  AuraWear (DTC Apparel)",
        "subtitle": "D2C apparel strong on SEO but invisible or misrepresented in AI shopping answers",
        "industry": "DTC apparel / E-commerce",
        "scenario": [
            "AuraWear is a mid-size Indian D2C apparel brand. Classic SEO is fine: many category pages rank on page 1 for 'organic cotton tees', 'workwear shirts women', etc. Monthly organic sessions are stable.",
            "But when shoppers ask AI assistants things like 'best sustainable everyday wear brands in India under 2000 INR' or 'good formal shirts for college placements', ChatGPT / Perplexity / Gemini often recommend 3-4 competitors and never mention AuraWear. When AuraWear does appear, the answer misstates pricing and calls it a 'premium luxury' brand.",
            "Competitor NovaKnit dominates AI answers via Quora threads, review roundups, and a stronger third-party footprint.",
        ],
        "facts": [
            "robots.txt blocks several AI crawlers; CDN returns 403 to unknown bots on /collections/*.",
            "Product pages are heavily client-rendered (JS). Key specs sit behind tabs.",
            "Blog last major refresh: 11 months ago. Few FAQ blocks in natural Q&A form.",
            "Wikipedia page is a stub. Reddit / Quora mentions are rare vs Competitor NovaKnit.",
            "Sample prompt board (20 prompts): AuraWear mention rate 15%, citation rate 5%, avg sentiment mixed/negative on price. NovaKnit mention rate 60%, citation 35%.",
            "Analytics shows almost no agentic bot hits on PDP URLs; a few hits on old blog posts.",
            "Top losing cluster: sustainable everyday wear under 2000 + placement formals. Rare win: branded AuraWear prompts only.",
        ],
        "questions": [
            (
                "8-10 min",
                "What are the top 3 reasons AuraWear is invisible or misrepresented in AI-generated answers despite decent SEO? Separate technical, content, and offsite/earned-media causes. Tie each to a case fact.",
            ),
            (
                "7-8 min",
                "Design a simple measurement plan for the next 8 weeks. Which metrics would you track across AI platforms, how often, and how would you know if the brand is actually winning visibility (not just traffic)?",
            ),
            (
                "10-12 min",
                "Propose a prioritized 30-day action plan (quick wins vs deeper work) for onsite and offsite GEO. Be specific. Tie each action to your diagnosis in Q1. Call out one thing you would NOT do first.",
            ),
            (
                "8-10 min",
                "AuraWear's growth lead wants an agent-era brand visibility workflow (monitor prompts -> find gaps -> fix content -> prove impact). Outline the workflow and what a tool like Adobe Brand Visibility (or a student-built agent) should automate vs leave to humans.",
            ),
        ],
    },
]


def answer_frame(pdf: FPDF):
    h2(pdf, "Answer frame (use on every question)")
    for b in [
        "One-line bottom line first",
        "2-3 causes tied to case facts (do not invent numbers)",
        "Prioritized actions: quick wins vs later bets",
        "Metrics / how you know it worked",
        "Optional one-line Adobe / agent angle if it fits",
    ]:
        bullet(pdf, b)
    para(
        pdf,
        "Judged on: analytical thinking, strategic approach, actionable insights. "
        "Write like a sharp student analyst under time pressure - specific, not buzzwordy.",
    )


def build_case(case: dict) -> Path:
    pdf = Doc(case["short"])
    pdf.set_auto_page_break(auto=True, margin=16)
    pdf.add_page()

    h1(pdf, "Adobe University Hackathon 2026")
    sx(pdf)
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(40, 40, 40)
    pdf.multi_cell(0, 6.2, case["title"], new_x="LMARGIN", new_y="NEXT")
    meta(
        pdf,
        f"{case['subtitle']}\n"
        f"Industry: {case['industry']}  |  Theme: Speak to Agents - Brand Visibility\n"
        "Practice paper  |  Timebox 45:00  |  Suggested: read 5 | Q1-Q4 as marked | buffer 2\n"
        "Unofficial - for team practice only. Official Round 2 may differ.",
    )

    h2(pdf, "Scenario")
    for p in case["scenario"]:
        para(pdf, p)

    h2(pdf, "Case facts / data")
    for f in case["facts"]:
        bullet(pdf, f)

    h2(pdf, "Questions")
    for i, (mins, text) in enumerate(case["questions"], 1):
        question(pdf, i, text, mins)

    answer_frame(pdf)
    meta(
        pdf,
        "Team tip: attempt alone under timer, then compare notes. Focus debate on prioritization "
        "and metrics - not who wrote longer answers.",
    )

    out = OUT_DIR / case["file"]
    pdf.output(out)
    return out


def build_index(paths: list[Path]):
    pdf = Doc("Team Index")
    pdf.set_auto_page_break(auto=True, margin=16)
    pdf.add_page()
    h1(pdf, "Team Distribution Index")
    meta(
        pdf,
        "9 case studies for Adobe Round 2 practice (including AuraWear). "
        "Clean split for a team of 3: each person owns exactly 3 cases.",
    )
    h2(pdf, "Suggested ownership (edit names)")
    para(pdf, "Member A: Cases 01 LearnOrbit, 02 TrailMuse, 03 MediLink")
    para(pdf, "Member B: Cases 04 StackPilot, 05 BiteBeam, 06 VoltRide")
    para(pdf, "Member C: Cases 07 GlowTheory, 08 ClaimWise, 09 AuraWear")
    h2(pdf, "Files in this folder")
    for case in CASES:
        bullet(pdf, f"{case['file']}  -  {case['title'].split('|')[1].strip()}")
    h2(pdf, "How to practice")
    for b in [
        "45-minute silent attempt, phone notes only if your real round allows similar aids",
        "Exchange PDFs; grade each other on specificity + prioritization + metrics",
        "Rebuild one weak answer together using the shared AI writing prompt (human tone)",
        "After individual attempts, do a joint debrief on Case 09 AuraWear (classic GEO pattern)",
    ]:
        bullet(pdf, b)
    out = OUT_DIR / "00_Team_Distribution_Index.pdf"
    pdf.output(out)
    return out


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    written = []
    for case in CASES:
        p = build_case(case)
        written.append(p)
        print(f"Wrote {p.name}")
    idx = build_index(written)
    print(f"Wrote {idx.name}")
    print(f"Done: {len(written)} case PDFs + index in {OUT_DIR}")
    # Keep folder tidy if older naming leftovers appear later
    expected = {c["file"] for c in CASES} | {"00_Team_Distribution_Index.pdf"}
    for p in OUT_DIR.glob("*.pdf"):
        if p.name not in expected:
            print(f"Note: unexpected file present: {p.name}")


if __name__ == "__main__":
    main()
