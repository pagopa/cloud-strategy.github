---
name: tech-ai-sync-copilot-configs
description: Analyze a local repository, select the minimum Copilot customization assets, tailor them, and align them conservatively with a final report.
---

# TechAI Sync Copilot Configs Skill

## When to use
- Create or update the `TechAISyncCopilotConfigs` alignment workflow.
- Align a local target repository with portable Copilot customization assets from this standards repository.
- Produce deterministic dry-run or apply reports for Copilot-core alignment only.

## Workflow
1. Inspect the target repository layout, manifests, `.github` contents, `AGENTS.md` location, and git state.
2. Classify the repository against `repo-profiles.yml`, then extend the profile with stack-specific rules only when needed.
3. Select the minimum Copilot core assets that the target repository actually needs.
4. Prefer canonical prompt families when multiple prompts cover the same workflow so consumer repositories keep the same capability with fewer tokens.
5. Render a target-specific `AGENTS.md` that uses GitHub Copilot wording only.
6. Apply conservative merge rules through the manifest file and never overwrite unmanaged divergent files.
7. Produce a final report with target actions and source-repository improvement recommendations.

## Scope rules
- Manage Copilot core assets only.
- Exclude README, changelog, templates, workflows, bootstrap helpers, and source-only review/audit agents from consumer sync.
- Prefer an existing root `AGENTS.md` over creating a second managed AGENTS file under `.github/`.
- Keep recommendation categories fixed and comparable across runs.

## Validation
- Run `bash .github/scripts/validate-copilot-customizations.sh --scope root --mode strict`.
- Run `python -m compileall .github/scripts/tech-ai-sync-copilot-configs.py tests`.
- Run `pytest` for the `TechAISyncCopilotConfigs` test suite.
