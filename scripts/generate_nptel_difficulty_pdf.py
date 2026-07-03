#!/usr/bin/env python3
"""Generate readable NPTEL course difficulty PDF with full tier data."""

import json
import ssl
import statistics
import urllib.request
from datetime import date
from pathlib import Path

from fpdf import FPDF

ROOT = Path(__file__).resolve().parents[1]
NPTEL_DIR = ROOT / "Reference Collection" / "NPTEL"
STATS_PATH = NPTEL_DIR / "NPTEL-STATS-FULL.json"
OUT = NPTEL_DIR / "NPTEL-Course-Difficulty-Ranking-2026.pdf"

ENROLLMENT = {
    "noc26_cs161": 13515, "noc26_cs157": 6188, "noc26_cs141": 4705, "noc26_cs160": 4387,
    "noc26_cs171": 3459, "noc26_cs95": 3019, "noc26_cs180": 2611, "noc26_cs188": 2404,
    "noc26_cs177": 2024, "noc26_cs159": 2016, "noc26_cs98": 1864, "noc26_cs145": 1848,
    "noc26_cs104": 1670, "noc26_cs97": 1623, "noc26_cs120": 1402, "noc26_cs131": 1381,
    "noc26_cs181": 1308, "noc26_cs158": 1151, "noc26_cs128": 1046, "noc26_cs170": 809,
    "noc26_cs115": 793, "noc26_cs169": 782, "noc26_cs96": 702, "noc26_cs175": 672,
    "noc26_cs135": 644, "noc26_cs140": 627, "noc26_cs108": 523, "noc26_cs178": 500,
    "noc26_cs90": 383, "noc26_cs173": 377, "noc26_cs176": 345, "noc26_cs187": 231,
    "noc26_cs92": 203, "noc26_cs103": 197, "noc26_cs167": 190, "noc26_cs154": 186,
    "noc26_cs121": 178, "noc26_cs165": 171, "noc26_cs100": 159, "noc26_cs149": 110,
    "noc26_ge57": 108, "noc26_cs94": 105, "noc26_cs172": 77, "noc26_cs148": 66,
}

COURSE_NIDS = {
    "noc26_cs100": "106105001", "noc26_cs103": "106104001", "noc26_cs104": "106103001",
    "noc26_cs108": "106108468", "noc26_cs115": "106106168", "noc26_cs120": "106105165",
    "noc26_cs121": "106105238", "noc26_cs128": "106108702", "noc26_cs131": "106105164",
    "noc26_cs135": "106106169", "noc26_cs140": "106105233", "noc26_cs141": "106105218",
    "noc26_cs145": "106105219", "noc26_cs148": "106105220", "noc26_cs149": "106105221",
    "noc26_cs154": "106105239", "noc26_cs157": "106105217", "noc26_cs158": "106105216",
    "noc26_cs159": "106105234", "noc26_cs160": "106105195", "noc26_cs161": "106105166",
    "noc26_cs165": "106105235", "noc26_cs167": "106105236", "noc26_cs169": "106106170",
    "noc26_cs170": "106105240", "noc26_cs171": "106105241", "noc26_cs172": "106105242",
    "noc26_cs173": "106105243", "noc26_cs175": "106105244", "noc26_cs176": "106105245",
    "noc26_cs177": "106105246", "noc26_cs178": "106105247", "noc26_cs180": "106105248",
    "noc26_cs181": "106105249", "noc26_cs187": "106105250", "noc26_cs188": "106105251",
    "noc26_cs90": "106106002", "noc26_cs92": "106106003", "noc26_cs94": "106106004",
    "noc26_cs95": "106106005", "noc26_cs96": "106106006", "noc26_cs97": "106106007",
    "noc26_cs98": "106106008", "noc26_ge57": "106106009",
}

# Landscape table widths (mm) - sum = 273
RANK_W = [8, 78, 20, 20, 20, 20, 20, 18, 18, 31]
RANK_HDR = ["#", "Course", "Gold 90+", "Silver 75+", "Elite 60-74", "60+ All", "Pass 40+", "Avg", "Enroll", "Code"]

RUN_W = [42, 20, 16, 16, 16, 16, 20, 20, 20, 20, 20, 18]
RUN_HDR = ["Run", "Registered", "Gold", "Silver", "Elite", "Pass", "G%", "S%", "E%", "60+%", "Cert%", "Avg"]


