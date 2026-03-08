# AGENTS.md - customization-standards

This file is for GitHub Copilot and AI assistants working in this repository.

## Naming Policy

- Use GitHub Copilot terminology in repository-facing content.
- Do not mention internal runtime names in repository artifacts.
- Treat prompt frontmatter `name:` as the canonical command identifier.
- Canonical repository-owned prompt, agent, and instruction filenames should use the `tech-ai-` prefix when introduced or renamed.
- Canonical prompt, skill, and agent `name:` values should use the `TechAI` prefix.
- Reserve the `TechAIGlobal` prefix only for repo-only agents that encode standards for this global configuration repository.
- The canonical project-owned `AGENTS.md` file must live in repository root as `AGENTS.md`.
- Keep legacy aliases only when required for backward compatibility, and prefer canonical `tech-ai-*` assets in docs, examples, and sync selection.

## Decision Priority

1. Apply repository non-negotiables from `copilot-instructions.md`.
2. Apply explicit user requirements for the current task.
3. Apply the selected agent behavior.
4. Apply matching files under `instructions/*.instructions.md` using `applyTo`.
5. Apply selected prompt constraints from `prompts/*.prompt.md`.
6. Apply implementation details from referenced `skills/*/SKILL.md`.
7. If no agent is explicitly selected, default to `TechAIImplementer`.

## Agent Routing

### When to use each agent

- Use `TechAIPlanner` for ambiguous scope, tradeoff analysis, or multi-step design.
- Use `TechAIImplementer` for direct code or configuration changes and validation-first delivery.
- Use `TechAIReviewer` for quality gates and defect or regression findings.
- Use `TechAIScriptReviewer` for exhaustive, nit-level reviews on Python, Bash, and Terraform.
- Use `TechAIGlobalCustomizationBuilder` as the default specialist for creating or updating GitHub Copilot customization assets in this repository.
- Use `TechAIGlobalCustomizationAuditor` as the final quality gate for GitHub Copilot customization changes in this repository.
- Use `TechAICustomizationAuditor` only as a deprecated compatibility alias while older references are migrated.
- Use `TechAISyncCopilotConfigs` for cross-repository Copilot-core alignment and source or target redundancy audits.
- Use specialist agents (`TechAIWorkflowSupplyChain`, `TechAISecurityReviewer`, `TechAITerraformGuardrails`, `TechAIIAMLeastPrivilege`, `TechAIPRWriter`) only when their domain matches the task.
- The `TechAIGlobalCustomizationBuilder` and `TechAIGlobalCustomizationAuditor` agents are repo-only and must not be synced to consumer repositories.

### Anti-patterns

- Do not use `TechAIPlanner` for trivial single-file changes with clear requirements; go directly to `TechAIImplementer`.
- Do not use `TechAIImplementer` when requirements are ambiguous or scope is unclear; use `TechAIPlanner` first.
- Do not use `TechAIImplementer` as the primary authoring agent for GitHub Copilot customization assets in this repository; use `TechAIGlobalCustomizationBuilder`.
- Do not use generic `TechAIReviewer` when the change is purely Terraform, IAM, workflows, or security; use the matching specialist instead.
- Do not use generic `TechAIReviewer` when you need exhaustive per-language nit-level review; use `TechAIScriptReviewer` instead.
- Do not use `TechAICustomizationAuditor` for new work; use `TechAIGlobalCustomizationAuditor`.
- Do not use `TechAIImplementer` alone when the task is cross-repository Copilot configuration alignment; use `TechAISyncCopilotConfigs`.

### Composition and Handoffs

- For changes spanning multiple specialist domains, run each relevant specialist and aggregate findings.
- The standard chain for non-trivial work is `TechAIPlanner` -> `TechAIImplementer` -> `TechAIReviewer` or a matching specialist.
- For GitHub Copilot customization changes in this repository, use `TechAIGlobalCustomizationBuilder` first and `TechAIGlobalCustomizationAuditor` before final handoff.
- `TechAIPlanner` output is input context for `TechAIImplementer`.
- `TechAIImplementer` output is input context for `TechAIReviewer`.
- `TechAIReviewer` findings flagged as `Critical` or `Major` route back to `TechAIImplementer` for remediation.
- `TechAIGlobalCustomizationBuilder` output is input context for `TechAIGlobalCustomizationAuditor`.
- `TechAIGlobalCustomizationAuditor` findings flagged as `Critical` or `Major` route back to `TechAIGlobalCustomizationBuilder` for remediation.

## Governance References

- `security-baseline.md`: portable security controls baseline for all Copilot customization.
- `DEPRECATION.md`: lifecycle and deprecation policy for all customization assets.
- `repo-profiles.yml`: advisory profile catalog for different repository types.
- `.github/scripts/validate-copilot-customizations.sh`: validation gate for customization changes.
- `.github/templates/AGENTS.template.md`: slimmer onboarding template that keeps asset paths in the inventory section only.
- `.github/templates/copilot-quickstart.md`: quick start guide for new teams.

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
- For GitHub Actions pinning, each full SHA must include an adjacent comment with release or tag reference.

