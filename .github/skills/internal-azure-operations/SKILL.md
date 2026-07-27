---
name: internal-azure-operations
description: Use when /internal-azure selects Azure preflight, observability, rollout evidence, backup/restore proof, continuity validation, or operational reporting.
---

# Internal Azure Operations

Use this workflow to validate, observe, and operationalize an Azure platform
decision.

## When to use

Use when `/internal-azure` selects an operational readiness, evidence,
monitoring, recovery, or reporting deliverable.

## Workflow

1. State the operational objective: the behavior, readiness condition, or
   recovery expectation that requires proof.
2. Record the evidence state: confirmed observations, inferred conditions, and
   open checks.
3. Define the rollout unit and its blast radius, owner, rollback trigger, and
   widening condition.
4. Run preflight for scope, identity, policy, connectivity, monitoring,
   logging, and backup assumptions relevant to the change.
5. Capture observation signals from Azure Monitor, Log Analytics, activity
   evidence, compliance state, intended operations, and regressions.
6. Add recovery proof when stateful services, business criticality, or
   continuity expectations make it relevant; distinguish backup, restore, and
   DR evidence.
7. Apply the completion criteria: evidence is attributable to the rollout unit,
   open risks are named, rollback conditions are actionable, and widening has
   fresh proof.

## Evidence patterns

- Keep confirmed and inferred evidence on separate lines.
- Tie monitoring and reporting to the affected control-plane surface.
- Validate a first safe unit before widening management-group, subscription,
  landing-zone, or region scope.
- Treat backup posture, restore viability, and continuity exercises as distinct
  proof paths.

## Current facts

Use current Microsoft documentation when the answer depends on Azure Monitor,
Backup, Site Recovery, Policy compliance, or service behavior.

Load `references/validation-and-evidence.md` for branch-specific preflight,
rollout, recovery, and evidence checklists.

## Completion criteria

Return the operational objective, evidence state, rollout unit, observed signals,
recovery proof when relevant, open risks, and next validation action.
