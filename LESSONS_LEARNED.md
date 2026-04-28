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
| 2026-04-24 | In source-side skill Markdown, do not cite target-only materialized paths such as `.github/copilot-instructions.override.md`; skill-lint resolves local references against files that exist on disk, so prefer `.github/copilot-instructions.override.md.template` or descriptive prose. | pending | `.github/skills/internal-skill-creator/SKILL.md` |
| 2026-04-29 | Before classifying a cleanup as high-evidence, verify the candidate path exists on the current filesystem; absent paths should be treated as stale plan evidence, not as executable deletion work. | pending | `.github/skills/internal-copilot-audit/SKILL.md` |
| 2026-04-29 | Prompt files under `.github/prompts/` need an explicit managed-vs-helper decision before plans recommend prompt inventory, sync, or matrix changes; current catalog automation tracks agents, instructions, and skills, not prompts. | pending | `AGENTS.md` |
| 2026-04-29 | Do not add a manual catalog matrix until existing catalog summaries are either generated or validator-covered; stale summary counts can become a second source of truth beside `.github/INVENTORY.md`. | pending | `.github/scripts/lib/inventory.py` |
| 2026-04-29 | Exact `applyTo` duplicates are not currently reported by catalog consistency checks, so intentional co-loads need an allowlisted contract and accidental duplicates need validator coverage. | pending | `.github/scripts/lib/catalog_checks.py` |
| 2026-04-29 | In multi-repo governance reviews, run the same quantitative scans across every repository before writing findings or severity (for example workflow count, `permissions:` coverage, `dependabot.yml`, `SECURITY.md`, and `pull_request_target` usage); narrative spot checks materially undercount blast radius and hide cross-repo outliers. | pending | `.github/agents/internal-planning-leader.agent.md` |
| 2026-04-29 | When extending an existing retained mega-review, preserve the original monolithic deep-dive and add numbered delta files around it (`01-riassunto-esecutivo.md`, focused category files, and separate open-questions notes) instead of rewriting the prior analysis; this keeps earlier evidence stable while making new findings and executive summaries incrementally reviewable. | pending | `.github/agents/internal-planning-leader.agent.md` |
| 2026-04-29 | In the standards and sync source repository, baseline violations found in the template or hub repo should be treated as org-wide propagation risks rather than ordinary local defects, because missing hardening there is likely to be copied into every consumer repository during sync. | pending | `.github/agents/internal-review-guard.agent.md` |
