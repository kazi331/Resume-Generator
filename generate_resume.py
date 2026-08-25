"""
Generates Resume.pdf from resume-data.json using reportlab only.
No LibreOffice, no Word, no Node.js — one Python script, two dependencies.

Font note: Calibri itself is a Microsoft-licensed font and can't be freely
redistributed. This script uses Carlito instead, bundled in fonts/ — it's
an open-source (SIL OFL) font specifically designed to be metrically
identical to Calibri (same letter widths/spacing), which is also exactly
what LibreOffice itself substitutes when Calibri isn't installed. Visually
it's a match; it just isn't literally the Microsoft file.

Usage:
    pip install reportlab
    python generate_resume.py

Output: Resume.pdf in the same folder.
"""
import json
import os
import re
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, ListFlowable, ListItem
)
from reportlab.lib.styles import ParagraphStyle

# ---------- FONT REGISTRATION ----------
FONT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")
pdfmetrics.registerFont(TTFont("Calibri", os.path.join(FONT_DIR, "Carlito-Regular.ttf")))
pdfmetrics.registerFont(TTFont("Calibri-Bold", os.path.join(FONT_DIR, "Carlito-Bold.ttf")))
pdfmetrics.registerFont(TTFont("Calibri-Italic", os.path.join(FONT_DIR, "Carlito-Italic.ttf")))
pdfmetrics.registerFont(TTFont("Calibri-BoldItalic", os.path.join(FONT_DIR, "Carlito-BoldItalic.ttf")))
pdfmetrics.registerFontFamily(
    "Calibri", normal="Calibri", bold="Calibri-Bold",
    italic="Calibri-Italic", boldItalic="Calibri-BoldItalic"
)

# ---------- LAYOUT SETTINGS — matches the Word/docx version exactly ----------
NAVY_HEX = "#1F2D3D"
GRAY_HEX = "#3A3A3A"
LINK_HEX = "#1F4E8C"
LIGHTLINE_HEX = "#AAAAAA"
NAVY = colors.HexColor(NAVY_HEX)
GRAY = colors.HexColor(GRAY_HEX)
LINK = colors.HexColor(LINK_HEX)
LIGHTLINE = colors.HexColor(LIGHTLINE_HEX)
FONT = "Calibri"
FONT_BOLD = "Calibri-Bold"
FONT_ITALIC = "Calibri-Italic"

# Same page margins as the docx version (460/420/620/620 twips)
MARGIN_TOP = 460 / 1440 * inch
MARGIN_BOTTOM = 420 / 1440 * inch
MARGIN_LEFT = 620 / 1440 * inch
MARGIN_RIGHT = 620 / 1440 * inch

# Same font sizes as the docx version (half-points -> points, i.e. /2)
SIZE = {
    "name": 18,
    "title": 10.5,
    "contact": 8.5,
    "section": 9.5,
    "body": 9,
    "bullet": 9,
    "job_title": 9.5,
    "job_dates": 8.5,
    "company": 8.5,
    "small": 8,
}

