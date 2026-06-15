# DOX — padrones/

## Purpose
- Own local/sample padron files used by the prototype and tests.

## Ownership
- Files here may include local working data; treat them as sensitive unless explicitly sanitized.
- `README.md` documents sample padron usage.

## Local Contracts
- Do not commit complete real padron datasets or client-provided files unless explicitly authorized.
- Do not stage or commit `PadronEntreRios.csv` without explicit user authorization.
- Keep fixtures/sanitized samples in `tests/fixtures/` when they are meant for regression tests.
- Avoid rewriting large padron files during unrelated work.

## Work Guidance
- Prefer importer scripts and manifests for controlled updates.
- Preserve encoding/format details needed to reproduce importer behavior.
- Store generated outputs outside versioned padron data unless intentionally documented.

## Verification
- For padron data/layout changes, run importer/layout tests or the relevant validation script.

## Child DOX Index
- No child DOX files yet.

