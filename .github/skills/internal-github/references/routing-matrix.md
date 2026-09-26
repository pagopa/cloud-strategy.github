# GitHub Routing Scenario Matrix

## Direct routes

| Request signal | Primary deliverable | Destination |
|---|---|---|
| Mono-repo versus multi-repo decision | Platform or operating-model choice | `/internal-github-strategic` |
| Organization ruleset design | Governance control design | `/internal-github-governance` |
| Runner fleet health | Operational evidence and continuity proof | `/internal-github-operations` |
| `.github/workflows/` or `.github/actions/**/action.yml` or `action.yaml` edit | GitHub Actions workflow or composite-action contract | `/internal-github-actions` |
| Non-empty diff or explicit read-only code target | Technical review findings | `/internal-review-code` |
| Merge readiness for one PR | Pull-request terminal state | `/internal-github-pr` |
| Current Copilot frontmatter behavior | Current-source platform research | `/internal-copilot-docs-research` |

## Collision rules

Choose by the primary deliverable when the same technical subject appears in
different work products. For workflow versus runner, technical review versus
PR readiness, and caller versus action collisions, apply the
[Collision boundaries](../SKILL.md#collision-boundaries) in the skill.

| Collision | Destination | Decision rule |
|---|---|---|
| OIDC policy versus OIDC workflow YAML | `/internal-github-governance` versus `/internal-github-actions` | Route the trust or permission boundary to governance; route the workflow implementation to Actions. |
| Required-review policy versus readiness of one PR | `/internal-github-governance` versus `/internal-github-pr` | Route the repository control to governance; route the state of one pull request to PR. |
| Reuse-pattern decision versus composite-action authoring | `/internal-github-actions` | Keep both deliverables under Actions; use the workflow reuse rules for the selection and the composite-action rules for the concrete `action.yml` contract. |

## Multi-deliverable sequencing

| Request | Sequence |
|---|---|
| Choose a repository model, define its ruleset, then prove rollout | `/internal-github-strategic` → `/internal-github-governance` → `/internal-github-operations` |
| Select a workflow or composite reuse pattern, author the Actions surface, then validate a failed run | `/internal-github-actions` for reuse selection and authoring → `/internal-github-operations` |
| Draft a PR body, verify required reviews, then confirm terminal state | `/internal-github-pr` for each PR deliverable in dependency order |
| Review a code diff, then verify readiness of its PR | `/internal-review-code` → `/internal-github-pr` |

## Near misses

| Request | Route |
|---|---|
| A ruleset change happens to be delivered in a pull request | `/internal-github-governance`; use `/internal-github-pr` only when the PR itself is a requested deliverable. |
| A workflow change requires a permission update | `/internal-github-actions` for workflow behavior and `/internal-github-governance` for the permission boundary. |
| A composite action is called from a reusable workflow | `/internal-github-actions` for both the action and workflow contracts; keep the two contract surfaces explicit within that skill. |
| A current Copilot or MCP fact informs another GitHub decision | `/internal-copilot-docs-research` for the fact, followed by the owner of the resulting deliverable. |
