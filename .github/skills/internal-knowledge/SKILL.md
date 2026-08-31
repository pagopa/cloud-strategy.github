---
name: internal-knowledge
description: Use when creating or materially refreshing repository README files, `docs/architecture.md`, or architectural decision records (ADRs).
---

# Internal Knowledge

Create durable repository documentation from bounded, on-disk evidence.

## Workflow

1. Resolve one repository root and the exact documentation targets requested by the user.
2. Select only the requested authoring branches:
   - create or materially refresh explicit README targets with [README maintenance](references/readme-maintenance.md);
   - create or refresh `docs/architecture.md` with [architecture maintenance](references/architecture-maintenance.md);
   - record, revise, or supersede a decision with [ADR maintenance](references/adr-maintenance.md).
3. Read applicable repository instructions, existing target content, and only the evidence needed to support material claims.
4. Recheck each destination immediately before writing, then write only the authorized documentation targets.
5. Run applicable Markdown and repository validators. Report changed paths, evidence used, validation run, and unresolved gaps.

## Boundaries

- This skill owns README, architecture, and ADR authoring only. Documentation setup, knowledge maps, coverage inventories, and CI assets remain with their nearest implementation owner.
- Route ordinary copy edits and Markdown structure fixes to `/internal-markdown`.
- Write only targets authorized by the selected reference.
- Preserve accepted ADR bodies; use the supersession flow for a changed accepted decision.
- Keep repository policy, application code, infrastructure, tests, and workflows outside the write scope.

## House Rules

- Treat the target repository's `docs/adr/README.md` as the authoritative ADR house format when present; use the bundled [minimal MADR reference](references/madr-minimal.md) only as a portable fallback.
- Store ADRs as `NNNN-<slug>.md` and keep at most one accepted ADR per number.
