# .github Configuration

This directory is the source-side catalog for reusable GitHub Copilot customization assets maintained in `cloud-strategy.github`.

- `.github/copilot-instructions.md` is the primary detailed policy layer.
- Root [`AGENTS.md`](../AGENTS.md) is the thin bridge for routing, naming, discovery, and the pointer to exact path inventory.
- [`INVENTORY.md`](INVENTORY.md) is the exact path inventory for the live catalog.
- This README is an orientation guide for maintainers of the source catalog. It should describe the live on-disk catalog only.

## Live Catalog Summary

- Instructions: 17 total (`13 internal-*`, `4 awesome-copilot-*`)
- Prompts: 0 total
- Skills: 85 total (`45 internal-*`, `14 obra-*`, `9 awesome-copilot-*`, `8 antigravity-*`, `7 openai-*`, `2 terraform-*`)
- Agents: 12 total (`7 internal-*`, `5 awesome-copilot-*`)
- Scripts: 17 total
- Workflows: 1 total

## Structure

### Policy and governance files

| Path | Purpose |
| --- | --- |
| `copilot-instructions.md` | Primary detailed policy, validation baseline, routing model, and completion-report contract. |
| `INVENTORY.md` | Exact path inventory for live instructions, prompts, skills, and agents. |
| `copilot-code-review-instructions.md` | Review-specific severity and defect-first guidance. |
| `copilot-commit-message-instructions.md` | Commit message conventions. |
| `security-baseline.md` | Cross-cutting security bar for workflows and infrastructure changes. |
| `repo-profiles.yml` | Advisory consumer-repository profile catalog. |
| `DEPRECATION.md` | Lifecycle policy for retiring assets. |
| `CHANGELOG.md` | Source-side history of meaningful catalog changes. |
| `PULL_REQUEST_TEMPLATE.md` | PR section order for this repository. |
| `dependabot.yml` | Dependency update configuration for this source repository. |
| `obra-superpowers-source-of-truth.json` | Pinned upstream mapping contract for imported `obra-*` skills. |
| `.bootstrap-ignore` | Legacy compatibility artifact retained outside the primary sync workflow. |

### Instructions (`instructions/`)

Instructions are path-driven and auto-apply via `applyTo`.

- Repository-owned `internal-*` instructions: `internal-bash`, `internal-docker`, `internal-github-action-composite`, `internal-github-actions`, `internal-java`, `internal-json`, `internal-lambda`, `internal-makefile`, `internal-markdown`, `internal-nodejs`, `internal-python`, `internal-terraform`, `internal-yaml`
- Imported `awesome-copilot-*` instructions: `awesome-copilot-azure-devops-pipelines`, `awesome-copilot-go`, `awesome-copilot-kubernetes-manifests`, `awesome-copilot-shell`

Use instructions as automatic file-path guidance. Do not hardcode instruction references into prompts when `applyTo` already resolves the behavior.

### Prompts (`prompts/`)

No prompt files currently ship in the live catalog.

If prompt assets are reintroduced, they must stay aligned with real files under `instructions/`, `skills/`, and `scripts/`.

### Skills (`skills/`)

Skills are grouped into three functional lanes plus imported support families.

- `internal-*`: repository-owned tactical execution, governance, routing, review, project lanes, CI/CD, data registry, cloud policy, Docker, Terraform, PR authoring support, and provider skill families for AWS, Azure, GCP, and GitHub
- `obra-*`: strategic workflow support for brainstorming, planning, debugging, verification, worktree usage, and skill authoring
- Imported support families:
  - `awesome-copilot-*`
  - `antigravity-*`
  - `openai-*`
  - `terraform-*`

Some skill directories include support material beyond `SKILL.md`. Current live examples include:

