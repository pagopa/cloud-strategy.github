# GitHub Strategic Lens Playbook

Use this reference when the user wants more depth than the base skill should load by default.

## Common lens combinations

| Situation | Start with | Add only if needed |
| --- | --- | --- |
| Enterprise or repo-model choice | governance, maintainability | FinOps, BC/DR |
| Automation or integration choice | security, governance | runner model, blast radius |
| Copilot rollout or licensing choice | Copilot, FinOps | governance, compliance |
| Runner-platform decision | runner model, operations | FinOps, BC/DR |
| High-risk workflow or release change | rollout and rollback, blast radius | operations, governance |

## Signals that another lens should be suggested

- Spend or licensing could materially change the recommendation: suggest `FinOps`
- The choice changes permissions, Apps, rulesets, OIDC, or environments: suggest `governance`
- The rollout adds runner, audit, or validation burden: suggest `operations`
- The decision changes delivery continuity or recovery posture: suggest `BC/DR`
- The choice materially affects developer workflow or repo shape: suggest `maintainability`

## Depth control

- Stay in `Quick answer` mode when one option is clearly better and the user asked a narrow question.
- Upgrade to `Decision note` when at least two viable options exist.
- Upgrade to `Deep analysis` only when the user asks for it or the risk profile justifies it.
