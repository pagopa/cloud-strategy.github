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

| 2026-04-21 | After Copilot baseline apply, if the target has no local catalog validation script, confirm convergence with a source-side sync plan and require zero managed create/update/delete operations. | pending | .github/skills/internal-agent-sync-global-copilot-configs-into-repo/references/sync-contract.md |
| 2026-04-22 | When Terraform `pre-commit` fails in GitHub Actions with provider checksum mismatches, do not stop at cache busting: test an affected root with `terraform providers lock -platform=linux_amd64` because the real defect can be lockfiles that pass locally on macOS but still lack Linux checksums for CI. | pending | .github/skills/internal-terraform/SKILL.md |
| 2026-04-22 | For self-authored PRs under required-review policy, green checks are not enough: GitHub rejects self-approval, and some repositories also reject merge commits, so the operational merge path must prefer `--squash` and may require explicit admin merge when policy allows. | pending | .github/copilot-instructions.md |
| 2026-04-22 | Organization-wide `gh search prs` results can lag briefly after a merge; confirm the terminal state of a just-merged PR with repository-scoped `gh pr view --json state,mergedAt` before treating it as still open. | pending | .github/copilot-instructions.md |
