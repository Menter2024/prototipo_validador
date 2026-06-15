# DOX — app/modules/

## Purpose
- Own fiscal validation, AFIP/ARCA integration, padron parsing/manifests, source monitoring, risk decisions, matrices, legajos, Excel output, georef, portal automation, and Supabase helpers.

## Ownership
- Each module owns one domain capability and its public functions consumed by `app/main.py`, scripts, or tests.
- Config-driven modules must stay aligned with `config/AGENTS.md`.

## Local Contracts
- Normalize CUITs consistently before validation, lookup, import, or evidence generation.
- Preserve auditability: importer, decision, and evidence outputs must include enough metadata for traceability without exposing secrets.
- Treat official-source/network failures as observable states, not silent success.
- Padron logic must keep source/layout provenance and avoid committing raw real datasets.

## Work Guidance
- Prefer pure functions for parsing, classification, and decisions.
- Keep IO boundaries explicit: paths, env vars, HTTP clients, and storage adapters should be easy to test.
- Add aliases/layout handling through config and tests rather than ad hoc string checks scattered across modules.

## Verification
- Run the specific `tests/test_*.py` covering the touched module.
- For parser/layout/risk changes, add or update fixture-backed regression tests.

## Child DOX Index
- No child DOX files yet.

