# GCP Governance

Org Policy, IAM policy composition, perimeters, workload identity,
privileged access, tags, and governed exceptions for Google Cloud. Rows with a
source were verified on 2026-09-27; recheck them when they drive a decision.

## Policy composition

IAM evaluates deny policies before allow policies. The layers compose; none
replaces another.

| Layer | Attached to | Effect | Does not |
| --- | --- | --- | --- |
| Allow policy | Organization, folder, project, resource | Grants roles | Remove access granted elsewhere in the hierarchy |
| Deny policy | Organization, folder, or project; inherited downward | Blocks listed permissions regardless of allow grants | Cover every permission; only supported permissions can be denied; conditions use resource tags only ([deny](https://docs.cloud.google.com/iam/docs/deny-overview)) |
| Principal Access Boundary (PAB) | Principal set (organization, folder, project, workforce or workload pool) | Limits which resources a principal is eligible to reach | Grant access; block permissions outside its enforcement version; fails closed on evaluation error ([PAB](https://docs.cloud.google.com/iam/docs/principal-access-boundary-policies)) |
| Org Policy | Organization, folder, project | Constrains resource configuration | Grant or remove IAM permissions |
| VPC Service Controls | Service perimeter around projects | Blocks data movement across the perimeter for supported services | Replace IAM; protect unsupported services |

PAB rules:

- PAB policies are additive: a principal is eligible for the union of all
  bound policies.
- Pin an enforcement version. `latest` can remove access without warning.
- Keep a principal bound to at least one PAB policy while narrowing;
  removing all bindings makes it eligible for every resource.

## Org Policy

| Topic | Rule |
| --- | --- |
| Constraint families | Managed (`*.managed.*`), legacy managed, and custom constraints ([constraints](https://docs.cloud.google.com/organization-policy/reference/org-policy-constraints)) |
| Dry-run | Supported only for custom, managed, and four legacy constraints: `gcp.restrictServiceUsage`, `gcp.restrictEndpointUsage`, `gcp.restrictTLSVersion`, and the TLS cipher suite restriction ([test policies](https://docs.cloud.google.com/organization-policy/test-policies)) |
| Legacy constraint without dry-run | Prefer the managed equivalent when it exists, for example `iam.managed.disableServiceAccountKeyCreation` for `iam.disableServiceAccountKeyCreation`; otherwise stage on one folder or project set |
| Simulation | Policy Simulator for Organization Policy tests changes; some constraints do not support simulation |
| Dry-run evidence | Violations appear in the policy audit log with `dryRunResult = "DENIED"` and `liveResult = "ALLOWED"` |
| Inheritance | A child policy can override the parent; the effective policy is evaluated per resource |
| Security baseline | New organizations may receive baseline constraints automatically, including key creation, domain-restricted sharing, and default service-account grants; check before adding duplicates |

Policy definition content (constraint YAML, custom conditions) belongs to
`/internal-cloud-policy`. This reference owns scope, sequencing, and
evidence.

## VPC Service Controls

- Start new or changed perimeters in dry-run mode. Dry-run logs violations
  and does not block ([dry-run](https://docs.cloud.google.com/vpc-service-controls/docs/dry-run-mode)).
- The enforced configuration is evaluated first; dry-run logs only requests
  that enforcement allows and dry-run would deny.
- A project can sit in one enforced and one dry-run configuration at a time.
  Sequence moves between perimeters.
- Access levels have no dry-run mode. Create a new access level and attach it
  to the dry-run configuration to test it.
- Dry-run does not cover restricted or private VIP routing. Confirm service
  support on the restricted VIP before using it.

## Workload identity

| Need | Pattern | Evidence |
| --- | --- | --- |
| External CI or cloud workload needs access | Workload identity federation provider with an attribute condition on repository, branch, or environment | The provider rejects tokens outside the condition; bindings target the narrowest principal set |
| Restrict which external providers can be configured | `constraints/iam.workloadIdentityPoolProviders` (legacy) or `iam.managed.workloadIdentityPoolProviders` | Only approved issuers appear in pool providers |
| Shared automation | One purpose-built service account per automation boundary | Each identity maps to one owner and purpose |
| Temporary key use | Time-bounded exception with rotation and migration plan | Owner, expiry, and closure deadline recorded |

## Privileged access

- Use Privileged Access Manager (PAM) entitlements for just-in-time,
  time-bound elevation on organizations, folders, and projects, with
  justification and optional approval ([PAM](https://docs.cloud.google.com/iam/docs/pam-overview)).
- PAM does not support the legacy basic roles `roles/owner`, `roles/editor`,
  and `roles/viewer`; grant predefined or custom roles instead.
- PAM writes time-conditioned bindings into allow policies. Manage IAM with
  non-authoritative Terraform resources so applies do not remove them.
- Keep a separately logged break-glass path for PAM outages.

## Least-privilege evidence

- Use IAM Recommender findings before narrowing roles, and move excess
  standing roles to PAM entitlements instead of deleting them outright.
- Use Policy Analyzer or Policy Troubleshooter to prove who can reach what
  before and after a change.

## Tags and labels

- Resource Manager tags drive conditional IAM, deny conditions, and Org
  Policy scoping.
- Labels drive cost reporting and filtering. They do not affect access.

## Governed exceptions

| Exception | Pattern | Required evidence |
| --- | --- | --- |
| Org Policy exception for a small project set | Scoped override at the lowest resource, with a reason tag | Business reason, compensating control, owner, expiry, closure condition |
| Temporary service-account key | Time-bounded exception with rotation and migration plan | Affected workload, owner, expiry, closure deadline |
| Broader IAM grant during migration | Narrow temporary binding or PAM entitlement | Approver, scope, expiry, rollback condition |
| Deny or PAB exemption | `exceptionPrincipals` or a binding condition on `principal.subject` | Named principal, reason, review date |
