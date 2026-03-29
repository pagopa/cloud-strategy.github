# .github Configuration

This folder is the **single source of truth** for GitHub Copilot customization assets propagated to all consumer repositories. It defines rules, prompts, skills, agents, and tooling that ensure consistent AI-assisted development across the organization.

---

## Structure

### Baseline files (always applied)

| File | Purpose | Use when | Do NOT use when |
| --- | --- | --- | --- |
| `copilot-instructions.md` | Global non-negotiable rules: language policy, least privilege, DDD preference, test execution order, script standards, validation baseline. | Every Copilot interaction — this is the root of the instruction chain. | Never skip — it's always loaded first. |
| `copilot-commit-message-instructions.md` | Commit message format: `<type>(<scope>): <summary>`, imperative mood, 72-char limit. | Writing commits via Copilot or reviewing commit messages. | Manual commits that follow the same convention already. |
| `copilot-code-review-instructions.md` | Review severity levels, baseline checks, escalation rules. References `tech-ai-code-review/SKILL.md` for anti-pattern catalogs. | Running Copilot code review or configuring review agents. | General implementation guidance (see reviewer agents for specialized reviews). |
| `security-baseline.md` | Portable security checklist: SHA-pinned actions, minimal permissions, OIDC, branch protection, prompt/agent safety. | Every infrastructure or workflow change. Referenced by all agents as a minimum bar. | Application-only code changes with no infra impact. |

### Configuration and governance

| File | Purpose | Use when | Do NOT use when |
| --- | --- | --- | --- |
| `repo-profiles.yml` | Advisory catalog of 6 profiles (`minimal`, `backend-java`, `backend-nodejs`, `backend-python`, `infrastructure-heavy`, `mixed-platform`). Maps each to recommended instructions, prompts, and skills. | Onboarding a new consumer repo — pick a profile to bootstrap the right asset set. | Enforcement — profiles are advisory today, not enforced by validators. |
| `DEPRECATION.md` | Lifecycle policy (Active → Deprecated → Removed) with 30-day window, migration guidance, emergency exception for security. | Sunsetting a prompt, skill, instruction, or agent. Check before removing anything. | Creating new assets (no lifecycle concerns for new additions). |
| `CHANGELOG.md` | Change log for notable modifications to customization assets. | After every meaningful change to `.github/` — update as last maintenance step. | Minor formatting or comment-only changes. |
| `dependabot.yml` | Dependabot configuration for automated dependency updates. | Configuring update schedules for consumer repos using this as a template. | This repo itself only uses Python stdlib + pytest — the npm/maven/gradle ecosystems are templates for consumers. |
| `PULL_REQUEST_TEMPLATE.md` | PR template with sections: Description, Change Type, Consumer Impact, Testing, Validation Evidence, Breaking Changes, Checklist. | Every PR to this repository. Auto-loaded by GitHub. | Consumer repos — they should define their own PR template. |
| `tech-ai-requirements-dev.txt` | Dev dependencies for the test suite (currently: `pytest==8.3.3`). | Running `make test` or `pytest` locally. | Production — there are no runtime dependencies. |
| `.bootstrap-ignore` | Rsync exclude patterns for the deprecated `bootstrap-copilot-config.sh`. | Only if still using the legacy bootstrap path. | The preferred sync script — it uses its own manifest logic. |

### Instructions (`instructions/`)

Path-specific rules auto-applied by Copilot when editing matching files. Each instruction targets a language or file type via `applyTo` glob patterns.

| Category | Files | Example use case |
| --- | --- | --- |
| **Languages** | `bash`, `java`, `nodejs`, `python` | Editing a `.py` file → `python.instructions.md` auto-applies with naming, testing, and style rules. |
| **Infrastructure** | `terraform`, `makefile` | Running `terraform plan` or editing a `Makefile` → relevant conventions auto-apply. |
| **CI/CD** | `github-actions`, `github-action-composite` | Editing a workflow YAML → SHA-pinning, permission, and caching rules auto-apply. |
| **Data formats** | `json`, `yaml`, `markdown` | Editing a `README.md` → Markdown linting and structural rules auto-apply. |
| **Scripts** | `scripts`, `lambda` | Editing a script or Lambda handler → orchestration and logging conventions auto-apply. |

