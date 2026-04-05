---
name: internal-sync-global-copilot-configs-into-repo
description: Mirror the shared Copilot catalog into consumer repos — dynamic repo analysis, source-authoritative mirroring, local-* preservation, full skill-bundle copying, and deterministic reporting. Use when syncing Copilot configs, aligning repos with the standards repo, or running the sync script.
---

# Internal Sync Global Copilot Configs Into Repo

## When to use
- Align a consumer repository with shared Copilot assets from this standards repository.
- Audit source-side or target-side asset health before or after sync.
- Produce deterministic dry-run or apply reports for Copilot-core alignment.
- Rebuild target `.github/copilot-instructions.md` and then refresh root `AGENTS.md` after a raw mirror completes.

## Three-phase sync model

### Phase 1 — Analyze
1. Inspect target repository: `.github` contents, `AGENTS.md`, git state.
2. Detect stacks dynamically from file extensions and project manifests so reporting and validation stay target-aware even though mirroring is full-catalog.
3. Classify target assets into: mirrored source-managed, preserved `local-*`, and target-only non-local assets that must be removed during apply.
4. Audit source standards repository: detect legacy aliases, canonical overlaps, and stale governance references.

### Phase 2 — Plan
1. Select every source asset under `.github/agents`, `.github/instructions`, `.github/prompts`, and `.github/skills`.
2. Expand each mirrored skill to include bundled support files such as `references/`, `assets/`, `scripts/`, licenses, and other on-disk resources.
3. Compute SHA-256 checksums for both source and target versions of each mirrored file.
4. Plan source-authoritative updates for every mirrored non-local target file that differs from source.
5. Plan deletions for target-only non-local assets inside mirrored categories.
6. Preserve target `local-*` assets and validate them as unmanaged local extensions.
7. Write `tmp/internal-sync-copilot-configs.plan.md` in the target repo with the pending sync actions, checks, and manual follow-up items.
8. When the sync needs retained auxiliary files such as saved reports, place them under target-root `tmp/` and create that directory if it does not exist.
9. Plan root-guidance refresh in this order: target `.github/copilot-instructions.md` first via the repository-local planning and authoring workflow anchored in `internal-planning-leader`, then target root `AGENTS.md` via `internal-agents-md-bridge`.
10. Generate plan report (JSON or Markdown).

### Phase 3 — Apply (opt-in)
1. Copy every mirrored source asset, including binary skill support files.
2. Overwrite non-local target drift inside mirrored categories so the source catalog remains authoritative.
3. Delete target-only non-local assets inside mirrored categories.
4. Update manifest with new SHA-256 checksums and timestamp.
5. Refresh target `.github/copilot-instructions.md` as the primary detailed Copilot policy file, deriving target-specific content from repository evidence when needed.
6. Refresh target-specific root `AGENTS.md` from the mirrored baseline plus preserved target-local assets, keeping it concise, bridge-oriented, and runtime-agnostic instead of duplicating Copilot policy text.
7. Re-check the objectives recorded in `tmp/internal-sync-copilot-configs.plan.md`; remove sections whose checks now pass and delete the file only when nothing remains pending.
8. Preserve target-local `local-*` resources and configuration unless the approved plan explicitly migrates them.
9. Produce final report: actions taken, preserved local assets, deleted target-only assets, and recommendations. End the report with `✅ Outcome`, `🤖 Agents`, `📘 Instructions`, and `🧩 Skills`; if a category was not used, explicitly say so and explain why.

## Managed always-sync files
These files are always synced regardless of detected stacks:
- `copilot-instructions.md`
- `copilot-commit-message-instructions.md`
- `copilot-code-review-instructions.md`
- `security-baseline.md`
- `DEPRECATION.md`
- `repo-profiles.yml`
- `scripts/validate-copilot-customizations.py`

## Target assumptions
- The source of truth is always this `cloud-strategy.github` repository.
- The target stores Copilot customization under `.github/`.
- The target keeps `AGENTS.md` in repository root.
- Stack detection still matters for reporting, validation commands, and target-specific `copilot-instructions` authoring, but not for mirror selection.

## Mirrored categories
- `.github/agents/**/*.agent.md`
- `.github/instructions/**/*.instructions.md`
- `.github/prompts/**/*.prompt.md`
- `.github/skills/**`, including `SKILL.md` and bundled support files
- Tracking artifact: `tmp/internal-sync-copilot-configs.plan.md`

## Scope rules
- Manage Copilot-core assets only.
- Exclude README, changelog, templates, workflows, and source-only agents from sync.
- Prefer existing root `AGENTS.md` over creating a second managed file under `.github/`.
- Keep preserved `local-*` assets visible in rendered AGENTS.md inventory.
- Overwrite non-local divergent files inside mirrored categories.
- Treat target `.github/copilot-instructions.md` as the primary home for detailed behavioral, validation, and implementation guidance.
- Treat target root `AGENTS.md` as a thin bridge for generic assistants: routing, naming, priority, and discovery of the Copilot-owned `.github` assets.
- Keep target root `AGENTS.md` light on purpose because some repositories cannot or should not declare a specific assistant runtime there.
- Preserve target-local `local-*` resources and configuration even when they are not part of the mirrored source catalog; report them instead of deleting or folding them into managed files.

## Common mistakes

| Mistake | Why it matters | Instead |
|---|---|---|
| Running apply without reviewing the plan first | Unintended overwrites or deletions | Always run plan mode first, review the report |
| Treating skill bundles as `SKILL.md` only | Mirrored skills break because references, assets, or scripts are missing | Mirror the full skill directory contents |
| Preserving target-owned non-local assets under mirrored categories | The target drifts away from the standards catalog | Delete non-local target-only assets during apply |
| Generating a plan only in stdout | The user loses visibility on pending or failed sync steps after the run ends | Persist `tmp/internal-sync-copilot-configs.plan.md` until every section is cleared |
| Updating root AGENTS.md before copilot-instructions.md | The bridge can drift from the source policy | Refresh target `.github/copilot-instructions.md` first, then regenerate root `AGENTS.md` |
| Copying detailed Copilot policy into root AGENTS.md | The root bridge becomes redundant and harder to maintain | Keep detailed policy in `.github/copilot-instructions.md` and keep `AGENTS.md` concise |
| Treating target `local-*` assets as disposable noise | Local configuration gets lost during alignment | Preserve `local-*` assets and surface them in the report |
| Hardcoding target assumptions beyond `.github/` and root `AGENTS.md` | The sync agent becomes repo-specific and brittle | Keep the agent target-agnostic and derive everything else from the repository state |

## Cross-references
- **internal-pair-architect** (`.github/skills/internal-pair-architect/SKILL.md`): for impact analysis when sync changes baseline behavior.

## Tooling
- Script: `.github/scripts/internal-sync-copilot-configs.py`
- Manifest: `.github/internal-sync-copilot-configs.manifest.json` (in target repo)

## Validation
- `python -m compileall .github/scripts tests`
- `pytest` for the sync test suite.
- `python3 .github/scripts/validate-copilot-customizations.py --scope root --mode strict`
