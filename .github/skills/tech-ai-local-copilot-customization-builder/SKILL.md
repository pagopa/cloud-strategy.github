---
name: TechAILocalCopilotCustomizationBuilder
description: Create or update repository-owned local GitHub Copilot customization assets in a consumer repository while preserving the shared synced baseline.
---

# TechAI Local Copilot Customization Builder Skill

## When to use
- Create or update repository-owned `local-*` prompts, skills, agents, or `AGENTS.md` wiring in a consumer repo.
- Extend a consumer repo with Copilot behavior that should stay local instead of entering the shared `tech-ai-*` baseline.
- Clean up or normalize existing target-local Copilot assets so they follow current naming, frontmatter, and inventory rules.

## Workflow
1. Inspect the target repository layout, `.github` contents, root `AGENTS.md`, git state, and existing local Copilot assets.
2. Confirm the baseline is current enough for local customization work:
   - if `copilot-instructions.md`, the validator script, or expected synced assets are missing or stale, run `TechAISyncCopilotConfigs` in `plan` mode first;
   - use the sync report to avoid creating a `local-*` asset that duplicates an available shared baseline capability.
3. Decide the narrowest asset type that solves the request:
   - create or update a `local-*.prompt.md` when the behavior is mostly task instructions;
   - add a `local-*` skill only when the workflow needs reusable implementation detail beyond the prompt;
   - add a `local-*` agent only when the repo needs durable routing or persona guidance that cannot stay in a prompt or skill.
4. Enforce local naming and ownership rules:
   - filenames for repo-owned prompts, skills, and agents must start with `local-`;
   - prompt, skill, and agent frontmatter `name:` values must also start with `local-`;
   - keep local assets in `.github/prompts`, `.github/skills/<local-family>/SKILL.md`, and `.github/agents`.
5. Keep local assets minimal and compatible with the shared baseline:
   - reuse `.github/instructions/*.instructions.md` and synced `tech-ai-*` skills when possible instead of copying large guidance blocks;
   - reference shared prompts or skills by path when they already cover most of the behavior;
   - avoid creating a local canonical duplicate of an existing `tech-ai-*` capability.
6. Update `AGENTS.md` in the target repository:
   - keep explicit `.github/...` paths;
   - add the local assets to the inventory;
   - adjust routing or preferred prompts or skills only when the new local capability should be discoverable by default;
   - avoid duplicating long prompt or skill descriptions inside `AGENTS.md`.
7. Validate the target repository after changes:
   - run `bash .github/scripts/validate-copilot-customizations.sh --scope root --mode strict`;
   - run stack-specific checks for touched Bash, Python, JSON, YAML, Markdown, or Terraform assets;
   - if the repo has a synced baseline manifest, preserve it and do not rewrite managed files opportunistically.
8. Report the result with changed files, validation output, residual repo-local risks, and whether the new capability should stay local or be proposed for promotion into the shared source baseline.

## Scope rules
- Manage consumer-repository Copilot assets only.
- Keep source-repository assets and shared baseline definitions unchanged unless promotion is explicitly requested.
- Prefer one local capability per repo-specific workflow; consolidate or deprecate duplicates instead of multiplying near-identical local prompts.
- Do not create local copies of source-only repo agents such as `TechAIGlobalCustomizationBuilder`, `TechAIGlobalCustomizationAuditor`, or `TechAISyncCopilotConfigs`.

## Validation
- Run `bash .github/scripts/validate-copilot-customizations.sh --scope root --mode strict` in the target repo after local customization changes.
- Run `bash -n` and `shellcheck -s bash` for changed Bash files when available.
- Run `python -m compileall <changed_python_paths>` and relevant `pytest` checks for changed Python files.
- Re-run `TechAISyncCopilotConfigs` in `plan` mode when you need to confirm that the new local assets remain clearly separated from the managed shared baseline.
