# AGENTS.md - customization-standards

This file is the repository-root bridge for GitHub Copilot customization resources.

`.github/copilot-instructions.md` is the primary detailed policy file.
Update `.github/copilot-instructions.md` first when policy, validation, or workflow guidance changes, then refresh root `AGENTS.md` only for routing, naming, discovery, or inventory alignment.

## Naming Policy

- Use GitHub Copilot terminology in repository-facing content.
- Do not mention internal or alternative assistant runtimes in repository artifacts.
- Treat prompt frontmatter `name:` as the canonical command identifier.
- External resources must use `<short-repo>-<original-resource-name>` in filenames and `name:` values.
- Resources created locally in `cloud-strategy.github` must use the `internal-` prefix in filenames and `name:` values.
- Resources created locally in other repositories must use the `local-` prefix in filenames and `name:` values.
- Root `AGENTS.md` is the canonical project-owned bridge file.
- Do not keep legacy aliases, fallback copies, or deprecated variants. Preserve an alias only when an active backward-compatibility requirement is explicitly documented.

## Imported Resource Policy

- Treat every non-`internal-*` resource in this repository as an imported upstream asset that should remain verbatim unless the user explicitly asks to refresh, replace, or fork that import.
- Express repository-specific behavior through `internal-*` resources only.
- Use `internal-*` resources as wrappers, extensions, adapters, or routing layers that map imported upstream resources to this repository's local needs.

## Layered Routing Model

- `obra-*` skills are the strategic lane for framing, planning, simplification, tradeoff handling, and verification.
- `internal-*` skills are the tactical lane and the default repository-owned execution or governance owners.
- Imported non-`internal-*` skills remain support-only unless no internal owner exists for the capability.

## Decision Priority

1. Apply `.github/copilot-instructions.md` as the primary detailed policy layer.
2. Apply explicit user requirements for the current task.
3. Apply the selected agent behavior.
4. Apply matching `.github/instructions/*.instructions.md` using `applyTo`.
5. Apply selected `.github/prompts/*.prompt.md`.
6. Apply implementation details from referenced `.github/skills/*/SKILL.md`.
7. Use the inventory below for discovery only; do not duplicate detailed policy in this file.

## Agent Routing

- `internal-router`: recommended operational front door when the correct owner is not obvious yet.
- `internal-fast-executor`: clear, local, execution-owned work with concrete verification.
- `internal-planning-leader`: ambiguity resolution, non-trivial repository-owned authoring, and strategy or rollout decisions.
- `internal-review-guard`: defect-first review, merge readiness, regression risk, and evidence-based validation.
- `internal-critical-challenger`: pre-mortems, reasoning stress tests, and failure-mode analysis.
- `internal-sync-control-center`: source-side governance of the live `.github/` Copilot catalog in this repository.
- `internal-sync-global-copilot-configs-into-repo`: cross-repository Copilot-core alignment and redundancy audits.
- `internal-pr-editor` is intentionally prompt-routed; use the `internal-pr-editor` prompt with the `internal-pr-editor` skill for pull request body generation.
- `internal-data-registry` remains installed as intentionally dormant tactical capacity until a dedicated routing owner is added.
- Imported `awesome-*` agents and repo-only `internal-sync-*` agents stay outside the canonical operational ownership model.
- Do not reference agents that are not present in `.github/agents/`.

## Repository Defaults

- Primary focus: reusable, repository-agnostic GitHub Copilot customization standards.
- Profile hint: `minimal`
- Keep root `AGENTS.md` light: naming, routing, discovery, and inventory only.
- Keep detailed behavior, validation, PR or workflow policy, and implementation guardrails in `.github/copilot-instructions.md`.
- Completion-report details live in `.github/copilot-instructions.md`; keep only the bridge-level pointer here.
- Prioritize these paths:
  - `.github/instructions`
  - `.github/prompts`
  - `.github/skills`
  - `.github/agents`
  - `.github/scripts`

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
- `.github/skills/antigravity-aws-serverless/SKILL.md`
- `.github/skills/antigravity-cloudformation-best-practices/SKILL.md`
- `.github/skills/antigravity-domain-driven-design/SKILL.md`
- `.github/skills/antigravity-golang-pro/SKILL.md`
- `.github/skills/antigravity-grafana-dashboards/SKILL.md`
- `.github/skills/antigravity-kubernetes-architect/SKILL.md`
- `.github/skills/antigravity-network-engineer/SKILL.md`
- `.github/skills/awesome-copilot-agentic-eval/SKILL.md`
- `.github/skills/awesome-copilot-azure-devops-cli/SKILL.md`
- `.github/skills/awesome-copilot-azure-pricing/SKILL.md`
- `.github/skills/awesome-copilot-azure-resource-health-diagnose/SKILL.md`
- `.github/skills/awesome-copilot-azure-role-selector/SKILL.md`
- `.github/skills/awesome-copilot-cloud-design-patterns/SKILL.md`
- `.github/skills/awesome-copilot-codeql/SKILL.md`
- `.github/skills/awesome-copilot-dependabot/SKILL.md`
- `.github/skills/awesome-copilot-secret-scanning/SKILL.md`
- `.github/skills/internal-agent-development/SKILL.md`
- `.github/skills/internal-agent-operating-model-engine/SKILL.md`
- `.github/skills/internal-agent-routing-engine/SKILL.md`
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
- `.github/skills/obra-dispatching-parallel-agents/SKILL.md`
- `.github/skills/obra-executing-plans/SKILL.md`
- `.github/skills/obra-finishing-a-development-branch/SKILL.md`
- `.github/skills/obra-receiving-code-review/SKILL.md`
- `.github/skills/obra-requesting-code-review/SKILL.md`
- `.github/skills/obra-subagent-driven-development/SKILL.md`
- `.github/skills/obra-systematic-debugging/SKILL.md`
- `.github/skills/obra-test-driven-development/SKILL.md`
- `.github/skills/obra-using-git-worktrees/SKILL.md`
- `.github/skills/obra-using-superpowers/SKILL.md`
- `.github/skills/obra-verification-before-completion/SKILL.md`
- `.github/skills/obra-writing-plans/SKILL.md`
- `.github/skills/obra-writing-skills/SKILL.md`
- `.github/skills/openai-gh-address-comments/SKILL.md`
- `.github/skills/openai-gh-fix-ci/SKILL.md`
- `.github/skills/openai-skill-creator/SKILL.md`
- `.github/skills/terraform-terraform-search-import/SKILL.md`
- `.github/skills/terraform-terraform-test/SKILL.md`

### Agents

- `.github/agents/awesome-copilot-azure-principal-architect.agent.md`
- `.github/agents/awesome-copilot-critical-thinking.agent.md`
- `.github/agents/awesome-copilot-devils-advocate.agent.md`
- `.github/agents/awesome-copilot-devops-expert.agent.md`
- `.github/agents/awesome-copilot-plan.agent.md`
- `.github/agents/internal-critical-challenger.agent.md`
- `.github/agents/internal-fast-executor.agent.md`
- `.github/agents/internal-planning-leader.agent.md`
- `.github/agents/internal-review-guard.agent.md`
- `.github/agents/internal-router.agent.md`
- `.github/agents/internal-sync-control-center.agent.md`
- `.github/agents/internal-sync-global-copilot-configs-into-repo.agent.md`
