---
name: internal-sync-global-copilot-configs-into-repo
description: Mirror the shared Copilot catalog into consumer repos — dynamic repo analysis, source-authoritative mirroring, local-* preservation, full skill-bundle copying, and deterministic reporting. Use when syncing Copilot configs, aligning repos with the standards repo, or running the sync script.
---

# Internal Sync Global Copilot Configs Into Repo

## When to use
- Align a consumer repository with shared Copilot assets from this standards repository.
- Audit source-side or target-side asset health before or after sync.
- Produce deterministic dry-run or apply reports for Copilot-core alignment.
- Rebuild target `AGENTS.md`, `.github/copilot-instructions.md`, and `.github/INVENTORY.md` after a raw mirror completes.

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
9. Plan root-guidance refresh around canonical ownership: target `AGENTS.md` for cross-surface defaults and precedence, target `.github/copilot-instructions.md` for the repo-wide Copilot projection, and target `.github/INVENTORY.md` for the exact live catalog.
10. Generate plan report (JSON or Markdown).

### Phase 3 — Apply (opt-in)
1. Copy every mirrored source asset, including binary skill support files.
2. Overwrite non-local target drift inside mirrored categories so the source catalog remains authoritative.
3. Delete target-only non-local assets inside mirrored categories.
4. Update manifest with new SHA-256 checksums and timestamp.
5. Refresh target-specific root `AGENTS.md` from the mirrored baseline plus preserved target-local assets, keeping it strategic, precedence-aware, and runtime-agnostic.
6. Refresh target `.github/copilot-instructions.md` as the repo-wide Copilot projection and rebuild target `.github/INVENTORY.md` as the exact live catalog, deriving target-specific content from repository evidence when needed.
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
- Keep preserved `local-*` assets visible in generated `.github/INVENTORY.md`.
- Overwrite non-local divergent files inside mirrored categories.
- Treat target `AGENTS.md` as the strategic entrypoint, precedence anchor, and bridge for generic assistants.
- Treat target `.github/copilot-instructions.md` as the repo-wide Copilot projection for native Copilot flows.
- Keep target `.github/INVENTORY.md` as the exact live catalog and do not duplicate it into target `AGENTS.md`.
- Preserve target-local `local-*` resources and configuration even when they are not part of the mirrored source catalog; report them instead of deleting or folding them into managed files.

## Common mistakes

| Mistake | Why it matters | Instead |
|---|---|---|
| Running apply without reviewing the plan first | Unintended overwrites or deletions | Always run plan mode first, review the report |
| Treating skill bundles as `SKILL.md` only | Mirrored skills break because references, assets, or scripts are missing | Mirror the full skill directory contents |
| Preserving target-owned non-local assets under mirrored categories | The target drifts away from the standards catalog | Delete non-local target-only assets during apply |
| Generating a plan only in stdout | The user loses visibility on pending or failed sync steps after the run ends | Persist `tmp/internal-sync-copilot-configs.plan.md` until every section is cleared |
| Treating root guidance as one flattened document | Rule ownership blurs and drift becomes hard to audit | Keep `AGENTS.md`, `.github/copilot-instructions.md`, and `.github/INVENTORY.md` aligned to their separate roles |
| Copying repo-wide Copilot policy or exact inventory into root `AGENTS.md` | The entrypoint becomes noisy and easier to contradict | Keep cross-surface defaults in `AGENTS.md`, repo-wide Copilot behavior in `.github/copilot-instructions.md`, and exact inventory in `.github/INVENTORY.md` |
| Treating target `local-*` assets as disposable noise | Local configuration gets lost during alignment | Preserve `local-*` assets and surface them in the report |
| Hardcoding target assumptions beyond `.github/` and root `AGENTS.md` | The sync agent becomes repo-specific and brittle | Keep the agent target-agnostic and derive everything else from the repository state |

## Cross-references
- **internal-pair-architect** (`.github/skills/internal-pair-architect/SKILL.md`): for impact analysis when sync changes baseline behavior.

## Tooling
- Workflow anchor: `.github/agents/internal-sync-global-copilot-configs-into-repo.agent.md`
- Manifest: `.github/internal-sync-copilot-configs.manifest.json` (in target repo)

## Validation
- Run the repository checks that currently exist for the touched source files.
- If the source repository does not ship a dedicated sync test suite, say so explicitly and use the closest existing verification instead.
