# AGENTS.md - eng-finops

This file is for GitHub Copilot and AI assistants working in this repository.

## Naming Policy

- Use GitHub Copilot terminology in repository-facing content.
- Do not mention internal runtime names in repository artifacts.
- Treat prompt frontmatter `name:` as the canonical command identifier.

## Decision Priority

1. Apply repository non-negotiables from `copilot-instructions.md`.
2. Apply explicit user requirements for the current task.
3. Apply the selected agent behavior (agent-first routing).
4. Apply matching files under `instructions/*.instructions.md` using `applyTo`.
5. Apply selected prompt constraints from `prompts/*.prompt.md`.
6. Apply implementation details from referenced `skills/*/SKILL.md`.
7. If no agent is explicitly selected, default to `Implementer`.

## Stack Resolution Rules

- The agent role is behavioral, not language-specific.
- Resolve stack from target files and explicit prompt inputs.
- Primary `applyTo` rules (one instruction per file type):
  - `**/*.py` -> `instructions/python.instructions.md`
  - `**/*.sh` -> `instructions/bash.instructions.md`
  - `**/*.tf` -> `instructions/terraform.instructions.md`
  - `**/*.yml,**/*.yaml` -> `instructions/yaml.instructions.md`
  - `**/*.md` -> `instructions/markdown.instructions.md`
  - `**/Makefile,**/*.mk` -> `instructions/makefile.instructions.md`
  - `**/workflows/**` -> `instructions/github-actions.instructions.md`
  - `**/actions/**/action.y*ml` -> `instructions/github-action-composite.instructions.md`
  - `**/authorizations/**/*.json,**/organization/**/*.json,**/src/**/*.json,**/data/**/*.json` -> `instructions/json.instructions.md`
- Overlay rules (additive — apply alongside the primary instruction above):
  - `**/*.sh,**/scripts/**/*.py,**/scripts/**/*.sh` -> `instructions/scripts.instructions.md`
- If a change spans multiple stacks, apply all relevant instruction files.
- Overlay instructions never conflict with primary instructions — they add cross-cutting standards.

## Agent Routing

### When to use each agent

- Use `Planner` for ambiguous scope, tradeoff analysis, or multi-step design.
- Use `Implementer` for direct code/config changes and validations.
- Use `Reviewer` for quality gates and defect/regression findings.
- Use `TechAIScriptReviewer` for exhaustive, nit-level code reviews on Python, Bash, and Terraform with per-language anti-pattern catalogs.
- Use specialist agents (`WorkflowSupplyChain`, `SecurityReviewer`, `TerraformGuardrails`, `IAMLeastPrivilege`, `PRWriter`) only when their domain matches the task.

### When NOT to use (anti-patterns)

- Do not use `Planner` for trivial single-file changes with clear requirements — go directly to `Implementer`.
- Do not use `Implementer` when requirements are ambiguous or scope is unclear — use `Planner` first.
- Do not use generic `Reviewer` when the change is purely Terraform, IAM, workflows, or security — use the matching specialist instead.
- Do not use generic `Reviewer` when you need exhaustive per-language nit-level review — use `TechAIScriptReviewer` instead.

### Agent composition

- For changes spanning multiple specialist domains (e.g., Terraform + IAM), run each relevant specialist and aggregate findings.
- The standard chain for non-trivial work is: `Planner` → `Implementer` → `Reviewer` (or specialist reviewer).

### Handoff protocol

- Planner output (implementation plan) is input context for Implementer.
- Implementer output (list of changed files + validation results) is input context for Reviewer.
- Reviewer findings flagged as `Critical` or `Major` route back to Implementer for remediation.

## Available Skills

- `cicd-workflow` (`skills/cicd-workflow/SKILL.md`): GitHub Actions workflow design and CI/CD patterns.
- `cloud-policy` (`skills/cloud-policy/SKILL.md`): AWS SCP, Azure Policy, GCP Org Policy governance.
- `code-review` (`skills/code-review/SKILL.md`): Exhaustive per-language anti-pattern catalogs for strict code reviews.
- `pr-writing` (`skills/pr-writing/SKILL.md`): PR title/body generation from template and diff.
- `project-python` (`skills/project-python/SKILL.md`): Python project code with DDD, pytest, type hints.
- `script-bash` (`skills/script-bash/SKILL.md`): Bash utility scripts with strict mode and shellcheck.
- `script-python` (`skills/script-python/SKILL.md`): Python utility scripts with argparse and tests.
- `terraform-feature` (`skills/terraform-feature/SKILL.md`): Terraform feature implementation patterns.
- `terraform-module` (`skills/terraform-module/SKILL.md`): Terraform reusable module design.

## Available Prompts

- `cs-add-unit-tests` (`prompts/cs-add-unit-tests.prompt.md`): Add or improve unit tests.
- `cs-code-review` (`prompts/cs-code-review.prompt.md`): Perform exhaustive, nit-level code reviews.
- `cs-bash-script` (`prompts/cs-bash-script.prompt.md`): Create or modify Bash scripts.
- `cs-cloud-policy` (`prompts/cs-cloud-policy.prompt.md`): Create cloud governance policies.
- `cs-python-script` (`prompts/cs-python-script.prompt.md`): Create Python utility scripts.
- `cs-python` (`prompts/cs-python.prompt.md`): Generate Python project code.
- `cs-terraform` (`prompts/cs-terraform.prompt.md`): Create Terraform modules and features.
- `cs-github-action` (`prompts/github-action.prompt.md`): Create GitHub Actions workflows.
- `cs-pr-description` (`prompts/github-pr-description.prompt.md`): Generate PR descriptions.

