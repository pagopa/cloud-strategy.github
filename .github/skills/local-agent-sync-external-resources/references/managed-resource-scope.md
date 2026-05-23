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
  `https://github.com/github/awesome-copilot/tree/4e4b34c48d3f50934a7a073aed0d05fd46e99b09/agents`
  (commit date: 2026-05-15)
- Skills:
  `https://github.com/github/awesome-copilot/tree/4e4b34c48d3f50934a7a073aed0d05fd46e99b09/skills`
  (commit date: 2026-05-15)
- Instructions:
  `https://github.com/github/awesome-copilot/tree/4e4b34c48d3f50934a7a073aed0d05fd46e99b09/instructions`
  (commit date: 2026-05-15)

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
- Instructions: `awesome-copilot-azure-devops-pipelines.instructions.md`;
  `awesome-copilot-go.instructions.md`;
  `awesome-copilot-kubernetes-manifests.instructions.md`;
  `awesome-copilot-shell.instructions.md`.

### `obra/superpowers`

Source:

- Skills:
  `https://github.com/obra/superpowers/tree/f2cbfbefebbfef77321e4c9abc9e949826bea9d7/skills`
  (release tag: v5.1.0)

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
  `https://github.com/hashicorp/agent-skills/tree/43ca9b0cde131e20a129c106bc9f6b6f9f1e5c9a/terraform/code-generation/skills`
  (commit date: 2026-05-11)

Managed skills:

- `terraform-search-import` -> `terraform-terraform-search-import`;
  `terraform-test` -> `terraform-terraform-test`.

### `mattpocock/skills`

Sources:

- Engineering skills:
  `https://github.com/mattpocock/skills/tree/e74f0061bb67222181640effa98c675bdb2fdaa7/skills/engineering`
  (commit date: 2026-05-13)
- Productivity skills:
  `https://github.com/mattpocock/skills/tree/e74f0061bb67222181640effa98c675bdb2fdaa7/skills/productivity`
  (commit date: 2026-05-13)

Managed skills:

- `caveman` -> `mattpocock-caveman`; `grill-me` -> `grill-me`.

Approved in-place overrides:

- `grill-me`: replay `grill-me-bulk-recommended-questions` after each refresh
  so the skill asks its initial question set as a dependency-ordered numbered
  list with recommendations accepted by default, while still surfacing
  contradictions, risks, and unresolved follow-up questions.

Retired upstream items that were extracted into internal owners are tracked in
the alert-only watchlist owned by `local-agent-sync-external-resources`.

### `openai/skills`

Sources:

- Curated skills:
  `https://github.com/openai/skills/tree/c25113bf4c64c8dba6bfe61acf06051d79aa43f6/skills/.curated`
  (commit date: 2026-05-12)
- System skills:
  `https://github.com/openai/skills/tree/c25113bf4c64c8dba6bfe61acf06051d79aa43f6/skills/.system`
  (commit date: 2026-05-12)
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

### `sickn33/antigravity-awesome-skills`

Source:

- Skills:
  `https://github.com/sickn33/antigravity-awesome-skills/tree/2e0c5a9cbf515a0611afcec73ef2a6644c4191e3/skills`
  (release tag: v11.3.0)

Managed skills:

- `api-design-principles` -> `antigravity-api-design-principles`;
  `aws-cost-optimizer` -> `antigravity-aws-cost-optimizer`;
  `cloudformation-best-practices` ->
  `antigravity-cloudformation-best-practices`; `golang-pro` ->
  `antigravity-golang-pro`; `grafana-dashboards` ->
  `antigravity-grafana-dashboards`; `kubernetes-architect` ->
  `antigravity-kubernetes-architect`; `network-engineer` ->
  `antigravity-network-engineer`.
