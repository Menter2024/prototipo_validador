# DOX — config/

## Purpose
- Own versioned JSON catalogs for fiscal sources, padron layouts, tax regimes, and portal adapters.

## Ownership
- `fuentes_catalogo.json` defines official-source coverage and operational status.
- `padron_layouts.json` defines import layouts and field mappings.
- `regimenes_catalogo.json` defines fiscal regime backlog/coverage.
- `portal_adapters.json` defines portal automation metadata.

## Local Contracts
- Config changes that affect runtime behavior require corresponding module/script tests.
- Keep source IDs, regime IDs, and layout IDs stable once referenced by docs, manifests, or tests.
- Record provenance URLs/status where available, without storing credentials.

## Work Guidance
- Prefer additive versioned entries over destructive renames.
- Keep JSON valid, deterministic, and human-reviewable.
- Align padron layouts with sanitized fixtures and docs.

## Verification
- Run catalog/layout tests after JSON changes.
- For large JSON edits, validate parseability before finalizing.

## Child DOX Index
- No child DOX files yet.

