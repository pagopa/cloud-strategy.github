# AWS Governance Controls

Load this reference to choose among AWS control mechanisms, design trust and
delegation, build a data perimeter, map Control Tower controls, or define
exceptions. Authoring the concrete policy document belongs to
`/internal-cloud-policy`; pass it the selected type, scope, constraints,
exclusions, and sources.

## Organizations policy types

AWS Organizations has authorization policies (SCPs and RCPs) and management
policies, which include declarative, tag, backup, and AI opt-out policies.

| | SCP | RCP | Declarative policy |
| --- | --- | --- | --- |
| Governs | IAM principals in member accounts | Resources in member accounts | Service configuration |
| How | Caps the maximum permissions of principals at API level | Caps the maximum permissions on resources at API level, for any caller | Enforces a baseline configuration without API-level evaluation |
| Affects callers outside the org | No | Yes | Not applicable |
| Affects service-linked roles | No | No | Yes |
| Management account | Its principals are not restricted | Its resources are not restricted | Applies to attached targets |
| Example | Deny leaving the organization | Require HTTPS or org-only access to S3 | EC2 image block public access |

Selection order:

1. When a declarative policy exists for the configuration you want to
   enforce, prefer it.
2. To cap what your principals can do, use an SCP.
3. To cap who can access your resources, including external principals, use
   an RCP.

### RCP limits

- RCPs apply only to supported services. Check the current list before you
  rely on coverage.
- RCPs do not restrict service-linked roles or AWS managed KMS keys.
- `RCPFullAWSAccess` is attached automatically and cannot be detached. Custom
  RCPs act as deny statements on top of it.
- A management-account principal that calls a member-account resource is
  still subject to that account's RCPs.

## Grants, trust, and delegation

| Need | Use first | Why |
| --- | --- | --- |
| Define what a role or workload can do in one account | Identity-based policy, plus resource-based policy where the service uses one | Grants the action at the execution boundary |
| Control who can assume a role | Trust policy with named principals and conditions | Separates assumption from permissions |
| Let builders create roles without escalation | Permission boundary plus a scoped role-creation role | Limits delegated builders without replacing trust design |
| Limit one session | Session policy | Narrows a single assumed-role session |

- Prefer roles and federation over long-lived IAM users unless a proven
  reason exists.
- A permission boundary does not replace trust design: boundaries limit what
  delegated roles can do; trust policies limit who can assume them.

## Trust-boundary patterns

| Need | Primary control | Review note |
| --- | --- | --- |
| Human access from an external IdP | Federation plus tightly scoped assume-role paths or IAM Identity Center permission sets | Keep identity-source trust separate from account authorization |
| CI or automation assuming deployment roles across accounts | Trust policy restricted to named principals and conditions (for OIDC: audience and subject) | Make environment scope and break-glass path explicit |
| Shared security tooling reading logs across accounts | Resource policy or role assumption with read-only scope | Prefer narrow data-access roles over broad admin trust |
| An AWS service acting on your behalf | Service role trust with `aws:SourceAccount` or `aws:SourceArn` | Prevents confused-deputy access |

## Data perimeter

A data perimeter combines three layers:

- SCPs keep your principals from reaching resources outside the org.
- RCPs keep principals outside the org from reaching your resources.
- VPC endpoint policies keep network paths on approved resources.

Grants still come from identity-based and resource-based policies. Roll out
by one OU or account set first, carry the known exceptions (partners, AWS
services acting on your behalf), and validate with observed access results.

## Control Tower controls

- Preventive controls are implemented with SCPs, RCPs, and declarative
  policies.
- Detective controls are implemented with AWS Config rules, including the
  integrated Security Hub controls.
- Proactive controls are implemented with CloudFormation Hooks and apply
  only to resources provisioned through CloudFormation.
- From landing zone version 4.0, mandatory controls are no longer applied by
  default.

## Tags

A tag policy standardizes keys and values centrally. Enforce it in deployment
paths as well (pipeline checks, SCP conditions on `aws:RequestTag`, or
proactive controls). A tag policy defines compliant keys and values; it does
not require a tag to exist, and its enforcement covers only the resource
types you list.

## Exceptions and break-glass

| Exception type | Pattern | Audit expectation |
| --- | --- | --- |
| Temporary break-glass for incident response | Time-bounded role path with an explicit approver and logging | Record who approved, who assumed the role, and when access ended |
| OU-level SCP or RCP carve-out for one team | Targeted OU or account exception with an expiry review | Record the business reason, compensating controls, and review date |
| Automation cannot yet meet a tag or policy condition | Narrow deployment exception with a compensating report | Track affected accounts or resources and the closure plan |

## Sources (retrieved 2026-09-27)

- Organizations policy types:
  <https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies.html>
- Authorization policies:
  <https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies_authorization_policies.html>
- SCPs: <https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies_scps.html>
- RCPs: <https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies_rcps.html>
- RCP evaluation:
  <https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies_rcps_evaluation.html>
- Declarative policies:
  <https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies_declarative_policies.html>
- IAM policy evaluation logic:
  <https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_evaluation-logic.html>
- Data perimeters on AWS: <https://aws.amazon.com/identity/data-perimeters-on-aws/>
- Tag policies:
  <https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies_tag-policies.html>
- Control Tower control behavior:
  <https://docs.aws.amazon.com/controltower/latest/controlreference/control-behavior.html>
