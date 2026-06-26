#!/usr/bin/env python3
"""Generate minimal NPTEL / SVNIT research brief PDF."""

from pathlib import Path

from fpdf import FPDF

OUT = Path(__file__).resolve().parents[1] / "NPTEL-MOOC-Research-SVNIT-NPTEL.pdf"


class Brief(FPDF):
    def footer(self):
        self.set_y(-12)
        self.set_font("Helvetica", "", 8)
        self.set_text_color(100, 100, 100)
        self.cell(0, 8, "Ojas Srivastava", align="C")


def body(pdf: FPDF):
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(20, 20, 20)
    pdf.multi_cell(0, 8, "NPTEL MOOC Courses at SVNIT\nA Brief Research Note", align="L")
    pdf.ln(2)

    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(0, 5, "Prepared for UG elective planning  |  July-December 2026 cycle", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    sections = [
        (
            "1. What This Is",
            [
                "NPTEL (National Programme on Technology Enhanced Learning) offers online courses "
                "coordinated by IIT Madras on behalf of SWAYAM, the Government of India MOOC platform. "
                "Courses are taught by IIT/IISc faculty, run for 8 or 12 weeks, and include weekly "
                "assignments plus a proctored certification exam.",
                "The department PDF lists approved courses for the Jul-Dec 2026 NPTEL run "
                "(noc26-*). The Google Form collects student preferences from that list so the "
                "department can coordinate registration and elective mapping.",
            ],
            ["1", "2", "3"],
        ),
        (
            "2. Relation to Your Semester",
            [
                "At SVNIT, NPTEL/SWAYAM courses approved by the Departmental Academic Advisory "
                "Committee (DAAC) may count toward degree requirements - typically as a department "
                "elective (DE) or open elective (OE), not as an extra subject on top of the regular load.",
                "Only courses on the institute-approved list qualify for credit transfer. Choosing a "
                "random NPTEL course without departmental approval may yield a certificate but not "
                "SVNIT credits.",
            ],
            ["4", "5"],
        ),
        (
            "3. Examination",
            [
                "Students must enroll on the NPTEL portal, register separately for the exam, and pay "
                "the exam fee. Evaluation: 25 marks from weekly assignments; 75 marks from an "
                "in-person proctored MCQ exam at a designated centre.",
                "Pass criteria (both required): minimum 10/25 in assignments AND 30/75 in the final "
                "exam; overall score at least 40/100. This is NPTEL's exam, not SVNIT's regular "
                "end-semester examination.",
            ],
            ["1", "2"],
        ),
        (
            "4. Marksheet & Credit Transfer",
            [
                "Credits are not automatic. After passing, submit the NPTEL e-certificate and score "
                "to the department/academic office. SVNIT maps the result to a grade on the regular "
                "grade card (transcript).",
                "Standard NPTEL credit equivalence: 12-week course ~ 3 credits; 8-week ~ 2 credits; "
                "4-week ~ 1 credit. During enrollment, select SVNIT as the SWAYAM local chapter "
                "so results are shared with the institute.",
            ],
            ["1", "2", "4"],
        ),
        (
            "5. Key Dates (Jul-Dec 2026 batch, main cohort)",
            [
                "Course window: 20 Jul 2026 - 9 Oct 2026  |  Enrollment deadline: 27 Jul 2026  |  "
                "Exam registration deadline: 14 Aug 2026  |  Exams: mid-late Oct 2026 (course-specific).",
            ],
            ["6"],
        ),
        (
            "6. Practical Checklist",
            [
                "Confirm with your professor which elective slot (DE/OE) your chosen course replaces.",
                "Fill the Google Form with a course from the approved PDF only.",
                "Enroll at onlinecourses.nptel.ac.in; select Local Chapter = Yes, college = SVNIT Surat.",
                "Complete assignments, register for and pass the NPTEL exam, then submit certificate "
                "to the department for credit transfer.",
            ],
            ["4"],
        ),
    ]

    for title, paragraphs, cites in sections:
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(30, 30, 30)
        pdf.cell(0, 7, title, new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(40, 40, 40)
        for para in paragraphs:
            pdf.multi_cell(0, 5.2, para)
            pdf.ln(1)
        pdf.set_font("Helvetica", "I", 8)
        pdf.set_text_color(90, 90, 90)
        pdf.cell(0, 4, f"Sources: [{', '.join(cites)}]", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(3)

    pdf.add_page()
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(20, 20, 20)
    pdf.cell(0, 8, "References", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    refs = [
        (
            "[1] NPTEL Online Certification FAQ",
            "https://archive.nptel.ac.in/noc/noc_faq.html",
            "Credit equivalence, exam format, pass criteria, local chapter registration.",
        ),
        (
            "[2] NPTEL Online Courses Portal",
            "https://onlinecourses.nptel.ac.in",
            "Course enrollment and exam registration.",
        ),
        (
            "[3] NPTEL Local Chapters",
            "https://nptel.ac.in/LocalChapter",
            "Institute participation and result sharing with colleges.",
        ),
        (
            "[4] SVNIT NPTEL Local Chapter",
            "https://www.svnit.ac.in/web/nptel.php",
            "SVNIT contact: ic_ccc@svnit.ac.in (Institute Continuing Education Cell).",
        ),
        (
            "[5] SVNIT B.Tech Regulations (NEP 2020 Annexure)",
            "https://www.svnit.ac.in/Data/Notice/2023/June/Regulation-2023-24-SVNIT-Annexure-62.1.pdf",
            "Institute credit framework; MOOC/NPTEL referenced for coursework.",
        ),
        (
            "[6] Department course list (Jul-Dec 2026 UG)",
            "NPTEL-MOOC-Courses-for-UG-July-December-2026 (department PDF)",
            "Approved noc26 course roster, dates, and elective/core tags.",
        ),
    ]

    for label, url, note in refs:
        pdf.set_x(pdf.l_margin)
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_text_color(30, 30, 30)
        pdf.multi_cell(0, 4.5, label)
        pdf.set_x(pdf.l_margin)
        pdf.set_font("Helvetica", "", 8)
        pdf.set_text_color(0, 80, 160)
        for chunk in _wrap_url(url, 95):
            pdf.multi_cell(0, 4, chunk)
        pdf.set_x(pdf.l_margin)
        pdf.set_text_color(60, 60, 60)
        pdf.multi_cell(0, 4.5, note)
        pdf.ln(2)


def _wrap_url(url: str, width: int) -> list[str]:
    if len(url) <= width:
        return [url]
    parts = []
    while len(url) > width:
        cut = url.rfind("/", 0, width)
        if cut < width // 2:
            cut = width
        parts.append(url[:cut])
        url = url[cut:].lstrip("/")
        if url:
            url = "/" + url
    if url:
        parts.append(url)
    return parts


def main():
    pdf = Brief()
    pdf.set_margins(20, 20, 20)
    body(pdf)
    pdf.output(str(OUT))
    print(OUT)


if __name__ == "__main__":
    main()
