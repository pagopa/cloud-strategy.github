# AGENTS.md - customization-standards

This file is for GitHub Copilot and AI assistants working in this repository.

## Naming Policy

- Use GitHub Copilot terminology in repository-facing content.
- Do not mention internal runtime names in repository artifacts.
- Treat prompt frontmatter `name:` as the canonical command identifier.
- External resources must use `<short-repo>-<original-resource-name>` in filenames and `name:` values.
- Resources created locally in `cloud-strategy.github` must use the `internal-` prefix in filenames and `name:` values.
- Resources created locally in other repositories must use the `local-` prefix in filenames and `name:` values.
- The canonical project-owned `AGENTS.md` file must live in repository root as `AGENTS.md`.
- Do not keep legacy aliases, fallback copies, or deprecated variants. Preserve an alias only when an active backward-compatibility requirement is explicitly documented.

## Imported Resource Policy

- Treat every non-`internal-*` resource in this repository as an imported upstream asset that should remain verbatim unless the user explicitly asks to refresh, replace, or fork that import.
- Do not normalize, rewrite, trim, or delete imported non-`internal-*` resources as part of local optimization work.
- Express repository-specific behavior through `internal-*` resources only.
- Use `internal-*` resources as wrappers, extensions, adapters, or routing layers that map imported upstream resources to this repository's local needs.

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

#### Installed agents
- Use `internal-ai-resource-creator` for creating or refining repository-owned Copilot agents, skills, prompts, and instructions when the task is focused on authoring one resource rather than synchronizing the whole catalog.
  Skill lists inside agent bodies are optional repository convention only, not a required agent contract.
- Use `internal-sync-control-center` for governing the managed `.github/` Copilot catalog in this repository: use repo state as the starting point for drift analysis, refresh declared approved external assets, enforce origin-based naming, consolidate overlapping skills, retire obsolete catalog entries, and keep downstream governance files including `.github/copilot-instructions.md` and root `AGENTS.md` aligned with the catalog.
  This command center absorbs the former standalone Copilot-governance role.
- Use `internal-sync-global-copilot-configs-into-repo` for cross-repository Copilot-core alignment and source or target redundancy audits.
  Use it when propagating this repository baseline into another repository, or when comparing source and target drift across repositories. Do not use it for single-resource editing inside this repository.
- Use `internal-cicd` for CI/CD workflows, composite actions, release automation, and deployment-pipeline design.

#### Planning and Architecture
- Use `internal-architect` for cloud-agnostic strategic software and platform architecture decisions.
- Use `internal-pair-architect-analysis` prompt with the `internal-pair-architect` skill for deep change-impact analysis with health scoring, blind-spot detection, and structured Markdown reports.
- Use `internal-aws-org-governance` for strategic AWS organization governance: org structure, payer and management-account boundaries, delegated administration, SCP and IAM operating model, StackSets across the organization, and high-level process design.
  Examples: OU design, management-account responsibility split, delegated-admin placement, SCP exception model, org-wide StackSet rollout.
- Use `internal-aws-platform-engineering` for tactical AWS platform engineering: service architecture, incident and bug analysis, remediation planning, runtime tradeoffs, and platform-team execution inside an established governance model.
  Examples: Lambda or ECS incident triage, VPC or DNS troubleshooting, workload cost or performance analysis, Terraform or rollout implementation guidance.
- Use `internal-azure-platform-strategy` for strategic Azure platform and governance decisions: landing-zone shape, management-group and subscription boundaries, identity and policy operating model, resilience posture, cost-governance direction, and high-level process design.
  Examples: landing-zone topology, subscription placement, RBAC operating model, policy placement, strategic resilience posture.
- Use `internal-azure-platform-engineering` for tactical Azure platform engineering: service architecture, incident and bug analysis, remediation planning, runtime tradeoffs, and platform-team execution inside an established Azure strategy.
  Examples: AKS or App Service incident triage, VNet or private connectivity troubleshooting, workload cost or performance analysis, Terraform or rollout implementation guidance.
