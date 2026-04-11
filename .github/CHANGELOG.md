# Changelog

## Entry template
Use this format for new updates:
- `## YYYY-MM-DD`
- One bullet per meaningful change.
- Include file/path scope when useful.

## 2026-04-11
- Strengthened `internal-critical-challenger` so the challenge lane now distinguishes hard constraints from assumed ones, applies a compact lateral-thinking challenge lens, and reports non-obvious reframes alongside failure modes; aligned the router, routing engine, operating-model engine, and agent selection guide so the expanded challenge contract is discoverable and routable.

## 2026-04-10
- Added the provider skill rollout beyond AWS by creating repository-owned Azure, GCP, and GitHub skill families under `.github/skills/internal-{azure,gcp,github}-*`, keeping the AWS boundary model as the baseline with short adaptive strategic skills, separate organization/governance/operations lanes where justified, minimal `references/`, and `agents/openai.yaml` metadata for every new skill.
- Refreshed `.github/README.md` and `.github/INVENTORY.md` so the maintainer-facing catalog now matches the live provider-skill inventory and the current prompt, skill, and script counts on disk.

## 2026-04-07
- Updated the completion-report policy in `.github/copilot-instructions.md`, `.github/README.md`, and the sync agent and skill contract so synced target repositories now inherit a summary format that lists only the actually used agents, instructions, prompts, skills, and other resources, each with a short reason.

## 2026-04-06
- Externalized the exact path inventory into `.github/INVENTORY.md`, reduced root `AGENTS.md` to a bridge pointer, removed the current repository validator/test layer, and updated maintainer docs, templates, and governance text to stop depending on deleted validation assets and the removed `internal-agents-md-bridge` skill.
- Refactored the instruction architecture around rule ownership: root `AGENTS.md` is now the strategic entrypoint and precedence anchor, `.github/copilot-instructions.md` is the compact repo-wide Copilot projection, `INTERNAL_CONTRACT.md` now captures rebuild-safe invariants instead of deleted automation behavior, scoped Markdown guidance now projects the central English-by-default rule, and sync governance assets were updated to stop treating root `AGENTS.md` as a subordinate thin bridge.
- Slimmed `.github/copilot-instructions.md` by removing stack-owned Python template, script, Java, and Node guidance, and reduced `.github/instructions/internal-bash.instructions.md` to repo-local Bash additions so runtime-specific rules now stay with their matching instruction owners instead of the primary policy layer.
- Removed the source-side `.github/scripts/vendor/` wheelhouse assumption from `scripts/internal-python-runner.sh`, `scripts/internal-sync-copilot-configs.py`, and `tests/test_contract_runner.py` so repository-owned Python wrappers now install only from pinned `requirements.txt` and no longer sync local vendored libraries into consumer repositories.
- Added an explicit Python dependency policy to `.github/copilot-instructions.md` and `.github/instructions/internal-python.instructions.md`: the source of truth is the Python entrypoint plus its adjacent requirements lock file, with no local vendored libraries, no fallback mirrors, and no deprecation path unless the user explicitly requests an exception.
- Corrected `.github/README.md` so the maintained script inventory matches the files that actually exist on disk and no longer advertises a nonexistent `scripts/report-copilot-usage.sh` wrapper.
- Tightened the active non-README governance layer after the refactor: reduced root `AGENTS.md` to a thinner bridge, refreshed `.github/INVENTORY.md` to match the live prompt catalog, removed stale prompt/script/source-of-truth references from active governance assets, and aligned the cross-repository sync agent/skill with the files that actually exist on disk.

