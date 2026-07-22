# GitHub Routing Scenario Matrix

## Fallback-positive cases

| Scenario | Why no primary owner |
|---|---|
| Underspecified cross-domain GitHub problem mixing governance, operations, and workflow authoring with no clear primary deliverable | The request names multiple GitHub domains but does not identify which deliverable takes priority. |
| GitHub platform question asking which lane should own the work without naming governance, operations, actions, composite, PR, or Copilot research | The user has not selected a domain; the fallback must clarify the lane before any specialist can engage. |
| Broad GitHub adoption review where the user wants a general health assessment across all domains | No single specialist owns a cross-domain health review; the fallback selects the minimum set. |

## Direct-specialist negative cases

| Scenario | Direct owner | Reason |
|---|---|---|
| Ruleset, branch protection, repository or organization permissions, GitHub Apps permissions, OIDC, secrets, environments, or Copilot governance | `internal-github-governance` | The deliverable is a guardrail or permission boundary. |
| Actions health, runner operations, audit-log review, reporting, drift, preflight, or post-rollout validation | `internal-github-operations` | The deliverable is operational evidence or continuity proof. |
| Workflow authoring under `.github/workflows/` or reusable workflow design | `internal-github-actions` | The deliverable is workflow behavior. |
| Composite action authoring under `.github/actions/` or contract compatibility | `internal-github-action-composite` | The deliverable is the reusable step unit. |
| PR creation, body, merge readiness, merge method, or terminal-state verification | `internal-github-pr` | The deliverable is PR lifecycle evidence. |
| Current GitHub Copilot or MCP platform behavior verification | `internal-copilot-docs-research` | The deliverable is current-source research. |

## Multi-domain primary-owner cases

| Scenario | Primary owner | Secondary | Reason |
|---|---|---|---|
| Org or repo-model decision with later ruleset work | `internal-github-governance` | `internal-github-operations` | The first deliverable is placement; ruleset validation follows once the model is settled. |
| Ruleset rollout evidence | `internal-github-governance` | `internal-github-operations` | The first deliverable is governance design; operations validates the rollout. |
| Workflow permission detail | `internal-github-actions` or `internal-github-governance` | depends on deliverable | Choose `internal-github-actions` when the deliverable is workflow behavior; choose `internal-github-governance` when the deliverable is the permission boundary. |

## Review rule

Prefer a direct specialist whenever a reasonable reviewer can name one primary owner from the request itself. Activate the fallback only when the request does not identify a primary owner and clarification is required before a specialist can engage.
