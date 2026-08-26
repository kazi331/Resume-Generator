# Resume PDF Generator

Turns resume content into `Resume.pdf` using pure Python (`reportlab`) —
no LibreOffice, no Word, no Node.js. Matches the exact fonts, sizes,
colors, and margins used throughout this project.

Two ways to use it:
- **CLI** (`generate_resume.py`) — edit a JSON file, run a script.
- **Web app** (`app.py`) — a form in your browser, paste and click, PDF downloads.
  Same underlying code (`resume_pdf.py`), so output is identical either way.

## Font note

Calibri itself is Microsoft-licensed and can't be freely bundled. `fonts/`
instead includes **Carlito** — an open-source (SIL OFL) font built to be
metrically identical to Calibri. This is the same substitution LibreOffice
makes automatically when Calibri isn't installed. The font is embedded
directly in the PDF, so it displays correctly on any machine.

## One-time setup

```bash
pip install -r requirements.txt
```

(Use `pip3` if `pip` isn't found. Get Python 3.9+ from https://python.org
if you don't have it.)

## Option A — Command line

```bash
python generate_resume.py
```

Reads `resume-data.json`, writes `<Title>_Resume.pdf` in the same folder.
Whenever I tailor your resume for a new JD, I'll give you the full updated
`resume-data.json` content to paste in before you re-run this.

## Option B — Web app (run locally)

```bash
python app.py
```

Then open **http://localhost:5000**. You'll see a textarea pre-filled with
your current resume data — edit it, click **Generate & Download PDF**, and
the browser downloads the file directly. Every generate also saves your
edits back into `resume-data.json`, so the next time you open the page (or
run the CLI), it starts from your latest version.

## Hosting it somewhere (so you don't run anything locally)

This is a standard Flask app, so any Python host works. A few
straightforward, free-tier-friendly options:

### Render.com (easiest)
1. Push this folder to a GitHub repo.
2. On Render: **New → Web Service**, connect the repo.
3. Build command: `pip install -r requirements.txt`
4. Start command: `gunicorn app:app` (already in the included `Procfile`,
   Render detects this automatically)
5. Deploy — Render gives you a public URL.

### Railway.app
1. Push to GitHub, then **New Project → Deploy from GitHub repo** on Railway.
2. Railway auto-detects the `Procfile` and `requirements.txt` — no config needed.
3. Deploy — Railway gives you a public URL.

### PythonAnywhere (good if you want a permanently free tier)
1. Upload the folder (or `git clone` your repo) in a Bash console there.
2. `pip install -r requirements.txt --user`
3. Set up a new Flask web app pointing at `app.py` in the dashboard's
   "Web" tab (PythonAnywhere's wizard asks for the entry file — pick this
   one and the `app` variable inside it).

### Fly.io
Needs a `Dockerfile`, which isn't included here since the above three are
simpler for this size of app — ask if you'd like one added.

## Persisted data across restarts

`resume-data.json` is a plain file on disk. On most free hosting tiers,
the filesystem resets on redeploy, so treat the web form as a place to
*generate* PDFs, not as permanent storage — keep the JSON you're actively
using saved on your own machine too (or in the repo you deployed from) so
a redeploy doesn't lose your latest edits.

## Editing content

`resume-data.json` fields:

- `name`, `title`, `location`, `phone`, `email` — header info
- `links` — list of `{text, url}` pairs (GitHub, LinkedIn, site)
- `summary` — one paragraph
- `skills` — list of `{label, value}` rows
- `experience` — list of jobs: `title`, `dates`, `company`, optional
  `companyLink` (`{text, url}` or `null`), and a `bullets` list
- `projects` — list: `title`, optional `link` (or `null`), `description`, `stack`
- `education` — list of `{degree, school}`
- `languages` — one line
- `references` — list of `{name, title, email}`

## Changing the design

Open `resume_pdf.py` — the `LAYOUT SETTINGS` section near the top controls
colors (`NAVY_HEX`, `GRAY_HEX`, `LINK_HEX`), margins (`MARGIN_TOP` etc.),
and font sizes (`SIZE` dict). Both the CLI and web app pick up changes
here automatically since they share this one file.

If content grows past one page, trim a bullet or shave a bit off the
`SIZE` values — neither the script nor the web app warns about page count,
so check the output after edits.

## Folder structure

```
local-resume-pdf/
├── resume_pdf.py         ← shared PDF-building logic (fonts, layout, styling)
├── generate_resume.py    ← CLI entry point
├── app.py                ← web app entry point
├── templates/index.html  ← web form UI
├── resume-data.json      ← your content — edit this
├── requirements.txt
├── Procfile               ← for Render/Railway-style deploys
└── fonts/                ← bundled Carlito font files + OFL license
```