## 2026-04-05
- Added `scripts/internal_yaml.py` and reused it from both `internal-sync-copilot-configs.py` and `validate-copilot-customizations.py` so repository-owned Python automation now shares one YAML/frontmatter parser instead of duplicating parsing logic.
- Restored hash-locked Python dependency policy for repository-owned scripts: `scripts/requirements.txt` now carries the pinned `PyYAML` wheel hash and `internal-python-runner.sh` installs with `--require-hashes` without any fallback path.
- Removed the hash-detection fallback from `scripts/internal-python-runner.sh`, switched repository-owned Python launcher guidance to install directly from `requirements.txt`, and deleted the internal Python-policy clause that allowed a non-locked fallback path.
- Added `.github/scripts/requirements.txt` with a pinned `PyYAML` dependency and switched `internal-sync-copilot-configs.py` from bespoke YAML parsing to `PyYAML` for `repo-profiles.yml` and frontmatter handling in repository-owned scripts.
- Aligned the medium-task threshold wording between `internal-agent-routing-engine` and `internal-agent-operating-model-engine`, clarified in `agents/README.md` that `internal-router` is dispatch-only, and hardened `scripts/internal-python-runner.sh` with explicit command and virtual-environment checks.
- Enforced router-only delegation across `internal-router`, the four canonical operational agents, `internal-agent-operating-model-engine`, `internal-agent-development`, `INTERNAL_CONTRACT.md`, and the validator/tests so non-router agents now define boundaries and recommend owners instead of routing actively.
- Added `internal-python-runner.sh`, Bash wrappers for every executable repository Python entrypoint, explicit `PyYAML` requirements for `openai-skill-creator`, and wrapper-first invocation guidance across prompts, skills, scripts, security docs, and maintainer workflow references.
- Hardened `.github/scripts/validate-copilot-customizations.py`, `tests/test_contract_runner.py`, and `tests/test_validate_copilot_customizations.py` so canonical operational agents must point only to real canonical escalation targets, must not self-route, and stale retired-agent references are caught case-insensitively.
- Clarified `internal-router` and `internal-agent-routing-engine` so medium-confidence routing asks at most one targeted clarification question with two clear options before falling back to `internal-planning-leader`.
- Strengthened `.github/skills/internal-code-review/SKILL.md` with a standalone quick-start so the skill stays usable directly as a tactical review asset, not only as the review guard's engine.
- Refreshed `.github/README.md` so the maintainer-facing catalog now matches the live `internal-*`, `obra-*`, and imported support families, the canonical internal agent model, and the actual scripts and workflow present on disk after recent repository restructuring.

## 2026-04-04
- Added a mandatory end-of-operation completion report contract to `.github/copilot-instructions.md`, documented the same emoji-based `Outcome` / `Agents` / `Instructions` / `Skills` structure in `.github/README.md`, and kept root `AGENTS.md` on a thin bridge pointer to the detailed policy.
- Extended `INTERNAL_CONTRACT.md`, `tests/test_contract_runner.py`, `tests/test_validate_copilot_customizations.py`, and `.github/scripts/validate-copilot-customizations.py` so the completion-report contract is now source-governed and strict-validator enforced.
- Updated `internal-sync-control-center`, `internal-sync-global-copilot-configs-into-repo`, and the sync skill workflow so completed sync runs must also end with the same completion-report categories and explicit unused-category explanations.
- Updated sync governance and `.github/scripts/internal-sync-copilot-configs.py` so retained sync plans now live under repository-root `tmp/` instead of `.github/`, and the tracking-plan flow creates `tmp/` automatically when it is missing.
- Updated `.github/copilot-instructions.md`, `.github/instructions/internal-python.instructions.md`, and `.github/skills/internal-script-python/SKILL.md` so new Python scripts must make an explicit stdlib-vs-library decision, prefer mature third-party packages when they clearly simplify the final code, and record that choice in a short dependency decision note before implementation.

## 2026-03-19
- Updated `.github/copilot-instructions.md`, `.github/instructions/python.instructions.md`, and `.github/prompts/tech-ai-python.prompt.md` so Python tasks now standardize on human-readable hash-locked `requirements.txt` files for external dependencies, clarify that the lock file should capture the full dependency closure, and treat third-party libraries as a recommendation only when they materially simplify the code.
- Updated `.github/prompts/tech-ai-python-script.prompt.md`, `.github/skills/tech-ai-script-python/SKILL.md`, and `.github/instructions/bash.instructions.md` so new standalone Python tools default to a self-contained folder with a `run.sh` launcher, add a local `requirements.txt` only when external packages are used, and bootstrap `.venv` plus locked dependency installation only when that file exists.

## 2026-03-13
- Updated `.pre-commit-config.yaml` to pin `pre-commit-hooks` `v6.0.0`, keep `pre-commit-terraform` explicitly annotated at `v1.105.0`, and move `shellcheck-py` to `v0.11.0.1`, adding inline release comments for each pinned revision.
- Updated `.github/workflows/github-validate-copilot-customizations.yml` to pin the runner to `ubuntu-24.04`, add `actions/setup-python` pinned by SHA for Python `3.14.3`, pin `pip` to `26.0.1`, and replace the unpinned `apt` shellcheck install with the pinned Python dependency set from `.github/tech-ai-requirements-dev.txt`.
- Annotated `.github/workflows/terraform-pre-commit.yml` image digest references with the corresponding `pre-commit-terraform` release version to make the SHA-based pin self-describing.
- Strengthened the Copilot baseline so Python guidance prefers hash-locked requirements, Terraform guidance pins external modules as well as providers, GitHub Actions guidance pins container images by digest, and Docker now has dedicated instruction/prompt/skill coverage across `AGENTS.md`, the sync planner, and validation tests.
- Removed `.github/workflows/github-validate-copilot-customizations.yml` from the source baseline and stopped the sync planner from recommending that workflow to consumer repositories.
- Updated `.github/scripts/internal-sync-copilot-configs.py` so the default VS Code PR description mode expected during consumer alignment is now `template` instead of `Copilot`.

