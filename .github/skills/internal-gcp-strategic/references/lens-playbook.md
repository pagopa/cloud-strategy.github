# GCP Strategic Lens Playbook

Use this reference when the user wants more depth than the base skill should load by default.

## Common lens combinations

| Situation | Start with | Add only if needed |
| --- | --- | --- |
| Org or Shared VPC choice | organization-structure, governance | FinOps, BC/DR |
| Identity or workload access choice | identity and access, governance | blast radius, compliance |
| Rollout planning across folders or projects | rollout and rollback, blast radius | operations, BC/DR |
| Cost-sensitive platform decision | FinOps, maintainability | operations, governance |
| Resilience-sensitive design | BC/DR, operations | FinOps, blast radius |

## Signals that another lens should be suggested

- Cost could materially change the recommended option: suggest `FinOps`
- The decision changes org, folder, project, or Shared VPC layout: suggest `organization-structure`
- The choice changes IAM, workload identity, or Org Policy behavior: suggest `governance`
- The rollout adds monitoring, backup, inventory, or validation burden: suggest `operations`
- A failure would interrupt critical platform capability: suggest `BC/DR`

## Depth control

- Stay in `Quick answer` mode when one option is clearly better and the user asked a narrow question.
- Upgrade to `Decision note` when at least two viable options exist.
- Upgrade to `Deep analysis` only when the user asks for it or the risk profile justifies it.
