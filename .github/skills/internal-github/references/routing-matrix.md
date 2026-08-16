# GitHub Routing Scenario Matrix

## Direct routes

| Request signal | Primary deliverable | Destination |
|---|---|---|
| Mono-repo versus multi-repo decision | Platform or operating-model choice | `/internal-github-strategic` |
| Organization ruleset design | Governance control design | `/internal-github-governance` |
| Runner fleet health | Operational evidence and continuity proof | `/internal-github-operations` |
| `.github/workflows/` deployment edit | Workflow behavior | `/internal-github-actions` |
| `.github/actions/` `action.yml` edit | Composite-action contract | `/internal-github-action-composite` |
| Non-empty diff or explicit read-only code target | Technical review findings | `/internal-review-code` |
| Merge readiness for one PR | Pull-request terminal state | `/internal-github-pr` |
| Current Copilot frontmatter behavior | Current-source platform research | `/internal-copilot-docs-research` |

## Collision rules

Choose by the primary deliverable when the same technical subject appears in
different work products:

| Collision | Destination | Decision rule |
|---|---|---|
| OIDC policy versus OIDC workflow YAML | `/internal-github-governance` versus `/internal-github-actions` | Route the trust or permission boundary to governance; route the workflow implementation to Actions. |
| Required-review policy versus readiness of one PR | `/internal-github-governance` versus `/internal-github-pr` | Route the repository control to governance; route the state of one pull request to PR. |
| Workflow failure versus runner-fleet health | `/internal-github-operations` | Route workflow-specific failure evidence and fleet-wide runner evidence to operations. |
| Reuse-pattern decision versus composite-action authoring | `/internal-github-actions` versus `/internal-github-action-composite` | Route the selection among inline, reusable-workflow, and composite options to Actions; route the concrete `action.yml` contract to composite. |
| Technical review versus PR readiness | `/internal-review-code` versus `/internal-github-pr` | Route technical findings to review; route current PR state, checks, reviews, merge, and terminal verification to PR. Findings do not establish readiness. |
| Caller workflow contract versus concrete action contract | `/internal-github-actions` versus `/internal-github-action-composite` | Route caller workflow events, jobs, permissions, reuse, and context to Actions; route concrete `action.yml` inputs, outputs, shell, compatibility, and documentation to composite. |

## Multi-deliverable sequencing

| Request | Sequence |
|---|---|
| Choose a repository model, define its ruleset, then prove rollout | `/internal-github-strategic` → `/internal-github-governance` → `/internal-github-operations` |
| Select a workflow reuse pattern, author the workflow, then validate a failed run | `/internal-github-actions` → `/internal-github-actions` → `/internal-github-operations` |
| Draft a PR body, verify required reviews, then confirm terminal state | `/internal-github-pr` for each PR deliverable in dependency order |
| Review a code diff, then verify readiness of its PR | `/internal-review-code` → `/internal-github-pr` |

## Near misses

| Request | Route |
|---|---|
| A ruleset change happens to be delivered in a pull request | `/internal-github-governance`; use `/internal-github-pr` only when the PR itself is a requested deliverable. |
| A workflow change requires a permission update | `/internal-github-actions` for workflow behavior and `/internal-github-governance` for the permission boundary. |
| A composite action is called from a reusable workflow | `/internal-github-action-composite` for the action contract and `/internal-github-actions` for the workflow contract. |
| A current Copilot or MCP fact informs another GitHub decision | `/internal-copilot-docs-research` for the fact, followed by the owner of the resulting deliverable. |
