# DOX — scripts/

## Purpose
- Own command-line workflows for padron imports, source downloads, audits, golden cases, Supabase indexing, and background jobs.

## Ownership
- Scripts should orchestrate modules and config, not duplicate business logic.
- Each script should remain runnable from repo root.

## Local Contracts
- Scripts that download, import, index, or process external data must preserve provenance, hashes, dry-run/preview behavior where applicable, and safe defaults.
- Avoid writing secrets or sensitive raw data to stdout, docs, or committed files.

## Work Guidance
- Prefer explicit CLI arguments and deterministic outputs.
- Keep scheduler/job-compatible scripts non-interactive unless explicitly for assisted workflows.
- Reuse `app/modules` functions for parsing and validation.

## Verification
- Run targeted script tests after behavior changes.
- Run `python scripts/check_dox.py --mode staged` before committing critical changes.
- For operational scripts, test dry-run or fixture mode when available.

## Child DOX Index
- No child DOX files yet.
