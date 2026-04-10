# GitHub Operations Validation And Evidence

Use this reference when the base skill needs a deeper operational checklist.

## Preflight checklist

- confirm scope and rollout unit
- confirm rollback trigger and owner
- confirm runner, workflow, and audit signals for the affected surface
- confirm permission and environment assumptions before widening rollout
- confirm reporting or export surfaces needed for follow-up evidence

## Rollout validation

- validate the first safe unit before widening scope
- check both success signals and unexpected permission, runner, or release regressions
- record what was actually observed versus what was only expected

## Post-rollout evidence

- audit trail for what changed
- evidence that intended workflows still run with the expected permissions
- evidence that runner capacity and health still match the operating assumptions
- evidence that audit or reporting surfaces still describe the intended state

## Continuity note

Continuity stays optional here as well.

Load it when the rollout affects build, release, or repository continuity expectations.
