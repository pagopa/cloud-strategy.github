# AWS Decision Shapes

Load this reference for a decision note. Use the output modes in `SKILL.md`;
this file adds AWS-specific framing only.

## When to upgrade from a quick answer

| Stay in a quick answer when | Write a decision note when |
| --- | --- |
| One option is clearly better and the downside is local | Two or more AWS options stay viable |
| The choice does not change organization, trust, or recovery posture | The choice changes account layout, delegated access, or continuity expectations |
| Freshness does not decide the outcome | Current AWS behavior, support boundaries, or limits could change the outcome |

## Landing zone and control plane

| Situation | Frame first | Recommendation shape |
| --- | --- | --- |
| New multi-account platform with central controls | Structure, governance | Compare a thin management account plus delegated administrators against a more centralized operating model; state the smallest safe rollout unit |
| Single-account estate moving into Organizations | Structure, blast radius | Focus on migration order, shared-services placement, and how guardrails land without locking out current operators |
| Control Tower versus a custom Organizations and StackSets landing zone | Governance, operations | State what managed controls and account vending buy, what flexibility is lost, the landing-zone version constraints, and which current facts need checking |

## Identity and delegated access

| Situation | Frame first | Recommendation shape |
| --- | --- | --- |
| A central team runs an integrated service day to day | Identity, governance | Compare delegated administrator patterns against management-account operation; state trust and audit implications |
| Workload teams need cross-account delivery access | Identity, blast radius | Compare broad roles against environment-scoped roles; state the rollback impact if trust is too wide |
| The federation model is still open | Governance, compliance | Stay at trust-boundary and operating-model level, not IdP implementation detail |

## Cost-sensitive platform choices

| Situation | Frame first | Recommendation shape |
| --- | --- | --- |
| Shared services could live centrally or per account | Cost, operations | Compare central efficiency against tenant isolation and operational burden; say when duplication is worth the spend |
| Multi-region posture is considered mainly for resilience | Cost, continuity | State the continuity target (RTO, RPO) before recommending the extra cost |
| Organization-wide baseline tooling is under review | Cost, maintainability | Compare managed-service convenience against steady-state ownership cost |

Route detailed spend analysis to `/antigravity-aws-cost-optimizer`.
