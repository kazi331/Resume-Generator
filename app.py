"""
Web app version of the resume generator.

Local run:
    pip install -r requirements.txt
    python app.py
    -> open http://localhost:5000

Deployment: see README.md for hosting options (Render, Railway, PythonAnywhere, Fly.io).
"""

import io
import json
import os
from typing import Any

from flask import Flask, jsonify, render_template, request, send_file

from resume_pdf import build_resume_pdf, slugify_filename

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROFILES: dict[str, dict[str, str]] = {
    "fullstack": {"label": "Full Stack", "filename": "resume-data-fullstack.json"},
    "frontend": {"label": "Frontend", "filename": "resume-data-frontend.json"},
}


def profile_path(profile: str) -> str:
    if profile not in PROFILES:
        raise KeyError(profile)
    return os.path.join(BASE_DIR, PROFILES[profile]["filename"])


def load_data(profile: str) -> str:
    with open(profile_path(profile), "r", encoding="utf-8") as f:
        return f.read()


def save_data(profile: str, raw_text: str) -> Any:
    # Validate it's parseable JSON before persisting
    parsed = json.loads(raw_text)
    with open(profile_path(profile), "w", encoding="utf-8") as f:
        json.dump(parsed, f, indent=2, ensure_ascii=False)
    return parsed


@app.route("/", methods=["GET"])
def index():
    current_profile = "fullstack"
    return render_template(
        "index.html",
        resume_json=load_data(current_profile),
        profiles=PROFILES,
        current_profile=current_profile,
    )


@app.route("/profile/<profile>", methods=["GET"])
def profile(profile: str):
    try:
        return jsonify(json.loads(load_data(profile)))
    except (KeyError, json.JSONDecodeError):
        return jsonify({"error": "Unknown or invalid resume profile."}), 404


@app.route("/download", methods=["GET"])
def download_default_resume():
    """Download the default full-stack resume."""
    try:
        data = json.loads(load_data("fullstack"))
        pdf_bytes = build_resume_pdf(data)
    except (json.JSONDecodeError, KeyError) as error:
        return jsonify({"error": f"Unable to generate resume: {error}"}), 500

    filename = slugify_filename(data.get("title", "full-stack-resume"))

    return send_file(
        io.BytesIO(pdf_bytes),
        mimetype="application/pdf",
        as_attachment=True,
        download_name=filename,
    )


@app.route("/generate", methods=["POST"])
def generate():
    raw_text = request.form.get("resume_json", "")
    selected_profile = request.form.get("profile", "fullstack")
    try:
        # data = save_data(selected_profile, raw_text) # changes file content
        data = json.loads(raw_text)
    except KeyError:
        return jsonify({"error": "Unknown resume profile."}), 400
    except json.JSONDecodeError as e:
        return jsonify({"error": f"Invalid JSON: {e}"}), 400

    try:
        pdf_bytes = build_resume_pdf(data)
    except KeyError as e:
        return jsonify({"error": f"Missing required field: {e}"}), 400

    filename = slugify_filename(data.get("title", ""))
    return send_file(
        io.BytesIO(pdf_bytes),
        mimetype="application/pdf",
        as_attachment=True,
        download_name=filename,
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=port, debug=True)