class Report(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=18)

    def footer(self):
        self.set_y(-14)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 8, f"Ojas Srivastava  |  Page {self.page_no()}/{{nb}}", align="C")

    def portrait_margins(self):
        self.set_margins(18, 18, 18)

    def landscape_margins(self):
        self.set_margins(12, 14, 12)

    def title_block(self, title, subtitle=None):
        self.set_x(self.l_margin)
        self.set_font("Helvetica", "B", 20)
        self.set_text_color(15, 15, 15)
        self.cell(0, 10, title, new_x="LMARGIN", new_y="NEXT")
        if subtitle:
            self.set_font("Helvetica", "", 11)
            self.set_text_color(80, 80, 80)
            self.cell(0, 7, subtitle, new_x="LMARGIN", new_y="NEXT")
        self.ln(4)

    def section(self, text):
        self.ln(3)
        self.set_x(self.l_margin)
        self.set_font("Helvetica", "B", 13)
        self.set_text_color(25, 25, 25)
        self.cell(0, 8, text, new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

    def para(self, text, size=10.5):
        self.set_x(self.l_margin)
        self.set_font("Helvetica", "", size)
        self.set_text_color(35, 35, 35)
        self.multi_cell(0, 5.5, text)
        self.ln(2)

    def bullet(self, text):
        self.set_x(self.l_margin + 4)
        self.set_font("Helvetica", "", 10.5)
        self.multi_cell(0, 5.5, f"  -  {text}")

    def table_header(self, widths, headers, font_size=8.5):
        self.set_x(self.l_margin)
        self.set_font("Helvetica", "B", font_size)
        self.set_fill_color(45, 55, 72)
        self.set_text_color(255, 255, 255)
        h = 8
        for w, hdr in zip(widths, headers):
            self.cell(w, h, hdr, border=1, fill=True, align="C")
        self.ln(h)
        self.set_text_color(30, 30, 30)

    def table_row(self, widths, cells, bold=False, fill=None, font_size=9, align="C"):
        self.set_x(self.l_margin)
        if fill:
            self.set_fill_color(*fill)
        else:
            self.set_fill_color(255, 255, 255)
        style = "B" if bold else ""
        h = 7
        for col, (w, cell) in enumerate(zip(widths, cells)):
            txt = str(cell)
            col_align = "L" if col == 1 else align
            fs = font_size - 1 if w < 22 and len(txt) > 8 else font_size
            self.set_font("Helvetica", style, fs)
            self.cell(w, h, txt, border=1, fill=bool(fill), align=col_align)
        self.ln(h)


def analyze_run(r):
    reg = r["Registered"] or 0
    if not reg:
        return None
    g = r.get("Gold") or 0
    s = r.get("Silver") or 0
    e = r.get("Elite") or 0
    su = r.get("Success") or 0
    cert = r.get("Certified") or 0
    avg = r.get("average")
    return {
        "timeline": r.get("Timeline"),
        "registered": reg,
        "gold": g, "silver": s, "elite": e, "success": su,
        "gold_pct": round(100 * g / reg, 1),
        "silver_pct": round(100 * s / reg, 1),
        "elite_pct": round(100 * e / reg, 1),
        "score_60_plus_pct": round(100 * (g + s + e) / reg, 1),
        "success_pct": round(100 * su / reg, 1),
        "cert_pct": round(100 * cert / reg, 1),
        "average": float(avg) if avg not in (None, "NULL", "") else None,
    }


def fetch_course(slug, name, nid=None):
    nid = nid or COURSE_NIDS.get(slug)
    row = {"slug": slug, "name": name, "nid": nid}
    if not nid:
        return {**row, "error": "no nid"}
    try:
        ctx = ssl.create_default_context()
        req = urllib.request.Request(
            f"https://nptel.ac.in/api/stats/{nid}", headers={"User-Agent": "Mozilla/5.0"},
        )
        with urllib.request.urlopen(req, context=ctx, timeout=30) as resp:
            data = json.loads(resp.read())
        if data.get("message") != "Success" or not data.get("data"):
            return {**row, "error": "no api data"}
        runs = data["data"][0]["run_wise_stats"]
        valid = [r for r in runs if r.get("Registered") and r.get("average") not in (None, "NULL", "")]
        if not valid:
            return {**row, "error": "no valid runs"}
        last5 = valid[-5:]
        analyzed = [analyze_run(r) for r in last5]

        def mean(key):
            return round(statistics.mean([a[key] for a in analyzed]), 1)

        return {
            **row, "runs_analyzed": len(last5), "run_details": analyzed,
            "gold_rate_pct": mean("gold_pct"), "silver_rate_pct": mean("silver_pct"),
            "elite_only_rate_pct": mean("elite_pct"), "score_60_plus_pct": mean("score_60_plus_pct"),
            "success_rate_pct": mean("success_pct"), "cert_rate_pct": mean("cert_pct"),
            "avg_exam_mean": mean("average"),
        }
    except Exception as ex:
        return {**row, "error": str(ex)}


def load_stats():
    if not STATS_PATH.exists():
        raise SystemExit(f"Missing {STATS_PATH}")
    with open(STATS_PATH) as f:
        return json.load(f)


def prepare(rows):
    with_data, unknown = [], []
    for r in rows:
        r["enrolled_2026"] = ENROLLMENT.get(r["slug"], 0)
        if r.get("gold_rate_pct") is None:
            unknown.append(r)
        else:
            with_data.append(r)
    by_gold = sorted(with_data, key=lambda x: x["gold_rate_pct"], reverse=True)
    by_60 = sorted(with_data, key=lambda x: x["score_60_plus_pct"], reverse=True)
    return with_data, unknown, by_gold, by_60


def short_name(name, n=34):
    return name if len(name) <= n else name[: n - 1] + "."


def add_ranking_table(pdf, courses, title, start_rank=1, highlight_slug="noc26_cs161"):
    pdf.add_page(orientation="L")
    pdf.landscape_margins()
    pdf.section(title)
    pdf.table_header(RANK_W, RANK_HDR)
    for i, c in enumerate(courses, start_rank):
        if pdf.get_y() > 185:
            pdf.add_page(orientation="L")
            pdf.landscape_margins()
            pdf.section(f"{title} (continued)")
            pdf.table_header(RANK_W, RANK_HDR)
        highlight = (235, 245, 255) if c["slug"] == highlight_slug else (
            (248, 248, 248) if i % 2 == 0 else None
        )
        pdf.table_row(
            RANK_W,
            [
                i,
                short_name(c["name"]),
                f"{c['gold_rate_pct']:.1f}%",
                f"{c['silver_rate_pct']:.1f}%",
                f"{c['elite_only_rate_pct']:.1f}%",
                f"{c['score_60_plus_pct']:.1f}%",
                f"{c['cert_rate_pct']:.1f}%",
                f"{c['avg_exam_mean']:.1f}",
                c["enrolled_2026"],
                c["slug"].replace("noc26_", ""),
            ],
            fill=highlight,
            align="C",
        )
        # left-align course name cell content by drawing over - skip, truncated is ok


def add_course_run_table(pdf, c):
    pdf.add_page(orientation="L")
    pdf.landscape_margins()
    pdf.section(f"{c['name']}")
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(0, 5, f"{c['slug']}  |  NPTEL ID {c['nid']}  |  Last {c.get('runs_analyzed', 5)} exam runs", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)
    summary_w = [50, 24, 24, 24, 24, 24, 24, 24]
    pdf.table_header(
        summary_w,
        ["Metric", "Gold 90+", "Silver 75+", "Elite 60-74", "60+ All", "Pass 40+", "Cert", "Avg"],
        font_size=9,
    )
    pdf.table_row(
        summary_w,
        [
            "5-run average",
            f"{c['gold_rate_pct']:.1f}%",
            f"{c['silver_rate_pct']:.1f}%",
            f"{c['elite_only_rate_pct']:.1f}%",
            f"{c['score_60_plus_pct']:.1f}%",
            f"{c['success_rate_pct']:.1f}%",
            f"{c['cert_rate_pct']:.1f}%",
            f"{c['avg_exam_mean']:.1f}",
        ],
        bold=True,
        fill=(235, 245, 255) if c["slug"] == "noc26_cs161" else (240, 240, 240),
        font_size=9,
    )
    pdf.ln(4)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 6, "Per-run breakdown", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)
    pdf.table_header(RUN_W, RUN_HDR, font_size=8)
    for j, run in enumerate(c.get("run_details", [])):
        fill = (248, 248, 248) if j % 2 == 0 else None
        pdf.table_row(
            RUN_W,
            [
                run["timeline"][:16],
                run["registered"],
                run["gold"],
                run["silver"],
                run["elite"],
                run["success"],
                f"{run['gold_pct']:.1f}",
                f"{run['silver_pct']:.1f}",
                f"{run['elite_pct']:.1f}",
                f"{run['score_60_plus_pct']:.1f}",
                f"{run['cert_pct']:.1f}",
                f"{run['average']}",
            ],
            fill=fill,
            font_size=8,
        )


