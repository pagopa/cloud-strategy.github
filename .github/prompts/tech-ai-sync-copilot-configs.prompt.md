---
description: Analyze and conservatively align a local repository with the minimum Copilot customization assets from this standards repo
name: TechAISyncCopilotConfigs
agent: agent
argument-hint: target_repo=<path> [source_repo=<path>] [mode=<plan|apply>] [report_format=<md|json>] [report_file=<path>]
---

# TechAI Sync Copilot Configs

## Context
Use this prompt to analyze a local repository, select the minimum Copilot customization assets from this standards repo, and align them conservatively.

## Required inputs
- **Target repository**: ${input:target_repo}
- **Source repository**: ${input:source_repo:.}
- **Mode**: ${input:mode:plan,apply}
- **Report format**: ${input:report_format:md,json}
- **Report file**: ${input:report_file}

## Instructions
1. Use `.github/skills/tech-ai-sync-copilot-configs/SKILL.md` as the workflow definition.
2. Use `.github/scripts/tech-ai-sync-copilot-configs.py` for deterministic execution.
3. Keep scope limited to Copilot core assets only.
4. Preserve unmanaged target files and report conflicts instead of overwriting them.
5. Render the target `AGENTS.md` with GitHub Copilot wording only.
6. Keep recommendation categories stable across runs.

## Minimal example
- Input: `target_repo=/workspace/consumer-repo mode=plan report_format=md`
- Expected output:
  - Target analysis summary with detected profile and stacks.
  - Conservative file action plan for Copilot core assets only.
  - Recommendations for improving the source standards repository.

## Validation
- Run the sync script in `plan` mode before any `apply` execution.
- Run `bash .github/scripts/validate-copilot-customizations.sh --scope root --mode strict` after changing prompt, skill, agent, or script assets.
