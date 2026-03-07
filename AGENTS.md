# AGENTS.md - customization-standards

This file is for GitHub Copilot and AI assistants working in this repository.

## Naming Policy

- Use GitHub Copilot terminology in repository-facing content.
- Do not mention internal runtime names in repository artifacts.
- Treat prompt frontmatter `name:` as the canonical command identifier.
- Canonical repository-owned prompt, agent, and instruction filenames should use the `tech-ai-` prefix when introduced or renamed.
- Canonical prompt, skill, and agent `name:` values should use the `TechAI` prefix.
- The canonical project-owned `AGENTS.md` file must live in repository root as `AGENTS.md`.
- Keep legacy aliases only when required for backward compatibility, and prefer canonical `tech-ai-*` assets in docs, examples, and sync selection.

## Decision Priority

1. Apply repository non-negotiables from `copilot-instructions.md`.
2. Apply explicit user requirements for the current task.
3. Apply the selected agent behavior (agent-first routing).
4. Apply matching files under `instructions/*.instructions.md` using `applyTo`.
5. Apply selected prompt constraints from `prompts/*.prompt.md`.
6. Apply implementation details from referenced `skills/*/SKILL.md`.
7. If no agent is explicitly selected, default to `TechAIImplementer`.

## Stack Resolution Rules

- The agent role is behavioral, not language-specific.
- Resolve stack from target files and explicit prompt inputs.
- Primary `applyTo` rules (one instruction per file type):
  - `**/*.py` -> `instructions/python.instructions.md`
  - `**/*.sh` -> `instructions/bash.instructions.md`
  - `**/*.tf` -> `instructions/terraform.instructions.md`
  - `**/*.java` -> `instructions/java.instructions.md`
  - `**/*.js,**/*.cjs,**/*.mjs,**/*.ts,**/*.tsx` -> `instructions/nodejs.instructions.md`
  - `**/*lambda*.tf,**/*lambda*.py,**/*lambda*.js,**/*lambda*.ts` -> `instructions/lambda.instructions.md`
  - `**/*.yml,**/*.yaml` -> `instructions/yaml.instructions.md`
  - `**/*.md` -> `instructions/markdown.instructions.md`
  - `**/Makefile,**/*.mk` -> `instructions/makefile.instructions.md`
  - `**/workflows/**` -> `instructions/github-actions.instructions.md`
  - `**/actions/**/action.y*ml` -> `instructions/github-action-composite.instructions.md`
  - `**/authorizations/**/*.json,**/organization/**/*.json,**/src/**/*.json,**/data/**/*.json` -> `instructions/json.instructions.md`
- Overlay rules (additive - apply alongside the primary instruction above):
  - `**/*.sh,**/scripts/**/*.py,**/scripts/**/*.sh` -> `instructions/scripts.instructions.md`
- If a change spans multiple stacks, apply all relevant instruction files.
- Overlay instructions never conflict with primary instructions - they add cross-cutting standards.

## Agent Routing

### When to use each agent

- Use `TechAIPlanner` for ambiguous scope, tradeoff analysis, or multi-step design.
- Use `TechAIImplementer` for direct code/config changes and validations.
- Use `TechAIReviewer` for quality gates and defect/regression findings.
- Use `TechAIScriptReviewer` for exhaustive, nit-level code reviews on Python, Bash, and Terraform with per-language anti-pattern catalogs.
- Use `TechAICustomizationAuditor` to validate and normalize Copilot customization assets for this repository.
- Use `TechAISyncCopilotConfigs` to analyze a local consumer repository and conservatively align the minimum Copilot customization assets from this standards repository.
- Use specialist agents (`TechAIWorkflowSupplyChain`, `TechAISecurityReviewer`, `TechAITerraformGuardrails`, `TechAIIAMLeastPrivilege`, `TechAIPRWriter`) only when their domain matches the task.

### When NOT to use (anti-patterns)

- Do not use `TechAIPlanner` for trivial single-file changes with clear requirements - go directly to `TechAIImplementer`.
- Do not use `TechAIImplementer` when requirements are ambiguous or scope is unclear - use `TechAIPlanner` first.
- Do not use generic `TechAIReviewer` when the change is purely Terraform, IAM, workflows, or security - use the matching specialist instead.
- Do not use generic `TechAIReviewer` when you need exhaustive per-language nit-level review - use `TechAIScriptReviewer` instead.
- Do not use `TechAIImplementer` alone when the task is cross-repository Copilot configuration alignment - use `TechAISyncCopilotConfigs`.

### Agent composition

- For changes spanning multiple specialist domains (for example Terraform + IAM), run each relevant specialist and aggregate findings.
- The standard chain for non-trivial work is: `TechAIPlanner` -> `TechAIImplementer` -> `TechAIReviewer` (or specialist reviewer).
- For Copilot customization changes (for example `.github/prompts`, `.github/skills`, `.github/agents`, `.github/scripts`), run `TechAICustomizationAuditor` before final handoff.

### Handoff protocol

