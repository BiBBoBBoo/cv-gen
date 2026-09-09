# Career Canvas Python

A lightweight Streamlit rebuild of the existing Career Canvas CV builder. It keeps the workflow local-first: enter career information, refine wording locally, review/edit the generated CV, and print or save it as PDF from the browser.

## Requirements

- Python 3.10 or newer
- Internet is only needed to install dependencies, or when optional AI refinement is enabled

## Install and run

From this directory:

```powershell
pip install -r requirements.txt
streamlit run app.py
```

Open the local URL shown by Streamlit, usually `http://localhost:8501`.

## Workflow

Use the six guided sections for personal information, professional profile, experience, skills, education, and additional information. Generate the CV, edit the summary, competencies, bullets, education, certifications, and additional information, then use `Print / Save PDF` inside the preview.

## Drafts and privacy

Drafts remain in Streamlit session state by default. The `Options` section provides `Download draft`, `Load draft`, and `Save draft locally` as `cv_draft.json`. There is no database, authentication, analytics, or remote storage. The local rewriter never sends CV content anywhere.

## Optional AI refinement

AI is disabled by default. To enable it for a session, set an environment variable and check `Use AI refinement` before generation:

```powershell
$env:OPENAI_API_KEY = "your-replacement-key"
$env:OPENAI_MODEL = "your-model-name"
streamlit run app.py
```

The app uses the OpenAI Python SDK and calls the Responses API once for the complete generated CV with `store=False`. It only accepts a response that preserves the source IDs and bullet counts; skills, dates, titles, companies, and structure remain controlled by the application. Missing credentials, quota errors, network errors, invalid responses, or any provider failure automatically fall back to `Local refinement used`.

Never commit API keys or put them in source files. AI refinement sends CV content to the configured provider; leave it disabled for entirely local processing.

## Static/hosted deployment

Streamlit Community Cloud is the simplest free deployment option: deploy this folder from a Git repository, set the app entry point to `app.py`, and add `OPENAI_API_KEY` only as a platform secret if optional AI is required. Local-only use needs no secret and works without AI.

## Migration notes

This is the sole application in the workspace. It preserves the six-step form, repeatable entries, local rule-based rewriting, plain ATS-friendly single-column structure, editable preview, print flow, and local/JSON draft handling. Optional AI refinement is isolated behind the same automatic local fallback contract.

When saving a PDF, turn off the browser print dialog's headers and footers to exclude the browser date, URL, and page count. Those elements are added by the browser and cannot be removed by the CV HTML.
