# Changelog

## Entry template
Use this format for new updates:
- `## YYYY-MM-DD`
- One bullet per meaningful change.
- Include file/path scope when useful.

## 2026-02-07
- Added missing global Copilot instruction files for commit messages and code review.
- Added new instruction files: YAML, Markdown, Makefile, Scripts, Lambda.
- Added new skills: `terraform-module`, `cloud-policy`.
- Added `.github/README.md` and `AGENTS` template.
- Added custom agents: `Planner`, `Implementer`, `Reviewer`, `SecurityReviewer`, `WorkflowSupplyChain`, `TerraformGuardrails`, `IAMLeastPrivilege`.
- Added `.github/agents/README.md` with routing guidance.
- Hardened prompt/skill/instruction/agent validation and workflow checks.
- Added validator scope/mode support: `--scope root|all|repo=<name>` and `--mode strict|legacy-compatible`.
- Added validator JSON reporting support: `--report json --report-file <path>`.
- Added `repo-profiles.yml` for reusable high-level repository profiles.
- Added `security-baseline.md` and `DEPRECATION.md`.
- Added `instructions/composite-action.instructions.md` for reusable composite actions.
- Added `scripts/bootstrap-copilot-config.sh` for safe `.github` bootstrap and sync.
- Added `templates/copilot-quickstart.md` for portable onboarding.
- Added PR authoring assets: `prompts/cs-pr-description.prompt.md` and `skills/pr-writing/SKILL.md`.
- Updated docs to be repository-agnostic and reusable across different tech stacks.
- Replaced non-portable `PagoPA standards` wording with generic repository standards in script prompts.
- Hardened validator frontmatter key detection for multiline YAML keys.
- Extended validator JSON output with per-finding details.
- Added `prompts/cs-composite-action.prompt.md` and `skills/composite-action/SKILL.md`.
- Added `prompts/cs-data-registry.prompt.md` and `skills/data-registry/SKILL.md`.
- Expanded `cloud-policy` skill with concrete AWS/Azure/GCP templates.
- Reduced duplication by moving Java/Node examples from instructions to skills.
- Reduced overlap in `scripts.instructions.md` to cross-cutting rules only.
- Added bootstrap hardening (`--include-workflows`, `--exclude`, `--exclude-file`, `.bootstrap-ignore` support).
- Added `.github/CODEOWNERS` baseline and expanded Dependabot ecosystems.
- Enriched instruction files: composite action safety, Lambda specificity, YAML schema hint, Markdown language policy, Makefile example.
- Replaced placeholder `AGENTS.md` with repository-specific operational guidance in all `eng-*` repositories.