- `TechAIPlanner` output (implementation plan) is input context for `TechAIImplementer`.
- `TechAIImplementer` output (list of changed files + validation results) is input context for `TechAIReviewer`.
- `TechAIReviewer` findings flagged as `Critical` or `Major` route back to `TechAIImplementer` for remediation.

## Available Skills

- `TechAICICDWorkflow` (`skills/tech-ai-cicd-workflow/SKILL.md`): GitHub Actions workflow design and CI/CD patterns.
- `TechAICloudPolicy` (`skills/tech-ai-cloud-policy/SKILL.md`): AWS SCP, Azure Policy, and GCP Org Policy governance.
- `TechAICodeReview` (`skills/tech-ai-code-review/SKILL.md`): Exhaustive per-language anti-pattern catalogs for strict code reviews.
- `TechAICompositeAction` (`skills/tech-ai-composite-action/SKILL.md`): GitHub composite action implementation patterns.
- `TechAIDataRegistry` (`skills/tech-ai-data-registry/SKILL.md`): Data registry schema and governance automation patterns.
- `TechAIPRWriting` (`skills/tech-ai-pr-writing/SKILL.md`): PR title/body generation from template and diff.
- `TechAIProjectJava` (`skills/tech-ai-project-java/SKILL.md`): Java project code with DDD and deterministic tests.
- `TechAIProjectNodejs` (`skills/tech-ai-project-nodejs/SKILL.md`): Node.js project code with module boundaries and tests.
- `TechAIProjectPython` (`skills/tech-ai-project-python/SKILL.md`): Python project code with DDD, pytest, and type hints.
- `TechAIScriptBash` (`skills/tech-ai-script-bash/SKILL.md`): Bash utility scripts with strict mode and shellcheck.
- `TechAIScriptPython` (`skills/tech-ai-script-python/SKILL.md`): Python utility scripts with argparse and tests.
- `TechAISyncCopilotConfigs` (`skills/tech-ai-sync-copilot-configs/SKILL.md`): Conservative local repository alignment for minimal Copilot customization assets with reporting.
- `TechAITerraformFeature` (`skills/tech-ai-terraform-feature/SKILL.md`): Terraform feature implementation patterns.
- `TechAITerraformModule` (`skills/tech-ai-terraform-module/SKILL.md`): Terraform reusable module design.

## Available Prompts

- `TechAIAddPlatform` (`prompts/tech-ai-add-platform.prompt.md`): Add a new supported platform/profile pattern in a generic way.
- `TechAIAddReportScript` (`prompts/tech-ai-add-report-script.prompt.md`): Add a reusable reporting/analysis automation script.
- `TechAICICDWorkflow` (`prompts/tech-ai-cicd-workflow.prompt.md`): Create or modify GitHub Actions workflows.
- `TechAIAddUnitTests` (`prompts/tech-ai-add-unit-tests.prompt.md`): Add or improve unit tests.
- `TechAICloudPolicy` (`prompts/tech-ai-cloud-policy.prompt.md`): Create cloud governance policies.
- `TechAICodeReview` (`prompts/tech-ai-code-review.prompt.md`): Perform exhaustive, nit-level code reviews.
- `TechAIDataRegistry` (`prompts/tech-ai-data-registry.prompt.md`): Create or update data registry assets.
- `TechAIJava` (`prompts/tech-ai-java.prompt.md`): Generate Java project code.
- `TechAINodejs` (`prompts/tech-ai-nodejs.prompt.md`): Generate Node.js project code.
- `TechAIPython` (`prompts/tech-ai-python.prompt.md`): Generate Python project code.
- `TechAITerraform` (`prompts/tech-ai-terraform.prompt.md`): Create Terraform modules and features.
- `TechAIGitHubAction` (`prompts/tech-ai-github-action.prompt.md`): Create GitHub Actions workflows.
- `TechAICompositeAction` (`prompts/tech-ai-github-composite-action.prompt.md`): Create GitHub composite actions.
- `TechAIPRDescription` (`prompts/tech-ai-github-pr-description.prompt.md`): Generate PR descriptions.
- `TechAIBashScript` (`prompts/tech-ai-bash-script.prompt.md`): Create or modify Bash scripts with the canonical low-duplication prompt.
- `TechAIPythonScript` (`prompts/tech-ai-python-script.prompt.md`): Create or modify Python utility scripts with the canonical low-duplication prompt.
- `TechAISyncCopilotConfigs` (`prompts/tech-ai-sync-copilot-configs.prompt.md`): Analyze and conservatively align a local repository with the minimum Copilot customization assets from this standards repo.
- `TechAITerraformModule` (`prompts/tech-ai-terraform-module.prompt.md`): Create or modify Terraform modules.

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

- Primary focus: reusable, repository-agnostic Copilot customization standards.
- Profile hint: `minimal`
- AGENTS.md is the external bridge for assistant behavior and naming; keep runtime references abstract.
- Prioritize these paths:
  - `.github/instructions`
  - `.github/prompts`
  - `.github/skills`
  - `.github/agents`
  - `.github/scripts`

### Default instruction routing

