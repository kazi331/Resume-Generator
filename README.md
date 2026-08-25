# Local Resume PDF Generator

Turns `resume-data.json` into `Resume.pdf` using pure Python — no LibreOffice,
no Word, no Node.js. One dependency (`reportlab`), one script.

This version matches the exact fonts, sizes, colors, and margins used in
the earlier Word/docx-generated resumes.

## Font note

Calibri itself is a Microsoft-licensed font that can't be freely bundled
with a script like this. Instead, `fonts/` includes **Carlito** — an
open-source (SIL Open Font License) font built specifically to be
metrically identical to Calibri (same letter widths and spacing). This is
the same substitution LibreOffice itself makes automatically when Calibri
isn't installed on a machine, so it's a well-established stand-in, not a
rough approximation. The font is embedded directly in the generated PDF,
so it'll look identical on any machine that opens it — you don't need
Carlito or Calibri installed to view the result correctly.

## One-time setup

```bash
pip install -r requirements.txt
```

(If `pip` isn't found, try `pip3`. If Python itself isn't installed, get
it from https://python.org — 3.9+ works fine.)

## Usage

Whenever I tailor your resume for a new JD going forward, I'll give you the
full updated content of `resume-data.json` directly in chat — just replace
the file's contents with what I give you, then run:

```bash
python generate_resume.py
```

This writes `Resume.pdf` in the same folder. Takes under a second, no
internet connection needed after the initial `pip install`.

## Editing content yourself

Same as before — `resume-data.json` is plain, readable fields:

- `name`, `title`, `location`, `phone`, `email` — header info
- `links` — list of `{text, url}` pairs (GitHub, LinkedIn, site)
- `summary` — one paragraph
- `skills` — list of `{label, value}` rows
- `experience` — list of jobs, each with `title`, `dates`, `company`,
  optional `companyLink` (`{text, url}` or `null`), and a `bullets` list
- `projects` — list with `title`, optional `link` (or `null`), `description`, `stack`
- `education` — list of `{degree, school}`
- `languages` — one line
- `references` — list of `{name, title, email}`

Edit any field, save, re-run the script. If a job has no company link, set
`"companyLink": null`. If a project has no live link, set `"link": null`.

## Changing the design (fonts, colors, spacing, margins)

Open `generate_resume.py` — everything under the `LAYOUT SETTINGS` comment
near the top controls appearance:

- `NAVY_HEX`, `GRAY_HEX`, `LINK_HEX`, `LIGHTLINE_HEX` — colors
- `MARGIN_TOP`/`BOTTOM`/`LEFT`/`RIGHT` — page margins
- `SIZE` — font sizes in points for each element
- The `styles` dictionary — line spacing (`leading`) and spacing
  before/after each element (`spaceBefore`/`spaceAfter`), in points

If content grows and it spills to a second page, either trim a bullet or
two, or shave a bit off the relevant `SIZE` entries and re-run. The script
doesn't warn you about page count — open the PDF after any edit to check.

## Why this instead of the old Node.js + LibreOffice setup

That version needed two separate tools (Node.js for building the .docx,
LibreOffice for converting it to PDF) and produced a .docx you didn't need.
This version is one Python script that goes straight to PDF, with the
fonts bundled in, so there's nothing else to install.

## Folder structure

```
local-resume-pdf/
├── resume-data.json     ← edit this for content changes
├── generate_resume.py   ← layout/logic (rarely needs touching)
├── requirements.txt
├── fonts/               ← bundled Carlito font files + OFL license
└── Resume.pdf           ← generated output
```

