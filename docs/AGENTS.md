# DOX — docs/

## Purpose
- Own durable product, architecture, operations, compliance, padron, source, and pilot-readiness documentation.

## Ownership
- Docs must reflect stable decisions, operating procedures, source coverage, and verified findings.
- README remains the top-level product/architecture entrypoint; docs provide deeper operational detail.

## Local Contracts
- Do not document raw secrets, credentials, full real padron records, or sensitive client evidence.
- Keep docs aligned with code/config/tests when behavior changes.
- Mark assumptions, manual steps, and unverified source coverage clearly.

## Work Guidance
- Prefer concise operational sections over chronological notes.
- Link related docs instead of duplicating long explanations.
- When generated from scripts, update via the script where practical.

## Verification
- For docs-only changes, check affected links/paths and run `git diff --check`.
- For generated docs/backlogs, rerun the owning script if behavior changed.

## Child DOX Index
- No child DOX files yet.

