---
name: internal-gcp-operations
description: Use when /internal-gcp selects operations for Google Cloud monitoring, logging, backup, restore, recovery validation, asset inventory, rollout evidence, or operational reporting.
---

# Internal GCP Operations

## Purpose

Validate, observe, and operationalize a Google Cloud platform decision through preflight signals, staged rollout observations, recovery evidence, inventory, and reporting.

## When to use

Use this skill when the requested deliverable is operational readiness, validation, reporting, or evidence for a Google Cloud surface.

## Process

1. Establish the operational objective, affected surface, rollout unit, business criticality, and recovery expectations.
2. Define preflight signals, owners, success criteria, and the rollback trigger before the change begins.
3. Define rollout observations for monitoring, logging, inventory, connectivity, identity, policy, and other affected signals.
4. Distinguish expected evidence, observed evidence, backup evidence, restore evidence, and recovery evidence.
5. Report remaining operational risk, evidence gaps, and the condition for widening the rollout.

Load `references/validation-and-evidence.md` only when an evidence path needs deeper detail.

## Output

- a concise operational-readiness report
- a staged validation plan
- an evidence package
- a risk and rollout recommendation

## Completion

- The affected surface and rollout unit are explicit.
- Preflight signals, success criteria, owner, and rollback trigger are named.
- Observations cover the signals needed to confirm the decision.
- Expected, observed, backup, restore, and recovery evidence are clearly distinguished.
- Remaining risk and the widening condition are reported.