## 2026-03-12
- Renamed the canonical PR prompt from `tech-ai-pr-description.prompt.md` / `TechAIPRDescription` to `tech-ai-pr-editor.prompt.md` / `TechAIPREditor`, and updated `AGENTS.md`, the validator, and review notes to use the new canonical name consistently.
- Updated `scripts/internal-sync-copilot-configs.py` and its tests so sync plans now delete manifest-managed files that were removed from the desired baseline, allowing canonical renames to cleanly remove deprecated managed assets in consumer repositories.

## 2026-03-11
- Updated `scripts/internal-sync-copilot-configs.py` so consumer sync now discovers new instructions from `applyTo`, automatically includes all portable consumer-facing agents, and merges consumer-facing prompt/skill capabilities declared in the source `AGENTS.md` preferred sections. This prevents newly added shared assets such as the PAIR analysis flow from being silently skipped in downstream repos.
- Updated `scripts/internal-sync-copilot-configs.py` and `tests/test_tech_ai_sync_copilot_configs.py` so consumer alignment now reports a target-side gap when `.vscode/settings.json` is missing or does not set `githubPullRequests.pullRequestDescription` to `Copilot`, making the VS Code PR-form Copilot dependency visible in sync reports.

## 2026-03-09
- Added the repo-only `TechAIRepoCopilotExtender` agent, prompt, and skill for creating consumer-repository `internal-*` Copilot assets without duplicating the shared baseline, and excluded the trio from consumer sync.
- Tightened `TechAIRepoCopilotExtender` so it must ground repo-local prompts, examples, schema snippets, and naming rules on concrete target files instead of generic remembered patterns.
- Deprecated `.github/scripts/bootstrap-copilot-config.sh` in favor of `.github/scripts/internal-sync-copilot-configs.py`, updated lifecycle docs, and made quickstart plus `.github/README.md` prefer sync-first alignment.
- Added source release metadata with root `VERSION`, contributor workflow documentation, and manifest provenance fields for source version and commit.
- Tightened consumer alignment: improved composite-action detection, enabled data-registry selection for JSON-heavy repositories, slimmed generated `AGENTS.md`, removed spurious `pytest` recommendations for repos without pytest tests, and added sync recommendations for missing Copilot validation workflows plus legacy source-only residues.
- Reduced source maintenance noise by trimming Dependabot ecosystems, updating the GitHub Actions checkout example, adding explicit `.github/` CODEOWNERS coverage, and documenting security-control enforcement status.
- Expanded validator and sync tests to cover new recommendation, rendering, provenance, and validation paths.

