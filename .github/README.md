# .github Configuration

This directory is the source-side catalog for reusable GitHub Copilot customization assets maintained in `cloud-strategy.github`.

- Root [`AGENTS.md`](../AGENTS.md) is the strategic entrypoint, precedence anchor, bridge for operational ownership, and home for compact AI configuration editing and fixed-load token-budget guidance.
- `.github/copilot-instructions.md` is the compact repo-wide Copilot projection for native Copilot flows.
- [`INVENTORY.md`](INVENTORY.md) is the exact path inventory for the live catalog.
- This README is an orientation guide for maintainers of the source catalog. It should describe the live on-disk catalog only.

## Live Catalog Summary

- Use [`INVENTORY.md`](INVENTORY.md) for the exact live counts and paths.
- Use `scripts/build_inventory.sh` when you need to rebuild or verify the generated inventory from filesystem state.
- This README intentionally avoids hand-maintained totals so orientation does not drift from the generated catalog.

## Structure

### Policy and governance files

| Path | Purpose |
| --- | --- |
| `copilot-instructions.md` | Compact Copilot-native projection of repo-wide policy, validation expectations, direct-entry operating model, and completion-report contract. |
| `INVENTORY.md` | Exact path inventory for live instructions, skills, and agents. |
| `copilot-code-review-instructions.md` | Review-specific severity and defect-first guidance. |
| `copilot-commit-message-instructions.md` | Commit message conventions. |
| `security-baseline.md` | Cross-cutting security bar for workflows and infrastructure changes. |
| `repo-profiles.yml` | Advisory consumer-repository profile catalog. |
| `DEPRECATION.md` | Lifecycle policy for retiring assets. |
| `CHANGELOG.md` | Source-side history of meaningful catalog changes. |
| `PULL_REQUEST_TEMPLATE.md` | PR section order for this repository. |
| `dependabot.yml` | Dependency update configuration for GitHub Actions, script requirements, and pre-commit hooks in this source repository. |

### Instructions (`instructions/`)

Instructions are path-driven and auto-apply via `applyTo`.

- Repository-owned `internal-*` instructions: `internal-bash`, `internal-docker`, `internal-github-action-composite`, `internal-github-actions`, `internal-java`, `internal-json`, `internal-lambda`, `internal-makefile`, `internal-markdown`, `internal-nodejs`, `internal-python`, `internal-terraform`, `internal-yaml`
- Imported `awesome-copilot-*` instructions: `awesome-copilot-azure-devops-pipelines`, `awesome-copilot-go`, `awesome-copilot-kubernetes-manifests`, `awesome-copilot-shell`

Use instructions as automatic file-path guidance. Do not restate path-driven behavior in skills when `applyTo` already resolves it.

### Skills (`skills/`)

Skills are grouped into three functional lanes plus imported support families.

- `internal-*`: repository-owned governance, ownership, review, execution, project, sync, platform, and provider skill families for AWS, Azure, GCP, and GitHub
- `obra-*`: strategic workflow support for brainstorming, planning, debugging, verification, worktree usage, and skill authoring
- Imported support families:
  - `awesome-copilot-*`
  - `antigravity-*`
  - `openai-*`
  - `terraform-*`

Some skill directories include support material beyond `SKILL.md`. Current live examples include:

- provider families with bundled references and UI metadata: `internal-aws-*`, `internal-azure-*`, `internal-gcp-*`, `internal-github-*`
- repository-owned support bundles such as `internal-agent-*`, `internal-change-impact-analysis`, `internal-github-actions`, `internal-github-pr`, `internal-cloud-policy`, `internal-code-review`, `internal-github-action-composite`, `internal-copilot-*`, `internal-ddd`, `internal-docker`, `internal-kubernetes`, `internal-kubernetes-deployment`, `internal-oop-design-patterns`, `internal-performance-optimization`, `internal-project-*`, `internal-script-*`, `internal-spring-boot-development`, `internal-sync-*`, and `internal-terraform`
- workflow packs with bundled references or helpers such as `obra-brainstorming`, `obra-requesting-code-review`, `obra-subagent-driven-development`, `obra-systematic-debugging`, `obra-test-driven-development`, `obra-using-superpowers`, and `obra-writing-plans`
- imported or upstream-derived bundles such as `awesome-copilot-agentic-eval`, `awesome-copilot-azure-devops-cli`, `awesome-copilot-azure-pricing`, `awesome-copilot-azure-role-selector`, `awesome-copilot-cloud-design-patterns`, `openai-docx`, `openai-gh-address-comments`, `openai-gh-fix-ci`, `openai-pdf`, `openai-skill-creator`, `openai-slides`, `openai-spreadsheet`, `terraform-terraform-search-import`, and `terraform-terraform-test`

Use [`INVENTORY.md`](INVENTORY.md) for the exact path inventory. Use root [`AGENTS.md`](../AGENTS.md) for bridge-level routing and discovery. Use this README for family-level orientation only.

### Knowledge docs (`../docs/`)

| Path | Purpose |
| --- | --- |
| `../docs/01-architecture.md` | Repository-specific architecture contract for boundaries, components, flows, and validation surfaces. |
| `../docs/02-repository-context.md` | Descriptive local context equivalent to non-policy runtime context when manually assembled. |
| `../docs/03-ai-runtime-operating-model.md` | Source-managed guidance for how Copilot, Codex, ChatGPT, and other assistants consume the AI customization assets. |

