"""
Shared resume-PDF-building logic. Used by both generate_resume.py (CLI)
and app.py (web app) so there's exactly one place styling/layout lives.
"""
import os
import re
import io
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
_FONTS_REGISTERED = False


def _register_fonts():
    global _FONTS_REGISTERED
    if _FONTS_REGISTERED:
        return
    pdfmetrics.registerFont(TTFont("Calibri", os.path.join(FONT_DIR, "Carlito-Regular.ttf")))
    pdfmetrics.registerFont(TTFont("Calibri-Bold", os.path.join(FONT_DIR, "Carlito-Bold.ttf")))
    pdfmetrics.registerFont(TTFont("Calibri-Italic", os.path.join(FONT_DIR, "Carlito-Italic.ttf")))
    pdfmetrics.registerFont(TTFont("Calibri-BoldItalic", os.path.join(FONT_DIR, "Carlito-BoldItalic.ttf")))
    pdfmetrics.registerFontFamily(
        "Calibri", normal="Calibri", bold="Calibri-Bold",
        italic="Calibri-Italic", boldItalic="Calibri-BoldItalic"
    )
    _FONTS_REGISTERED = True


# ---------- LAYOUT SETTINGS — matches the Word/docx version exactly ----------
NAVY_HEX = "#1F2D3D"
GRAY_HEX = "#3A3A3A"
LINK_HEX = "#1F4E8C"
LIGHTLINE_HEX = "#AAAAAA"
NAVY = colors.HexColor(NAVY_HEX)
GRAY = colors.HexColor(GRAY_HEX)
LIGHTLINE = colors.HexColor(LIGHTLINE_HEX)
FONT = "Calibri"
FONT_BOLD = "Calibri-Bold"
FONT_ITALIC = "Calibri-Italic"

MARGIN_TOP = 460 / 1440 * inch
MARGIN_BOTTOM = 420 / 1440 * inch
MARGIN_LEFT = 620 / 1440 * inch
MARGIN_RIGHT = 620 / 1440 * inch

SIZE = {
    "name": 18, "title": 10.5, "contact": 8.5, "section": 9.5,
    "body": 9, "bullet": 9, "job_title": 9.5, "job_dates": 8.5,
    "company": 8.5, "small": 8,
}


def _styles():
    return {
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


def _link_run(text, url):
    return f'<link href="{url}"><font color="{LINK_HEX}"><u>{text}</u></font></link>'


def _section_heading(text, styles):
    return [
        Paragraph(text.upper(), styles["section"]),
        HRFlowable(width="100%", thickness=0.75, color=NAVY, spaceAfter=3),
    ]


def slugify_filename(text, suffix="_Resume.pdf", fallback="Resume"):
    """
    Turns an arbitrary title (which may contain dashes, slashes, em dashes,
    etc.) into a safe filename. This is what was missing before — em dashes
    (—) and slashes (/) are valid in a job title string but not in a
    filename, which is exactly what caused the FileNotFoundError.
    """
    if not text:
        text = fallback
    # Replace anything that isn't a letter, digit, space, or hyphen with a space
    cleaned = re.sub(r"[^\w\s-]", " ", text, flags=re.UNICODE)
    # Collapse whitespace/hyphen runs into a single underscore
    cleaned = re.sub(r"[\s-]+", "_", cleaned).strip("_")
    if not cleaned:
        cleaned = fallback
    return f"{cleaned}{suffix}"


def build_resume_pdf(data, output_path=None):
    """
    Builds the resume PDF from a resume-data dict.
    If output_path is given, writes to that path and returns the path.
    If output_path is None, returns the PDF as bytes (for web app use).
    """
    _register_fonts()
    styles = _styles()
    story = []

    story.append(Paragraph(data["name"], styles["name"]))
    story.append(Paragraph(data["title"], styles["title"]))
    story.append(Paragraph(
        f'{data["location"]}  |  {data["phone"]}  |  {_link_run(data["email"], "mailto:" + data["email"])}',
        styles["contact"]
    ))
    link_parts = [_link_run(l["text"], l["url"]) for l in data["links"]]
    story.append(Paragraph("  |  ".join(link_parts), styles["contact"]))
    story.append(Spacer(1, 3))
    # story.append(HRFlowable(width="100%", thickness=0.75, color=LIGHTLINE, spaceAfter=4))

    story += _section_heading("Summary", styles)
    story.append(Paragraph(data["summary"], styles["body"]))

    story += _section_heading("Core Skills", styles)
    for s in data["skills"]:
        story.append(Paragraph(f'<b><font color="{NAVY_HEX}">{s["label"]}:</font></b> {s["value"]}',
                                styles["body"]))

    story += _section_heading("Work Experience", styles)
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
            company_text = f'{job["company"]} ({_link_run(job["companyLink"]["text"], job["companyLink"]["url"])})'
        else:
            company_text = job["company"]
        story.append(Paragraph(company_text, styles["company"]))

        bullets = [ListItem(Paragraph(b, styles["bullet"]), spaceAfter=1) for b in job["bullets"]]
        story.append(ListFlowable(bullets, bulletType="bullet", start="•",
                                   leftIndent=12, bulletFontName=FONT, bulletFontSize=SIZE["bullet"]))

    story += _section_heading("Key Projects", styles)
    for p in data["projects"]:
        title_html = _link_run(p["title"], p["link"]) if p.get("link") else f'<b><font color="{NAVY_HEX}">{p["title"]}</font></b>'
        story.append(Paragraph(
            f'{title_html}: {p["description"]} <font color="{GRAY_HEX}"><i>Stack: {p["stack"]}</i></font>',
            styles["body"]
        ))
        story.append(Spacer(1, 1.5))

    story += _section_heading("Education & Languages", styles)
    edu_text = "   |   ".join(f'{e["degree"]} — {e["school"]}' for e in data["education"])
    story.append(Paragraph(edu_text, styles["company"]))
    story.append(Paragraph(data["languages"], styles["company"]))

    story += _section_heading("References", styles)
    ref_text = "   |   ".join(f'{r["name"]} — {r["title"]} — {r["email"]}' for r in data["references"])
    story.append(Paragraph(ref_text, styles["small"]))

    doc_kwargs = dict(
        pagesize=letter,
        topMargin=MARGIN_TOP, bottomMargin=MARGIN_BOTTOM,
        leftMargin=MARGIN_LEFT, rightMargin=MARGIN_RIGHT,
        title=f'{data["name"]} - Resume'
    )

    if output_path:
        doc = SimpleDocTemplate(output_path, **doc_kwargs)
        doc.build(story)
        return output_path
    else:
        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, **doc_kwargs)
        doc.build(story)
        return buf.getvalue()
