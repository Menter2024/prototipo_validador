# DOX — app/static/

## Purpose
- Own static HTML pages, shared styles, and browser JavaScript for the prototype UI.

## Ownership
- HTML files map to FastAPI-rendered pages.
- `menter.css` and `menter-ui.js` own shared presentation and client helpers.

## Local Contracts
- Keep UI text aligned with product terminology in `README.md` and user-facing docs.
- Do not embed secrets, tokens, credentials, or real sensitive client data.
- Preserve simple static deployment compatibility; avoid build steps unless explicitly introduced.

## Work Guidance
- Prefer progressive enhancement with plain HTML/JS.
- Keep route links consistent with `app/main.py`.
- Maintain print/PDF-friendly behavior for manual and pilot pages.

## Verification
- For page changes, verify route loads and browser console has no obvious JS errors when practical.

## Child DOX Index
- No child DOX files yet.