Keep token-budget estimates in root [`AGENTS.md`](../AGENTS.md); this README intentionally does not duplicate those counts.

### Prompts (`prompts/`)

Prompt files are parameterized entrypoints for repeatable advisory or orchestration starts. Use them when an operator needs a structured kickoff package rather than always-on policy or a reusable skill body.

- `internal-mega-review`: general advisor-only mega review for one or more repositories; writes retained English review artifacts under `tmp/`.
- `internal-ai-resources-review`: focused review for the AI resource control plane itself, including agents, skills, instructions, prompts, scripts, docs, memory, inventory, and governance drift.
- `internal-agent-plan-next-step`, `internal-agent-review-next-actions`, and `internal-agent-pressure-test-plan`: compact planning, review, and pressure-test entrypoints aligned with the gateway wrapper lanes.
- `internal-sync-plan` and `internal-architecture-md-creator`: targeted prompts for sync planning and architecture contract refresh work.

Prefer `internal-ai-resources-review` when the subject is the repository's AI catalog. Prefer `internal-mega-review` when the target is a broader repository review outside the catalog-governance surface.

### Agents (`agents/`)

See [`agents/README.md`](agents/README.md) for the selection guide.

- Canonical repository-owned gateway agents: `internal-gateway-operational-flow`, `internal-gateway-critical-master`, `internal-gateway-simple-task`
- Deprecated compatibility operational agents: `internal-delivery-operator`, `internal-planning-leader`, `internal-review-guard`, `internal-critical-master`
- Repository-owned source-side sync and governance agents: `local-sync-external-resources`, `local-sync-global-copilot-configs-into-repo`
- No imported support agents currently ship in the live catalog.

The current repository-owned operating model uses direct entry to the three gateway wrappers. When the right owner is unclear, default to `internal-gateway-operational-flow`. Deprecated compatibility wrappers must stay non-canonical during the deprecation window.

### Scripts and workflow

This table highlights the most commonly maintained source-side entrypoints rather than every tracked helper under `.github/scripts/`.

| Path | Purpose |
| --- | --- |
| `scripts/run.sh` | Shared wrapper that resolves the canonical repository Python entrypoints and runs them with the local script environment. |
| `scripts/audit_copilot_catalog.sh` | Wrapper entrypoint for source-side catalog audit runs. |
| `scripts/build_inventory.sh` | Wrapper entrypoint for rebuilding or checking `.github/INVENTORY.md` from filesystem state. |
| `scripts/check_catalog_consistency.sh` | Wrapper entrypoint for aggregated catalog consistency checks, including optional token-risk analysis. |
| `scripts/detect_token_risks.sh` | Wrapper entrypoint for focused token-budget and overlap risk analysis. |
| `scripts/sync_copilot_catalog.sh` | Supported sync planner and apply entrypoint for source-to-consumer Copilot alignment. |
| `scripts/validate_internal_skills.py` | Validates repository-owned internal skill metadata, local references, and token hygiene. |
| `scripts/requirements.txt` | Local pinned dependency set for repository-owned Python scripts under `.github/scripts/`. |
| `workflows/_pre-commit.yml` | Source repository workflow for repository-wide pre-commit checks. |

The matching `.py` entrypoints and `scripts/lib/*.py` modules are part of the same tracked script catalog and stay aligned with these wrappers.

## Source-of-Truth Rules

- Trust real on-disk paths and [`INVENTORY.md`](INVENTORY.md) over remembered historical names. Use root [`AGENTS.md`](../AGENTS.md) for bridge-level routing and discovery.
- Keep root [`AGENTS.md`](../AGENTS.md) as the strategic bridge. When a repository-wide default changes, update `AGENTS.md` first, then `.github/copilot-instructions.md`, then downstream orientation surfaces.
- Treat this README as maintainer-facing orientation, not as the normative contract.
- Historical documents and older changelog entries may intentionally mention removed legacy assets. Do not use them as live catalog references.

## Maintenance Workflow

1. Inspect the real target files first.
2. Update the relevant asset under `.github/`.
3. If routing, naming, or repository-wide defaults changed, update root `AGENTS.md` first and then refresh `.github/copilot-instructions.md`.
4. Refresh `.github/INVENTORY.md` when the live catalog changed, and update this README only when orientation text still needs adjustment.
5. Run the repository checks that currently exist for the touched assets.
6. Update `CHANGELOG.md` for meaningful `.github/` changes.

## Completion Report Contract

Completed operations must end with a concise recap.

### ✅ Outcome

- Summarize the completed operation and any relevant validation status or blockers.
- Keep this section concise by default.
- If more detail is available, offer it as an optional follow-up instead of appending every detail block automatically.
- The offer should support number-only replies, for example `1 = resources used`, `2 = files changed`, `3 = validations`, `4 = full detail`.

### 🤖 Agents

- Include this section only when agents were used and the user asked for the detail, or when a narrower scoped contract requires inline disclosure.
- State which agents were used and why they were relevant.

### 📘 Instructions

- Include this section only when instructions were used and the user asked for the detail, or when a narrower scoped contract requires inline disclosure.
- State which instructions were used and why they mattered.

### 🧩 Skills

- Include this section only when skills were used and the user asked for the detail, or when a narrower scoped contract requires inline disclosure.
- State which skills were used and why they were relevant.

### 📦 Other Resources

- Include this section only when other resources were used and the user asked for the detail, or when a narrower scoped contract requires inline disclosure.
- State which other resources were used and why they were relevant.
