# AGENTS.md - customization-standards

This file is for GitHub Copilot and AI assistants working in this repository.

## Naming Policy

- Use GitHub Copilot terminology in repository-facing content.
- Do not mention internal runtime names in repository artifacts.
- Treat prompt frontmatter `name:` as the canonical command identifier.
- Canonical repository-owned prompt, agent, and instruction filenames should use the `tech-ai-` prefix when introduced or renamed.
- Canonical prompt, skill, and agent `name:` values should use the `TechAI` prefix.
- Repository-owned prompt, skill, and agent filenames in consumer repositories should use the `internal-` prefix.
- Repository-owned prompt, skill, and agent `name:` values in consumer repositories should also use the `internal-` prefix.
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
7. If no agent is explicitly selected, use the default agent with matching language instructions.

## Agent Routing

### When to use each agent

#### Specialist Reviewers (per-language, nit-level review)
- Use `TechAIBashReviewer` for exhaustive, nit-level Bash script reviews.
- Use `TechAIJavaReviewer` for exhaustive, nit-level Java code reviews.
- Use `TechAINodejsReviewer` for exhaustive, nit-level Node.js code reviews.
- Use `TechAIPythonReviewer` for exhaustive, nit-level Python code reviews.
- Use `TechAITerraformReviewer` for exhaustive, nit-level Terraform code reviews.
- Use `TechAISecurityReviewer` for security-focused review across all languages.

#### Planning and Architecture
- Use `TechAIPlanner` for ambiguous scope, tradeoff analysis, or multi-step design.
- Use `TechAIPairArchitectAnalysis` prompt with the `TechAIPairArchitect` skill for deep change-impact analysis with health scoring, blind-spot detection, and structured Markdown reports.

#### Editing and Delivery
- Use `TechAIPREditor` for pull request body generation from diffs.

#### Repository Configuration (source-only, not synced to consumers)
- Use `TechAIStandardsRepoConfigBuilder` for creating or updating GitHub Copilot customization assets in this repository.
- Use `TechAIStandardsRepoConfigAuditor` as the final quality gate for GitHub Copilot customization changes in this repository.
- Use `TechAISyncGlobalCopilotConfigsIntoRepo` for cross-repository Copilot-core alignment and source or target redundancy audits.
- Use `TechAIRepoCopilotExtender` when a consumer repository needs repo-owned `internal-*` prompts, skills, agents, or `AGENTS.md` wiring that should remain internal instead of entering the shared baseline.

### Anti-patterns

- Do not use `TechAIPlanner` for trivial single-file changes with clear requirements; work directly.
- Do not use a specialist reviewer outside its language domain; pick the matching one.
- Do not use `TechAIStandardsRepoConfigBuilder` in consumer repos; it is source-only for this repository.
- Do not use `TechAISyncGlobalCopilotConfigsIntoRepo` alone when the task is to author new repository-owned `internal-*` assets; use `TechAIRepoCopilotExtender` after baseline alignment.
- Do not use `TechAIRepoCopilotExtender` to add new shared `tech-ai-*` assets in this standards repository; use `TechAIStandardsRepoConfigBuilder`.

### Composition and Handoffs

- For changes spanning multiple specialist domains, run each relevant specialist reviewer and aggregate findings.
- For GitHub Copilot customization changes in this repository, use `TechAIStandardsRepoConfigBuilder` first and `TechAIStandardsRepoConfigAuditor` before final handoff.
- For consumer-repository Copilot customization work, use `TechAISyncGlobalCopilotConfigsIntoRepo` first if the target baseline is unknown, then use `TechAIRepoCopilotExtender` for repo-owned `internal-*` assets.
- `TechAIStandardsRepoConfigBuilder` output is input context for `TechAIStandardsRepoConfigAuditor`.
- `TechAIStandardsRepoConfigAuditor` findings flagged as `Critical` or `Major` route back to `TechAIStandardsRepoConfigBuilder` for remediation.

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
- `**/Dockerfile,**/Dockerfile.*,**/.dockerignore,**/docker-compose*.yml,**/compose*.yml` -> `docker.instructions.md`
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

