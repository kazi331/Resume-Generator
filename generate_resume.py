"""
CLI entry point: builds a PDF from the Full Stack resume profile.

Usage:
    pip install -r requirements.txt
    python generate_resume.py
"""

import json

from resume_pdf import build_resume_pdf, slugify_filename

with open("resume-data-fullstack.json", "r", encoding="utf-8") as f:
    data = json.load(f)

filename = slugify_filename(data["title"])
build_resume_pdf(data, output_path=filename)
print(f"{filename} written.")
