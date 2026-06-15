# DOX — app/

## Purpose
- Own the FastAPI application, HTTP/API routing, static UI pages, and Python domain modules used by Menter Fiscal.

## Ownership
- `main.py` owns app setup, middleware, routes, request/response schemas, and static page mounting.
- `modules/AGENTS.md` owns fiscal/domain logic.
- `static/AGENTS.md` owns browser-facing HTML/CSS/JS assets.

## Local Contracts
- Keep route behavior aligned with README route table and relevant docs.
- Do not leak secrets or raw sensitive evidence through diagnostics, logs, API responses, or rendered pages.
- Keep APIs deterministic enough for tests; isolate network/live-source calls behind modules.

## Work Guidance
- Add business logic in `modules/`; keep `main.py` focused on orchestration and HTTP concerns.
- Prefer explicit request models and clear error responses.
- Preserve `/healthz` and `/api/info` as non-sensitive endpoints.

## Verification
- Run targeted API/module tests for route or behavior changes.
- For UI route changes, verify page path and linked static asset still resolve.

## Child DOX Index
- `modules/AGENTS.md` — fiscal validation, padrones, sources, matrices, legajos, Supabase helpers.
- `static/AGENTS.md` — HTML pages, shared CSS, and browser JS.