## 2026-03-08
- Updated the PR-writing prompt, skill, and agent guidance to derive required sections from the resolved repository PR template instead of hardcoding older headings such as `Security and Compliance` or `Related Links`.
- Updated `scripts/internal-sync-copilot-configs.py` and `scripts/validate-copilot-customizations.sh` so repository-owned prompt, skill, and agent assets outside the synced global baseline must use `internal-*` in both filenames and `name:` values, making internal customizations visibly distinct from synced `tech-ai-*` assets.
- Updated `scripts/internal-sync-copilot-configs.py` so target-only skill detection compares full relative paths instead of the shared `SKILL.md` filename, fixing missed unmanaged skill assets in consumer repositories.
- Expanded sync planning to audit unmanaged target-local instructions, prompts, skills, and agents for strict validation gaps and legacy alias drift, and added the new report section in both markdown and JSON outputs.
- Updated sync planning so legacy aliases such as `cs-*`, unprefixed prompt names, and legacy skill directories are reported even when the canonical family is outside the selected minimum baseline.
- Updated generated `AGENTS.md` inventory rendering and `.github/templates/AGENTS.template.md` so inventory reflects the desired managed baseline plus target-local Copilot assets already present in the consumer repository.
- Added source-side redundancy auditing to `scripts/internal-sync-copilot-configs.py`, including canonical asset inventory, legacy alias detection, triad role-overlap checks, and `AGENTS.md` inventory-repeat detection in both markdown and JSON reports.
- Refactored `agents/tech-ai-sync-global-copilot-configs-into-repo.agent.md`, `skills/tech-ai-sync-global-copilot-configs-into-repo/SKILL.md`, and `prompts/tech-ai-sync-global-copilot-configs-into-repo.prompt.md` so workflow detail lives in the skill while the agent and prompt stay thin.
- Simplified root `AGENTS.md` and `.github/templates/AGENTS.template.md` to keep asset paths in the inventory section only and remove descriptive prompt or skill catalogs.
- Expanded sync and validator tests to cover source audit behavior, slimmer AGENTS structure, and JSON report sections.
- Updated `agents/tech-ai-sync-global-copilot-configs-into-repo.agent.md`, `skills/tech-ai-sync-global-copilot-configs-into-repo/SKILL.md`, and `prompts/tech-ai-sync-global-copilot-configs-into-repo.prompt.md` so the sync workflow explicitly detects redundant legacy aliases before apply.
- Updated `scripts/internal-sync-copilot-configs.py` to recognize legacy `cs-*`, unprefixed prompt names, and legacy agent or skill aliases, report them as redundant target assets, and raise sync conflicts instead of creating duplicate canonical `tech-ai-*` assets.
- Updated `tests/test_tech_ai_sync_copilot_configs.py` to cover duplicate-alias detection and conflict behavior during sync planning.

## 2026-03-07
- Added repo-only global customization agents `TechAIStandardsRepoConfigBuilder` and `TechAIStandardsRepoConfigAuditor` for standards-authoring and final quality gates in this repository.
- Marked `TechAICustomizationAuditor` as a deprecated compatibility alias that now points to `TechAIStandardsRepoConfigAuditor`.
- Updated root `AGENTS.md`, agent catalog docs, sync exclusions, validator semantics, and tests to treat the `TechAIGlobal*` pair as repo-only standards agents.
- Added `.gitignore` coverage for Python caches/virtualenvs and macOS Finder artifacts so local validation runs stop creating noisy untracked files.
- Added canonical low-duplication script prompts: `prompts/tech-ai-bash-script.prompt.md` (`TechAIBashScript`) and `prompts/tech-ai-python-script.prompt.md` (`TechAIPythonScript`).
- Reduced the legacy `cs-*` and `script-*` Bash/Python prompts to thin compatibility aliases that now point to the canonical TechAI prompts.
- Updated `scripts/internal-sync-copilot-configs.py`, `AGENTS.md`, and tests to prefer the new `tech-ai-*` canonical script prompts.
- Reduced token overlap by trimming repository-specific catalog content out of `copilot-instructions.md` and keeping `AGENTS.md` as the single repository-specific source of truth.
- Normalized the `name:` frontmatter for the TechAI sync prompt and skill to `TechAISyncGlobalCopilotConfigsIntoRepo`.
- Renamed the remaining canonical `cs-*` prompt files to `tech-ai-*` and updated profile, AGENTS, sync, and test references accordingly.
- Removed the redundant `script-bash.prompt.md` and `script-python.prompt.md` alias prompts to keep one canonical script prompt per stack.

## 2026-03-06
- Added `agents/tech-ai-sync-global-copilot-configs-into-repo.agent.md`: `TechAISyncGlobalCopilotConfigsIntoRepo` for local repository analysis and conservative Copilot-core alignment.
- Added `prompts/tech-ai-sync-global-copilot-configs-into-repo.prompt.md` and `skills/tech-ai-sync-global-copilot-configs-into-repo/SKILL.md` for repeatable alignment workflows.
- Added `scripts/internal-sync-copilot-configs.py` plus `tests/test_tech_ai_sync_copilot_configs.py` for deterministic analysis, manifest-based sync planning, and reporting.
- Updated `AGENTS.md` with `TechAISyncGlobalCopilotConfigsIntoRepo` routing, inventory, and preferred asset references.
- Reduced `copilot-code-review-instructions.md` to a lighter-weight review protocol that delegates the detailed anti-pattern catalog to `skills/tech-ai-code-review/SKILL.md`.
- Updated `scripts/internal-sync-copilot-configs.py` to prefer canonical `cs-*` script prompts during consumer alignment, reducing prompt duplication and token footprint without removing legacy source assets.
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
- Added PR authoring assets: `prompts/tech-ai-pr-description.prompt.md` and `skills/tech-ai-pr-editor/SKILL.md`.
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
