# Lessons

This file retains durable lessons discovered while completing tasks in this repository. It is a learning ledger, not the canonical policy source.

## Entry Rules

- Before editing this file, read its current on-disk contents and treat them as the source of truth for in-progress local lessons, including local uncommitted rows already present on disk.
- Record only lessons that were not already codified in repository resources at the time they were learned.
- Also record durable corrections to repeated or consequential misapplication of already-codified repository rules when that correction is likely to prevent future mistakes.
- Keep only stable, reusable, repository-relevant lessons.
- Exclude secrets, transient debugging notes, raw conversation logs, and task-local noise.
- Keep new or still-uncodified lessons in the pending table until they are codified or deliberately dropped.
- Add a new lesson by appending one new row to the pending table; do not regenerate, reorder, or rewrite unrelated rows.
- Preserve unrelated existing lessons, including local uncommitted ones already on disk.
- Only update or remove a specific lesson row when that same lesson is being codified, disproven, narrowed, or deduplicated.

## Pending Rules

| Date | Lesson | Status | Intended canonical target |
| --- | --- | --- | --- |
| 2026-04-12 | For repo-owned standards work that deepens parallel skill sets, split planning into staged working documents under `tmp/superpowers/`, make anti-scope explicit, and sequence in-place parity work (`Common mistakes`, `Validation`, existing reference depth) before optional new skills, validators, or shared assets. | Pending | .github/copilot-instructions.md |
| 2026-04-12 | For provider-specific cloud skills, keep guidance provider-native and omit cross-cloud comparison or cloud-selection content when provider choice is already upstream of skill activation. | Pending | .github/copilot-instructions.md |
| 2026-04-12 | In source-of-truth guidance repositories, judge new GitHub Actions depth against downstream reuse needs, but keep auto-loaded instructions lean and move advanced patterns into skill references. | Pending | .github/copilot-instructions.md |
