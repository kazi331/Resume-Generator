"""
Web app version of the resume generator.

Local run:
    pip install -r requirements.txt
    python app.py
    -> open http://localhost:5000

Deployment: see README.md for hosting options (Render, Railway, PythonAnywhere, Fly.io).
"""
import json
import os
from flask import Flask, render_template, request, send_file, jsonify
import io

from resume_pdf import build_resume_pdf, slugify_filename

app = Flask(__name__)

DATA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resume-data.json")


def load_data():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return f.read()


def save_data(raw_text):
    # Validate it's parseable JSON before persisting
    parsed = json.loads(raw_text)
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(parsed, f, indent=2, ensure_ascii=False)
    return parsed


@app.route("/", methods=["GET"])
def index():
    current_json = load_data()
    return render_template("index.html", resume_json=current_json)


@app.route("/generate", methods=["POST"])
def generate():
    raw_text = request.form.get("resume_json", "")
    try:
        data = save_data(raw_text)
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
