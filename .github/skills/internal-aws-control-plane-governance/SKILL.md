---
name: internal-aws-control-plane-governance
description: Use when the user needs principal-level AWS governance for the organization control plane management account or payer responsibilities, delegated administrators, service control policies, IAM operating model, account access strategy, or CloudFormation StackSets across the organization.
---

# Internal AWS Control Plane Governance

Use this skill when the work is about governing AWS as a platform control plane rather than implementing one isolated workload.

## Purpose

This skill helps frame and drive strategic AWS decisions across:

- AWS Organizations structure
- management account and payer responsibilities
- delegated administrator design
- SCP and policy guardrails
- IAM operating model and cross-account access
- CloudFormation StackSets across the organization

Use `internal-aws-mcp-research` whenever the decision depends on current AWS documentation, service behavior, IAM semantics, or account-safe IAM inspection.

## Strategic principles

- Clarify whether "payer" and "management" mean the same AWS Organizations management account or separate finance and operating concerns in your internal model.
- Keep workloads and routine platform execution out of the management account whenever AWS allows a delegated administrator pattern.
- Treat SCPs as guardrails that limit the maximum available permissions. They do not grant access.
- Distinguish organization guardrails from in-account access design:
  - SCP or RCP for org-level limits
  - IAM identity and resource policies for in-account authorization
  - permissions boundaries and session policies for delegated execution constraints
  - trust policies for role assumption boundaries
- Prefer org-aware rollout mechanisms over bespoke per-account drift:
  - trusted access plus delegated admin where supported
  - StackSets with service-managed permissions for repeatable cross-account baselines when the model fits
- Every recommendation must name scope, blast radius, validation path, and rollback path.

## Control-plane decision map

| Question | Primary control surface | Typical operating location | Why |
|---|---|---|---|
| Limit what principals can ever do across accounts | SCP | AWS Organizations from the management account | Central guardrail on member accounts |
| Restrict external access to supported resources org-wide | RCP | AWS Organizations from the management account | Resource-centric org guardrail |
| Define who can do what inside one account | IAM policies, trust policies, permissions boundaries | Member account or delegated admin workflow | Execution-level authorization |
| Roll out a baseline stack across OUs or many accounts | CloudFormation StackSets | Management account or delegated admin using service-managed permissions | Standardized multi-account rollout |
| Reduce routine use of the management account | Trusted access plus delegated admin | Management account to enable, delegated admin to operate | Lowers blast radius in the control plane |
| Separate financial oversight from platform execution | Account ownership model plus delegated services | Management account and dedicated member accounts | Cleaner accountability and safer operations |

## Decision examples

- You need a preventive org-wide deny on unsupported regions:
  - Prefer an SCP at root or OU scope.
  - Validate against exception accounts first.
  - Roll out OU by OU with a rollback path that removes or narrows the SCP.
- You need Security Hub or Config operated centrally across many accounts:
  - Prefer trusted access plus delegated administrator rather than daily operations from the management account.
  - Document which account owns operations and which account only enables the org integration.
- You need a baseline IAM role or logging stack across many accounts:
  - Prefer CloudFormation StackSets with service-managed permissions when supported by the target service and org model.
  - Call out whether any template resource has global or organization-sensitive blast radius.

## Flagging examples

- Flag recommendations that say "apply this in the management account" without proving management-account necessity.
- Flag designs that mix SCP decisions and IAM grant decisions into one undifferentiated policy answer.
- Flag org-wide rollout plans that skip a staging OU, simulation step, or rollback instructions.
- Flag proposals that treat delegated admin as optional convenience when it materially reduces control-plane blast radius.

## Workflow

1. Frame the strategic question.
   Capture business goal, affected accounts or OUs, control surface, and urgency.
2. Place the decision in the correct layer.
   Decide whether the change belongs in Organizations, IAM, CloudFormation StackSets, or service-specific delegated administration.
3. Check management-account necessity.
   Ask whether the task must happen from the management account or can move to a delegated administrator or member account.
4. Load current AWS facts.
   Use `internal-aws-mcp-research` for current AWS documentation, IAM semantics, regional availability, and account-safe IAM inspection.
5. Produce the operating recommendation.
   State the target ownership model, the guardrail stack, the rollout method, and the failure containment plan.
6. Validate before rollout.
   Require simulation, non-production OU or account testing, staged rollout, and rollback instructions.

## Mandatory outputs

- Strategic objective
- Scope: organization, root, OU, account set, region set
- Control-plane placement: management account, delegated admin, or member account
- Recommended mechanisms: SCP, RCP, IAM, StackSets, trusted access, delegated admin
- Main risks and blast radius
- Validation and rollback plan

## Anti-patterns

- Putting routine workloads or shared services in the management account without a strong reason
- Using SCPs as if they grant access
- Mixing org-level guardrails with account-level IAM decisions in the same recommendation without separating them
- Recommending organization-wide rollout without a staged OU or account validation plan
- Treating StackSets as harmless when templates include global resources or organization-sensitive permissions

## References

- `references/control-plane-map.md`
- `../internal-aws-mcp-research/SKILL.md`
