# DOX — supabase/

## Purpose
- Own Supabase schema/migration artifacts for the MVP persistence and storage path.

## Ownership
- `migrations/` contains ordered SQL migrations.
- Runtime integration lives in `app/modules/supabase_mvp.py`.

## Local Contracts
- Migrations must be forward-only, reviewable, and safe for MVP data.
- Do not commit Supabase credentials, project tokens, service keys, or environment-specific secrets.
- Keep schema changes aligned with module expectations and pilot documentation.

## Work Guidance
- Prefer additive migrations over editing applied migration history.
- Document manual apply steps in docs when connector access is unavailable.

## Verification
- Validate SQL syntax where possible.
- Run Supabase module/status tests after schema-contract changes.

## Child DOX Index
- No child DOX files yet.

