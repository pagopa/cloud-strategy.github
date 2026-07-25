# Azure Strategic Lens Playbook

Use this reference when the user wants more depth than the base skill should load by default.

## Common lens combinations

| Situation | Start with | Add only if needed |
| --- | --- | --- |
| Landing-zone or platform-topology choice | organization-structure, governance | FinOps, BC/DR |
| Identity or delegated access choice | identity and access, governance | blast radius, compliance |
| Rollout planning across management groups or subscriptions | rollout and rollback, blast radius | operations, BC/DR |
| Cost-sensitive platform decision | FinOps, maintainability | operations, governance |
| Resilience-sensitive design | BC/DR, operations | FinOps, blast radius |

## Signals that another lens should be suggested

- Cost could materially change the recommended option: suggest `FinOps`
- The decision changes management groups, subscriptions, or connectivity layout: suggest `organization-structure`
- The choice changes RBAC, managed identity, or Policy behavior: suggest `governance`
- The rollout adds monitoring, backup, or validation burden: suggest `operations`
- A failure would interrupt critical platform capability: suggest `BC/DR`

## Decision note pattern

Use this when the question is too consequential for a quick answer but does not need a full deep analysis.

1. Decision statement: what Azure choice is being made.
2. Assumptions: what current state, constraints, or timelines the recommendation depends on.
3. Viable options: usually two or three realistic Azure-local paths.
4. Recommendation: which option wins and why.
5. Tradeoffs and blast radius: what gets better, what gets harder, and what is hard to reverse.
6. Validation note: what current-fact check, proof, or next-owner handoff is still required.

## When to stay quick answer versus upgrade to a decision note

| Stay in `Quick answer` when | Upgrade to `Decision note` when |
| --- | --- |
| One option is clearly better and the downside is local | At least two Azure-local options are still viable |
| The choice does not alter the platform, identity, or recovery posture | The choice changes management groups, subscriptions, delegated access, or continuity expectations |
| The answer can stay within one lens without hiding material risk | A second lens changes the recommendation or the risk statement |
| Freshness is not the deciding factor | Current Azure behavior, service support, or limits could change the outcome |

## Depth control

- Stay in `Quick answer` mode when one option is clearly better and the user asked a narrow question.
- Upgrade to `Decision note` when at least two viable options exist.
- Upgrade to `Deep analysis` only when the user asks for it or the risk profile justifies it.