## Backlog Triggers

- Add `instructions/docker.instructions.md` when the first Dockerfile is introduced in this repository.

## Repository Defaults

- Primary focus: reusable, repository-agnostic Copilot customization standards.
- Profile hint: `minimal`
- AGENTS.md is the external bridge for assistant behavior and naming; keep runtime references abstract.
- Resolve stack from target files and explicit prompt inputs; the agent role remains behavioral, not language-specific.
- Prioritize these paths:
  - `.github/instructions`
  - `.github/prompts`
  - `.github/skills`
  - `.github/agents`
  - `.github/scripts`

### Default instruction routing

- `**/*.py` -> `python.instructions.md`
- `**/*.sh` -> `bash.instructions.md`
- `**/*.tf` -> `terraform.instructions.md`
- `**/*.java` -> `java.instructions.md`
- `**/*.js,**/*.cjs,**/*.mjs,**/*.ts,**/*.tsx` -> `nodejs.instructions.md`
- `**/*lambda*.tf,**/*lambda*.py,**/*lambda*.js,**/*lambda*.ts` -> `lambda.instructions.md`
- `**/*.yml,**/*.yaml` -> `yaml.instructions.md`
- `**/*.md` -> `markdown.instructions.md`
- `**/Makefile,**/*.mk` -> `makefile.instructions.md`
- `**/workflows/**` -> `github-actions.instructions.md`
- `**/actions/**/action.y*ml` -> `github-action-composite.instructions.md`
- `**/authorizations/**/*.json,**/organization/**/*.json,**/src/**/*.json,**/data/**/*.json` -> `json.instructions.md`
- `**/*.sh,**/scripts/**/*.py,**/scripts/**/*.sh` -> `scripts.instructions.md` as an overlay

### Preferred prompts

- `TechAICodeReview`: exhaustive, nit-level code review.
- `TechAIGitHubAction`: GitHub Actions workflow authoring.
- `TechAISyncCopilotConfigs`: cross-repository alignment and redundancy analysis.
- `TechAIPRDescription`: pull request body generation.
- `TechAIAddUnitTests`: test authoring and improvement.
- `TechAITerraform`: Terraform feature or module authoring.

### Preferred skills

- `TechAICodeReview`: strict review workflow and anti-pattern catalog.
- `TechAICICDWorkflow`: CI or CD workflow design patterns.
- `TechAISyncCopilotConfigs`: deterministic sync planning and reporting.
- `TechAIPRWriting`: PR writing conventions aligned to the repository template.
- `TechAICloudPolicy`: reusable cloud policy authoring patterns.
- `TechAITerraformModule`: reusable Terraform module design.

### Required validations before PR

- `bash .github/scripts/validate-copilot-customizations.sh --scope root --mode strict`
- `bash -n` and `shellcheck -s bash` for changed Bash scripts when available.
- `python -m compileall <changed_python_paths>` and relevant `pytest` checks for Python changes.
- `terraform fmt` and `terraform validate` for Terraform changes.

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
- `.github/prompts/tech-ai-add-unit-tests.prompt.md`
- `.github/prompts/tech-ai-bash-script.prompt.md`
- `.github/prompts/tech-ai-cicd-workflow.prompt.md`
- `.github/prompts/tech-ai-cloud-policy.prompt.md`
- `.github/prompts/tech-ai-code-review.prompt.md`
- `.github/prompts/tech-ai-data-registry.prompt.md`
- `.github/prompts/tech-ai-github-action.prompt.md`
- `.github/prompts/tech-ai-github-composite-action.prompt.md`
- `.github/prompts/tech-ai-github-pr-description.prompt.md`
- `.github/prompts/tech-ai-java.prompt.md`
- `.github/prompts/tech-ai-nodejs.prompt.md`
- `.github/prompts/tech-ai-python-script.prompt.md`
- `.github/prompts/tech-ai-python.prompt.md`
- `.github/prompts/tech-ai-sync-copilot-configs.prompt.md`
- `.github/prompts/tech-ai-terraform-module.prompt.md`
- `.github/prompts/tech-ai-terraform.prompt.md`

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
- `.github/agents/tech-ai-global-customization-auditor.agent.md`
- `.github/agents/tech-ai-global-customization-builder.agent.md`
- `.github/agents/tech-ai-iam-least-privilege.agent.md`
- `.github/agents/tech-ai-implementer.agent.md`
- `.github/agents/tech-ai-planner.agent.md`
- `.github/agents/tech-ai-reviewer.agent.md`
- `.github/agents/tech-ai-script-reviewer.agent.md`
- `.github/agents/tech-ai-security-reviewer.agent.md`
- `.github/agents/tech-ai-sync-copilot-configs.agent.md`
- `.github/agents/tech-ai-terraform-guardrails.agent.md`
