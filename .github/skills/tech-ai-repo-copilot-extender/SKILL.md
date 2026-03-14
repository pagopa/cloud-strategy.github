---
name: TechAIRepoCopilotExtender
description: Generation patterns for repo-specific internal-* Copilot assets in consumer repos — naming rules, baseline preservation, and AGENTS.md integration. Use when a consumer repository needs its own internal prompts, skills, agents, or AGENTS.md wiring that must stay internal.
---

# TechAI Repo Copilot Extender — Skill

## When to use
- Create or update repository-owned `internal-*` prompts, skills, agents, or `AGENTS.md` wiring in a consumer repo.
- Extend a consumer repo with Copilot behavior that stays local (not in the shared `tech-ai-*` baseline).
- Normalize existing internal Copilot assets to follow current naming and frontmatter rules.

## Naming rules
See `references/naming-rules.md` for the full naming convention. Summary:

| Asset type | Filename pattern | Frontmatter `name:` |
|---|---|---|
| Prompt | `internal-<domain>.prompt.md` | `internal-<domain>` |
| Skill | `.github/skills/internal-<domain>/SKILL.md` | `internal-<domain>` |
| Agent | `internal-<domain>.agent.md` | `internal-<domain>` |

**Key rule**: everything repo-owned starts with `internal-`. Never use `tech-ai-*` for repo-local assets.

## Workflow
1. **Inspect** target repo: `.github` contents, `AGENTS.md`, git state, existing internal assets.
2. **Check baseline freshness**: if `copilot-instructions.md` or validator script is missing/stale, run sync first.
3. **Ground on evidence**: extract schema fields, naming patterns, and validation commands from real target files — never invent patterns.
4. **Choose narrowest asset type**:
   - `internal-*.prompt.md` → task instructions only.
   - `internal-*` skill → reusable implementation detail.
   - `internal-*` agent → durable routing/persona.
5. **Reuse baseline**: reference shared `tech-ai-*` skills by path instead of duplicating content.
6. **Update `AGENTS.md`**: add internal assets to inventory with explicit `.github/...` paths.
7. **Validate**: run `bash .github/scripts/validate-copilot-customizations.sh --scope root --mode strict`.
8. **Report**: changed files, validation output, grounding evidence, promotion recommendation.

## Scope rules
- Manage consumer-repository Copilot assets only.
- Keep source-repository assets unchanged unless promotion is explicitly requested.
- Consolidate duplicates instead of multiplying near-identical internal prompts.
- Do not create internal copies of source-only agents (`TechAIStandardsRepoConfigBuilder`, `TechAIStandardsRepoConfigAuditor`, `TechAISyncGlobalCopilotConfigsIntoRepo`).

## Common mistakes

| Mistake | Why it matters | Instead |
|---|---|---|
| Using `tech-ai-*` prefix for repo-local assets | Collides with shared baseline during sync | Always use `internal-*` prefix |
| Inventing fields or naming conventions not in target files | Internal asset gives wrong guidance, causes runtime errors | Ground every pattern on inspected target files |
| Duplicating shared skill content into internal prompt | Drift between copies, double maintenance | Reference shared skill by path: `See .github/skills/tech-ai-xxx/SKILL.md` |
| Creating an internal asset for something the baseline already covers | Unnecessary complexity, sync conflicts | Check baseline capabilities before creating |
| Missing `AGENTS.md` update after adding internal assets | Asset exists but is not discoverable | Always update `AGENTS.md` inventory |
| No validation after changes | Broken frontmatter or missing files go undetected | Run validator after every change |

## Cross-references
- **TechAISyncGlobalCopilotConfigsIntoRepo** (`.github/skills/tech-ai-sync-global-copilot-configs-into-repo/SKILL.md`): for ensuring baseline is current before extending.
- **TechAIPairArchitect** (`.github/skills/tech-ai-pair-architect/SKILL.md`): for impact analysis when internal assets modify repo behavior.

## Validation
- `bash .github/scripts/validate-copilot-customizations.sh --scope root --mode strict`
- `bash -n` and `shellcheck -s bash` for changed Bash files.
- `python -m compileall <paths>` and `pytest` for changed Python files.
