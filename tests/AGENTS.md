# DOX — tests/

## Purpose
- Own pytest coverage, regression fixtures, and behavior guarantees for the prototype.

## Ownership
- Tests should cover public behavior of modules, APIs, scripts, config, and docs generated from code/config.
- `fixtures/` owns sanitized sample inputs for importers and batch flows.

## Local Contracts
- Fixtures must be sanitized and minimal; do not add full real padron datasets.
- Tests should prove fiscal/parser behavior without requiring live secrets or external paid services.
- Keep tests deterministic across local, CI, and lightweight deploy environments.

## Work Guidance
- Add targeted tests with every behavior change.
- Prefer fixture-backed tests for padron/layout/source edge cases.
- Keep test names descriptive by capability/source.

## Verification
- Run targeted `pytest tests/test_name.py` for changed areas.
- Run broader pytest only when cross-module behavior changed.

## Child DOX Index
- No child DOX files yet.

