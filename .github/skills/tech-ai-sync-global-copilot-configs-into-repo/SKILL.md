---
name: TechAISyncGlobalCopilotConfigsIntoRepo
description: Sync shared Copilot baseline into consumer repos — dynamic stack detection, manifest-based conservative merge, conflict detection, and deterministic reporting. Use when syncing Copilot configs, aligning repos with the baseline, or running the sync script.
---

# TechAI Sync Global Copilot Configs Into Repo — Skill

## When to use
- Align a consumer repository with shared Copilot assets from this standards repository.
- Audit source-side or target-side asset health before or after sync.
- Produce deterministic dry-run or apply reports for Copilot-core alignment.

## Three-phase sync model

### Phase 1 — Analyze
1. Inspect target repository: `.github` contents, `AGENTS.md`, git state.
2. Detect stacks dynamically from file extensions and project manifests (no hardcoded profiles — detect `*.tf`, `*.py`, `*.java`, `*.js`, `*.ts`, `Dockerfile`, `*.sh`, etc.).
3. Classify target assets into: managed (synced baseline), internal (`internal-*`), and unmanaged (everything else).
4. Audit source standards repository: detect legacy aliases, canonical overlaps, and source-only assets.

### Phase 2 — Plan
1. Select minimum Copilot-core assets the target actually needs based on detected stacks.
2. Compute SHA-256 checksums for both source and target versions of each managed file.
3. Flag conflicts: target file diverged from last-synced version (manifest mismatch).
4. Flag redundancies: legacy aliases coexisting with canonical assets.
5. Flag internal naming violations: repo-owned assets missing `internal-*` prefix.
6. Generate plan report (JSON or Markdown).

### Phase 3 — Apply (opt-in)
1. Copy selected assets using conservative merge (never overwrite unmanaged divergent files).
2. Update manifest with new SHA-256 checksums and timestamp.
3. Render target-specific `AGENTS.md` from managed baseline + existing internal assets.
4. Produce final report: actions taken, conflicts skipped, recommendations.

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
| Terraform (`*.tf`) | `terraform.instructions.md` | `tech-ai-terraform`, `tech-ai-cloud-policy` | `tech-ai-terraform.prompt.md` |
| Python (`*.py`) | `python.instructions.md` | `tech-ai-project-python`, `tech-ai-script-python` | `tech-ai-python.prompt.md` |
| Java (`*.java`) | `java.instructions.md` | `tech-ai-project-java` | `tech-ai-java.prompt.md` |
| Node.js (`*.js`, `*.ts`) | `nodejs.instructions.md` | `tech-ai-project-nodejs` | `tech-ai-nodejs.prompt.md` |
| Docker (`Dockerfile`) | `docker.instructions.md` | `tech-ai-docker` | `tech-ai-docker.prompt.md` |
| Bash (`*.sh`) | `bash.instructions.md` | `tech-ai-script-bash` | `tech-ai-bash-script.prompt.md` |
| GitHub Actions (`workflows/`) | `github-actions.instructions.md` | `tech-ai-cicd-workflow` | `tech-ai-github-action.prompt.md` |

Always included: `markdown.instructions.md`, `yaml.instructions.md`, `json.instructions.md`.

## Source-only assets (never synced)
These assets exist only in this standards repository:
- Agents: `tech-ai-standards-repo-config-builder`, `tech-ai-standards-repo-config-auditor`, `tech-ai-sync-global-copilot-configs-into-repo`, `tech-ai-repo-copilot-extender`
- Skills: `tech-ai-repo-copilot-extender`, `tech-ai-skill-creator`, `tech-ai-sync-global-copilot-configs-into-repo`
- Prompts: `tech-ai-add-platform`, `tech-ai-add-report-script`, `tech-ai-code-review`, `tech-ai-repo-copilot-extender`, `tech-ai-sync-global-copilot-configs-into-repo`

## Scope rules
- Manage Copilot-core assets only.
- Exclude README, changelog, templates, workflows, and source-only agents from sync.
- Prefer existing root `AGENTS.md` over creating a second managed file under `.github/`.
- Keep `internal-*` assets visible in rendered AGENTS.md inventory.
- Never overwrite unmanaged divergent files — flag as conflicts instead.

## Common mistakes

| Mistake | Why it matters | Instead |
|---|---|---|
| Running apply without reviewing the plan first | Unintended overwrites or deletions | Always run plan mode first, review the report |
| Syncing source-only agents to consumer repos | Consumer gets assets meant for standards repo only | Check exclusion lists |
| Ignoring manifest checksum mismatches | Target edits get silently overwritten | Flag as conflict, require manual resolution |
| Not updating AGENTS.md after sync | Inventory drifts from actual file state | Always regenerate AGENTS.md from current state |
| Hardcoding profiles instead of detecting stacks | New stacks in target repo get no coverage | Detect dynamically from file extensions |

## Cross-references
- **TechAIRepoCopilotExtender** (`.github/skills/tech-ai-repo-copilot-extender/SKILL.md`): for creating repo-owned `internal-*` assets after sync.
- **TechAIPairArchitect** (`.github/skills/tech-ai-pair-architect/SKILL.md`): for impact analysis when sync changes baseline behavior.

## Tooling
- Script: `.github/scripts/tech-ai-sync-copilot-configs.py`
- Manifest: `.github/tech-ai-sync-copilot-configs.manifest.json` (in target repo)

## Validation
- `python -m compileall .github/scripts tests`
- `pytest` for the sync test suite.
- `bash .github/scripts/validate-copilot-customizations.sh --scope root --mode strict`
