# Changelog

## Entry template
Use this format for new updates:
- `## YYYY-MM-DD`
- One bullet per meaningful change.
- Include file/path scope when useful.

## 2026-03-07
- Added `.gitignore` coverage for Python caches/virtualenvs and macOS Finder artifacts so local validation runs stop creating noisy untracked files.
- Added canonical low-duplication script prompts: `prompts/tech-ai-bash-script.prompt.md` (`TechAIBashScript`) and `prompts/tech-ai-python-script.prompt.md` (`TechAIPythonScript`).
- Reduced the legacy `cs-*` and `script-*` Bash/Python prompts to thin compatibility aliases that now point to the canonical TechAI prompts.
- Updated `scripts/tech-ai-sync-copilot-configs.py`, `AGENTS.md`, and tests to prefer the new `tech-ai-*` canonical script prompts.
- Reduced token overlap by trimming repository-specific catalog content out of `copilot-instructions.md` and keeping `AGENTS.md` as the single repository-specific source of truth.
- Normalized the `name:` frontmatter for the TechAI sync prompt and skill to `TechAISyncCopilotConfigs`.
- Renamed the remaining canonical `cs-*` prompt files to `tech-ai-*` and updated profile, AGENTS, sync, and test references accordingly.
- Removed the redundant `script-bash.prompt.md` and `script-python.prompt.md` alias prompts to keep one canonical script prompt per stack.

## 2026-03-06
- Added `agents/tech-ai-sync-copilot-configs.agent.md`: `TechAISyncCopilotConfigs` for local repository analysis and conservative Copilot-core alignment.
- Added `prompts/tech-ai-sync-copilot-configs.prompt.md` and `skills/tech-ai-sync-copilot-configs/SKILL.md` for repeatable alignment workflows.
- Added `scripts/tech-ai-sync-copilot-configs.py` plus `tests/test_tech_ai_sync_copilot_configs.py` for deterministic analysis, manifest-based sync planning, and reporting.
- Updated `AGENTS.md` with `TechAISyncCopilotConfigs` routing, inventory, and preferred asset references.
- Reduced `copilot-code-review-instructions.md` to a lighter-weight review protocol that delegates the detailed anti-pattern catalog to `skills/tech-ai-code-review/SKILL.md`.
- Updated `scripts/tech-ai-sync-copilot-configs.py` to prefer canonical `cs-*` script prompts during consumer alignment, reducing prompt duplication and token footprint without removing legacy source assets.
- Added `.github/tech-ai-requirements-dev.txt`, CI pytest execution, `shellcheck` pre-commit coverage, and validator integration tests for stronger local and CI validation.

## 2026-03-04
- Added `skills/tech-ai-code-review/SKILL.md`: per-language anti-pattern catalogs with severity mappings and good-vs-bad examples.
- Added `prompts/cs-code-review.prompt.md`: on-demand strict code review prompt with configurable strictness.
- Added `agents/tech-ai-script-reviewer.agent.md`: exhaustive, nit-level code reviewer (`TechAIScriptReviewer`) for Python, Bash, and Terraform with review persona inspired by Martin Fowler, Raymond Hettinger, and Kelsey Hightower.
- Expanded `copilot-code-review-instructions.md` with Python/Bash/Terraform-specific check sections, `Nit` severity level, and escalation rules.
- Updated `AGENTS.md` with `TechAIScriptReviewer` routing, `code-review` skill, and `cs-code-review` prompt.

## 2026-02-28
- Renamed GitHub-related files to `github-*` prefix for consistency across agents, prompts, instructions, and workflows.

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
- Added PR authoring assets: `prompts/tech-ai-github-pr-description.prompt.md` and `skills/tech-ai-pr-writing/SKILL.md`.
- Updated docs to be repository-agnostic and reusable across different tech stacks.
- Standardized script prompt wording to remove organization-specific terminology and keep language portable.
- Hardened validator frontmatter key detection for multiline YAML keys.
- Extended validator JSON output with per-finding details.
- Added `prompts/tech-ai-github-composite-action.prompt.md` and `skills/tech-ai-composite-action/SKILL.md`.
- Added `prompts/tech-ai-data-registry.prompt.md` and `skills/tech-ai-data-registry/SKILL.md`.
- Expanded `cloud-policy` skill with concrete AWS/Azure/GCP templates.
- Reduced duplication by moving Java/Node examples from instructions to skills.
- Reduced overlap in `scripts.instructions.md` to cross-cutting rules only.
- Added bootstrap hardening (`--include-workflows`, `--exclude`, `--exclude-file`, `.bootstrap-ignore` support).
- Added `.github/CODEOWNERS` baseline and expanded Dependabot ecosystems.
- Enriched instruction files: composite action safety, Lambda specificity, YAML schema hint, Markdown language policy, Makefile example.
- Replaced placeholder `AGENTS.md` with operational guidance tailored for consumer repositories.