def build_pdf():
    rows = load_stats()
    with_data, unknown, by_gold, by_60 = prepare(rows)
    iot = next((r for r in with_data if r["slug"] == "noc26_cs161"), None)
    iot_gold_rank = next(i + 1 for i, r in enumerate(by_gold) if r["slug"] == "noc26_cs161")
    top90 = by_gold[0]

    pdf = Report()
    pdf.alias_nb_pages()

    # ---- Cover ----
    pdf.add_page()
    pdf.portrait_margins()
    pdf.ln(20)
    pdf.title_block(
        "NPTEL Course Rankings",
        "Jul-Dec 2026  |  SVNIT UG List  |  Full Certificate Tier Data",
    )
    pdf.para(f"Generated {date.today().strftime('%d %B %Y')}. Source: nptel.ac.in/api/stats")
    pdf.ln(4)

    pdf.section("How to read this report")
    pdf.bullet("Gold 90+ = % of paid exam takers who scored 90-100 (your target)")
    pdf.bullet("Silver 75+ = scored 75-89")
    pdf.bullet("Elite 60-74 = scored 60-74 (NPTEL calls this 'Elite' on certificate)")
    pdf.bullet("60+ All = Gold + Silver + Elite combined")
    pdf.bullet("Pass 40+ = Success tier (40-59)")
    pdf.bullet("All % based on exam registrants, averaged over last 5 runs")
    pdf.ln(4)

    pdf.section("Key finding for 90+")
    pdf.para(
        f"Best historical 90+ odds: {top90['name']} ({top90['gold_rate_pct']}% Gold rate). "
        f"IoT (your pick) ranks #{iot_gold_rank} for 90+ at {iot['gold_rate_pct']}% Gold, "
        f"but #{next(i+1 for i,r in enumerate(by_60) if r['slug']=='noc26_cs161')} for 60+ "
        f"({iot['score_60_plus_pct']}%) and has the highest pass rate ({iot['cert_rate_pct']}%)."
    )

    pdf.section("Top 5 for 90+ (Gold)")
    for i, c in enumerate(by_gold[:5], 1):
        pdf.bullet(
            f"{i}. {c['name']} - Gold {c['gold_rate_pct']}%, 60+ {c['score_60_plus_pct']}%, "
            f"avg {c['avg_exam_mean']}"
        )

    # ---- Main ranking by 90+ ----
    add_ranking_table(
        pdf, by_gold,
        f"TABLE 1: All courses ranked by 90+ Gold rate ({len(by_gold)} courses)",
    )

    # ---- Ranking by 60+ ----
    add_ranking_table(
        pdf, by_60,
        f"TABLE 2: All courses ranked by 60+ rate ({len(by_60)} courses)",
        start_rank=1,
    )

    # ---- Worst for 90+ ----
    pdf.add_page(orientation="L")
    pdf.landscape_margins()
    pdf.section("TABLE 3: Worst 10 courses for 90+ (lowest Gold rate)")
    pdf.table_header(RANK_W, RANK_HDR)
    worst = by_gold[-10:]
    for i, c in enumerate(worst, len(by_gold) - 9):
        pdf.table_row(
            RANK_W,
            [
                i, short_name(c["name"]),
                f"{c['gold_rate_pct']:.1f}%", f"{c['silver_rate_pct']:.1f}%",
                f"{c['elite_only_rate_pct']:.1f}%", f"{c['score_60_plus_pct']:.1f}%",
                f"{c['cert_rate_pct']:.1f}%", f"{c['avg_exam_mean']:.1f}",
                c["enrolled_2026"], c["slug"].replace("noc26_", ""),
            ],
            fill=(255, 240, 240),
        )

    # ---- Unknown courses ----
    pdf.add_page()
    pdf.portrait_margins()
    pdf.section("Courses with NO exam history (high risk)")
    pdf.table_header([12, 95, 35, 30], ["#", "Course", "Slug", "Enrolled"])
    for i, r in enumerate(unknown, 1):
        pdf.table_row(
            [12, 95, 35, 30],
            [i, short_name(r.get("name", r["slug"]), 50), r["slug"], ENROLLMENT.get(r["slug"], "?")],
            fill=(248, 248, 248) if i % 2 == 0 else None,
            align="L",
        )

    # ---- Detail pages: top 5 for 90+ (includes IoT at #5) ----
    for c in by_gold[:5]:
        add_course_run_table(pdf, c)

    # ---- References ----
    pdf.add_page()
    pdf.portrait_margins()
    pdf.section("References")
    pdf.bullet("NPTEL Stats API: https://nptel.ac.in/api/stats/{nid}")
    pdf.bullet("Raw JSON: Reference Collection/NPTEL/NPTEL-STATS-FULL.json")
    pdf.bullet("Regenerate: python scripts/generate_nptel_difficulty_pdf.py")
    pdf.ln(6)
    pdf.para(
        "Note: Rankings use historical data. New courses have no stats. "
        "Verify SVNIT credit mapping with your professor before enrolling.",
        size=9,
    )

    pdf.output(str(OUT))
    print(OUT)


if __name__ == "__main__":
    build_pdf()