- Use `internal-gcp-platform-strategy` for strategic GCP platform and governance decisions: organization and folder structure, project boundaries, identity and policy operating model, resilience posture, cost-governance direction, and high-level process design.
  Examples: organization topology, project placement, IAM operating model, policy placement, strategic resilience posture.
- Use `internal-gcp-platform-engineering` for tactical GCP platform engineering: service architecture, incident and bug analysis, remediation planning, runtime tradeoffs, and platform-team execution inside an established GCP strategy.
  Examples: GKE or Cloud Run incident triage, VPC or private connectivity troubleshooting, workload cost or performance analysis, Terraform or rollout implementation guidance.

#### Editing and Delivery
- Use `internal-developer` for polyglot implementation work in Java, Node.js, Python, and Bash.
- Use `internal-infrastructure` for Terraform, Docker, Kubernetes, and infrastructure delivery.
- Use `internal-quality-engineering` for test strategy, performance, SQL or PostgreSQL tuning, and observability.
- Use `internal-code-review` for defect-first code review and merge-readiness checks.
  Use `internal-pair-architect` after line-level review when the question is change impact, ripple effects, or architecture risk rather than code defects alone.
- Use the `internal-pr-editor` prompt with the `internal-pr-editor` skill for pull request body generation from diffs.

### Anti-patterns

- Do not reference agents that are not present in `.github/agents/`; prefer installed agents plus prompts and skills that exist in the repository.
- Do not route PR editing through a missing agent when the repository provides the prompt and skill directly.


### Composition and Handoffs

- For changes spanning multiple domains, combine the installed agent with the matching repository prompt and skill rather than referencing legacy missing agents.
- Prefer cohesive command-center agents over artificially tiny agents.
- Split an agent only when responsibilities are disjoint, routing becomes ambiguous, or the instructions would conflict across tasks.
- Route cloud-specific governance or platform decisions to the matching cloud agent first; use `internal-architect` only when the decision is intentionally cloud-agnostic.
- Route in-repo catalog governance to `internal-sync-control-center`; route cross-repository baseline propagation to `internal-sync-global-copilot-configs-into-repo`.

## Governance References

- `security-baseline.md`: portable security controls baseline for all Copilot customization.
- `DEPRECATION.md`: lifecycle and deprecation policy for all customization assets.
- `repo-profiles.yml`: advisory profile catalog for different repository types.
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

- `internal-add-platform`: reusable platform/profile definition updates.
- `internal-add-report-script`: reusable governance and maintenance reporting scripts.
- `internal-add-unit-tests`: unit test authoring and improvement.
- `internal-github-action`: GitHub Actions workflow authoring.
- `internal-terraform-module`: reusable Terraform module and component authoring.

### Preferred skills

#### Domain-Specific Skills
- `internal-code-review`: strict review workflow and anti-pattern catalog.
- `internal-cicd-workflow`: CI or CD workflow design patterns.
- `internal-changelog-automation`: changelog generation, release notes, and semver-aware release documentation.
- `internal-sync-global-copilot-configs-into-repo`: deterministic sync planning and reporting.
- `internal-pr-editor`: PR body templates and diff-to-body mapping patterns.
- `internal-cloud-policy`: reusable cloud policy authoring patterns.
- `internal-aws-control-plane-governance`: principal-level AWS organization, delegated-admin, SCP, IAM, and StackSets control-plane strategy.
- `internal-aws-mcp-research`: AWS-docs and AWS MCP-first research workflow for current AWS guidance and safe IAM inspection.
- `internal-devops-core-principles`: DevOps operating model, CALMS, and DORA-driven delivery guidance.
- `internal-performance-optimization`: cross-stack profiling and performance decision framework.
- `internal-kubernetes-deployment`: production Kubernetes deployment and rollout guidance.
- `internal-agent-development`: repository-owned agent creation and agent-splitting guidance.
- `internal-agents-md-bridge`: lightweight `AGENTS.md` bridge design to `.github/copilot-instructions.md`.
- `internal-copilot-audit`: catalog overlap, hollow-reference, and bridge-quality auditing.
- `internal-copilot-docs-research`: official GitHub Copilot documentation and MCP-aware research workflow for validating customization decisions.
- `openai-skill-creator`: canonical skill creation, evaluation, and trigger-hardening guidance for this repository.
- `internal-skill-management`: catalog import, deduplication, normalization, and lifecycle governance.
- `internal-terraform`: unified Terraform skill for features and modules.
- `internal-pair-architect`: change-set-level impact, health scoring, risk matrix, and blind-spot detection.