**When to use**: Instructions are automatic — they apply based on file path. No manual invocation needed.
**When NOT to use**: Don't reference instructions directly in prompts — Copilot resolves them from `applyTo` rules.

### Prompts (`prompts/`)

Slash-command prompts invoked via `/` in Copilot chat for structured, repeatable tasks.

**When to use**: You need a consistent, reproducible output for a known task type.
**When NOT to use**: Ad-hoc questions, exploratory conversations, or one-off edits — just chat normally.

#### Language and project scaffolding

| Prompt | Purpose | Example trigger |
| --- | --- | --- |
| `tech-ai-java` | Create or modify Java project components (services, controllers, handlers) with JUnit 5 tests. | `/tech-ai-java action=create component_type=service component_name=PaymentService purpose="process payments"` |
| `tech-ai-nodejs` | Create or modify Node.js modules (services, handlers, adapters) with `node:test` tests. | `/tech-ai-nodejs action=create component_type=handler component_name=webhook purpose="receive Stripe events"` |
| `tech-ai-python` | Create or modify Python application components (DDD entities, services, adapters) with pytest. | `/tech-ai-python action=create component_type=domain_service component_name=InvoiceService purpose="invoice generation"` |
| `tech-ai-python-script` | Create or modify standalone Python scripts with explicit interfaces, emoji logs, pinned deps. | `/tech-ai-python-script action=create script_name=migrate-data purpose="migrate legacy DB records"` |
| `tech-ai-bash-script` | Create or modify Bash scripts with strict mode, guard clauses, emoji logs. | `/tech-ai-bash-script action=create script_name=cleanup-ecr purpose="prune untagged ECR images"` |

#### Infrastructure

| Prompt | Purpose | Example trigger |
| --- | --- | --- |
| `tech-ai-terraform` | Create or modify Terraform resources and features in an existing stack. | `/tech-ai-terraform action=create type=resource description="S3 bucket for logs" target_dir=src/infra/prod` |
| `tech-ai-terraform-module` | Create or modify reusable Terraform modules with standard file layout. | `/tech-ai-terraform-module action=create module_name=vpc purpose="shared VPC with public/private subnets"` |
| `tech-ai-cloud-policy` | Create or modify cloud governance policies (AWS SCP, Azure Policy, GCP Org Policy). | `/tech-ai-cloud-policy action=create cloud=aws policy_name=deny-public-s3 purpose="block public S3 buckets"` |

#### CI/CD

| Prompt | Purpose | Example trigger |
| --- | --- | --- |
| `tech-ai-cicd-workflow` | Create or modify reusable GitHub Actions workflows for CI/CD and governance. | `/tech-ai-cicd-workflow action=create workflow_name=deploy-staging purpose="deploy to staging on push to main" trigger=push` |
| `tech-ai-github-action` | Create or modify a single GitHub Actions workflow file. | `/tech-ai-github-action action=create workflow_name=lint purpose="run linters on PR" triggers=pull_request` |
| `tech-ai-github-composite-action` | Create or modify a reusable GitHub composite action. | `/tech-ai-github-composite-action action=create action_name=setup-node purpose="install Node.js with caching"` |

#### Review, analysis, and PR

| Prompt | Purpose | Example trigger |
| --- | --- | --- |
| `tech-ai-code-review` | Exhaustive, nit-level code review on Python, Bash, or Terraform files. | `/tech-ai-code-review target=src/infra/modules/vpc language=terraform strictness=strict` |
| `tech-ai-pair-architect-analysis` | Deep change-impact analysis: errors, improvements, blind spots, DDD, and architecture. Generates `ANALYSIS_REPORT.md`. | `/tech-ai-pair-architect-analysis target=main depth=full mode=devil` |
| `tech-ai-pr-description` | Generate a PR description from the repo template and the current diff. | `/tech-ai-pr-description title="Add VPC module" intent="shared networking" changed_files=src/infra/modules/vpc` |

#### Testing and reporting