- provider families with bundled references and UI metadata: `internal-aws-*`, `internal-azure-*`, `internal-gcp-*`, `internal-github-*`
- repository-owned support bundles such as `internal-agent-*`, `internal-change-impact-analysis`, `internal-cicd-workflow`, `internal-cloud-policy`, `internal-code-review`, `internal-copilot-*`, `internal-ddd`, `internal-docker`, `internal-oop-design-patterns`, `internal-performance-optimization`, `internal-pr-editor`, `internal-project-*`, `internal-script-*`, `internal-spring-boot-development`, `internal-sync-global-copilot-configs-into-repo`, and `internal-terraform`
- workflow packs with bundled references or helpers such as `obra-brainstorming`, `obra-requesting-code-review`, `obra-subagent-driven-development`, `obra-systematic-debugging`, `obra-test-driven-development`, `obra-using-superpowers`, `obra-writing-plans`, and `obra-writing-skills`
- imported or upstream-derived bundles such as `awesome-copilot-azure-devops-cli`, `awesome-copilot-azure-pricing`, `awesome-copilot-azure-role-selector`, `awesome-copilot-cloud-design-patterns`, `openai-docx`, `openai-gh-address-comments`, `openai-gh-fix-ci`, `openai-pdf`, `openai-skill-creator`, `openai-slides`, `openai-spreadsheet`, and `terraform-terraform-search-import`

Use [`INVENTORY.md`](INVENTORY.md) for the exact path inventory. Use root [`AGENTS.md`](../AGENTS.md) for bridge-level routing and discovery. Use this README for family-level orientation only.

### Agents (`agents/`)

See [`agents/README.md`](agents/README.md) for the selection guide.

- Canonical repository-owned operational agents: `internal-router`, `internal-fast-executor`, `internal-planning-leader`, `internal-review-guard`, `internal-critical-challenger`
- Repository-owned source-side sync and governance agents: `internal-sync-control-center`, `internal-sync-global-copilot-configs-into-repo`
- Imported support agents: `awesome-copilot-azure-principal-architect`, `awesome-copilot-critical-thinking`, `awesome-copilot-devils-advocate`, `awesome-copilot-devops-expert`, `awesome-copilot-plan`

The current repository-owned operating model is the internal router plus the four canonical internal owners. Do not document retired operational routes here.
Only `internal-router` actively routes between canonical owners; the four canonical owners stay boundary-driven and user-directed.

### Scripts and workflow

This table highlights the most commonly maintained source-side entrypoints rather than every helper under `.github/scripts/`.

| Path | Purpose |
| --- | --- |
| `scripts/internal-python-runner.sh` | Shared Bash bootstrap for local `.venv` setup and `requirements.txt` installation before running repository Python entrypoints. |
| `scripts/internal_yaml.py` | Shared repository-owned YAML and frontmatter helper used by internal Python automation. |
| `scripts/requirements.txt` | Local pinned dependency set for repository-owned Python scripts under `.github/scripts/`. |
| `scripts/internal-sync-copilot-configs.sh` | Supported sync planner and apply entrypoint for source-to-consumer Copilot alignment. |
| `scripts/internal-sync-copilot-configs.py` | Sync planner implementation used by the wrapper and source-side automation. |
| `scripts/report-copilot-usage.py` | Reporting entrypoint for Copilot catalog telemetry aggregation. |
| `workflows/terraform-pre-commit.yml` | Source repository workflow for Terraform-focused pre-commit checks. |

## Source-of-Truth Rules

- Trust real on-disk paths and [`INVENTORY.md`](INVENTORY.md) over remembered historical names. Use root [`AGENTS.md`](../AGENTS.md) for bridge-level routing and discovery.
- Keep `.github/copilot-instructions.md` as the normative policy layer and update it before root `AGENTS.md` when both must change.
- Treat this README as maintainer-facing orientation, not as the normative contract.
- Historical documents such as `../COPILOT_REVIEW.md` and older changelog entries may intentionally mention removed legacy assets. Do not use them as live catalog references.

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

### 🤖 Agents

- Include this section only when agents were used.
- State which agents were used and why they were relevant.

### 📘 Instructions

- Include this section only when instructions were used.
- State which instructions were used and why they mattered.

### 📝 Prompts

- Include this section only when prompts were used.
- State which prompts were used and why they were relevant.

### 🧩 Skills

- Include this section only when skills were used.
- State which skills were used and why they were relevant.

### 📦 Other Resources

- Include this section only when other resources were used.
- State which other resources were used and why they were relevant.
