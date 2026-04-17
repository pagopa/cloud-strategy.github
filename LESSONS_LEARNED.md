# Lessons

This file retains durable lessons discovered while completing tasks in this repository. It is a learning ledger, not the canonical policy source.

## Entry Rules

- Before editing this file, read its current on-disk contents and treat them as the source of truth for in-progress local lessons, including local uncommitted rows already present on disk.
- Record only lessons that were not already codified in repository resources at the time they were learned.
- Also record durable corrections to repeated or consequential misapplication of already-codified repository rules when that correction is likely to prevent future mistakes.
- When a validator, IDE, schema check, or runtime error overturns an earlier assumption, re-check immediately whether the correction is durable enough to retain until it is codified or deliberately dropped.
- Before deciding whether to retain, codify, or drop such a correction, read the relevant primary documentation instead of relying on memory alone.
- Prefer the smallest canonical home: if the correction belongs in a scoped instruction, skill, agent, or repository config and is being codified there, do not retain a duplicate lesson row.
- Keep only stable, reusable, repository-relevant lessons.
- Do not retain incident-specific or implementation-specific fixes that are too narrow to reuse beyond the triggering task or log.
- Exclude secrets, transient debugging notes, raw conversation logs, and task-local noise.
- Keep new or still-uncodified lessons in the pending table until they are codified or deliberately dropped.
- Add a new lesson by appending one new row to the pending table; do not regenerate, reorder, or rewrite unrelated rows.
- Preserve unrelated existing lessons, including local uncommitted ones already on disk.
- Only update or remove a specific lesson row when that same lesson is being codified, disproven, narrowed, or deduplicated.

## Pending Rules

| Date | Lesson | Status | Intended canonical target |
| --- | --- | --- | --- |
| 2026-04-16 | Post-sync validation for consumer repositories must run from the source repository wrappers with `--root <target>` because `.github/scripts` is intentionally outside the mirrored baseline and target repos do not receive those maintenance entrypoints. | pending | `.github/skills/internal-agent-sync-global-copilot-configs-into-repo/references/sync-contract.md` |
| 2026-04-17 | GitHub Actions `inputs` context is only available in reusable or `workflow_dispatch` workflows, so workflows that also run on `push` or `pull_request` must not rely on shared `inputs.*` expressions for default env or cache keys. | pending | `.github/instructions/internal-github-actions.instructions.md` |
