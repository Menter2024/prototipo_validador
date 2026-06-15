# DOX framework — Menter Fiscal

## Core Contract
- `AGENTS.md` files are binding work contracts for their subtrees.
- Before editing, read this file and every child `AGENTS.md` on the path to the target files.
- The closest `AGENTS.md` controls local details; children may specialize but not weaken repo-wide safety, verification, or privacy rules.
- After meaningful changes, re-check the affected DOX chain and update the nearest owning `AGENTS.md` if purpose, workflow, contracts, inputs, outputs, artifacts, verification, or child indexes changed.

## Project Contract
- Product: Menter Fiscal, a FastAPI prototype for fiscal validation of suppliers, padron imports, official-source monitoring, tax-decision evidence, batch validation, and pilot readiness.
- Keep fiscal/compliance behavior auditable: changes that affect tax rules, padron interpretation, evidence, or decisions must update tests and durable docs.
- Do not commit secrets, real client credentials, complete real padron datasets, raw uploads, generated outputs, or sensitive evidence.
- Prefer small, traceable changes. Avoid broad rewrites across backend, UI, scripts, and docs unless the task explicitly needs them.
- Keep `README.md` as the product/architecture entrypoint and `docs/` as durable operational/compliance documentation.

## Work Guidance
- Use Python 3.11+ conventions and existing FastAPI/Pydantic style.
- Prefer existing modules over new dependencies.
- Keep local file persistence compatible with the prototype unless the task targets Supabase/cloud migration.
- Preserve Basic Auth and non-sensitive diagnostics behavior for deploy targets.
- When editing generated/data-heavy areas, avoid normalizing or re-saving full datasets unless explicitly requested.

## Verification
- Run targeted `pytest` for changed behavior when relevant.
- For pure DOX/doc changes, verify by checking the DOX chain and `git diff --check`.
- Before committing critical staged changes, run `python scripts/check_dox.py --mode staged` to confirm docs/tests/AGENTS review is present.
- For padron/importer changes, include tests or scripts that prove the affected source/layout.

## User Preferences
- Responder en español.
- No stagear/commitear `padrones/PadronEntreRios.csv` ni padrones reales completos salvo autorización explícita.
- Push remoto solo con autorización explícita del usuario.

## Child DOX Index
- `app/AGENTS.md` — FastAPI app, route wiring, static pages, and domain modules.
- `config/AGENTS.md` — versioned fiscal catalogs, source catalogs, layouts, and portal adapters.
- `docs/AGENTS.md` — durable product, operations, architecture, compliance, and padron documentation.
- `padrones/AGENTS.md` — local/sample padron files and data-safety rules.
- `scripts/AGENTS.md` — operational CLIs for imports, downloads, audits, indexing, and jobs.
- `supabase/AGENTS.md` — database migrations and Supabase MVP integration contracts.
- `tests/AGENTS.md` — pytest coverage, fixtures, and regression expectations.
