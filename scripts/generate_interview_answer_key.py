#!/usr/bin/env python3
"""Generate 1:1 mapped interview answer key PDF for Ojas Srivastava."""

from __future__ import annotations

from datetime import date
from pathlib import Path

from generate_brutal_interview_prep import latex_escape
from interview_answer_bank import resolve_answer
from interview_questions_shared import (
    CODING_PROBLEMS,
    COMPANY_EXTRA,
    CS_FUNDAMENTALS,
    EXTRA_BEHAVIORAL,
    HR_LOGISTICS,
    HR_SCREEN,
    INTERNET_BY_COMPANY,
    LEADERSHIP,
    MOCK_SCRIPTS,
    PANEL_STRESS,
    PROJECT_QUESTIONS,
    QUESTIONS_TO_ASK,
    RAPID_FIRE,
    RED_TEAM,
    RESUME_LINES,
    TRAP_QUESTIONS,
    UNIVERSAL_BEHAVIORAL,
)
from interview_questions_shared import COMPANIES

OUT_TEX = (
    Path(__file__).resolve().parents[1]
    / "Reference Collection"
    / "Planning"
    / "ojas_interview_answer_key.tex"
)


def qa_block(question: str, answer: str, label: str = "Q") -> str:
    return (
        f"\\textbf{{{label}:}} {latex_escape(question)}\n\n"
        f"\\begin{{quote}}\\small\\textbf{{Say:}} {latex_escape(answer)}\\end{{quote}}\n"
        "\\vspace{2mm}\n"
    )


def qa_pair(question: str, followups: list[str], company: str | None = None) -> str:
    parts = [qa_block(question, resolve_answer(question, company=company), "Q")]
    for i, fu in enumerate(followups, 1):
        parts.append(
            qa_block(
                fu,
                resolve_answer(fu, company=company, is_followup=True, parent=question),
                f"FU{i}",
            )
        )
    return "".join(parts)


def qblock_answered(title: str, questions: list[tuple[str, list[str]]], company: str | None = None) -> str:
    out = [f"\\subsection{{{latex_escape(title)}}}\n"]
    for q, fus in questions:
        out.append(qa_pair(q, fus, company=company))
    return "".join(out)