## Governance References

- `security-baseline.md`: Portable security controls baseline for all Copilot customization.
- `DEPRECATION.md`: Lifecycle and deprecation policy for all customization assets.
- `repo-profiles.yml`: Advisory profile catalog for different repository types.
- `.github/scripts/validate-copilot-customizations.sh`: Validation gate for customization changes.
- `templates/AGENTS.template.md`: Template for onboarding new repositories.
- `templates/copilot-quickstart.md`: Quick start guide for new teams.

## Template Placeholders

- `CODEOWNERS` may keep `@your-org/platform-governance-team` only in template repositories.
- Consumer repositories must replace placeholder owners before enabling review enforcement.
- The validator should warn when the placeholder owner is still present.

## Prohibitions

- Never hardcode secrets, tokens, or credentials.
- Never modify `README.md` files unless explicitly requested by the user.
- Never introduce new patterns when existing repository conventions exist.
- Keep all repository artifacts in English (user chat may be in other languages).
- Never run destructive commands unless explicitly requested.
- Never skip validation after making changes.

## PR and Workflow Conventions

- PR content must follow `PULL_REQUEST_TEMPLATE.md` in exact section order.
- For GitHub Actions pinning, each full SHA must include an adjacent comment with release/tag reference.

## Backlog Triggers

- Add `instructions/docker.instructions.md` when the first Dockerfile is introduced in this repository.

## Repository Defaults

- Primary focus: FinOps repository for Azure and AWS cost extraction, data normalization, and anomaly detection automation.
- Profile hint: `backend-python`
- AGENTS.md is the external bridge for assistant behavior and naming; keep runtime references abstract.
- Prioritize these paths:
  - `aws`
  - `azure`

### Default instruction routing

- `instructions/python.instructions.md`
- `instructions/scripts.instructions.md`
- `instructions/terraform.instructions.md`
- `instructions/json.instructions.md`
- `instructions/yaml.instructions.md`

### Preferred prompts

- `prompts/add-report-script.prompt.md`
- `prompts/add-platform.prompt.md`
- `prompts/cs-python.prompt.md`
- `prompts/cs-python-script.prompt.md`
- `prompts/github-pr-description.prompt.md`

### Preferred skills

- `skills/project-python/SKILL.md`
- `skills/script-python/SKILL.md`
- `skills/script-bash/SKILL.md`
- `skills/terraform-feature/SKILL.md`
- `skills/pr-writing/SKILL.md`

### Required validations before PR

- `python -m pytest (if tests exist for changed logic)`
- `python -m compileall <changed_python_paths>`
- `terraform fmt/validate for terraform changes`
- `sample run for cost/anomaly scripts when feasible`

## Repository Inventory (Auto-generated)

### Instructions

- `.github/instructions/bash.instructions.md`
- `.github/instructions/github-action-composite.instructions.md`
- `.github/instructions/github-actions.instructions.md`
- `.github/instructions/json.instructions.md`
- `.github/instructions/makefile.instructions.md`
- `.github/instructions/markdown.instructions.md`
- `.github/instructions/python.instructions.md`
- `.github/instructions/scripts.instructions.md`
- `.github/instructions/terraform.instructions.md`
- `.github/instructions/yaml.instructions.md`

### Prompts

- `.github/prompts/add-platform.prompt.md`
- `.github/prompts/add-report-script.prompt.md`
- `.github/prompts/cicd-workflow.prompt.md`
- `.github/prompts/cs-add-unit-tests.prompt.md`
- `.github/prompts/cs-bash-script.prompt.md`
- `.github/prompts/cs-cloud-policy.prompt.md`
- `.github/prompts/cs-code-review.prompt.md`
- `.github/prompts/cs-python-script.prompt.md`
- `.github/prompts/cs-python.prompt.md`
- `.github/prompts/cs-terraform.prompt.md`
- `.github/prompts/github-action.prompt.md`
- `.github/prompts/github-pr-description.prompt.md`
- `.github/prompts/script-bash.prompt.md`
- `.github/prompts/script-python.prompt.md`
- `.github/prompts/terraform-module.prompt.md`

### Skills

- `.github/skills/cicd-workflow/SKILL.md`
- `.github/skills/cloud-policy/SKILL.md`
- `.github/skills/code-review/SKILL.md`
- `.github/skills/pr-writing/SKILL.md`
- `.github/skills/project-python/SKILL.md`
- `.github/skills/script-bash/SKILL.md`
- `.github/skills/script-python/SKILL.md`
- `.github/skills/terraform-feature/SKILL.md`
- `.github/skills/terraform-module/SKILL.md`

### Agents

- `.github/agents/github-pr-writer.agent.md`
- `.github/agents/github-workflow-supply-chain.agent.md`
- `.github/agents/iam-least-privilege.agent.md`
- `.github/agents/implementer.agent.md`
- `.github/agents/planner.agent.md`
- `.github/agents/reviewer.agent.md`
- `.github/agents/security-reviewer.agent.md`
- `.github/agents/tech-ai-script-reviewer.agent.md`
- `.github/agents/terraform-guardrails.agent.md`
