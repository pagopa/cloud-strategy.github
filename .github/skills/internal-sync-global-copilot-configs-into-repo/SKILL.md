---
name: internal-sync-global-copilot-configs-into-repo
description: Sync shared Copilot baseline into consumer repos — dynamic stack detection, manifest-based conservative merge, conflict detection, and deterministic reporting. Use when syncing Copilot configs, aligning repos with the baseline, or running the sync script.
---

# Internal Sync Global Copilot Configs Into Repo

## When to use
- Align a consumer repository with shared Copilot assets from this standards repository.
- Audit source-side or target-side asset health before or after sync.
- Produce deterministic dry-run or apply reports for Copilot-core alignment.

## Three-phase sync model

### Phase 1 — Analyze
1. Inspect target repository: `.github` contents, `AGENTS.md`, git state.
2. Detect stacks dynamically from file extensions and project manifests (no hardcoded profiles — detect `*.tf`, `*.py`, `*.java`, `*.js`, `*.ts`, `Dockerfile`, `*.sh`, etc.).
3. Classify target assets into: managed (synced baseline), origin-prefixed (`internal-*`, `local-*`, or supported external prefixes), and unmanaged (everything else).
4. Audit source standards repository: detect legacy aliases, canonical overlaps, and source-only assets.

### Phase 2 — Plan
1. Select minimum Copilot-core assets the target actually needs based on detected stacks.
2. Compute SHA-256 checksums for both source and target versions of each managed file.
3. Flag conflicts: target file diverged from last-synced version (manifest mismatch).
4. Flag redundancies: legacy aliases coexisting with canonical assets.
5. Flag origin-prefix violations: repo-owned assets missing `internal-*`, `local-*`, or a supported external short-repo prefix.
6. Plan root-guidance refresh in this order: target `.github/copilot-instructions.md` first via `awesome-copilot-instructions-blueprint-generator`, then target root `AGENTS.md` via `internal-agents-md-bridge`.
7. Generate plan report (JSON or Markdown).

### Phase 3 — Apply (opt-in)
1. Copy selected assets using conservative merge (never overwrite unmanaged divergent files).
2. Update manifest with new SHA-256 checksums and timestamp.
3. Refresh target `.github/copilot-instructions.md` as the primary detailed Copilot policy file, preserving target-local rules that are still valid and do not conflict with the managed baseline.
4. Refresh target-specific root `AGENTS.md` from the managed baseline plus existing target-local assets, keeping it concise, bridge-oriented, and runtime-agnostic instead of duplicating Copilot policy text.
5. Preserve target-local unmanaged resources, prompts, skills, agents, and configuration unless the approved plan explicitly migrates them.
6. Produce final report: actions taken, conflicts skipped, preserved local assets, and recommendations.

## Managed always-sync files
These files are always synced regardless of detected stacks:
- `copilot-instructions.md`
- `copilot-commit-message-instructions.md`
- `copilot-code-review-instructions.md`
- `security-baseline.md`
- `DEPRECATION.md`
- `scripts/validate-copilot-customizations.sh`

## Stack-to-asset mapping
The sync script detects stacks dynamically and selects assets accordingly:

| Detected stack | Instructions | Skills | Prompts |
|---|---|---|---|
| Terraform (`*.tf`) | `internal-terraform.instructions.md` | `internal-terraform`, `internal-cloud-policy` | `internal-terraform.prompt.md` |
| Python (`*.py`) | `internal-python.instructions.md` | `internal-project-python`, `internal-script-python` | `internal-python.prompt.md` |
| Java (`*.java`) | `internal-java.instructions.md` | `internal-project-java` | `internal-java.prompt.md` |
| Node.js (`*.js`, `*.ts`) | `internal-nodejs.instructions.md` | `internal-project-nodejs` | `internal-nodejs.prompt.md` |
| Docker (`Dockerfile`) | `internal-docker.instructions.md` | `internal-docker` | `internal-docker.prompt.md` |
| Bash (`*.sh`) | `internal-bash.instructions.md` | `internal-script-bash` | `internal-bash-script.prompt.md` |
| GitHub Actions (`workflows/`) | `internal-github-actions.instructions.md` | `internal-cicd-workflow` | `internal-github-action.prompt.md` |

Always included: `internal-markdown.instructions.md`, `internal-yaml.instructions.md`, `internal-json.instructions.md`.

## Source-only assets (never synced)
These assets exist only in this standards repository:
- Agents: `internal-sync-global-copilot-configs-into-repo`
- Skills: `internal-agent-development`, `internal-agents-md-bridge`, `internal-copilot-audit`, `internal-skill-management`, `internal-sync-global-copilot-configs-into-repo`
- Prompts: `internal-add-platform`, `internal-add-report-script`, `internal-code-review`, `internal-sync-global-copilot-configs-into-repo`

## Scope rules
- Manage Copilot-core assets only.
- Exclude README, changelog, templates, workflows, and source-only agents from sync.
- Prefer existing root `AGENTS.md` over creating a second managed file under `.github/`.
- Keep origin-prefixed assets visible in rendered AGENTS.md inventory.
- Never overwrite unmanaged divergent files — flag as conflicts instead.
- Treat target `.github/copilot-instructions.md` as the primary home for detailed behavioral, validation, and implementation guidance.
- Treat target root `AGENTS.md` as a thin bridge for generic assistants: routing, naming, priority, and discovery of the Copilot-owned `.github` assets.
- Keep target root `AGENTS.md` light on purpose because some repositories cannot or should not declare a specific assistant runtime there.
- Preserve target-local unmanaged resources and configuration even when they are not part of the selected sync baseline; report them instead of deleting or folding them into managed files.

## Common mistakes

| Mistake | Why it matters | Instead |
|---|---|---|
| Running apply without reviewing the plan first | Unintended overwrites or deletions | Always run plan mode first, review the report |
| Syncing source-only agents to consumer repos | Consumer gets assets meant for standards repo only | Check exclusion lists |
| Ignoring manifest checksum mismatches | Target edits get silently overwritten | Flag as conflict, require manual resolution |
| Updating root AGENTS.md before copilot-instructions.md | The bridge can drift from the source policy | Refresh target `.github/copilot-instructions.md` first, then regenerate root `AGENTS.md` |
| Copying detailed Copilot policy into root AGENTS.md | The root bridge becomes redundant and harder to maintain | Keep detailed policy in `.github/copilot-instructions.md` and keep `AGENTS.md` concise |
| Treating target-local unmanaged assets as disposable noise | Local configuration gets lost during alignment | Preserve unmanaged local assets and surface them in the report or as conflicts |
| Hardcoding profiles instead of detecting stacks | New stacks in target repo get no coverage | Detect dynamically from file extensions |

## Cross-references
- **internal-pair-architect** (`.github/skills/internal-pair-architect/SKILL.md`): for impact analysis when sync changes baseline behavior.

## Tooling
- Script: `.github/scripts/internal-sync-copilot-configs.py`
- Manifest: `.github/internal-sync-copilot-configs.manifest.json` (in target repo)

## Validation
- `python -m compileall .github/scripts tests`
- `pytest` for the sync test suite.
- `python3 .github/scripts/validate-copilot-customizations.sh --scope root --mode strict`