def main() -> None:
    lines: list[str] = []
    a = lines.append

    a(r"""\documentclass[9pt,a4paper]{article}
\usepackage[margin=1.6cm]{geometry}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage{enumitem}
\usepackage{booktabs}
\usepackage{longtable}
\usepackage{hyperref}
\usepackage{fancyhdr}
\usepackage{titlesec}
\usepackage{xcolor}

\definecolor{qcolor}{RGB}{120,0,0}
\definecolor{acolor}{RGB}{0,80,120}

\pagestyle{fancy}
\fancyhf{}
\fancyhead[L]{\small Ojas Srivastava --- Interview Answer Key}
\fancyhead[R]{\small """ + date.today().strftime("%d %b %Y") + r"""}
\fancyfoot[C]{\thepage}

\titleformat{\section}{\large\bfseries\color{qcolor}}{}{0em}{}[\titlerule]
\titleformat{\subsection}{\normalsize\bfseries}{}{0em}{}
\setlist{nosep}

\begin{document}
""")

    a(r"""
\begin{center}
{\LARGE\bfseries Interview Answer Key}\\[4pt]
{\large Ojas Srivastava --- 1:1 Mapped to Brutal Interview Simulation}\\[2pt]
{\small Every question has a spoken answer. Read aloud until natural. Numbers must match resume.}\\[4pt]
{\color{acolor}\textit{Companion to \texttt{ojas\_brutal\_interview\_simulation.pdf}}}
\end{center}

\tableofcontents
\newpage

\section{How to Use This Answer Key}
\begin{enumerate}
  \item Find the section matching your mock (company, HackerRank screen, project deep-dive).
  \item Read \textbf{Say:} blocks out loud; time yourself (60--90s behavioral, 30s rapid-fire).
  \item Replace \texttt{[COMPANY]} with the company name before the interview.
  \item If interrupted, jump to the relevant \textbf{FU} answer immediately.
\end{enumerate}

\newpage
\section{Universal Behavioral + Resume Integrity}
""")
    a(qblock_answered("Every company will ask these", UNIVERSAL_BEHAVIORAL))

    a(r"\newpage\section{Computer Science Fundamentals}" + "\n")
    for area, qs in CS_FUNDAMENTALS:
        items = [
            (q, ["Go deeper.", "Give a number from your project.", "What breaks at scale?"])
            for q in qs
        ]
        a(qblock_answered(area, items))

    a(r"\newpage\section{Project Deep-Dive Answers}" + "\n")
    for proj, qs in PROJECT_QUESTIONS.items():
        a(qblock_answered(proj, qs))

    a(r"\newpage\section{Company-Specific Answers}" + "\n")
    for c in COMPANIES:
        name = c["name"]
        a(f"\\subsection{{{latex_escape(name)} --- {latex_escape(c['role'])}}}\n")
        extras = COMPANY_EXTRA.get(name, [])
        if extras:
            a(qblock_answered(f"{name} targeted", extras, company=name))
        generic = [
            (f"Why {name}?", [f"Why not a competitor of {name}?", "What did you read about our stack last week?"]),
            (
                f"What would you build in your first 30 days at {name}?",
                ["How is that not arrogant for an intern?", "Dependencies on onboarding?"],
            ),
            (
                "Tell me about LogiFlow in 2 minutes.",
                ["Interrupt at 60s: get to YOUR contribution only.", "What would you rebuild?"],
            ),
        ]
        a(qblock_answered(f"{name} standard probes", generic, company=name))
        a("\\newpage\n")

    a(r"\section{HackerRank AI Screen --- Full Answers}" + "\n")
    a(qblock_answered("Screen question bank", HR_SCREEN))

    a(r"\newpage\section{Internet-Sourced Question Answers}" + "\n")
    for company, blocks in INTERNET_BY_COMPANY.items():
        a(f"\\subsection{{{latex_escape(company)}}}\n")
        for title, probes in blocks:
            a(qa_block(title, resolve_answer(title, company=company), "Topic"))
            for i, probe in enumerate(probes, 1):
                a(
                    qa_block(
                        probe,
                        resolve_answer(probe, company=company, is_followup=True, parent=title),
                        f"Probe{i}",
                    )
                )

    a(r"\newpage\section{Extended Behavioral Answers}" + "\n")
    a(qblock_answered("Round 2 HR + Hiring Manager", EXTRA_BEHAVIORAL))

    a(r"\section{HR + Logistics Answers}" + "\n")
    a(qblock_answered("Logistics", HR_LOGISTICS))

    a(r"\section{Resume Line-by-Line Answers}" + "\n")
    a(qblock_answered("BATCH-6 bullets", RESUME_LINES))

    a(r"\section{Leadership + POR Answers}" + "\n")
    a(qblock_answered("ACM SVNIT / Nexus", LEADERSHIP))

    a(r"\newpage\section{Rapid-Fire Answers (30 seconds each)}" + "\n")
    for i, rf in enumerate(RAPID_FIRE, 1):
        a(qa_block(rf, resolve_answer(rf), f"RF{i}"))

    a(r"\newpage\section{Trap Questions --- Exact Responses}" + "\n")
    for i, (trap, _) in enumerate(TRAP_QUESTIONS, 1):
        a(qa_block(trap, resolve_answer(trap), f"Trap{i}"))

    a(r"\section{Questions YOU Should Ask (with intent)}" + "\n")
    for i, q in enumerate(QUESTIONS_TO_ASK, 1):
        a(qa_block(q, resolve_answer(q), f"Ask{i}"))

    a(r"\newpage\section{Mock Script Interruption Answers}" + "\n")
    for mock in MOCK_SCRIPTS:
        a(f"\\subsection{{{latex_escape(mock['title'])}}}\n")
        a("\\textbf{Flow prompts:}\n\\begin{enumerate}\n")
        for slot, action in mock["flow"]:
            ans = resolve_answer(action, company=mock["title"])
            a(f"  \\item \\textbf{{{latex_escape(slot)}}}: {latex_escape(action)}\\\\\n")
            a(f"  \\textit{{Say:}} {latex_escape(ans)}\n")
        a("\\end{enumerate}\n")
        a("\\textbf{Brutal interruptions:}\n")
        for j, moment in enumerate(mock["brutal_moments"], 1):
            clean = moment.strip("'")
            a(qa_block(clean, resolve_answer(clean), f"Int{j}"))

    a(r"\newpage\section{Red-Team Counter Answers}" + "\n")
    for i, (tactic, desc) in enumerate(RED_TEAM, 1):
        q = f"{tactic}: {desc}"
        a(qa_block(q, resolve_answer(q), f"RT{i}"))

    a(r"\section{Panel Stress Interview Answers}" + "\n")
    for i, item in enumerate(PANEL_STRESS, 1):
        a(qa_block(item, resolve_answer(item), f"PS{i}"))

    a(r"\newpage\section{OA / Coding Problem Talking Tracks}" + "\n")
    for tag, probs in CODING_PROBLEMS:
        a(f"\\subsection{{{latex_escape(tag)}}}\n")
        for j, p in enumerate(probs, 1):
            q = f"{p} --- approach, complexity, edge cases"
            a(qa_block(p, resolve_answer(q), f"P{j}"))

    a(r"\newpage\section{STAR Story Scripts (Pre-Filled)}" + "\n")
    star_stories = [
        "IFFCO production delivery under mentor oversight",
        "LogiFlow latency crisis during Solution Challenge",
        "Community Hero solo ship under hackathon deadline",
        "OA Forge security/scoping decision",
        "ACM/Nexus mentoring breakthrough",
        "Code review conflict resolution",
        "Failed approach you pivoted from",
    ]
    for story in star_stories:
        a(f"\\subsection{{{latex_escape(story)}}}\n")
        a(qa_block(f"Tell me about: {story}", resolve_answer(story), "Prompt"))

    a(r"\newpage\section{Verbatim Mock Transcript Answers}" + "\n")
    transcript_qs = [
        "What happens when I click Pay on a Stripe Checkout page?",
        "What did you own at IFFCO?",
        "LogiFlow 100 to 400 ms. Measured how?",
        "If Redis evaporates?",
        "Implement rate limiter, 10 req/sec per API key.",
        "Why Stripe over building payments yourself?",
        "Why healthcare software if your projects are logistics and civic apps?",
        "Walk SDLC for one IFFCO feature.",
        "Workday says B.S. Computer Science. Resume B.Tech AI. Explain.",
        "How do you test software where mistakes hurt patients?",
        "OA Forge judge sandbox escape in 30 seconds.",
        "std::vector reallocation what invalidates?",
        "Parse 10M integers from stdin fast outline.",
        "Why trading?",
        "Summarize LogiFlow in 30 seconds.",
    ]
    for i, tq in enumerate(transcript_qs, 1):
        a(qa_block(tq, resolve_answer(tq), f"T{i}"))

    a(r"""
\vfill
\begin{center}
\textit{Generated for Ojas Srivastava --- Resume Optimiser repo --- """ + date.today().strftime("%B %Y") + r"""}\\
\small Practice: question $\rightarrow$ answer without reading $\rightarrow$ interview.
\end{center}
\end{document}
""")

    OUT_TEX.parent.mkdir(parents=True, exist_ok=True)
    OUT_TEX.write_text("".join(lines), encoding="utf-8")
    print(f"Wrote {OUT_TEX} ({len(lines)} chunks, {OUT_TEX.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
