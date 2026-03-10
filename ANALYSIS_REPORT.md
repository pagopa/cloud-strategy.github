# Cloud Strategy GitHub — Comprehensive Analysis Report

> **STATUS**: SUPERSEDED by `COPILOT_REVIEW.md` dated 2026-03-09. Some findings below are already resolved and should be treated as historical context, not the current source of truth.

> **Generated**: 2025-07-17
> **Scope**: Full repository audit of `cloud-strategy.github`
> **Purpose**: Identify issues, improvement opportunities, and unconsidered areas in the central Copilot customization standards repository.

---

## Table of Contents

- [Executive Summary](#executive-summary)
- [1 — Issues Found (Things That Are Wrong)](#1--issues-found-things-that-are-wrong)
- [2 — Improvements (Things That Can Be Better)](#2--improvements-things-that-can-be-better)
- [3 — Unconsidered Areas (Gaps and Missing Pieces)](#3--unconsidered-areas-gaps-and-missing-pieces)
- [4 — Structural and Architectural Observations](#4--structural-and-architectural-observations)
- [5 — Security and Compliance](#5--security-and-compliance)
- [6 — Testing and Quality](#6--testing-and-quality)
- [7 — Documentation and Onboarding](#7--documentation-and-onboarding)
- [8 — Prioritized Action Plan](#8--prioritized-action-plan)

---

## Executive Summary

The `cloud-strategy.github` repository serves as the authoritative source for GitHub Copilot customization assets propagated to all consumer repositories. The framework is well-structured with a clear hierarchy (instructions → prompts → skills → agents) and demonstrates strong conventions for Terraform, Bash, and Python workflows. However, the audit reveals **critical prompt duplication**, **incomplete test coverage**, **missing governance enforcement mechanisms**, and several **unconsidered areas** that could weaken configuration quality as the organization scales.

**Severity summary**:

| Severity | Count |
|----------|-------|
| Critical | 4 |
| Major | 11 |
| Minor | 14 |
| Advisory | 9 |

---

## 1 — Issues Found (Things That Are Wrong)

### 1.1 [Critical] Prompt Duplication Creates Ambiguity

Two pairs of prompts serve nearly identical purposes with overlapping content:

- `cs-bash-script.prompt.md` vs `script-bash.prompt.md`
- `cs-python-script.prompt.md` vs `script-python.prompt.md`

Both pairs reference the same skills (`script-bash` / `script-python`) and produce the same deliverables. The `cs-*` variants add `${input:...}` variables, while the `script-*` variants use the `mode:` input variable. This creates a confusion surface for consumer repositories: which prompt should they use? The `cs-bash-script` prompt references `"agent: implementer"` while `script-bash` references `"agent: Implementer"` — inconsistent casing in the agent name.

**Impact**: Consumer repos adopting this configuration may select the wrong prompt, leading to inconsistent output. Agents referencing one prompt may miss the other.

**Recommendation**: Consolidate each pair into a single prompt. Keep the `cs-*` naming convention for consistency with other prompts (`cs-terraform`, `cs-java`, etc.), and deprecate the `script-*` variants using the lifecycle process defined in `DEPRECATION.md`.

### 1.2 [Critical] Agent Name Casing Inconsistency

Agent references across prompts use inconsistent casing:

| File | Value |
|------|-------|
| `cs-bash-script.prompt.md` | `agent: implementer` |
| `script-bash.prompt.md` | `agent: Implementer` |
| `cs-python-script.prompt.md` | `agent: implementer` |
| `script-python.prompt.md` | `agent: Implementer` |
| `cs-terraform.prompt.md` | `agent: implementer` |
| `cs-java.prompt.md` | `agent: implementer` |
| `cs-nodejs.prompt.md` | `agent: implementer` |

This inconsistency could cause agent routing failures in tools that perform case-sensitive matching.

**Recommendation**: Standardize to `agent: implementer` (lowercase) across all prompts and validate in the `validate-copilot-customizations.sh` script.

### 1.3 [Critical] `copilot-code-review-instructions.md` Duplicates `code-review` SKILL Content

The file `.github/copilot-code-review-instructions.md` contains inline anti-pattern catalogs for Python, Bash, and Terraform that substantially overlap with `skills/code-review/SKILL.md`. When both are loaded, the LLM receives contradictory or redundant severity mappings.

The SKILL file is far more comprehensive (detailed per-language tables, escalation rules, output templates) while the review instructions are a condensed subset. Maintaining both creates a divergence risk.

**Recommendation**: Reduce `copilot-code-review-instructions.md` to a lightweight pointer that establishes severity levels and escalation rules only, then explicitly references the `code-review` SKILL for the anti-pattern catalogs. This ensures single-source-of-truth for review patterns.

### 1.4 [Critical] Validator Does Not Check for Prompt Duplication

The `validate-copilot-customizations.sh` script validates frontmatter keys, section headings, agent structure, and inventory consistency, but it does **not** detect:

- Prompts with overlapping `name:` values or duplicate purpose
- Prompts referencing the same skill set with identical deliverables
- Inconsistent `agent:` casing across prompts

**Recommendation**: Add a validation pass that groups prompts by referenced skill and flags potential duplicates with a warning.

---

## 2 — Improvements (Things That Can Be Better)

### 2.1 [Major] No Versioning or Release Strategy

The configurations lack a versioning mechanism. Consumer repositories cannot pin to a specific version of the standards. The `CHANGELOG.md` documents changes by date, but there are no git tags, no semantic versioning, and no release process.

**Impact**: When a breaking change is introduced (e.g., renaming a prompt, removing a skill), all consumers are immediately affected with no rollback path.

**Recommendation**:
1. Adopt semantic versioning (`vMAJOR.MINOR.PATCH`) with git tags.
2. Add a `VERSION` file at the repository root.
3. Update the sync script to include the source version in the manifest.
4. Document the release process in `CONTRIBUTING.md` or a new `RELEASING.md`.

### 2.2 [Major] Profile System Is Advisory-Only

`repo-profiles.yml` defines 6 profiles (`minimal`, `backend-java`, `backend-nodejs`, `backend-python`, `infrastructure-heavy`, `mixed-platform`) but enforcement is purely advisory. The sync script auto-detects profiles, but consumer repos can ignore the recommendations entirely.

**Recommendation**:
1. Add a `.github/copilot-profile.yml` to consumer repos that locks the selected profile.
2. Have the validator script check that the consumer's active instructions/prompts/skills match the declared profile.
3. Generate a "profile compliance" section in sync reports.

### 2.3 [Major] `dependabot.yml` Includes Unused Ecosystems

The `dependabot.yml` file configures updates for `pip`, `npm`, `maven`, `gradle`, and `terraform` ecosystems. This repository itself only contains Bash scripts, Python scripts, and Terraform pre-commit hooks. The `npm`, `maven`, and `gradle` ecosystems will never find package manifests in this repo.

**Impact**: Unnecessary Dependabot runs consume CI minutes and create noise.

**Recommendation**: Remove `npm`, `maven`, and `gradle` ecosystems from `dependabot.yml`. If they are included as a template for consumers, document this clearly and move the full template to `templates/dependabot.template.yml`.

### 2.4 [Major] Bootstrap Script and Sync Script Overlap

Two tools exist for propagating configurations to consumer repos:

- `bootstrap-copilot-config.sh`: rsync-based, simple copy with exclude patterns, destructive by default with `--clean`.
- `tech-ai-sync-copilot-configs.py`: manifest-based, conservative merge with conflict detection, SHA256 checksums, reporting.

The bootstrap script is older and less sophisticated. Its existence alongside the sync script creates confusion about which to use.

**Recommendation**: Deprecate the bootstrap script in favor of the sync script. Add a deprecation notice to the bootstrap script header and update documentation. If the bootstrap script serves a "quick start" use case, make it a thin wrapper that calls the sync script with `--mode apply`.

### 2.5 [Major] No Automated Integration Tests for Sync Workflow

The test file `tests/test_tech_ai_sync_copilot_configs.py` has only 5 tests covering basic plan/apply scenarios. Missing coverage includes:

- Conflict resolution behavior (manual merge scenarios)
- `--mode plan` vs `--mode apply` with dirty state
- Profile override via `--profile` flag
- Report format (JSON and Markdown output validation)
- Error handling (missing source, corrupted manifest, permission issues)
- AGENTS.md rendering accuracy per profile
- `copilot-instructions.md` Repository Alignment section tailoring

**Recommendation**: Expand the test suite to at least 15-20 tests covering edge cases. Add a `Makefile` target for running tests (`make test`).

### 2.6 [Major] Missing `Makefile` for Developer Workflow

The repository has no `Makefile`. The `eng-azure-governance` consumer repo has one, but the standards repo itself lacks standardized development commands.

**Recommendation**: Add a `Makefile` with targets:
- `lint`: Run shellcheck, bash -n, python compile, yaml lint
- `validate`: Run `validate-copilot-customizations.sh --scope root --mode strict`
- `test`: Run pytest on the tests directory
- `fmt`: Run terraform fmt, pre-commit autofixes
- `all`: Run lint + validate + test

### 2.7 [Major] `.bootstrap-ignore` Is Empty

The file exists but contains only comments. It appears to be a placeholder that was never populated.

**Recommendation**: Either populate it with sensible defaults (e.g., `templates/`, `tests/`, `ANALYSIS_REPORT.md`) or remove it and document the exclusion mechanism in the bootstrap script itself.

### 2.8 [Major] No `LICENSE` File

The repository has no license file. For an internal repository this may be intentional, but leaving it absent creates ambiguity about usage rights for other teams or future open-sourcing.

**Recommendation**: Add an appropriate license file. For internal-only use, a simple `LICENSE` stating "Internal use only — [Organization Name]" suffices.

### 2.9 [Major] Prompt `argument-hint` Inconsistency

Some prompts use `argument-hint:` in frontmatter, others omit it. The validator does not enforce its presence:

| Has `argument-hint` | Count |
|---------------------|-------|
| Yes | ~14 |
| No | ~6 |

Prompts without `argument-hint` force the user to read the full prompt body to understand expected inputs.

**Recommendation**: Require `argument-hint` in all prompts and add a validator check.

### 2.10 [Major] `tech-ai-sync-copilot-configs.py` Has No `requirements.txt`

The Python script imports only stdlib (`argparse`, `dataclasses`, `hashlib`, `json`, `pathlib`, `re`, `sys`, `textwrap`), so no external deps are needed today. However, per the repository's own convention (`copilot-instructions.md` — "Python: if external dependencies are used, pin versions in `requirements.txt`"), there is no `requirements.txt` at all, not even an empty one or one with `pytest` for the test runner.

**Recommendation**: Add a `requirements.txt` (or `requirements-dev.txt`) that pins `pytest` for test execution. This also supports CI reproducibility.

### 2.11 [Major] Workflow SHA Pinning Comment Format Varies

The CI workflow uses:
```yaml
uses: actions/checkout@de0fac2e4500dabe0009e67214ff5f5447ce83dd # v6.0.2
```

This follows the convention, but the validator should be verifying that **every** `uses:` with a SHA has an adjacent version comment. Currently the validator checks for SHA format but the regex for the adjacent comment could miss edge cases (e.g., multi-line `uses` with `with:` block between the SHA and comment).

**Recommendation**: Strengthen the SHA-pinning validation regex to handle edge cases and add a test case for it.

---

## 3 — Unconsidered Areas (Gaps and Missing Pieces)

### 3.1 [Major] No Docker/Container Instruction or Skill

The `AGENTS.md` has a backlog trigger: "Add `instructions/docker.instructions.md` when the first Dockerfile is introduced." However, many consumer repos likely already use Dockerfiles. The standards repo should proactively provide Docker instructions rather than waiting for a trigger that may never fire in this repo.

**Recommendation**: Create `instructions/docker.instructions.md` with standards for multi-stage builds, non-root users, layer caching, `.dockerignore`, and health checks. Add a corresponding `skills/docker/SKILL.md`.

### 3.2 [Minor] No .NET / C# / Go Instruction Coverage

The sync script explicitly lists unsupported file types: `.cs`, `.go`, `.rs`, `.rb`. If any consumer repos use .NET or Go, they have no Copilot instruction guidance from the standards repo.

**Recommendation**: Prioritize based on consumer repo inventory. If .NET or Go repos exist, add instructions and skills for those stacks.

### 3.3 [Minor] No Instruction for SQL / Database Migrations

Consumer repos with database components have no SQL instruction file. Database migrations are a common source of errors and data loss.

**Recommendation**: Consider adding `instructions/sql.instructions.md` covering migration safety (backward-compatible migrations, no DROP in production, idempotent scripts).

### 3.4 [Minor] No Observability / Logging Standard in Instructions

While several skills mention logging patterns (emoji logs for scripts), there is no cross-cutting instruction for application-level observability (structured logging, correlation IDs, metric naming).

**Recommendation**: Add an `instructions/observability.instructions.md` overlay for application code.

### 3.5 [Minor] No Secret Scanning Configuration

The repository has `detect-private-key` in pre-commit, but there is no GitHub secret scanning configuration, no `.gitleaks.toml`, and no mention of scanning in the CI workflow.

**Recommendation**: Add a secret scanning tool (e.g., `gitleaks` or `trufflehog`) to the pre-commit config and CI pipeline.

### 3.6 [Minor] No Branch Protection Documentation

The `security-baseline.md` mentions branch protection as a required control but does not provide a reference configuration. Consumer repos have no template to follow.

**Recommendation**: Add a `templates/branch-protection.json` or document the expected branch protection settings in `security-baseline.md`.

### 3.7 [Minor] No Renovate Alternative Mentioned

`dependabot.yml` is the only dependency update mechanism. Some organizations prefer Renovate for its configurability and auto-merge capabilities.

**Recommendation**: At minimum, document why Dependabot was chosen over alternatives. Optionally provide a `templates/renovate.json` for teams that prefer it.

### 3.8 [Minor] No CODEOWNERS Template for Consumers

The `CODEOWNERS` file in this repo has only 2 owners. The validator warns about placeholder owners in consumer repos, but there is no `templates/CODEOWNERS.template` that consumers can adapt.

**Recommendation**: Add a CODEOWNERS template with team-based ownership patterns and documentation.

### 3.9 [Advisory] No Metrics on Configuration Effectiveness

There is no mechanism to measure whether the Copilot configurations actually improve code quality, reduce review cycles, or increase developer productivity. Without metrics, the ROI of maintaining this framework is unmeasurable.

**Recommendation**: Consider tracking:
- PR review cycle time before/after configuration adoption
- Number of Copilot-assisted commits per repo
- Code review finding rate (Critical/Major findings per PR)
- Developer satisfaction surveys

### 3.10 [Minor] No Stale Configuration Detection

When a consumer repo drifts from the standards (e.g., manually editing managed files), there is no automated detection mechanism other than running the sync script.

**Recommendation**: Add a scheduled CI workflow that runs the sync script in `plan` mode on all consumer repos and reports drift.

### 3.11 [Minor] No Rollback Mechanism in Sync Script

The sync script has `apply` mode but no `rollback` mode. If a sync introduces issues, the consumer must manually revert.

**Recommendation**: Before applying changes, save a backup snapshot (tarball of affected files) and provide a `--rollback` flag.

### 3.12 [Advisory] No Prompt Testing Framework

Prompts are validated for frontmatter structure, but their actual effectiveness (whether they produce the expected output quality) is never tested. This is a known industry gap, but some frameworks exist for prompt regression testing.

**Recommendation**: Long-term, consider a prompt evaluation framework that runs sample inputs through prompts and validates output quality against rubrics.

---

## 4 — Structural and Architectural Observations

### 4.1 [Minor] Skill Reference Chain Is Implicit

Skills reference other skills and instructions only by name in prose. There is no machine-readable dependency graph. For example, `terraform-feature` SKILL references `terraform.instructions.md` by convention but not explicitly.

**Recommendation**: Add a `dependencies:` frontmatter field to SKILL.md files listing required instructions and other skills. This enables automated validation of complete dependency chains.

### 4.2 [Minor] Agent `tools:` Section Is Inconsistent

Some agents list `tools:` with VS Code-specific tool names (`semantic_search`, `run_in_terminal`), while others omit the section entirely. The tool names are runtime-specific and may not apply across all Copilot hosts.

**Recommendation**: Either standardize the `tools:` section across all agents or remove it entirely from agent files (since tool availability is determined by the runtime, not the agent definition).

### 4.3 [Advisory] `AGENTS.md` Inventory Is Not Auto-Updated

The `AGENTS.md` "Repository Inventory" section claims to be auto-generated, but there is no automation that actually updates it. It must be manually maintained, creating a drift risk.

**Recommendation**: Add a script (or extend `validate-copilot-customizations.sh`) that regenerates the inventory section from the filesystem and fails validation if it is stale.

### 4.4 [Advisory] Prompt Input Variables Are Not Standardized

Prompts use `${input:variable_name}` syntax, but variable names are inconsistent:

- `${input:target_file}` vs `${input:file_path}` vs `${input:target_path}`
- `${input:feature_description}` vs `${input:description}` vs `${input:purpose}`

**Recommendation**: Define a canonical set of input variable names (e.g., `target_path`, `purpose`, `language`, `test_framework`) and document them. Ensure prompts use these canonical names.

### 4.5 [Advisory] No Explicit Order of Instruction Application

When multiple instructions apply to the same file (e.g., a Bash script under `scripts/` gets both `bash.instructions.md` and `scripts.instructions.md`), the application order is documented in `AGENTS.md` as "primary + overlay," but there is no mechanism to enforce that the overlay does not contradict the primary.

**Recommendation**: Add a "conflict resolution" section to the overlay instructions explicitly stating which primary rules they defer to.

### 4.6 [Advisory] The `add-platform.prompt.md` Prompt Is Too Generic

The prompt for adding a new platform profile is very broad and relies heavily on the agent understanding the full frameworks conventions. It could produce inconsistent results across different sessions.

**Recommendation**: Add a checklist of required deliverables (instruction file, profile entry, skills selection, AGENTS.md template updates) directly in the prompt body.

---

## 5 — Security and Compliance

### 5.1 [Minor] `security-baseline.md` Lacks Enforcement Automation

The security baseline document lists controls (SHA pinning, OIDC, branch protection, etc.) but enforcement is only partial:

- SHA pinning: validated by the shell script ✅
- OIDC: not validated ❌
- Branch protection: not validated ❌
- Prompt safety (no embedded secrets): partially validated (pre-commit `detect-private-key`) ⚠️
- Agent safety (read-only by default): not validated ❌

**Recommendation**: Map each security baseline control to an automated check and track coverage.

### 5.2 [Minor] Pre-commit Hooks Missing `shellcheck`

The `.pre-commit-config.yaml` includes `check-executables-have-shebangs` but not `shellcheck`. The CI workflow installs shellcheck, but developers do not get local feedback before pushing.

**Recommendation**: Add `shellcheck` to pre-commit config for immediate developer feedback:
```yaml
- repo: https://github.com/shellcheck-py/shellcheck-py
  rev: v0.10.0.1
  hooks:
    - id: shellcheck
      args: ["-s", "bash"]
```

### 5.3 [Advisory] No GPG Commit Signing Requirement

The repository enforces conventional commits via `copilot-commit-message-instructions.md` but does not require or recommend GPG/SSH commit signing.

**Recommendation**: Add commit signing guidance to `security-baseline.md` and document the setup process.

### 5.4 [Advisory] `CODEOWNERS` Has Very Narrow Ownership

Only `@pagopa/engineering-cloud` and `@GNuccio96` own all files. For a repository that impacts all consumer repos, this creates a bus factor of approximately 2.

**Recommendation**: Consider adding more reviewers or team-based ownership patterns (e.g., a dedicated `@pagopa/copilot-standards` team).

---

## 6 — Testing and Quality

### 6.1 [Major] Test Coverage Is Minimal

The single test file `tests/test_tech_ai_sync_copilot_configs.py` has only 5 test functions:

1. `test_build_plan_detects_infrastructure_heavy_and_root_agents_conflict` — profile detection + conflict
2. `test_build_plan_adopts_matching_source_files_and_reports_target_only_prompts` — adopt + missing asset detection
3. `test_apply_plan_writes_manifest_and_managed_files` — basic apply
4. `test_rendered_agents_markdown_keeps_github_copilot_wording` — naming policy
5. `test_main_supports_targets_without_existing_github_directory` — no .github dir scenario

**Not covered**:
- `validate-copilot-customizations.sh` has zero tests
- `bootstrap-copilot-config.sh` has zero tests
- Profile override (`--profile` flag)
- Multiple target profiles (`backend-java`, `backend-nodejs`, `backend-python`, `minimal`, `mixed-platform`)
- Conflict handling beyond AGENTS.md
- Manifest corruption/migration
- Markdown report output format
- Error paths (missing source repo, invalid arguments, permission errors)
- Edge cases (empty consumer repo, consumer with `.github` but no instructions)

**Recommendation**:
1. Add shell test framework (e.g., `bats-core`) for Bash script testing.
2. Expand Python tests to cover all profiles and edge cases.
3. Add a `make test` target that runs both test suites.
4. Target at least 80% line coverage for the Python sync script.

### 6.2 [Minor] No CI Step for Running Python Tests

The CI workflow (`github-validate-copilot-customizations.yml`) runs the Bash validator and shellcheck but does **not** run `pytest` on the Python tests.

**Recommendation**: Add a job step that installs pytest and runs the test suite.

### 6.3 [Minor] No Test for Validator Script Output

The `validate-copilot-customizations.sh` script supports `--report-json` and `--report-file` options, but these are not tested in CI or in any test file.

**Recommendation**: Add CI steps or test scripts that validate the JSON report output format.

---

## 7 — Documentation and Onboarding

### 7.1 [Minor] `copilot-quickstart.md` Template Is Generic

The quickstart template provides general instructions but lacks:
- Screenshot or diagram of the framework hierarchy
- Troubleshooting section ("Why is my instruction not applying?")
- FAQ section
- Link to example consumer repo that demonstrates proper setup

**Recommendation**: Enrich the quickstart with visual aids, FAQ, and a troubleshooting guide.

### 7.2 [Minor] No Architecture Diagram

The framework has a clear hierarchy (instructions → prompts → skills → agents) but no visual representation. A Mermaid diagram in the README or a dedicated `ARCHITECTURE.md` would significantly improve comprehension.

**Recommendation**: Add a Mermaid diagram showing:
- The hierarchy of customization assets
- The flow from standards repo to consumer repos
- The validation and sync pipeline

### 7.3 [Advisory] `CONTRIBUTING.md` Is Missing

There is no `CONTRIBUTING.md` file. Contributors have no documented process for adding new instructions, prompts, skills, or agents.

**Recommendation**: Add `CONTRIBUTING.md` covering:
- How to add a new instruction file
- How to add a new prompt
- How to add a new skill
- How to add a new agent
- Naming conventions
- Validation requirements before PR
- Review process

### 7.4 [Advisory] `CHANGELOG.md` Entries Use Future Dates

The changelog has entries dated in 2026 (e.g., `2026-02-07`, `2026-02-28`, `2026-03-04`, `2026-03-06`). If the current year is 2025, these dates are incorrect and suggest a timezone or date misconfiguration. If the current year is 2026, ignore this finding.

**Recommendation**: Verify changelog dates are accurate.

---

## 8 — Prioritized Action Plan

### Phase 1 — Immediate (Week 1-2)

| # | Action | Severity | Effort |
|---|--------|----------|--------|
| 1 | Consolidate duplicate prompts (bash/python script pairs) | Critical | Low |
| 2 | Standardize agent name casing in all prompts | Critical | Low |
| 3 | Add validator check for prompt duplication | Critical | Medium |
| 4 | Refactor `copilot-code-review-instructions.md` to reference `code-review` SKILL | Critical | Medium |
| 5 | Add `requirements-dev.txt` with `pytest` | Major | Low |
| 6 | Add pytest step to CI workflow | Minor | Low |

### Phase 2 — Short Term (Week 3-4)

| # | Action | Severity | Effort |
|---|--------|----------|--------|
| 7 | Add `Makefile` for developer workflow | Major | Low |
| 8 | Clean up `dependabot.yml` unused ecosystems | Major | Low |
| 9 | Deprecate `bootstrap-copilot-config.sh` in favor of sync script | Major | Medium |
| 10 | Expand Python test suite (target 15+ tests) | Major | Medium |
| 11 | Add `CONTRIBUTING.md` | Advisory | Medium |
| 12 | Add architecture Mermaid diagram | Minor | Low |

### Phase 3 — Medium Term (Month 2)

| # | Action | Severity | Effort |
|---|--------|----------|--------|
| 13 | Implement semantic versioning with git tags | Major | Medium |
| 14 | Create `instructions/docker.instructions.md` | Major | Medium |
| 15 | Add `shellcheck` to pre-commit config | Minor | Low |
| 16 | Add profile compliance validation | Major | High |
| 17 | Add `bats-core` tests for Bash scripts | Minor | Medium |
| 18 | Standardize prompt input variable names | Advisory | Medium |

### Phase 4 — Long Term (Quarter 2)

| # | Action | Severity | Effort |
|---|--------|----------|--------|
| 19 | Add stale configuration drift detection workflow | Minor | High |
| 20 | Add rollback mechanism to sync script | Minor | High |
| 21 | Add secret scanning tool (gitleaks) | Minor | Medium |
| 22 | Map security baseline controls to automated checks | Minor | High |
| 23 | Add .NET/Go instructions if consumer repos need them | Minor | Medium |
| 24 | Explore prompt evaluation/regression framework | Advisory | High |
| 25 | Implement configuration effectiveness metrics | Advisory | High |

---

## Appendix A — File Inventory Audit

### Files with Issues

| File | Issue |
|------|-------|
| `.github/prompts/cs-bash-script.prompt.md` | Duplicate of `script-bash.prompt.md` |
| `.github/prompts/cs-python-script.prompt.md` | Duplicate of `script-python.prompt.md` |
| `.github/prompts/script-bash.prompt.md` | Duplicate of `cs-bash-script.prompt.md` |
| `.github/prompts/script-python.prompt.md` | Duplicate of `cs-python-script.prompt.md` |
| `.github/copilot-code-review-instructions.md` | Content duplicates `code-review` SKILL |
| `.github/.bootstrap-ignore` | Empty file (placeholder only) |
| `.github/dependabot.yml` | Contains unused ecosystems |

### Files in Good Shape

| File | Notes |
|------|-------|
| `.github/copilot-instructions.md` | Well-structured, clear hierarchy |
| `.github/copilot-commit-message-instructions.md` | Clean and focused |
| `.github/security-baseline.md` | Comprehensive control catalog |
| `.github/DEPRECATION.md` | Clear lifecycle policy |
| `.github/PULL_REQUEST_TEMPLATE.md` | Thorough template with all needed sections |
| `.github/scripts/validate-copilot-customizations.sh` | Robust validator (~500 lines) |
| `.github/scripts/tech-ai-sync-copilot-configs.py` | Well-architected sync tool (~900 lines) |
| `AGENTS.md` | Comprehensive agent routing and decision priority |
| `.github/skills/code-review/SKILL.md` | Excellent anti-pattern catalogs |
| `.github/skills/tech-ai-sync-copilot-configs/SKILL.md` | Thorough implementation reference |

---

## Appendix B — Cross-Reference Matrix

| Instruction | Primary Prompts | Skills | Agents |
|-------------|----------------|--------|--------|
| `bash.instructions.md` | `cs-bash-script`, `script-bash` | `script-bash` | Implementer |
| `python.instructions.md` | `cs-python`, `cs-python-script`, `script-python` | `project-python`, `script-python` | Implementer |
| `terraform.instructions.md` | `cs-terraform`, `terraform-module` | `terraform-feature`, `terraform-module` | Implementer, TerraformGuardrails |
| `java.instructions.md` | `cs-java` | `project-java` | Implementer |
| `nodejs.instructions.md` | `cs-nodejs` | `project-nodejs` | Implementer |
| `github-actions.instructions.md` | `cicd-workflow`, `cs-github-action` | `cicd-workflow` | Implementer, WorkflowSupplyChain |
| `github-action-composite.instructions.md` | `cs-composite-action` | `composite-action` | Implementer |
| `json.instructions.md` | `cs-data-registry` | `data-registry` | Implementer |
| `lambda.instructions.md` | — | — | Implementer |
| `makefile.instructions.md` | — | — | Implementer |
| `markdown.instructions.md` | — | — | Implementer |
| `yaml.instructions.md` | — | — | Implementer |
| `scripts.instructions.md` (overlay) | All script prompts | All script skills | Implementer |

**Gaps identified**: `lambda.instructions.md`, `makefile.instructions.md`, `markdown.instructions.md`, and `yaml.instructions.md` have no corresponding prompts or skills. Consider whether these are needed or if the instruction alone is sufficient.

---

> **Next steps**: Review this report, prioritize the Phase 1 actions, and create issues/tasks for each item in the action plan.
