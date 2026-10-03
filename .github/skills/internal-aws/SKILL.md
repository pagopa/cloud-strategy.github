---
name: internal-aws
description: Use when designing, deciding, reviewing, or proving AWS platform controls, including Organizations, accounts and OUs, delegated administrators, StackSets, platform network placement, IAM and trust, SCPs, RCPs, declarative policies, rollout and recovery evidence, or current AWS platform facts. Route Lambda function contracts to /internal-aws-lambda, Organizations policy documents to /internal-cloud-policy, IaC authoring to /internal-terraform, and spend analysis to /antigravity-aws-cost-optimizer.
---

# Internal AWS

The single owner for AWS platform placement, controls, decisions, and
evidence. The body is the always-on baseline; each reference adds AWS depth
for one concern.

## When to use

Use for an AWS deliverable at organization, OU, account, identity, policy, or
evidence level:

- placement: accounts, OUs, delegated administrators, StackSets topology,
  shared services, platform network and multi-region placement;
- control: IAM identity, resource, and trust policies, federation, permission
  boundaries, SCPs, RCPs, declarative policies, tag policies, exceptions;
- proof: preflight, staged rollout, audit, backup and restore evidence;
- current facts: service behavior, limits, regional availability, policy
  semantics, live IAM state;
- decision: a comparison of two or three realistic AWS options.

Hand off the artifacts that other owners control:

- Lambda handler, event-source, retry, concurrency, or packaging work:
  `/internal-aws-lambda`;
- a concrete Organizations policy document or a cross-cloud policy
  comparison: `/internal-cloud-policy`, with the selected policy type, scope,
  constraints, exclusions, and sources;
- any HCL file, module, state, plan, or apply: `/internal-terraform`;
- CloudFormation template review: `/antigravity-cloudformation-best-practices`;
- spend analysis or savings opportunities: `/antigravity-aws-cost-optimizer`.

The AWS side of every handoff stays here: scope, control choice, trust
conditions, rollout unit, and evidence.

## Core rules

1. Name the scope: root, OU, account set, account, principal, session, or
   region.
2. State what each control does:
   - an SCP limits the maximum permissions of principals in member accounts;
   - an RCP limits the maximum permissions on resources in member accounts,
     including for principals outside the organization;
   - a declarative policy enforces service configuration, including for
     service-linked roles;
   - identity-based and resource-based policies grant; a trust policy
     controls who may assume a role;
   - a permission boundary or session policy constrains delegation.

   SCPs and RCPs never grant. RCPs cover only supported services and do not
   restrict service-linked roles or AWS managed KMS keys.
3. Keep the management account minimal. SCPs do not restrict its principals,
   and RCPs do not restrict its resources. A management-account principal
   that calls a member-account resource is still subject to that account's
   RCPs. A delegated administrator is a member account and stays under SCPs
   and RCPs.
4. Settle placement (where a capability lives) before controls (what applies
   there), and keep the two decisions separate.
5. For a risky rollout, name the smallest unit, preflight, rollback trigger,
   and owner. Widen only after the first unit is validated.
6. Label every claim as AWS documentation, live observation, or inference.
   Backup success and restore proof are separate evidence lines.
7. Verify limits, support boundaries, regional availability, and policy
   semantics before stating them as fact; otherwise mark them unverified.
   Keep live IAM access read-only unless the user explicitly asks for a
   change.
8. Validate each control with a method that covers it. IAM policy simulation
   covers identity policies and SCPs where supported; it does not prove an
   RCP or declarative policy effect. Those need an authorized staged check
   and observed evidence.
9. Do decision work only when a decision is requested.

## Output modes

- **Quick answer** for a narrow ask: recommendation, reason, and the main
  risk or evidence note.
- **Decision note** when two or more options stay viable: decision,
  assumptions, two or three realistic options, recommendation, strongest
  tradeoff, blast radius and reversibility, remaining evidence.

## References

- [`references/organization.md`](references/organization.md): load for
  account and OU layout, delegated administrators, StackSets, shared
  services, ownership split, or platform network placement.
- [`references/governance.md`](references/governance.md): load for choosing
  among SCP, RCP, declarative, IAM, trust, and boundary controls, data
  perimeters, Control Tower controls, tags, break-glass, or exceptions.
- [`references/evidence.md`](references/evidence.md): load for preflight,
  rollout-stage evidence, backup versus restore proof, or AWS signals.
- [`references/current-facts.md`](references/current-facts.md): load when a
  current fact, live IAM observation, or policy simulation controls the
  answer.
- [`references/decisions.md`](references/decisions.md): load for a decision
  note on landing zone, delegated access, or cost-sensitive platform choices.

## Completion criteria

- The scope is explicit and each control states what it limits, enforces,
  grants, or constrains.
- Management-account and delegated-administrator effects are stated when
  they matter.
- Risky rollouts name the unit, preflight, rollback trigger, and owner.
- Claims carry a source label; unverified current facts are flagged.
- Validation matches the mechanism.
- Handoffs name the owning skill and keep the AWS side here.
