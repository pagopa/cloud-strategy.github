# Azure Strategic Lens Playbook

Use this reference for lens combinations, depth selection, and decision-note
structure.

## Common lens combinations

| Situation | Start with | Add only when it changes the recommendation |
|---|---|---|
| Landing-zone or platform-topology choice | organization-structure, governance | FinOps, continuity, or operations |
| Identity or delegated-access choice | identity and access, governance | blast radius or compliance |
| Rollout across management groups or subscriptions | rollout and rollback, blast radius | operations or continuity |
| Cost-sensitive platform decision | FinOps, maintainability | operations or governance |
| Resilience-sensitive design | continuity, operations | FinOps or blast radius |

## Lens activation signals

- Cost changes the recommendation: activate FinOps.
- Management groups, subscriptions, or connectivity layout changes: activate
  organization-structure.
- RBAC, managed identity, or Policy behavior changes: activate governance.
- Monitoring, backup, or validation burden changes: activate operations.
- Critical platform capability depends on recovery posture: activate continuity.

## BC/DR activation

Activate the BC/DR lens when the user asks about resilience, backup, recovery,
failover, RTO, RPO, Site Recovery, or regional continuity; when the decision
has clear continuity implications; or when the recommendation would otherwise
omit material recovery risk.

## Decision note pattern

1. Decision statement: the Azure choice being made.
2. Assumptions: current state, constraints, and timeline.
3. Viable options: two or three realistic Azure-local paths.
4. Recommendation: the direction that best fits the assumptions and tradeoff.
5. Tradeoffs and blast radius: benefits, costs, and hard-to-reverse effects.
6. Validation note: current-fact checks, proof, and follow-up conditions.

## Depth control

- Stay in quick-answer mode when one option is clearly better and downside is
  local.
- Use decision-note mode when at least two viable options remain.
- Use deep-analysis mode when the question or risk profile justifies explicit
  context, options, active lenses, recommendation, and validation.
