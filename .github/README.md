# .github Configuration

This directory is the source-side catalog for reusable GitHub Copilot customization assets maintained in `cloud-strategy.github`.

- `.github/copilot-instructions.md` is the primary detailed policy layer.
- Root [`AGENTS.md`](../AGENTS.md) is the strategic entrypoint, precedence anchor, and bridge for operational ownership, naming, discovery, and the pointer to exact path inventory.
- [`INVENTORY.md`](INVENTORY.md) is the exact path inventory for the live catalog.
- This README is an orientation guide for maintainers of the source catalog. It should describe the live on-disk catalog only.

## Live Catalog Summary

- Instructions: 17 total (`13 internal-*`, `4 awesome-copilot-*`)
- Skills: 85 total (`45 internal-*`, `14 obra-*`, `9 awesome-copilot-*`, `8 antigravity-*`, `7 openai-*`, `2 terraform-*`)
- Agents: 7 total (`7 internal-*`)
- Scripts: 21 tracked files
- Workflows: 1 total

## Structure

### Policy and governance files

| Path | Purpose |
| --- | --- |
| `copilot-instructions.md` | Primary detailed policy, validation baseline, direct-entry operating model, and completion-report contract. |
| `INVENTORY.md` | Exact path inventory for live instructions, skills, and agents. |
| `copilot-code-review-instructions.md` | Review-specific severity and defect-first guidance. |
| `copilot-commit-message-instructions.md` | Commit message conventions. |
| `security-baseline.md` | Cross-cutting security bar for workflows and infrastructure changes. |
| `repo-profiles.yml` | Advisory consumer-repository profile catalog. |
| `DEPRECATION.md` | Lifecycle policy for retiring assets. |
| `CHANGELOG.md` | Source-side history of meaningful catalog changes. |
| `PULL_REQUEST_TEMPLATE.md` | PR section order for this repository. |
| `dependabot.yml` | Dependency update configuration for this source repository. |

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
- repository-owned support bundles such as `internal-agent-*`, `internal-change-impact-analysis`, `internal-github-actions`, `internal-cloud-policy`, `internal-code-review`, `internal-github-action-composite`, `internal-copilot-*`, `internal-ddd`, `internal-docker`, `internal-kubernetes`, `internal-kubernetes-deployment`, `internal-oop-design-patterns`, `internal-performance-optimization`, `internal-pr-editor`, `internal-project-*`, `internal-script-*`, `internal-spring-boot-development`, `internal-sync-*`, and `internal-terraform`
- workflow packs with bundled references or helpers such as `obra-brainstorming`, `obra-requesting-code-review`, `obra-subagent-driven-development`, `obra-systematic-debugging`, `obra-test-driven-development`, `obra-using-superpowers`, and `obra-writing-plans`
- imported or upstream-derived bundles such as `awesome-copilot-agentic-eval`, `awesome-copilot-azure-devops-cli`, `awesome-copilot-azure-pricing`, `awesome-copilot-azure-role-selector`, `awesome-copilot-cloud-design-patterns`, `openai-docx`, `openai-gh-address-comments`, `openai-gh-fix-ci`, `openai-pdf`, `openai-skill-creator`, `openai-slides`, `openai-spreadsheet`, `terraform-terraform-search-import`, and `terraform-terraform-test`

Use [`INVENTORY.md`](INVENTORY.md) for the exact path inventory. Use root [`AGENTS.md`](../AGENTS.md) for bridge-level routing and discovery. Use this README for family-level orientation only.

### Agents (`agents/`)

See [`agents/README.md`](agents/README.md) for the selection guide.

- Canonical repository-owned operational agents: `internal-delivery-operator`, `internal-planning-leader`, `internal-review-guard`, `internal-critical-master`
- Repository-owned source-side sync and governance agents: `internal-sync-external-resources`, `internal-sync-global-copilot-configs-into-repo`
- No imported support agents currently ship in the live catalog.

The current repository-owned operating model uses direct entry to the four canonical internal owners. When the right owner is unclear, default to `internal-planning-leader`. Do not document retired operational routes here.

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
- Keep `.github/copilot-instructions.md` as the normative policy layer and update it before root `AGENTS.md` when both must change.
- Treat this README as maintainer-facing orientation, not as the normative contract.
- Historical documents and older changelog entries may intentionally mention removed legacy assets. Do not use them as live catalog references.

## Maintenance Workflow

1. Inspect the real target files first.
2. Update the relevant asset under `.github/`.
3. If routing, naming, discovery, or inventory changed, refresh root `AGENTS.md` and `.github/INVENTORY.md`.
4. Run the repository checks that currently exist for the touched assets.
5. Update `CHANGELOG.md` for meaningful `.github/` changes.

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
