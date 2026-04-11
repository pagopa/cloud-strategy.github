# Azure Operations Validation And Evidence

Use this reference when the base skill needs a deeper operational checklist.

## Preflight checklist

- confirm scope and rollout unit
- confirm rollback trigger and owner
- confirm monitoring, alerting, and logging signals for the affected surface
- confirm backup or recovery expectations when stateful services are involved
- confirm identity and policy assumptions before widening rollout

## Rollout validation

- validate the first safe unit before widening scope
- check both success signals and unexpected deny, drift, or connectivity regressions
- record what was actually observed versus what was only expected

## Post-rollout evidence

- audit trail for what changed
- evidence that preventive controls still allow intended operations
- evidence that Azure Monitor and Log Analytics still receive the expected signals
- evidence that restore or recovery assumptions were tested when relevant

## BC/DR note

BC/DR stays optional here as well.

Load it when the rollout affects continuity expectations, recovery posture, or business-critical platform capability.
