#!/usr/bin/env python3
"""Generate personal Cursor / local tooling stats PDF for Ojas."""

from pathlib import Path

from fpdf import FPDF

OUT = (
    Path(__file__).resolve().parents[1]
    / "Resume Collection"
    / "Ojas_Cursor_Personal_Stats.pdf"
)


class Doc(FPDF):
    def footer(self):
        self.set_y(-12)
        self.set_font("Helvetica", "", 8)
        self.set_text_color(100, 100, 100)
        self.cell(0, 8, "Personal Cursor stats (local)  |  Ojas Srivastava  |  Not for public resume as raw dump", align="C")


def sx(p):
    p.set_x(p.l_margin)


def h1(p, t):
    sx(p)
    p.set_font("Helvetica", "B", 15)
    p.set_text_color(20, 20, 20)
    p.multi_cell(0, 7.5, t, new_x="LMARGIN", new_y="NEXT")
    p.ln(1)


def h2(p, t):
    p.ln(2)
    sx(p)
    p.set_font("Helvetica", "B", 11)
    p.set_text_color(30, 30, 30)
    p.multi_cell(0, 6, t, new_x="LMARGIN", new_y="NEXT")
    p.ln(0.6)


def para(p, t):
    sx(p)
    p.set_font("Helvetica", "", 10)
    p.set_text_color(25, 25, 25)
    p.multi_cell(0, 5.2, t, new_x="LMARGIN", new_y="NEXT")
    p.ln(0.8)


def meta(p, t):
    sx(p)
    p.set_font("Helvetica", "I", 9)
    p.set_text_color(80, 80, 80)
    p.multi_cell(0, 4.8, t, new_x="LMARGIN", new_y="NEXT")
    p.ln(1.2)


def bullet(p, t, indent=3):
    p.set_x(p.l_margin + indent)
    p.set_font("Helvetica", "", 10)
    p.set_text_color(25, 25, 25)
    p.multi_cell(p.epw - indent, 5.1, f"- {t}", new_x="LMARGIN", new_y="NEXT")
    p.ln(0.2)


def build():
    p = Doc()
    p.set_auto_page_break(auto=True, margin=16)
    p.add_page()

    h1(p, "Ojas Srivastava --- Cursor Personal Stats Snapshot")
    meta(
        p,
        "Generated from local Cursor data on this machine (15 Aug 2026).\n"
        "Account: srivastavaojas.socialmedia@gmail.com  |  Plan: Cursor Pro\n"
        "Token / $ spend is NOT in this file --- open cursor.com/dashboard/usage while logged in.",
    )

    h2(p, "What could NOT be fetched automatically")
    bullet(p, "Included / on-demand token spend and per-request $ (needs Cursor web session).")
    bullet(p, "Official analytics leaderboard (Teams/Enterprise analytics API; you are on personal Pro).")
    para(
        p,
        "To get tokens: open https://cursor.com/dashboard/usage and https://cursor.com/dashboard/spending.",
    )

    h2(p, "Account & setup")
    bullet(p, "Plan: Pro (Google signup)")
    bullet(p, "MCP servers configured: 6 --- GitHub, Supabase, Vercel, Firebase, Redis, Stitch (+ built-in browser MCP in agent)")
    bullet(p, "Cursor Agent skills installed: 20 (automate, canvas, sdk, review-security, split-to-prs, ...)")
    bullet(p, "Editor extensions installed: ~27 (Python, Jupyter, C/C++, CMake, Live Server, ChatGPT, PDF, CP helper, ...)")
    bullet(p, "Composer / Agent sessions tracked in local headers: 234")
    bullet(p, "Saved Cursor plans on disk: 5")

    h2(p, "AI code tracking (local DB since ~10 Jan 2026)")
    bullet(p, "AI code-hash events: 56,459")
    bullet(p, "Distinct Agent/Composer requests: 256")
    bullet(p, "Distinct conversations with code hashes: 30")
    bullet(p, "Distinct files touched: 358")
    bullet(p, "By source: composer 55,932 | tagged human 527")
    bullet(p, "Top models in hashes: default 47,216 | grok-4.5 6,707 | grok-4.6 1,372 | composer-2.5 637")
    bullet(p, "Top file types: .py 33,646 | .tex 7,930 | .md 4,044 | .sh 2,553 | .tsx 1,824 | .cpp 1,293")

    h2(p, "Scored commits (Cursor AI attribution)")
    bullet(p, "Commits scored: 437 (284 with line breakdowns)")
    bullet(p, "Lines added (tracked): ~317,577 | deleted: ~47,665")
    bullet(p, "Attributed composer lines added: ~172,314 | human lines added (tracker): ~333")
    bullet(p, "Note: AI%% on scored commits is high and biased toward Agent-heavy workflows --- do NOT put raw AI%% on a job resume.")

    h2(p, "Git activity (Desktop scan, author match 'ojas')")
    bullet(p, "~1,077 commits matching author 'ojas' across ~16 local repos scanned")
    bullet(p, "Top: LogiFlow (~436), Ojas-Srivastava05 (~150), TLE Eliminators (~123), Resume Optimiser (~97), Portfolio (~79)")

    h2(p, "Resume-safe framing (recommended)")
    para(
        p,
        "Recruiters care about shipped outcomes, not token counts. Prefer: Cursor Pro daily user; "
        "Agent/Composer for multi-file shipping; MCP to GitHub/Supabase/Vercel/Firebase/Redis; "
        "skills/rules workflows; human review on every merge. Avoid: token totals, AI%% of commits, extension vanity counts.",
    )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    p.output(OUT)
    print("Wrote", OUT)


if __name__ == "__main__":
    build()
