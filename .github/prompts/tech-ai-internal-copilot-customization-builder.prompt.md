---
description: Create or update repository-owned internal GitHub Copilot customization assets in a consumer repo while preserving the shared baseline
name: TechAIInternalCopilotCustomizationBuilder
agent: agent
argument-hint: target_repo=<path> change=<summary> [internal_asset_type=<prompt|skill|agent|triad>] [promote_to_source=<yes|no>]
---

# TechAI Internal Copilot Customization Builder

## Context
Use this prompt to create or refine repository-owned `internal-*` Copilot assets in a consumer repository without duplicating the shared `tech-ai-*` baseline.

## Required inputs
- **Target repository**: ${input:target_repo}
- **Requested change**: ${input:change}
- **Internal asset type**: ${input:internal_asset_type:prompt,skill,agent,triad}
- **Promote to source**: ${input:promote_to_source:no}

## Instructions
1. Use `.github/skills/tech-ai-internal-copilot-customization-builder/SKILL.md` as the workflow definition.
2. If the target baseline is missing or stale, run `TechAISyncCopilotConfigs` in `plan` mode first.
3. Inspect one or more concrete target files that the internal asset will operate on, then derive schema, naming conventions, identity formats, examples, and validations from those files.
4. If no suitable target file exists, stop and report the missing grounding instead of inventing schema fields, examples, or naming rules.
5. Create only the narrowest internal asset set that solves the request.
6. Keep repository-owned prompt, skill, and agent filenames plus frontmatter `name:` values on the `internal-*` convention.
7. Update the target `AGENTS.md` inventory and routing only as needed, keeping `.github/...` paths explicit.
8. Do not create internal duplicates of existing `tech-ai-*` capabilities unless the repo-specific behavior materially differs.
9. Report whether the capability should remain internal or be proposed for promotion into the shared source baseline.

## Minimal example
- Input: `target_repo=/workspace/consumer-repo change="Add a repo-internal prompt for onboarding external users" internal_asset_type=prompt`
- Expected output:
  - Baseline check for synced Copilot core assets in the target repo.
  - Target evidence listing the concrete repo files used to derive schema, naming, and examples.
  - Minimal `internal-*` asset plan with naming and placement rationale.
  - `AGENTS.md` inventory and routing updates only if needed.
  - Target-repo validation results and promotion recommendation.

## Validation
- Run `bash .github/scripts/validate-copilot-customizations.sh --scope root --mode strict` in the target repo after changing internal Copilot assets.
- Run relevant Bash, Python, Terraform, YAML, JSON, or Markdown checks for the touched files.
