---
name: internal-gcp
description: Use when designing, deciding, governing, or proving Google Cloud platform work, including org, folder, and project layout, billing ownership, Shared VPC, IAM and workload identity, Org Policy, VPC Service Controls, governed exceptions, and monitoring, inventory, backup, or recovery evidence. Route concrete policy definitions to /internal-cloud-policy and Terraform code to /internal-terraform.
---

# Internal GCP

The single owner for Google Cloud platform design, controls, decisions, and
evidence. The body is the always-on baseline; each reference adds GCP depth
for one concern.

## When to use

Use for a Google Cloud deliverable at organization, folder, project, network,
identity, policy, or evidence level:

- placement: hierarchy, billing ownership, Shared VPC, residency;
- control: IAM, workload identity, Org Policy, deny layers, perimeters,
  privileged access, governed exceptions;
- proof: rollout evidence, audit, inventory, posture, backup, restore;
- decision: a comparison of two or three realistic GCP options.

Hand off the artifacts that other owners control:

- policy definition content (constraint YAML or JSON, custom constraint
  conditions, cross-cloud policy comparison): `/internal-cloud-policy`;
- any HCL file, module, state, plan, apply, or import, including Terraform
  policy and IAM resources: `/internal-terraform`;
- GKE workload manifests and rollout: `/internal-kubernetes`;
- the GitHub side of OIDC trust (workflow permissions, `sub` claim):
  `/internal-github-platform`.

The GCP side of every handoff stays here: scope, control choice, trust
conditions, rollout unit, and evidence.

## Baseline

Apply these rules to every recommendation. A deviation needs a governed
exception (see Workflow step 5).

- Do not grant basic roles (`roles/owner`, `roles/editor`, `roles/viewer`) to
  human or workload principals. Use predefined or custom roles.
- Do not bind `allUsers` or `allAuthenticatedUsers`.
- Prefer workload identity federation or attached service accounts over
  service-account keys. A federation provider needs an attribute condition.
- Name the scope of every control: organization, folder, or project.
- State whether each control grants, constrains, or prevents access.
- Keep one purpose-built service account per automation boundary.

## Workflow

1. **Frame.** Name the deliverable, scope, owners, principals, and blast
   radius.
2. **Place before control.** When placement and controls depend on each
   other, settle placement first, then controls, then operational proof.
3. **Select.** Choose the placement or control plan and load only the
   matching reference.
4. **Stage.** Name the smallest rollout unit: one folder, project set, host
   project, perimeter, or region set. Use dry-run where the control supports
   it; otherwise use a documented staged unit. Name the rollback trigger and
   the widening condition.
5. **Except.** Record every exception with owner, reason, scope, compensating
   control, expiry date, and closure condition.
6. **Prove.** Define expected evidence before the change and observed
   evidence after it. For stateful scope, include restore and integrity
   proof. Report missing evidence as a gap.

## Decision mode

Use this mode when the deliverable is an option comparison. This skill stays
the decision owner.

1. State the decision and the assumptions that shape it.
2. Compare two or three realistic options on value, cost, operational burden,
   risk, blast radius, continuity, and reversibility.
3. Recommend one option and say why it wins under the assumptions.
4. Name the fact that still needs verification.

Return a quick answer for a narrow choice or a decision note when two or more
options stay viable. Load `references/structure.md` "Decision lenses" for lens
selection. `/internal-gateway-critical-master` may add critique; it does not
replace this owner.

## Freshness

Constraint identifiers, dry-run support, launch stage (preview or GA),
regional availability, and quotas change often. Verify them against current
Google Cloud documentation before stating them as fact. Otherwise mark them as
assumptions to verify.

## References

- [`references/structure.md`](references/structure.md): load for hierarchy,
  billing, Shared VPC, connectivity, residency, change units, or decision
  lenses.
- [`references/governance.md`](references/governance.md): load for Org
  Policy, IAM allow, deny, and Principal Access Boundary composition, VPC
  Service Controls, workload identity, privileged access, tags, or
  exceptions.
- [`references/operations.md`](references/operations.md): load for audit
  logs, inventory, posture, monitoring, backup and recovery, or stage-aware
  rollout evidence.

## Completion criteria

- The scope is explicit at organization, folder, or project level.
- The baseline holds, or each deviation has a governed exception.
- Each control states whether it grants, constrains, or prevents.
- The rollout unit, dry-run or staged path, rollback trigger, and widening
  condition are named.
- Expected and observed evidence are separate, and gaps are reported.
- Handoffs name the owning skill and keep the GCP side here.
- Unverified current facts are flagged.