#### Workflow Skills (obra/superpowers)
- `obra-brainstorming`: structured creative exploration before implementation.
- `obra-dispatching-parallel-agents`: coordinating parallel sub-agent work.
- `obra-executing-plans`: structured plan execution with checkpoints.
- `obra-finishing-a-development-branch`: pre-merge checklist and branch cleanup.
- `obra-using-git-worktrees`: efficient multi-branch work with git worktrees.
- `obra-receiving-code-review`: processing and addressing review feedback.
- `obra-requesting-code-review`: preparing changes for effective review.
- `obra-subagent-driven-development`: delegating implementation to focused sub-agents.
- `obra-systematic-debugging`: root-cause-first debugging with 4-phase process.
- `obra-test-driven-development`: TDD red-green-refactor workflow.
- `obra-using-skills`: skill capability awareness and reuse best practices.
- `obra-verification-before-completion`: evidence-based verification before claiming completion.
- `obra-writing-plans`: structured plan authoring.

### Required validations before PR

- `bash -n` and `shellcheck -s bash` for changed Bash scripts when available.
- `python -m compileall <changed_python_paths>` and relevant `pytest` checks for Python changes.
- `terraform fmt` and `terraform validate` for Terraform changes.

## Repository Inventory (Auto-generated)

### Instructions

- `.github/instructions/awesome-copilot-azure-devops-pipelines.instructions.md`
- `.github/instructions/awesome-copilot-copilot-sdk-python.instructions.md`
- `.github/instructions/awesome-copilot-go.instructions.md`
- `.github/instructions/awesome-copilot-instructions.instructions.md`
- `.github/instructions/awesome-copilot-kubernetes-manifests.instructions.md`
- `.github/instructions/awesome-copilot-oop-design-patterns.instructions.md`
- `.github/instructions/awesome-copilot-shell.instructions.md`
- `.github/instructions/awesome-copilot-springboot.instructions.md`
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
- `.github/instructions/internal-terraform.instructions.md`
- `.github/instructions/internal-yaml.instructions.md`

### Prompts

- `.github/prompts/internal-add-platform.prompt.md`
- `.github/prompts/internal-add-report-script.prompt.md`
- `.github/prompts/internal-add-unit-tests.prompt.md`
- `.github/prompts/internal-github-action.prompt.md`
- `.github/prompts/internal-terraform-module.prompt.md`

### Skills