| Prompt | Purpose | Example trigger |
| --- | --- | --- |
| `tech-ai-add-unit-tests` | Add or improve unit tests for Python code following org conventions. | `/tech-ai-add-unit-tests target_file=src/services/payment.py` |
| `tech-ai-add-report-script` | Add or update a reporting/governance script with configurable output format. | `/tech-ai-add-report-script action=create script_name=orphan-finder purpose="find unused IAM roles" output_format=json` |

#### Operations and governance

| Prompt | Purpose | Example trigger |
| --- | --- | --- |
| `tech-ai-data-registry` | Add, modify, or remove entries in structured JSON/YAML registry files. | `/tech-ai-data-registry action=create file=config/users.json key=new-user change="add service account"` |
| `tech-ai-add-platform` | Add or update a reusable platform/profile definition for repo standards. | `/tech-ai-add-platform action=add platform_id=ml-training primary_stack=python goal="ML training pipelines"` |
| `tech-ai-sync-global-copilot-configs-into-repo` | Analyze and align a consumer repo with the minimum Copilot customization assets from this standards repo. | `/tech-ai-sync-global-copilot-configs-into-repo target_repo=../oneidentity mode=plan` |

### Agents (`agents/`)

Implementation knowledge bases loaded on demand by agents and prompts. They contain templates, anti-pattern catalogs, and generation patterns. You rarely invoke skills directly — they are consumed automatically when you use the matching prompt or agent.

**When to use**: Referenced automatically by agents/prompts. Read a SKILL.md directly only when debugging agent behavior or understanding what patterns are applied.
**When NOT to use**: Don't load skills manually in normal workflows.

| Skill | Purpose | Consumed by |
| --- | --- | --- |
| `tech-ai-pair-architect` | DDD analysis dimensions, severity mappings, health score, risk matrix format, report template for change-impact analysis. | Agent `TechAIPairArchitect`, prompt `tech-ai-pair-architect-analysis` |
| `tech-ai-pair-architect-analysis-executor` | Decision-table format, execution plan template, disagreement protocol, quality checklist for re-evaluating analysis reports. | Agent `TechAIPairArchitectAnalysisExecutor` |
| `tech-ai-code-review` | Per-language anti-pattern catalogs (Python, Bash, Terraform), severity mappings, escalation rules for exhaustive code review. | Agents `TechAIBashReviewer`, `TechAIPythonReviewer`, `TechAITerraformReviewer`, `TechAIPairArchitect`; prompt `tech-ai-code-review` |
| `tech-ai-pr-editor` | PR description templates, section structure, and diff-to-description mapping for generating review-ready PR bodies. | Agent `TechAIPREditor`, prompt `tech-ai-pr-description` |
| `tech-ai-project-java` | Java component scaffolding: purpose JavaDoc, BDD-like JUnit 5 tests, module conventions. | Prompt `tech-ai-java` |
| `tech-ai-project-nodejs` | Node.js module scaffolding: purpose comments, `node:test` tests, adapter patterns. | Prompt `tech-ai-nodejs` |
| `tech-ai-project-python` | Python application scaffolding: DDD boundaries, early returns, pytest coverage. | Prompt `tech-ai-python` |
| `tech-ai-script-bash` | Bash script patterns: purpose header, emoji logs, guard-clause flow, shellcheck compliance. | Prompt `tech-ai-bash-script` |
| `tech-ai-script-python` | Python script patterns: purpose docstring, emoji logs, pinned deps, unit tests. | Prompt `tech-ai-python-script` |
| `tech-ai-terraform-feature` | Terraform resource/variable/output/data source implementation patterns. | Prompt `tech-ai-terraform` |
| `tech-ai-terraform-module` | Terraform module scaffolding: standard file layout (`main.tf`, `variables.tf`, `outputs.tf`), validation. | Prompt `tech-ai-terraform-module` |
| `tech-ai-cloud-policy` | Cloud governance policy patterns for AWS SCP, Azure Policy, GCP Org Policy. | Prompt `tech-ai-cloud-policy` |
| `tech-ai-cicd-workflow` | Secure GitHub Actions workflow patterns: SHA-pinning, permissions, caching, matrix strategies. | Prompt `tech-ai-cicd-workflow` |
| `tech-ai-composite-action` | Composite action patterns: secure Bash steps, input/output contracts, deterministic behavior. | Prompt `tech-ai-github-composite-action` |
| `tech-ai-data-registry` | JSON/YAML registry update patterns: safe mutations, key validation, schema consistency. | Prompt `tech-ai-data-registry` |
| `tech-ai-sync-global-copilot-configs-into-repo` | Manifest-based sync logic for propagating the shared baseline into consumer repos — asset selection, SHA256 checksums, conflict detection, and reporting. | Agent `TechAISyncGlobalCopilotConfigsIntoRepo`, prompt `tech-ai-sync-global-copilot-configs-into-repo` |

