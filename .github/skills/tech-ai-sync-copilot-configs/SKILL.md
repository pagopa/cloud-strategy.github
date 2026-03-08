---
name: TechAISyncCopilotConfigs
description: Analyze a local repository, select the minimum Copilot customization assets, tailor them, and align them conservatively with a final report.
---

# TechAI Sync Copilot Configs Skill

## When to use
- Create or update the `TechAISyncCopilotConfigs` alignment workflow.
- Align a local target repository with portable Copilot customization assets from this standards repository.
- Produce deterministic dry-run or apply reports for Copilot-core alignment only.

## Workflow
1. Inspect the target repository layout, manifests, `.github` contents, `AGENTS.md` location, and git state.
2. Audit the source standards repository before syncing:
   - classify canonical instructions, prompts, skills, and agents;
   - detect source-side legacy aliases such as `cs-*` and unprefixed equivalents;
   - detect operational overlap across prompt/skill/agent triads;
   - detect repeated asset references across `AGENTS.md` sections.
3. Classify the repository against `repo-profiles.yml`, then extend the profile with stack-specific rules only when needed.
4. Select the minimum Copilot core assets that the target repository actually needs.
5. Prefer canonical prompt families when multiple prompts cover the same workflow so consumer repositories keep the same capability with fewer tokens.
6. Detect redundant legacy aliases for selected canonical assets, especially `cs-*`, unprefixed prompt names, and legacy agent or skill filenames.
7. Treat redundant canonical-vs-legacy overlaps as conflicts instead of silently creating duplicate configuration families.
8. Render a target-specific `AGENTS.md` only when the selected inventory is conflict-safe:
   - keep `Preferred prompts` and `Preferred skills` as a curated shortlist;
   - keep asset path references in `Repository Inventory (Auto-generated)` only;
   - avoid descriptive prompt/skill catalogs that duplicate the inventory.
9. Apply conservative merge rules through the manifest file and never overwrite unmanaged divergent files.
10. Produce a final report that separates source-side redundancy from target-side conflicts and actions.

## Scope rules
- Manage Copilot core assets only.
- Exclude README, changelog, templates, workflows, bootstrap helpers, and source-only review/audit agents from consumer sync.
- Prefer an existing root `AGENTS.md` over creating a second managed AGENTS file under `.github/`.
- Keep recommendation categories fixed and comparable across runs.
- Keep legacy alias logic in code and tests instead of repeating the same rules across prompt, skill, and agent prose.

## Validation
- Run `python -m compileall .github/scripts tests`.
- Run `pytest` for the `TechAISyncCopilotConfigs` test suite.
- Run `bash .github/scripts/validate-copilot-customizations.sh --scope root --mode strict`.