with open("resume-data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

styles = {
    "name": ParagraphStyle("name", fontName=FONT_BOLD, fontSize=SIZE["name"], leading=SIZE["name"] * 1.15,
                           textColor=NAVY, alignment=TA_CENTER, spaceAfter=1),
    "title": ParagraphStyle("title", fontName=FONT_BOLD, fontSize=SIZE["title"], leading=SIZE["title"] * 1.2,
                            textColor=GRAY, alignment=TA_CENTER, spaceBefore=2, spaceAfter=3),
    "contact": ParagraphStyle("contact", fontName=FONT, fontSize=SIZE["contact"], leading=SIZE["contact"] * 1.2,
                              textColor=GRAY, alignment=TA_CENTER, spaceAfter=1.5),
    "section": ParagraphStyle("section", fontName=FONT_BOLD, fontSize=SIZE["section"], leading=SIZE["section"] * 1.15,
                              textColor=NAVY, spaceBefore=6.5, spaceAfter=2.5),
    "body": ParagraphStyle("body", fontName=FONT, fontSize=SIZE["body"], textColor=GRAY, leading=SIZE["body"] * 1.25),
    "bullet": ParagraphStyle("bullet", fontName=FONT, fontSize=SIZE["bullet"], textColor=GRAY, leading=SIZE["bullet"] * 1.25),
    "job_title": ParagraphStyle("job_title", fontName=FONT_BOLD, fontSize=SIZE["job_title"], leading=SIZE["job_title"] * 1.15, textColor=NAVY),
    "job_dates": ParagraphStyle("job_dates", fontName=FONT_BOLD, fontSize=SIZE["job_dates"], leading=SIZE["job_dates"] * 1.15, textColor=GRAY, alignment=2),
    "company": ParagraphStyle("company", fontName=FONT_ITALIC, fontSize=SIZE["company"], leading=SIZE["company"] * 1.2, textColor=GRAY, spaceAfter=1.5),
    "small": ParagraphStyle("small", fontName=FONT, fontSize=SIZE["small"], leading=SIZE["small"] * 1.2, textColor=GRAY),
}


def link_run(text, url):
    return f'<link href="{url}"><font color="{LINK_HEX}"><u>{text}</u></font></link>'


def section_heading(text):
    return [
        Paragraph(text.upper(), styles["section"]),
        HRFlowable(width="100%", thickness=0.75, color=NAVY, spaceAfter=3),
    ]


def build():
    story = []

    # Header
    story.append(Paragraph(data["name"], styles["name"]))
    story.append(Paragraph(data["title"], styles["title"]))
    story.append(Paragraph(
        f'{data["location"]}  |  {data["phone"]}  |  {link_run(data["email"], "mailto:" + data["email"])}',
        styles["contact"]
    ))
    link_parts = [link_run(l["text"], l["url"]) for l in data["links"]]
    story.append(Paragraph("  |  ".join(link_parts), styles["contact"]))
    story.append(Spacer(1, 3))
    story.append(HRFlowable(width="100%", thickness=0.75, color=LIGHTLINE, spaceAfter=4))

    # Summary
    story += section_heading("Summary")
    story.append(Paragraph(data["summary"], styles["body"]))

    # Skills
    story += section_heading("Core Skills")
    for s in data["skills"]:
        story.append(Paragraph(f'<b><font color="{NAVY_HEX}">{s["label"]}:</font></b> {s["value"]}',
                                styles["body"]))

    # Experience
    story += section_heading("Work Experience")
    for job in data["experience"]:
        row = Table(
            [[Paragraph(job["title"], styles["job_title"]), Paragraph(job["dates"], styles["job_dates"])]],
            colWidths=[5.5 * inch, 2.0 * inch]
        )
        row.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ("TOPPADDING", (0, 0), (-1, -1), 4.5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ]))
        story.append(row)

        if job.get("companyLink"):
            company_text = f'{job["company"]} ({link_run(job["companyLink"]["text"], job["companyLink"]["url"])})'
        else:
            company_text = job["company"]
        story.append(Paragraph(company_text, styles["company"]))

        bullets = [ListItem(Paragraph(b, styles["bullet"]), spaceAfter=1) for b in job["bullets"]]
        story.append(ListFlowable(bullets, bulletType="bullet", start="•",
                                   leftIndent=12, bulletFontName=FONT, bulletFontSize=SIZE["bullet"]))

    # Projects
    story += section_heading("Key Projects")
    for p in data["projects"]:
        title_html = link_run(p["title"], p["link"]) if p.get("link") else f'<b><font color="{NAVY_HEX}">{p["title"]}</font></b>'
        story.append(Paragraph(
            f'{title_html}: {p["description"]} <font color="{GRAY_HEX}"><i>Stack: {p["stack"]}</i></font>',
            styles["body"]
        ))
        story.append(Spacer(1, 1.5))

    # Education & Languages
    story += section_heading("Education & Languages")
    edu_text = "   |   ".join(f'{e["degree"]} — {e["school"]}' for e in data["education"])
    story.append(Paragraph(edu_text, styles["company"]))
    story.append(Paragraph(data["languages"], styles["company"]))

    # References
    story += section_heading("References")
    ref_text = "   |   ".join(f'{r["name"]} — {r["title"]} — {r["email"]}' for r in data["references"])
    story.append(Paragraph(ref_text, styles["small"]))

    # Output filename and dir
    output_dir = Path("resume")
    output_dir.mkdir(exist_ok=True)
    file_title = re.sub(r'[^a-zA-Z0-9\s_-]', '', data["title"])
    file_title = re.sub(r'\s+', '_', file_title)
    output_file = output_dir / f"{file_title}-Kazi_Shariful_Islam.pdf"

    doc = SimpleDocTemplate(
        str(output_file),
        pagesize=letter,
        topMargin=MARGIN_TOP, bottomMargin=MARGIN_BOTTOM,
        leftMargin=MARGIN_LEFT, rightMargin=MARGIN_RIGHT,
        title=f'{data["name"]} - Resume',
    )
    doc.build(story)
    print(f"{output_file} written.")


if __name__ == "__main__":
    build()
