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
6. Detect redundant legacy aliases for canonical prompt/skill/agent families, including families that are not part of the selected minimum baseline, so `cs-*` and unprefixed leftovers still appear in the plan.
7. Audit target-local instructions, prompts, skills, and agents that are outside the selected sync baseline:
   - report strict validation gaps for unmanaged files;
   - report legacy aliases even when the canonical family is not selected;
   - keep target-only custom assets visible instead of silently omitting them.
8. Treat redundant canonical-vs-legacy overlaps as conflicts instead of silently creating duplicate configuration families.
9. Render a target-specific `AGENTS.md` only when the selected inventory is conflict-safe:
   - keep `Preferred prompts` and `Preferred skills` as a curated shortlist;
   - keep asset path references in `Repository Inventory (Auto-generated)` only;
   - build the inventory from the desired managed baseline plus existing target-local instructions/prompts/skills/agents so the rendered inventory reflects the real target state;
   - avoid descriptive prompt/skill catalogs that duplicate the inventory.
10. Apply conservative merge rules through the manifest file and never overwrite unmanaged divergent files.
11. Produce a final report that separates source-side redundancy from target-side unmanaged asset issues, legacy alias drift, conflicts, and file actions.

## Scope rules
- Manage Copilot core assets only.
- Exclude README, changelog, templates, workflows, bootstrap helpers, and source-only review/audit agents from consumer sync.
- Prefer an existing root `AGENTS.md` over creating a second managed AGENTS file under `.github/`.
- Keep recommendation categories fixed and comparable across runs.
- Keep legacy alias logic in code and tests instead of repeating the same rules across prompt, skill, and agent prose.
- Do not omit existing target-local Copilot assets from the rendered AGENTS inventory just because they are outside the selected sync baseline.

## Validation
- Run `python -m compileall .github/scripts tests`.
- Run `pytest` for the `TechAISyncCopilotConfigs` test suite.
- Run `bash .github/scripts/validate-copilot-customizations.sh --scope root --mode strict`.