### Preferred prompts

- `TechAICodeReview`: exhaustive, nit-level code review.
- `TechAIGitHubAction`: GitHub Actions workflow authoring.
- `TechAIRepoCopilotExtender`: consumer-repository `internal-*` customization authoring.
- `TechAISyncGlobalCopilotConfigsIntoRepo`: cross-repository alignment and redundancy analysis.
- `TechAIPREditor`: pull request body generation.
- `TechAIAddUnitTests`: test authoring and improvement.
- `TechAITerraform`: Terraform feature or module authoring.
- `TechAIPairArchitectAnalysis`: deep change-impact analysis with health score, risk matrix, and devil's advocate mode.

### Preferred skills

#### Domain-Specific Skills
- `TechAICodeReview`: strict review workflow and anti-pattern catalog.
- `TechAICICDWorkflow`: CI or CD workflow design patterns.
- `TechAIRepoCopilotExtender`: consumer-repository Copilot customization workflow.
- `TechAISyncGlobalCopilotConfigsIntoRepo`: deterministic sync planning and reporting.
- `TechAIPREditor`: PR body templates and diff-to-body mapping patterns.
- `TechAICloudPolicy`: reusable cloud policy authoring patterns.
- `TechAITerraformModule`: reusable Terraform module design.
- `TechAIChangeImpactAnalysis`: change-set-level impact, health scoring, risk matrix, and blind-spot detection.

#### Workflow Skills (obra/superpowers)
- `TechAIBrainstorming`: structured creative exploration before implementation.
- `TechAIDispatchingParallelAgents`: coordinating parallel sub-agent work.
- `TechAIExecutingPlans`: structured plan execution with checkpoints.
- `TechAIFinishingDevBranch`: pre-merge checklist and branch cleanup.
- `TechAIGitWorktrees`: efficient multi-branch work with git worktrees.
- `TechAIReceivingCodeReview`: processing and addressing review feedback.
- `TechAIRequestingCodeReview`: preparing changes for effective review.
- `TechAISubagentDrivenDev`: delegating implementation to focused sub-agents.
- `TechAISystematicDebugging`: root-cause-first debugging with 4-phase process.
- `TechAITestDrivenDev`: TDD red-green-refactor workflow.
- `TechAIUsingSuperpowers`: agent capability awareness and best practices.
- `TechAIVerification`: evidence-based verification before claiming completion.
- `TechAIWritingPlans`: structured plan authoring.
- `TechAIWritingSkills`: skill authoring and improvement.
- `TechAISkillCreator`: meta-skill for creating, testing, and improving skills (source-only).

### Required validations before PR

- `bash .github/scripts/validate-copilot-customizations.sh --scope root --mode strict`
- `bash -n` and `shellcheck -s bash` for changed Bash scripts when available.
- `python -m compileall <changed_python_paths>` and relevant `pytest` checks for Python changes.
- `terraform fmt` and `terraform validate` for Terraform changes.

## Repository Inventory (Auto-generated)

### Instructions

- `.github/instructions/bash.instructions.md`
- `.github/instructions/docker.instructions.md`
- `.github/instructions/github-action-composite.instructions.md`
- `.github/instructions/github-actions.instructions.md`
- `.github/instructions/java.instructions.md`
- `.github/instructions/json.instructions.md`
- `.github/instructions/lambda.instructions.md`
- `.github/instructions/makefile.instructions.md`
- `.github/instructions/markdown.instructions.md`
- `.github/instructions/nodejs.instructions.md`
- `.github/instructions/python.instructions.md`
- `.github/instructions/terraform-aws.instructions.md`
- `.github/instructions/terraform-azure.instructions.md`
- `.github/instructions/terraform-gcp.instructions.md`
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
- `.github/prompts/tech-ai-docker.prompt.md`
- `.github/prompts/tech-ai-github-action.prompt.md`
- `.github/prompts/tech-ai-github-composite-action.prompt.md`
- `.github/prompts/tech-ai-java.prompt.md`
- `.github/prompts/tech-ai-nodejs.prompt.md`
- `.github/prompts/tech-ai-pair-architect-analysis.prompt.md`
- `.github/prompts/tech-ai-pr-editor.prompt.md`
- `.github/prompts/tech-ai-python-script.prompt.md`
- `.github/prompts/tech-ai-python.prompt.md`
- `.github/prompts/tech-ai-repo-copilot-extender.prompt.md`
- `.github/prompts/tech-ai-sync-global-copilot-configs-into-repo.prompt.md`
- `.github/prompts/tech-ai-terraform-module.prompt.md`
- `.github/prompts/tech-ai-terraform.prompt.md`

