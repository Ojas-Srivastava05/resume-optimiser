#!/usr/bin/env python3
"""Blind Codeforces practice PDF - recent hard problems for Specialist+."""

import json
from pathlib import Path

from fpdf import FPDF

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "OA-Topic-Mastery-Practice.pdf"
SETS_JSON = Path("/tmp/cf_sets_oju.json")


class PDF(FPDF):
    def footer(self):
        self.set_y(-12)
        self.set_font("Helvetica", "", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 8, f"Page {self.page_no()}", align="C")


def cell(pdf, text, h=5):
    pdf.multi_cell(0, h, text, new_x="LMARGIN", new_y="NEXT")


def h1(pdf, text):
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(20, 20, 20)
    cell(pdf, text, 8)
    pdf.ln(2)


def h2(pdf, text):
    pdf.ln(2)
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(20, 20, 20)
    cell(pdf, text, 6)
    pdf.ln(1)


def body(pdf, text):
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(30, 30, 30)
    cell(pdf, text, 5)


def bullet(pdf, text):
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(30, 30, 30)
    cell(pdf, f"  - {ascii_safe(text)}", 5)


def mono(pdf, text):
    pdf.set_font("Courier", "", 8)
    pdf.set_text_color(20, 20, 20)
    pdf.set_fill_color(245, 245, 245)
    pdf.multi_cell(0, 4.2, ascii_safe(text), fill=True, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)


def rule(pdf):
    pdf.ln(1)
    y = pdf.get_y()
    pdf.set_draw_color(200, 200, 200)
    pdf.line(pdf.l_margin, y, pdf.w - pdf.r_margin, y)
    pdf.ln(3)


def ascii_safe(text):
    repl = {
        "\u2019": "'",
        "\u2018": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2013": "-",
        "\u2014": "-",
        "\u2026": "...",
        "\u00d7": "x",
    }
    for a, b in repl.items():
        text = text.replace(a, b)
    return text.encode("latin-1", "replace").decode("latin-1")


def load_sets():
    sets = json.loads(SETS_JSON.read_text())
    # drop empty
    return [s for s in sets if s.get("problems")]


def set_block(pdf, idx, problems):
    h2(pdf, f"Set {idx}")
    for pr in problems:
        bullet(pdf, f"{pr['id']}  {pr['name']}")
    rule(pdf)


def build():
    sets = load_sets()
    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=16)
    pdf.add_page()

    h1(pdf, "Codeforces Practice Sets")
    body(
        pdf,
        "Recent contest problems (mostly 2024-2026), Specialist+ band. "
        "Grouped into sets. Topics and ratings are hidden until the answer key. "
        "Figure out the pattern yourself.",
    )
    pdf.ln(1)
    body(
        pdf,
        "Calibrated against Codeforces handle Oju (Specialist, max 1419): "
        "excludes problems already AC'd on that account.",
    )
    pdf.ln(2)

    h2(pdf, "How to open a problem")
    mono(
        pdf,
        "2230D -> https://codeforces.com/problemset/problem/2230/D\n"
        "2149E -> https://codeforces.com/problemset/problem/2149/E\n"
        "Format: /problemset/problem/{contestId}/{index}",
    )

    h2(pdf, "Rules")
    bullet(pdf, "No AI until AFTER you submit (or timebox ends).")
    bullet(pdf, "Timer: 40-70 min per problem. These are not Div2 A toys.")
    bullet(pdf, "Before code: guess the pattern in one line. Write what you track.")
    bullet(pdf, "Stuck 25 min: write a correct slow solution, then optimize.")
    bullet(pdf, "Editorial only after a real attempt. Re-solve fails cold in 3 days.")
    bullet(pdf, "Finish one full set before the next. Do NOT open the answer key early.")
    rule(pdf)

    h2(pdf, "One problem flow")
    mono(
        pdf,
        "1. Guess pattern (2 min)\n"
        "2. What state / data structure? (3 min)\n"
        "3. Dry-run samples + edge cases (5 min)\n"
        "4. Code + stress tiny cases if needed\n"
        "5. Submit. Editorial only for gaps\n"
        "6. Log: guessed pattern | key topic | bug",
    )
    rule(pdf)

    for i, s in enumerate(sets, 1):
        if pdf.get_y() > 248:
            pdf.add_page()
        set_block(pdf, i, s["problems"])

    # Answer key
    pdf.add_page()
    h1(pdf, "ANSWER KEY - open only after practice")
    body(
        pdf,
        "Topic + rating per set. Use to check pattern recognition after you solve, "
        "not to cheat the technique beforehand.",
    )
    body(
        pdf,
        "Band: roughly 1500-1900 CF. Source: recent problemset, unsolved by Oju.",
    )
    rule(pdf)

    for i, s in enumerate(sets, 1):
        if pdf.get_y() > 250:
            pdf.add_page()
        h2(pdf, f"Set {i}: {s['topic']}")
        for pr in s["problems"]:
            tags = ", ".join(pr.get("tags", [])[:4])
            bullet(pdf, f"{pr['id']} ({pr['rating']})  {pr['name']}")
            if tags:
                body(pdf, f"    tags: {tags}")
        rule(pdf)

    pdf.ln(1)
    body(
        pdf,
        "If your guessed pattern matched most of the time, push Set difficulty upward "
        "(virtual Div2 C/D). If not, redo that set cold.",
    )

    pdf.output(str(OUT))
    print(f"Wrote {OUT} ({sum(len(s['problems']) for s in sets)} problems, {len(sets)} sets)")


if __name__ == "__main__":
    build()
