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

| Date | Lesson | Status | Codification target |
| --- | --- | --- | --- |
| 2026-04-16 | Terraform roots validated with `terraform init -lockfile=readonly` in GitHub Actions should commit a `.terraform.lock.hcl` and pre-populate checksums for both local and CI platforms, for example with `terraform providers lock -platform=darwin_arm64 -platform=linux_amd64`, to avoid provider cache checksum mismatches and read-only init failures. | pending | .github/instructions/internal-terraform.instructions.md |
| 2026-04-30 | Terraform root configurations validated in isolation should declare their own `terraform` block with `required_version` and `required_providers`, and child modules that read adjacent templates or query files should resolve them from `path.module` so `terraform validate` and TFLint stay stable across different caller directories and CI runners. | pending | .github/instructions/internal-terraform.instructions.md |
| 2026-04-30 | For same-repository composite actions, GitHub’s documented and recommended organization is a dedicated folder under `.github/actions/<name>/action.yml`; keeping them under `.github/workflows/...` invites workflow-lint false positives and hides the boundary between reusable actions and actual workflows. | pending | .github/instructions/internal-github-actions.instructions.md |
