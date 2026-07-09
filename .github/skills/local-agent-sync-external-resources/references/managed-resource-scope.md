# Managed Resource Scope

Use this reference when `local-sync-external-resources` needs the exact managed
upstream family map, normalized local ids, retained support-only posture, or
approved imported-override context without re-expanding that detail in the
wrapper agent.

## Ownership Posture

- `internal-*` is the default prefix for repository-owned resources in this
  standards repository.
- `local-*` is reserved for source-only sync tooling in this repository.
- Imported upstream resources keep their external-prefixed local ids unless an
  approved repository-owned replacement or managed normalization takes over.
- Imported assets are support depth by default. Prefer an `internal-*` owner
  only when routing, governance, terminology, output shape, safety
  expectations, or a missing owner requires it.
- Approved imported in-place overrides must stay registered in
  `references/imported-asset-overrides.yaml` and replayable through the paired
  scripts.

## Managed Families

### `github/awesome-copilot`

Sources:

- Agents:
  `https://github.com/github/awesome-copilot/tree/e986f49695491311df2774030ebe11efabd0fb77/agents`
  (commit date: 2026-07-03)
- Skills:
  `https://github.com/github/awesome-copilot/tree/e986f49695491311df2774030ebe11efabd0fb77/skills`
  (commit date: 2026-07-03)
- Retired instruction source:
  `https://github.com/github/awesome-copilot/tree/e986f49695491311df2774030ebe11efabd0fb77/instructions`
  (commit date: 2026-07-03; alert-only watchlist, not managed source scope)

Managed assets:

- Agents: none.
- Skills: `agentic-eval` -> `awesome-copilot-agentic-eval`;
  `azure-devops-cli` -> `awesome-copilot-azure-devops-cli`; `azure-pricing` ->
  `awesome-copilot-azure-pricing`; `azure-resource-health-diagnose` ->
  `awesome-copilot-azure-resource-health-diagnose`; `azure-role-selector` ->
  `awesome-copilot-azure-role-selector`; `cloud-design-patterns` ->
  `awesome-copilot-cloud-design-patterns`; `codeql` ->
  `awesome-copilot-codeql`; `dependabot` -> `awesome-copilot-dependabot`;
  `secret-scanning` -> `awesome-copilot-secret-scanning`.
Retired upstream instruction assets are tracked in the alert-only watchlist when
their content has a repository-owned replacement owner.

### `obra/superpowers`

Source:

- Skills:
  `https://github.com/obra/superpowers/tree/d884ae04edebef577e82ff7c4e143debd0bbec99/skills`
  (release tag: v6.1.1; commit date: 2026-07-02)

Managed skills:

- `brainstorming` -> `superpowers-brainstorming`;
  `dispatching-parallel-agents` -> `superpowers-dispatching-parallel-agents`;
  `executing-plans` -> `superpowers-executing-plans`;
  `finishing-a-development-branch` ->
  `superpowers-finishing-a-development-branch`;
  `receiving-code-review` -> `superpowers-receiving-code-review`;
  `requesting-code-review` -> `superpowers-requesting-code-review`;
  `subagent-driven-development` ->
  `superpowers-subagent-driven-development`;
  `systematic-debugging` -> `superpowers-systematic-debugging`;
  `test-driven-development` -> `superpowers-test-driven-development`;
  `using-git-worktrees` -> `superpowers-using-git-worktrees`;
  `using-superpowers` -> `superpowers-using-superpowers`;
  `verification-before-completion` ->
  `superpowers-verification-before-completion`; `writing-plans` ->
  `superpowers-writing-plans`.

### `hashicorp/agent-skills`

Source:

- Skills:
  `https://github.com/hashicorp/agent-skills/tree/339a113935812ad75c6ff90d418b739a021826d1/terraform/code-generation/skills`
  (commit date: 2026-05-28)

Managed skills:

- `terraform-search-import` -> `terraform-terraform-search-import`;
  `terraform-test` -> `terraform-terraform-test`.

### `mattpocock/skills`

Sources:

- Engineering skills:
  `https://github.com/mattpocock/skills/tree/efa058a349f5ce98b6115bf8b4e0d0ef9c310e0d/skills/engineering`
  (commit date: 2026-07-03)
- Productivity skills:
  `https://github.com/mattpocock/skills/tree/efa058a349f5ce98b6115bf8b4e0d0ef9c310e0d/skills/productivity`
  (commit date: 2026-07-03)

