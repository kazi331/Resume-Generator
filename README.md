# Resume PDF Generator

A simple resume builder that turns structured JSON into a polished PDF.
It includes a browser editor with a live preview, so resume content can be
updated without editing templates or rebuilding the application.

## Features

- Live resume preview while editing JSON
- Full Stack and Frontend resume profiles
- Separate JSON file for each profile
- Switch profiles without losing the other profile
- Generate and download a PDF from the selected profile
- Save edits back to the selected profile
- Consistent layout, typography, spacing, and link formatting

## Run Locally

Install the dependencies once:

```bash
pip install -r requirements.txt
```

Start the web app:

```bash
python app.py
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## How To Use

1. Choose **Full Stack** or **Frontend** from the profile selector.
2. Edit or paste JSON in the editor.
3. Check the live preview for formatting and content.
4. Click **Generate & Download PDF**.

The selected profile is saved when the PDF is generated. Switching profiles
loads the other profile's JSON and does not overwrite your previous edits.

The default profile files are:

- `resume-data-fullstack.json` - Full Stack resume
- `resume-data-frontend.json` - Frontend resume

## JSON Content

Each profile contains the resume sections used by the generator:

- Personal information and contact links
- Summary
- Skills
- Work experience and bullet points
- Projects and technology stacks
- Education and languages

Keep the JSON valid when pasting or editing it. The preview will pause and
show an error until invalid JSON is corrected.

## Command Line Usage

To generate a PDF directly from the Full Stack profile:

```bash
python generate_resume.py
```

The PDF is created in the project folder using the data in `resume-data-fullstack.json`.