### Agents (`agents/`)

Custom chat agents for focused tasks. Each agent has a single responsibility. See [`agents/README.md`](agents/README.md) for the full selection guide.

**When to use**: Route to agents based on your workflow step.
**When NOT to use**: Simple questions or one-off edits — Copilot's default behavior is sufficient.

#### Core workflow agents

These agents form the main plan → analyze → execute → review pipeline.

| Agent | Purpose | Example trigger | Read-only? |
| --- | --- | --- | --- |
| `TechAIPlanner` | Produce implementation plans with risks, assumptions, and validation criteria. Does not touch files. | "Plan the migration of the payment service to a hexagonal architecture." | Yes |
| `TechAIPairArchitect` | Deep change-impact analysis: DDD, architecture, blind spots, risk matrix. Generates `ANALYSIS_REPORT.md`. | "Analyze all changes on this branch and generate the analysis report." | Yes (writes report only) |
| `TechAIPairArchitectAnalysisExecutor` | Re-evaluate the analysis report, challenge each finding, produce `EXECUTION_PLAN.md` with decision tables and lessons learned. | "Take the ANALYSIS_REPORT.md, verify every finding, and create the execution plan." | Yes (writes plan only) |
| `TechAIImplementer` | Execute changes end-to-end with safe, minimal, testable modifications. Follows plans from Planner or Executor. | "Execute work package WP-3 from the execution plan." | **No** — edits files |

#### Review agents

Three complementary levels of review — they do NOT overlap.

| Agent | Purpose | Scope | Example trigger | When to use instead of the others |
| --- | --- | --- | --- | --- |
| `TechAIReviewer` | Structured code review: defects, regressions, maintainability. Diff-first, broad. | Any language, any change | "Review this PR for quality before merge." | **Default choice** for general PR review. Delegates to specialists when needed. |
| `TechAISecurityReviewer` | Security-focused review: secrets, permissions, attack surface, compliance. | Any change with security impact | "Security review of the new IAM module and workflow changes." | When the change touches **security-sensitive** code (IAM, secrets, auth, networking). |