Managed skills:

- `code-review` -> `mattpocock-code-review`; `grill-me` -> `grill-me`;
  `handoff` -> `mattpocock-handoff` (productivity, compact conversation
  handoff for a fresh agent); `research` ->
  `mattpocock-research` (engineering, background-agent primary-source
  investigation).
- `caveman` -> `mattpocock-caveman` was retired from the managed catalog
  by explicit user scope reduction; see `references/external-watchlist.yaml`
  for the alert-only retired entry. Do not reimport `caveman` unless the
  user re-approves the retained import.

Approved in-place overrides:

- `grill-me`: replay `grill-me-bulk-recommended-questions` after each refresh
  so the skill asks its initial question set as a dependency-ordered numbered
  list with recommendations accepted by default, while still surfacing
  contradictions, risks, and unresolved follow-up questions.

Retired upstream items that were extracted into internal owners are tracked in
the alert-only watchlist owned by `local-agent-sync-external-resources`.

### `vercel-labs/skills`

Source:

- Skills:
  `https://github.com/vercel-labs/skills/tree/4ce6d48ac44c8b637db87b2102fea3baca719df1/skills`
  (commit date: 2026-07-06)

Managed skills:

- `find-skills` -> `vercel-find-skills` (helps users discover and install
  agent skills from the open agent skills ecosystem). The local prefix is
  `vercel`; keep this prefix narrow to the `vercel-labs/skills` family and
  do not reuse it for other imported families.

### `openai/skills`

Sources:

- Curated skills:
  `https://github.com/openai/skills/tree/49f948faa9258a0c61caceaf225e179651397431/skills/.curated`
  (commit date: 2026-06-23)
- System skills:
  `https://github.com/openai/skills/tree/49f948faa9258a0c61caceaf225e179651397431/skills/.system`
  (commit date: 2026-06-23)
- Retained document skill:
  `https://github.com/openai/skills/tree/45d05d75363abf13f99d09e899d61e07b8010685/skills/.curated/doc`
  (commit date: 2026-05-01; absent from current pinned upstream)
- Retained spreadsheet skill:
  `https://github.com/openai/skills/tree/e6afb0d74cc75d220df2faf3dd6c635c2dc6a108/skills/.curated/spreadsheet`
  (commit date: 2026-04-14; absent from current pinned upstream)
- Retained slides skill:
  `https://github.com/openai/skills/tree/e6afb0d74cc75d220df2faf3dd6c635c2dc6a108/skills/.curated/slides`
  (commit date: 2026-04-14; absent from current pinned upstream)

Managed skills:

- `gh-address-comments` -> `openai-gh-address-comments`; `gh-fix-ci` ->
  `openai-gh-fix-ci`; `skill-creator` -> `openai-skill-creator`; `pdf` ->
  `openai-pdf`.

Retained support-only office skills:

- `doc` -> `openai-docx`; `spreadsheet` -> `openai-spreadsheet`; `slides` ->
  `openai-slides`.

Approved in-place overrides:

- `openai-docx`: replay `openai-docx-executable-renderer` after each refresh so
  the bundled `scripts/render_docx.py` keeps a valid executable shebang and
  does not trip repository pre-commit validation.
- `openai-spreadsheet`: replay
  `openai-spreadsheet-structured-data-evidence-budget` after each refresh so
  large spreadsheet and tabular workflows keep the repository-specific
  structured-data evidence budget while preserving full-file correctness checks.

### `sickn33/antigravity-awesome-skills`

Source:

- Skills:
  `https://github.com/sickn33/antigravity-awesome-skills/tree/8946c6cdc8468183426d52f85054639b3e1844ae/skills`
  (release tag: v13.9.0; commit date: 2026-07-03)

Managed skills:

- `api-design-principles` -> `antigravity-api-design-principles`;
  `aws-cost-optimizer` -> `antigravity-aws-cost-optimizer`;
  `cloudformation-best-practices` ->
  `antigravity-cloudformation-best-practices`; `golang-pro` ->
  `antigravity-golang-pro`; `grafana-dashboards` ->
  `antigravity-grafana-dashboards`; `kubernetes-architect` ->
  `antigravity-kubernetes-architect`; `network-engineer` ->
  `antigravity-network-engineer`.
