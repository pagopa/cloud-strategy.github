# AGENTS.md - customization-standards

This file is for GitHub Copilot and AI assistants working in this repository.

## Naming Policy

- Use GitHub Copilot terminology in repository-facing content.
- Do not mention internal runtime names in repository artifacts.
- Treat prompt frontmatter `name:` as the canonical command identifier.
- External resources must use `<short-repo>-<original-resource-name>` in filenames and `name:` values.
- Resources created locally in `cloud-strategy.github` must use the `internal-` prefix in filenames and `name:` values.
- Resources created locally in other repositories must use the `local-` prefix in filenames and `name:` values.
- Reserve the `TechAIGlobal` prefix only for repo-only agents that encode standards for this global configuration repository.
- The canonical project-owned `AGENTS.md` file must live in repository root as `AGENTS.md`.
- Keep legacy aliases only when required for backward compatibility.

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
- Use `internal-bash-reviewer` for exhaustive, nit-level Bash script reviews.
- Use `internal-java-reviewer` for exhaustive, nit-level Java code reviews.
- Use `internal-nodejs-reviewer` for exhaustive, nit-level Node.js code reviews.
- Use `internal-python-reviewer` for exhaustive, nit-level Python code reviews.
- Use `internal-terraform-reviewer` for exhaustive, nit-level Terraform code reviews.
- Use `internal-security-reviewer` for security-focused review across all languages.

#### Planning and Architecture
- Use `internal-planner` for ambiguous scope, tradeoff analysis, or multi-step design.
- Use `internal-pair-architect-analysis` prompt with the `internal-pair-architect` skill for deep change-impact analysis with health scoring, blind-spot detection, and structured Markdown reports.

#### Editing and Delivery
- Use `internal-pr-editor` for pull request body generation from diffs.

#### Repository Configuration (source-only, not synced to consumers)
- Use `internal-sync-global-copilot-configs-into-repo` for cross-repository Copilot-core alignment and source or target redundancy audits.

### Anti-patterns

- Do not use `internal-planner` for trivial single-file changes with clear requirements; work directly.
- Do not use a specialist reviewer outside its language domain; pick the matching one.


### Composition and Handoffs

- For changes spanning multiple specialist domains, run each relevant specialist reviewer and aggregate findings.

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

- `**/*.py` -> `internal-python.instructions.md`
- `**/Dockerfile,**/Dockerfile.*,**/.dockerignore,**/docker-compose*.yml,**/compose*.yml` -> `internal-docker.instructions.md`
- `**/*.sh` -> `internal-bash.instructions.md`
- `**/*.tf` -> `internal-terraform.instructions.md`
- `**/*.java` -> `internal-java.instructions.md`
- `**/*.js,**/*.cjs,**/*.mjs,**/*.ts,**/*.tsx` -> `internal-nodejs.instructions.md`
- `**/*lambda*.tf,**/*lambda*.py,**/*lambda*.js,**/*lambda*.ts` -> `internal-lambda.instructions.md`
- `**/*.yml,**/*.yaml` -> `internal-yaml.instructions.md`
- `**/*.md` -> `internal-markdown.instructions.md`
- `**/Makefile,**/*.mk` -> `internal-makefile.instructions.md`
- `**/workflows/**` -> `internal-github-actions.instructions.md`
- `**/actions/**/action.y*ml` -> `internal-github-action-composite.instructions.md`
- `**/authorizations/**/*.json,**/organization/**/*.json,**/src/**/*.json,**/data/**/*.json` -> `internal-json.instructions.md`

### Preferred prompts

- `internal-code-review`: exhaustive, nit-level code review.
- `internal-github-action`: GitHub Actions workflow authoring.
- `internal-sync-global-copilot-configs-into-repo`: cross-repository alignment and redundancy analysis.
- `internal-pr-editor`: pull request body generation.
- `internal-add-unit-tests`: test authoring and improvement.
- `internal-terraform`: Terraform feature or module authoring.
- `internal-pair-architect-analysis`: deep change-impact analysis with health score, risk matrix, and devil's advocate mode.

### Preferred skills

