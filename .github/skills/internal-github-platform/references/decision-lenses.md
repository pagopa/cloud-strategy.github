# Decision Lenses

Use in decide mode. Activate only lenses that can change the recommendation
and name each active lens.

## Lens combinations

| Situation | Start with | Add only if needed |
| --- | --- | --- |
| Mono-repo versus multi-repo, or org layout | ownership, ruleset scope | blast radius, cost |
| Automation or integration choice | security, governance | runner model, blast radius |
| Copilot rollout or licensing | Copilot policy, cost | governance, compliance |
| Runner platform | runner model, operations | cost, continuity |
| High-risk workflow or release change | rollout and rollback, blast radius | operations, governance |

## Signals for another lens

- Spend or licensing could change the answer: add cost.
- Permissions, Apps, rulesets, OIDC, or environments change: add governance.
- Runner, audit, or validation burden changes: add operations.
- Delivery continuity or recovery changes: add continuity.
- Developer workflow or repository shape changes: add maintainability.

## Worked shapes

| Decision | Compare on |
|---|---|
| Mono-repo versus multi-repo | Code ownership, ruleset and CODEOWNERS scope, CI blast radius, release independence |
| Central versus delegated repository ownership | Who administers rulesets, smallest safe rollout unit |
| GitHub App versus `GITHUB_TOKEN` versus external integration | Trust boundary, permission surface, audit burden |
| Managed hosted runners versus fleet ownership | Queue time, cost, continuity, security isolation |
| Broad versus staged Copilot enablement | Policy controls, licensing cost, exception handling |
