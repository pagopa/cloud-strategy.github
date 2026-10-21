# Azure Operations

Use this reference for preflight, observability, rollout evidence, recovery
proof, and operational reporting.

## Preflight checklist

- Confirm scope, rollout unit, owner, and rollback trigger.
- Confirm monitoring, alerting, and logging signals for the affected surface.
- Confirm identity and policy assumptions before widening rollout.
- Confirm backup or recovery expectations for stateful services.

## Observation and rollout evidence

- Validate the first safe unit before widening scope.
- Check success signals alongside deny, drift, and connectivity regressions.
- Record observed behavior separately from expected behavior.
- Tie monitoring and reporting to the affected control-plane surface.
- Preserve the audit trail for the change and the widening decision.

## Staged rollout

| Change | Start with | Collect before widening |
| --- | --- | --- |
| New management-group branch | One low-risk subscription family | Inheritance behavior, policy scope, monitoring presence, and rollback-owner confirmation. |
| Landing-zone baseline update | One landing zone or environment slice | Connectivity, automation, alerting, and rollback behavior. |
| Platform subscription introduction | One shared capability with named consumers | Ownership, dependencies, and routing impact. |
| Region or residency split | One workload set with explicit fallback | Connectivity, sovereignty, and continuity assumptions. |
| Identity, RBAC, or Policy rollout | First management group or subscription set | Intended operations still succeed; deny and drift regressions investigated. |
| Broad subscription or region expansion | Prior wave completed | Prior-wave observations, investigated regressions, and escalation readiness. |

## Azure Monitor and Log Analytics signals

| Surface | Signals | Confirmation |
| --- | --- | --- |
| Identity or RBAC rollout | Sign-in or activity signals, denied-action evidence, successful intended operations | Access still permits intended work and exposes regressions. |
| Policy rollout | Compliance state, remediation outcome, and scoped exceptions | Guardrails apply as expected without unintended drift. |
| Platform topology or shared services | Health, logs, and alert continuity | Core visibility and routing remain available. |

## Recovery proof

Treat backup posture, restore viability, and continuity exercises as distinct
proof paths.

| Evidence need | Proof | What it establishes |
| --- | --- | --- |
| Backup success | Protected-resource inventory, policy attachment, and recent job success | Backup posture exists for the scoped resource. |
| Restore proof | Restore exercise, observed recovery time, and post-recovery integrity check | Recovery is viable for the tested scope. |
| DR exercise | Site Recovery or equivalent continuity exercise for the scoped service | Continuity posture is credible under the tested scenario. |