### Skills

- `.github/skills/tech-ai-brainstorming/SKILL.md`
- `.github/skills/tech-ai-cicd-workflow/SKILL.md`
- `.github/skills/tech-ai-cloud-policy/SKILL.md`
- `.github/skills/tech-ai-code-review/SKILL.md`
- `.github/skills/tech-ai-composite-action/SKILL.md`
- `.github/skills/tech-ai-data-registry/SKILL.md`
- `.github/skills/tech-ai-dispatching-parallel-agents/SKILL.md`
- `.github/skills/tech-ai-docker/SKILL.md`
- `.github/skills/tech-ai-executing-plans/SKILL.md`
- `.github/skills/tech-ai-finishing-dev-branch/SKILL.md`
- `.github/skills/tech-ai-git-worktrees/SKILL.md`
- `.github/skills/tech-ai-pair-architect/SKILL.md`
- `.github/skills/tech-ai-pr-editor/SKILL.md`
- `.github/skills/tech-ai-project-java/SKILL.md`
- `.github/skills/tech-ai-project-nodejs/SKILL.md`
- `.github/skills/tech-ai-project-python/SKILL.md`
- `.github/skills/tech-ai-receiving-code-review/SKILL.md`
- `.github/skills/tech-ai-repo-copilot-extender/SKILL.md`
- `.github/skills/tech-ai-requesting-code-review/SKILL.md`
- `.github/skills/tech-ai-script-bash/SKILL.md`
- `.github/skills/tech-ai-script-python/SKILL.md`
- `.github/skills/tech-ai-skill-creator/SKILL.md`
- `.github/skills/tech-ai-subagent-driven-dev/SKILL.md`
- `.github/skills/tech-ai-sync-global-copilot-configs-into-repo/SKILL.md`
- `.github/skills/tech-ai-systematic-debugging/SKILL.md`
- `.github/skills/tech-ai-terraform-feature/SKILL.md`
- `.github/skills/tech-ai-terraform-module/SKILL.md`
- `.github/skills/tech-ai-test-driven-dev/SKILL.md`
- `.github/skills/tech-ai-using-superpowers/SKILL.md`
- `.github/skills/tech-ai-verification/SKILL.md`
- `.github/skills/tech-ai-writing-plans/SKILL.md`
- `.github/skills/tech-ai-writing-skills/SKILL.md`

### Agents

- `.github/agents/tech-ai-bash-reviewer.agent.md`
- `.github/agents/tech-ai-java-reviewer.agent.md`
- `.github/agents/tech-ai-nodejs-reviewer.agent.md`
- `.github/agents/tech-ai-planner.agent.md`
- `.github/agents/tech-ai-pr-editor.agent.md`
- `.github/agents/tech-ai-python-reviewer.agent.md`
- `.github/agents/tech-ai-repo-copilot-extender.agent.md`
- `.github/agents/tech-ai-security-reviewer.agent.md`
- `.github/agents/tech-ai-standards-repo-config-auditor.agent.md`
- `.github/agents/tech-ai-standards-repo-config-builder.agent.md`
- `.github/agents/tech-ai-sync-global-copilot-configs-into-repo.agent.md`
- `.github/agents/tech-ai-terraform-reviewer.agent.md`