> **How they differ**: `TechAIReviewer` is the broad quality gate (like a senior engineer's PR review). `TechAISecurityReviewer` focuses exclusively on security concerns. Use `TechAIReviewer` first; it will recommend routing to a specialist when needed.

#### Infrastructure specialist agents

| Agent | Purpose | Example trigger |
| --- | --- | --- |
| `TechAITerraformGuardrails` | Review Terraform changes for guardrails, lifecycle safety, state hygiene, and drift detection. | "Check the Terraform changes in src/infra/ for policy compliance." |
| `TechAIIAMLeastPrivilege` | Analyze IAM and policy changes for least-privilege compliance across AWS, Azure, and GCP. | "Audit the new IAM role — is it least privilege?" |
| `TechAIWorkflowSupplyChain` | Review GitHub Actions workflows for supply-chain risk, SHA-pinning, and reusable CI/CD design. | "Check the new deploy workflow for supply chain risks." |

#### PR agent

| Agent | Purpose | Example trigger |
| --- | --- | --- |
| `TechAIPREditor` | Generate or update PR title and body using the repo template and real diff context. | "Write the PR description for this branch." |

#### Copilot customization lifecycle agents (this repo only)

These agents manage the **lifecycle** of Copilot customization assets. They are repo-only (not synced to consumers):

| Agent | Lifecycle stage | Purpose | Example trigger |
| --- | --- | --- | --- |
| `TechAISyncGlobalCopilotConfigsIntoRepo` | **Propagate** | Push the shared Copilot baseline from this standards repo into a consumer repo (e.g. onemail, oneidentity) with conflict detection and SHA256 checksums. | "Sync the baseline config to the oneidentity repo." |

> **How they differ**: Sync pushes the shared baseline to consumer repos. They form a pipeline, not overlapping alternatives.

#### Overlap analysis

| Potential confusion | Verdict | Distinction |
| --- | --- | --- |
| `TechAIPairArchitect` vs `TechAIReviewer` | **Different scope** | PairArchitect does cross-cutting architecture/DDD analysis of the full change set. Reviewer does per-file defect-focused PR review. Use PairArchitect for design-level assessment, Reviewer for merge readiness. |
| `TechAIPlanner` vs `TechAIPairArchitectAnalysisExecutor` | **Different input** | Planner works from requirements/user intent. Executor works from an existing `ANALYSIS_REPORT.md`. Planner is upstream (before code); Executor is downstream (after analysis). |

### Scripts (`scripts/`)

| Script | Purpose | Use when | Do NOT use when |
| --- | --- | --- | --- |
| `validate-copilot-customizations.sh` | Validates frontmatter, section structure, agent metadata, inventory consistency, and SHA-pinning across all customization assets. | After any change to `.github/` — run with `--scope root --mode strict`. | Validating application code (run linters instead). |
| `internal-sync-copilot-configs.py` | Manifest-based conservative sync with conflict detection, SHA256 checksums, and reporting. Preferred tool for aligning consumer repos. | Propagating config updates to consumer repos — run with `--mode plan` first, then `--mode apply`. | This repo itself — it's the source, not a target. |
| `bootstrap-copilot-config.sh` | ⚠️ **Deprecated** — rsync-based simple copy. See `DEPRECATION.md`. | Only as a legacy fallback for consumers not yet migrated to the sync script. | New consumers — use `internal-sync-copilot-configs.py` instead. |

### Templates (`templates/`)

| Template | Purpose | Use when |
| --- | --- | --- |
| `AGENTS.template.md` | Template for consumer repository `AGENTS.md`: naming policy, decision priority, agent routing, inventory sections. | Onboarding a new consumer repo or regenerating its `AGENTS.md`. |
| `copilot-quickstart.md` | Short onboarding guide: copy baseline, add stack assets, run validator. | First-time setup of Copilot customization in a consumer repo. |

### Workflow (`workflows/`)

| Workflow | Purpose |
| --- | --- |
| `github-validate-copilot-customizations.yml` | CI workflow that runs the validator on PRs touching `.github/` assets. |

---

## Maintenance workflow

1. Edit files under `.github/`.
2. Run validation: `./scripts/validate-copilot-customizations.sh --scope root --mode strict`.
3. Optional JSON report: `./scripts/validate-copilot-customizations.sh --scope root --mode strict --report json --report-file /tmp/copilot-report.json`.
4. Cross-repo alignment: `python scripts/internal-sync-copilot-configs.py --target <repo-path> --mode plan` → review → `--mode apply`.
5. Optional cross-repo assessment: `./scripts/validate-copilot-customizations.sh --scope all --mode legacy-compatible`.
6. Ensure CI workflow passes.
7. Update `CHANGELOG.md` for notable changes.

---

## Notes

- `repo-profiles.yml` is advisory-only (human-readable profile catalog, not enforced by validators).
- The canonical project `AGENTS.md` belongs at repository root, not under `.github/`.
- **Repo-only agents** (not synced to consumers): `TechAISyncGlobalCopilotConfigsIntoRepo`.
- **Source-only assets** (excluded from consumer baselines): `.github/README.md`, `agents/README.md`, `templates/**`, `scripts/bootstrap-copilot-config.sh`, `tech-ai-requirements-dev.txt`, `.bootstrap-ignore`.
- Use `templates/copilot-quickstart.md` for onboarding new consumer repos.

---

## Deprecated assets

| Asset | Deprecated in favor of | Status | Notes |
| --- | --- | --- | --- |
| `scripts/bootstrap-copilot-config.sh` | `scripts/internal-sync-copilot-configs.py` | Deprecated — pending removal after migration window | See `DEPRECATION.md` for timeline. |