- `instructions/markdown.instructions.md`
- `instructions/yaml.instructions.md`
- `instructions/json.instructions.md`
- `instructions/github-actions.instructions.md`
- `instructions/github-action-composite.instructions.md`

### Preferred prompts

- `prompts/tech-ai-code-review.prompt.md`
- `prompts/tech-ai-github-action.prompt.md`
- `prompts/tech-ai-sync-copilot-configs.prompt.md`
- `prompts/tech-ai-github-pr-description.prompt.md`
- `prompts/tech-ai-add-unit-tests.prompt.md`
- `prompts/tech-ai-terraform.prompt.md`

### Preferred skills

- `skills/tech-ai-code-review/SKILL.md`
- `skills/tech-ai-cicd-workflow/SKILL.md`
- `skills/tech-ai-sync-copilot-configs/SKILL.md`
- `skills/tech-ai-pr-writing/SKILL.md`
- `skills/tech-ai-cloud-policy/SKILL.md`
- `skills/tech-ai-terraform-module/SKILL.md`

### Required validations before PR

- `bash .github/scripts/validate-copilot-customizations.sh --scope root --mode strict`
- `bash -n` and `shellcheck -s bash` for changed Bash scripts (when available)
- `python -m compileall <changed_python_paths>` and relevant `pytest` checks for Python changes
- `terraform fmt` and `terraform validate` for Terraform changes

## Repository Inventory (Auto-generated)

### Instructions

- `.github/instructions/bash.instructions.md`
- `.github/instructions/github-action-composite.instructions.md`
- `.github/instructions/github-actions.instructions.md`
- `.github/instructions/java.instructions.md`
- `.github/instructions/json.instructions.md`
- `.github/instructions/lambda.instructions.md`
- `.github/instructions/makefile.instructions.md`
- `.github/instructions/markdown.instructions.md`
- `.github/instructions/nodejs.instructions.md`
- `.github/instructions/python.instructions.md`
- `.github/instructions/scripts.instructions.md`
- `.github/instructions/terraform.instructions.md`
- `.github/instructions/yaml.instructions.md`

### Prompts

- `.github/prompts/tech-ai-add-platform.prompt.md`
- `.github/prompts/tech-ai-add-report-script.prompt.md`
- `.github/prompts/tech-ai-cicd-workflow.prompt.md`
- `.github/prompts/tech-ai-github-action.prompt.md`
- `.github/prompts/tech-ai-github-composite-action.prompt.md`
- `.github/prompts/tech-ai-github-pr-description.prompt.md`
- `.github/prompts/tech-ai-add-unit-tests.prompt.md`
- `.github/prompts/tech-ai-bash-script.prompt.md`
- `.github/prompts/tech-ai-cloud-policy.prompt.md`
- `.github/prompts/tech-ai-code-review.prompt.md`
- `.github/prompts/tech-ai-data-registry.prompt.md`
- `.github/prompts/tech-ai-java.prompt.md`
- `.github/prompts/tech-ai-nodejs.prompt.md`
- `.github/prompts/tech-ai-python-script.prompt.md`
- `.github/prompts/tech-ai-python.prompt.md`
- `.github/prompts/tech-ai-sync-copilot-configs.prompt.md`
- `.github/prompts/tech-ai-terraform.prompt.md`
- `.github/prompts/tech-ai-terraform-module.prompt.md`

### Skills

- `.github/skills/tech-ai-cicd-workflow/SKILL.md`
- `.github/skills/tech-ai-cloud-policy/SKILL.md`
- `.github/skills/tech-ai-code-review/SKILL.md`
- `.github/skills/tech-ai-composite-action/SKILL.md`
- `.github/skills/tech-ai-data-registry/SKILL.md`
- `.github/skills/tech-ai-pr-writing/SKILL.md`
- `.github/skills/tech-ai-project-java/SKILL.md`
- `.github/skills/tech-ai-project-nodejs/SKILL.md`
- `.github/skills/tech-ai-project-python/SKILL.md`
- `.github/skills/tech-ai-script-bash/SKILL.md`
- `.github/skills/tech-ai-script-python/SKILL.md`
- `.github/skills/tech-ai-sync-copilot-configs/SKILL.md`
- `.github/skills/tech-ai-terraform-feature/SKILL.md`
- `.github/skills/tech-ai-terraform-module/SKILL.md`

### Agents

- `.github/agents/tech-ai-customization-auditor.agent.md`
- `.github/agents/tech-ai-github-pr-writer.agent.md`
- `.github/agents/tech-ai-github-workflow-supply-chain.agent.md`
- `.github/agents/tech-ai-iam-least-privilege.agent.md`
- `.github/agents/tech-ai-implementer.agent.md`
- `.github/agents/tech-ai-planner.agent.md`
- `.github/agents/tech-ai-reviewer.agent.md`
- `.github/agents/tech-ai-security-reviewer.agent.md`
- `.github/agents/tech-ai-sync-copilot-configs.agent.md`
- `.github/agents/tech-ai-script-reviewer.agent.md`
- `.github/agents/tech-ai-terraform-guardrails.agent.md`