#### Domain-Specific Skills
- `internal-code-review`: strict review workflow and anti-pattern catalog.
- `internal-cicd-workflow`: CI or CD workflow design patterns.
- `internal-sync-global-copilot-configs-into-repo`: deterministic sync planning and reporting.
- `internal-pr-editor`: PR body templates and diff-to-body mapping patterns.
- `internal-cloud-policy`: reusable cloud policy authoring patterns.
- `internal-terraform`: unified Terraform skill for features and modules.
- `internal-pair-architect`: change-set-level impact, health scoring, risk matrix, and blind-spot detection.

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

- `.github/instructions/internal-bash.instructions.md`
- `.github/instructions/internal-docker.instructions.md`
- `.github/instructions/internal-github-action-composite.instructions.md`
- `.github/instructions/internal-github-actions.instructions.md`
- `.github/instructions/internal-java.instructions.md`
- `.github/instructions/internal-json.instructions.md`
- `.github/instructions/internal-lambda.instructions.md`
- `.github/instructions/internal-makefile.instructions.md`
- `.github/instructions/internal-markdown.instructions.md`
- `.github/instructions/internal-nodejs.instructions.md`
- `.github/instructions/internal-python.instructions.md`
- `.github/instructions/internal-terraform-aws.instructions.md`
- `.github/instructions/internal-terraform-azure.instructions.md`
- `.github/instructions/internal-terraform-gcp.instructions.md`
- `.github/instructions/internal-terraform.instructions.md`
- `.github/instructions/internal-yaml.instructions.md`

### Prompts

- `.github/prompts/internal-add-platform.prompt.md`
- `.github/prompts/internal-add-report-script.prompt.md`
- `.github/prompts/internal-add-unit-tests.prompt.md`
- `.github/prompts/internal-bash-script.prompt.md`
- `.github/prompts/internal-cicd-workflow.prompt.md`
- `.github/prompts/internal-cloud-policy.prompt.md`
- `.github/prompts/internal-code-review.prompt.md`
- `.github/prompts/internal-data-registry.prompt.md`
- `.github/prompts/internal-docker.prompt.md`
- `.github/prompts/internal-github-action.prompt.md`
- `.github/prompts/internal-github-composite-action.prompt.md`
- `.github/prompts/internal-java.prompt.md`
- `.github/prompts/internal-nodejs.prompt.md`
- `.github/prompts/internal-pair-architect-analysis.prompt.md`
- `.github/prompts/internal-pr-editor.prompt.md`
- `.github/prompts/internal-python-script.prompt.md`
- `.github/prompts/internal-python.prompt.md`
- `.github/prompts/internal-sync-global-copilot-configs-into-repo.prompt.md`
- `.github/prompts/internal-terraform-module.prompt.md`
- `.github/prompts/internal-terraform.prompt.md`

### Skills

- `.github/skills/internal-cicd-workflow/SKILL.md`
- `.github/skills/internal-cloud-policy/SKILL.md`
- `.github/skills/internal-code-review/SKILL.md`
- `.github/skills/internal-composite-action/SKILL.md`
- `.github/skills/internal-data-registry/SKILL.md`
- `.github/skills/claude-agent-development/SKILL.md`
- `.github/skills/internal-docker/SKILL.md`
- `.github/skills/internal-pair-architect/SKILL.md`
- `.github/skills/internal-pr-editor/SKILL.md`
- `.github/skills/internal-project-java/SKILL.md`
- `.github/skills/internal-project-nodejs/SKILL.md`
- `.github/skills/internal-project-python/SKILL.md`
- `.github/skills/internal-script-bash/SKILL.md`
- `.github/skills/internal-script-python/SKILL.md`
- `.github/skills/claude-skill-creator/SKILL.md`
- `.github/skills/internal-sync-global-copilot-configs-into-repo/SKILL.md`
- `.github/skills/internal-terraform/SKILL.md`

### Agents

- `.github/agents/internal-bash-reviewer.agent.md`
- `.github/agents/internal-agent-sync.agent.md`
- `.github/agents/internal-java-reviewer.agent.md`
- `.github/agents/internal-nodejs-reviewer.agent.md`
- `.github/agents/internal-planner.agent.md`
- `.github/agents/internal-pr-editor.agent.md`
- `.github/agents/internal-python-reviewer.agent.md`
- `.github/agents/internal-security-reviewer.agent.md`
- `.github/agents/internal-sync-global-copilot-configs-into-repo.agent.md`
- `.github/agents/internal-terraform-reviewer.agent.md`
