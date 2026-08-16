---
name: internal-github
description: Official entry point for any GitHub task. Routes every GitHub request to the right specialist - governance, operations, Actions workflows, composite actions, PR lifecycle, or Copilot platform research - or to /internal-github-strategic for high-level decision framing. Use for any GitHub request, scoped or ambiguous.
user-invocable: true
---

# Internal GitHub

Use this skill as the single explicit entry point for GitHub work. Classify
the requested deliverable, invoke the minimum owner set, and stop routing
after every requested deliverable has an owner.

## When to use

Use for any GitHub request, including a scoped implementation, an operational
check, a governance decision, a pull-request task, current-platform research,
or an ambiguous request whose deliverable is not yet clear.

## Destination table

| Destination | Primary deliverable |
|---|---|
| `/internal-github-strategic` | Platform or operating-model decision with option comparison, tradeoff analysis, or multi-lens framing |
| `/internal-github-governance` | Rulesets, permissions, Apps, Actions permissions, OIDC trust, secrets, environments, CODEOWNERS, or Copilot policy |
| `/internal-github-operations` | Actions health, runners, audit evidence, reporting, drift, preflight, rollout validation, or post-rollout proof |
| `/internal-github-actions` | Workflow authoring or debugging under `.github/workflows/`, including `workflow_call` and reuse-pattern selection |
| `/internal-github-action-composite` | Composite-action work under `.github/actions/`, including inputs, outputs, shell safety, tests, documentation, and compatibility |
| `/internal-review-code` | Technical review of a non-empty diff or explicit read-only code target, with conditional domain contributors by changed surface |
| `/internal-github-pr` | Pull-request creation, body updates, readiness, reviews, merge, or terminal-state verification |
| `/internal-copilot-docs-research` | Current Copilot or MCP platform behavior when freshness materially affects the answer |

## Classification algorithm

1. Identify the requested deliverable and the repository surface it changes or
   verifies.
2. Choose one primary destination from the table. Select the decision owner
   for platform or operating-model choices, the control owner for resulting
   policy design, and the implementation or evidence owner for concrete work.
3. Ask one focused question only when the deliverable cannot be inferred
   safely. Do not ask merely because a request mentions more than one domain.
4. Invoke the selected destination using its slash-prefixed name, with the
   deliverable and relevant evidence in the request.

Technical review of a non-empty diff or explicit read-only code target routes
to `/internal-review-code`. A request for PR readiness, merge, or terminal
state routes to `/internal-github-pr`; technical findings do not establish PR
readiness.

## Multi-deliverable sequencing

When independent deliverables are requested, assign each a primary owner and
invoke them in dependency order. A decision precedes its resulting control
design; a control design precedes rollout evidence; workflow behavior and
composite-action authoring remain separate implementation deliverables. Keep
each invocation focused on its own output.

## Completion criteria

- Every requested deliverable has exactly one primary owner.
- The selected owner is invoked with a slash-prefixed skill name.
- Any sequencing dependency is explicit and independently verifiable.
- Routing stops once all requested deliverables have an owner.

## Collision boundaries

- Technical review versus PR readiness: route findings and static contract
  evidence to `/internal-review-code`; route current PR state, checks, reviews,
  merge, and terminal verification to `/internal-github-pr`.
- Workflow failure versus runner health: route workflow-specific failure
  evidence and fleet-wide runner evidence to `/internal-github-operations`.
- Caller workflow contract versus concrete action contract: route events, jobs,
  permissions, reuse, and context to `/internal-github-actions`; route
  `action.yml` inputs, outputs, shell, compatibility, and documentation to
  `/internal-github-action-composite`.

When both technical review and PR readiness are explicitly requested, invoke
`/internal-review-code` before `/internal-github-pr`.
