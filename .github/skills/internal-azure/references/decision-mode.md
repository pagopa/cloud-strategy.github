# Azure Decision Mode

Use this reference when cost or recovery is material, or when two or more
viable Azure options remain.

## Lens activation signals

Activate only the lenses that can change the recommendation.

- Cost changes the recommendation: activate FinOps.
- Management groups, subscriptions, or connectivity layout changes: activate
  structure.
- RBAC, managed identity, or Policy behavior changes: activate governance.
- Monitoring, backup, or validation burden changes: activate operations.
- Critical platform capability depends on recovery posture: activate
  continuity.

FinOps and continuity apply even when only one option is viable. Route current
price data to `/awesome-copilot-azure-pricing`.

## BC/DR activation

Activate the BC/DR lens when the user asks about resilience, backup, recovery,
failover, RTO, RPO, Site Recovery, or regional continuity; when the decision
has clear continuity implications; or when the recommendation would otherwise
omit material recovery risk.

## Common lens combinations

| Situation | Start with | Add only when it changes the recommendation |
| --- | --- | --- |
| Landing-zone or platform-topology choice | structure, governance | FinOps, continuity, or operations |
| Identity or delegated-access choice | identity and access, governance | blast radius or compliance |
| Rollout across management groups or subscriptions | rollout and rollback, blast radius | operations or continuity |
| Cost-sensitive platform decision | FinOps, maintainability | operations or governance |
| Resilience-sensitive design | continuity, operations | FinOps or blast radius |

## Depth control

- Quick answer: one option is clearly better and the downside is local.
- Decision note: at least two viable options remain.
- Deep analysis: the question or risk profile justifies explicit context,
  options, active lenses, recommendation, and validation.

## Decision note

1. Decision statement: the Azure choice being made.
2. Assumptions: current state, constraints, ownership, and timeline.
3. Viable options: two or three realistic Azure paths.
4. Recommendation: the direction that best fits the assumptions.
5. Tradeoffs and blast radius: benefits, costs, and hard-to-reverse effects.
6. Reversibility: conditions for staged adoption or rollback.
7. Validation: current-fact checks, proof, and follow-up conditions.