- `.github/skills/antigravity-api-design-principles/SKILL.md`
- `.github/skills/antigravity-aws-cost-optimizer/SKILL.md`
- `.github/skills/antigravity-aws-penetration-testing/SKILL.md`
- `.github/skills/antigravity-aws-serverless/SKILL.md`
- `.github/skills/antigravity-backend-architect/SKILL.md`
- `.github/skills/antigravity-bash-pro/SKILL.md`
- `.github/skills/antigravity-clean-code/SKILL.md`
- `.github/skills/antigravity-cloud-architect/SKILL.md`
- `.github/skills/antigravity-cloudformation-best-practices/SKILL.md`
- `.github/skills/antigravity-code-refactoring-refactor-clean/SKILL.md`
- `.github/skills/antigravity-code-refactoring-tech-debt/SKILL.md`
- `.github/skills/antigravity-code-review-checklist/SKILL.md`
- `.github/skills/antigravity-domain-driven-design/SKILL.md`
- `.github/skills/antigravity-elon-musk/SKILL.md`
- `.github/skills/antigravity-github/SKILL.md`
- `.github/skills/antigravity-golang-pro/SKILL.md`
- `.github/skills/antigravity-grafana-dashboards/SKILL.md`
- `.github/skills/antigravity-java-pro/SKILL.md`
- `.github/skills/antigravity-javascript-pro/SKILL.md`
- `.github/skills/antigravity-kaizen/SKILL.md`
- `.github/skills/antigravity-kubernetes-architect/SKILL.md`
- `.github/skills/antigravity-kubernetes-deployment/SKILL.md`
- `.github/skills/antigravity-network-101/SKILL.md`
- `.github/skills/antigravity-network-engineer/SKILL.md`
- `.github/skills/antigravity-nodejs-best-practices/SKILL.md`
- `.github/skills/antigravity-python-patterns/SKILL.md`
- `.github/skills/antigravity-python-pro/SKILL.md`
- `.github/skills/antigravity-python-testing-patterns/SKILL.md`
- `.github/skills/antigravity-simplify-code/SKILL.md`
- `.github/skills/antigravity-software-architecture/SKILL.md`
- `.github/skills/antigravity-steve-jobs/SKILL.md`
- `.github/skills/antigravity-terraform-specialist/SKILL.md`
- `.github/skills/antigravity-warren-buffett/SKILL.md`
- `.github/skills/antigravity-web-scraper/SKILL.md`
- `.github/skills/antigravity-youtube-summarizer/SKILL.md`
- `.github/skills/awesome-copilot-agent-governance/SKILL.md`
- `.github/skills/awesome-copilot-agentic-eval/SKILL.md`
- `.github/skills/awesome-copilot-architecture-blueprint-generator/SKILL.md`
- `.github/skills/awesome-copilot-azure-devops-cli/SKILL.md`
- `.github/skills/awesome-copilot-azure-pricing/SKILL.md`
- `.github/skills/awesome-copilot-azure-resource-health-diagnose/SKILL.md`
- `.github/skills/awesome-copilot-azure-role-selector/SKILL.md`
- `.github/skills/awesome-copilot-cloud-design-patterns/SKILL.md`
- `.github/skills/awesome-copilot-codeql/SKILL.md`
- `.github/skills/awesome-copilot-create-github-action-workflow-specification/SKILL.md`
- `.github/skills/awesome-copilot-create-github-pull-request-from-specification/SKILL.md`
- `.github/skills/awesome-copilot-create-implementation-plan/SKILL.md`
- `.github/skills/awesome-copilot-create-readme/SKILL.md`
- `.github/skills/awesome-copilot-dependabot/SKILL.md`
- `.github/skills/awesome-copilot-documentation-writer/SKILL.md`
- `.github/skills/awesome-copilot-instructions-blueprint-generator/SKILL.md`
- `.github/skills/awesome-copilot-java-junit/SKILL.md`
- `.github/skills/awesome-copilot-java-springboot/SKILL.md`
- `.github/skills/awesome-copilot-javascript-typescript-jest/SKILL.md`
- `.github/skills/awesome-copilot-postgresql-optimization/SKILL.md`
- `.github/skills/awesome-copilot-pytest-coverage/SKILL.md`
- `.github/skills/awesome-copilot-refactor-plan/SKILL.md`
- `.github/skills/awesome-copilot-secret-scanning/SKILL.md`
- `.github/skills/awesome-copilot-sql-optimization/SKILL.md`
- `.github/skills/internal-agent-development/SKILL.md`
- `.github/skills/internal-agents-md-bridge/SKILL.md`
- `.github/skills/internal-aws-control-plane-governance/SKILL.md`
- `.github/skills/internal-aws-mcp-research/SKILL.md`
- `.github/skills/internal-changelog-automation/SKILL.md`
- `.github/skills/internal-cicd-workflow/SKILL.md`
- `.github/skills/internal-cloud-policy/SKILL.md`
- `.github/skills/internal-code-review/SKILL.md`
- `.github/skills/internal-composite-action/SKILL.md`
- `.github/skills/internal-copilot-audit/SKILL.md`
- `.github/skills/internal-copilot-docs-research/SKILL.md`
- `.github/skills/internal-data-registry/SKILL.md`
- `.github/skills/internal-devops-core-principles/SKILL.md`
- `.github/skills/internal-docker/SKILL.md`
- `.github/skills/internal-kubernetes-deployment/SKILL.md`
- `.github/skills/internal-pair-architect/SKILL.md`
- `.github/skills/internal-performance-optimization/SKILL.md`
- `.github/skills/internal-pr-editor/SKILL.md`
- `.github/skills/internal-project-java/SKILL.md`
- `.github/skills/internal-project-nodejs/SKILL.md`
- `.github/skills/internal-project-python/SKILL.md`
- `.github/skills/internal-script-bash/SKILL.md`
- `.github/skills/internal-script-python/SKILL.md`
- `.github/skills/internal-skill-management/SKILL.md`
- `.github/skills/internal-sync-global-copilot-configs-into-repo/SKILL.md`
- `.github/skills/internal-terraform/SKILL.md`
- `.github/skills/obra-brainstorming/SKILL.md`
- `.github/skills/obra-collision-zone-thinking/SKILL.md`
- `.github/skills/obra-condition-based-waiting/SKILL.md`
- `.github/skills/obra-defense-in-depth/SKILL.md`
- `.github/skills/obra-dispatching-parallel-agents/SKILL.md`
- `.github/skills/obra-executing-plans/SKILL.md`
- `.github/skills/obra-finishing-a-development-branch/SKILL.md`
- `.github/skills/obra-gardening-skills-wiki/SKILL.md`
- `.github/skills/obra-inversion-exercise/SKILL.md`
- `.github/skills/obra-meta-pattern-recognition/SKILL.md`
- `.github/skills/obra-preserving-productive-tensions/SKILL.md`
- `.github/skills/obra-pulling-updates-from-skills-repository/SKILL.md`
- `.github/skills/obra-receiving-code-review/SKILL.md`
- `.github/skills/obra-remembering-conversations/SKILL.md`
- `.github/skills/obra-requesting-code-review/SKILL.md`
- `.github/skills/obra-root-cause-tracing/SKILL.md`
- `.github/skills/obra-scale-game/SKILL.md`
- `.github/skills/obra-sharing-skills/SKILL.md`
- `.github/skills/obra-simplification-cascades/SKILL.md`
- `.github/skills/obra-subagent-driven-development/SKILL.md`
- `.github/skills/obra-systematic-debugging/SKILL.md`
- `.github/skills/obra-test-driven-development/SKILL.md`
- `.github/skills/obra-testing-anti-patterns/SKILL.md`
- `.github/skills/obra-testing-skills-with-subagents/SKILL.md`
- `.github/skills/obra-tracing-knowledge-lineages/SKILL.md`
- `.github/skills/obra-using-git-worktrees/SKILL.md`
- `.github/skills/obra-using-skills/SKILL.md`
- `.github/skills/obra-verification-before-completion/SKILL.md`
- `.github/skills/obra-when-stuck/SKILL.md`
- `.github/skills/obra-writing-plans/SKILL.md`
- `.github/skills/openai-gh-address-comments/SKILL.md`
- `.github/skills/openai-gh-fix-ci/SKILL.md`
- `.github/skills/openai-skill-creator/SKILL.md`
- `.github/skills/terraform-terraform-search-import/SKILL.md`
- `.github/skills/terraform-terraform-style-guide/SKILL.md`
- `.github/skills/terraform-terraform-test/SKILL.md`

### Agents

- `.github/agents/internal-ai-resource-creator.agent.md`
- `.github/agents/internal-architect.agent.md`
- `.github/agents/internal-aws-org-governance.agent.md`
- `.github/agents/internal-aws-platform-engineering.agent.md`
- `.github/agents/internal-cicd.agent.md`
- `.github/agents/internal-code-review.agent.md`
- `.github/agents/internal-developer.agent.md`
- `.github/agents/internal-infrastructure.agent.md`
- `.github/agents/internal-azure-platform-strategy.agent.md`
- `.github/agents/internal-azure-platform-engineering.agent.md`
- `.github/agents/internal-gcp-platform-strategy.agent.md`
- `.github/agents/internal-gcp-platform-engineering.agent.md`
- `.github/agents/internal-quality-engineering.agent.md`
- `.github/agents/internal-sync-control-center.agent.md`
- `.github/agents/internal-sync-global-copilot-configs-into-repo.agent.md`
