# GCP Governance Guardrail Map

When the control surface or exception pattern needs deeper comparison, load this reference.

## Control patterns

| Need | Primary control | Acceptance criteria |
| --- | --- | --- |
| Limit risky services, locations, or defaults across many projects | Org Policy at org or folder scope | Preventive behavior and inheritance are visible |
| Grant people, groups, or workloads access to a project set | IAM binding model with explicit scope | Authorization follows ownership boundaries |
| Remove long-lived workload credentials | Workload identity federation | External trust and resource authorization are reviewed separately |
| Limit service-account sprawl and privilege creep | Purpose-built service-account boundaries plus scoped IAM | Workload identities remain attributable and reviewable |
| Standardize security posture | Org or folder guardrails with governed exceptions | Exceptions retain the same evidence and review discipline |

## Federation and service-account patterns

- External CI systems use federation with narrow project or folder IAM scope.
- Shared automation uses a purpose-built service account per automation boundary.
- Human operators use a time-bounded emergency path with explicit approval and logging.
- Identity mechanism, token trust, and resource authorization remain separate review points.

## Governed exception evidence

| Exception type | Control pattern | Required evidence |
| --- | --- | --- |
| Org Policy exception for a small project set | Scoped exception with reason, owner, and review date | Business reason, compensating controls, and revalidation date |
| Temporary service-account key use | Time-bounded exception with rotation and migration plan | Affected workload, owner, and closure deadline |
| Broader IAM grant during migration | Narrow temporary binding with rollback note | Approver, scope, expiration, and rollback condition |
