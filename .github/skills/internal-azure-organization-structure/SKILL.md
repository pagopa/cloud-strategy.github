---
name: internal-azure-organization-structure
description: Use when /internal-azure selects Azure hierarchy, subscription, landing-zone, residency, or platform-topology work.
---

# Internal Azure Organization Structure

Use this workflow for Azure tenant and platform layout decisions.

## When to use

Use when `/internal-azure` selects a hierarchy, subscription, landing-zone,
residency, or platform-topology deliverable.

## Workflow

1. State the Azure objective: the platform capability, ownership model, or
   residency requirement the structure must support.
2. Make the placement choice across tenant, management group, subscription,
   landing zone, and platform network topology.
3. Compare candidate layouts and state platform ownership, workload ownership,
   inheritance scope, residency assumptions, and blast radius.
4. Name the rollout unit: a management group, subscription set, landing zone,
   or region set that can be validated safely.
5. Define validation conditions for inheritance, connectivity, automation,
   ownership, and continuity assumptions before widening the rollout.

## Azure structure patterns

- Use management groups for enterprise segmentation and inheritance scope.
- Use subscriptions for workload, platform, environment, or residency
  boundaries with explicit purpose and ownership.
- Use landing zones to package platform capabilities, connectivity, and
  operating-model expectations.
- Keep hub-spoke, Virtual WAN, private connectivity, and regional placement
  visible when they shape the platform topology.
- Separate platform subscriptions from workload subscriptions when shared
  services need stable ownership.

## Current facts

Use current Microsoft documentation when the recommendation depends on landing-
zone guidance, management-group behavior, subscription constraints, networking
capabilities, or region-sensitive platform limits.

Load `references/topology-map.md` for structural mappings, placement heuristics,
or safe rollout examples.

## Completion criteria

Return the recommended structure, the placement rationale, the smallest safe
rollout unit, the material risks, and the validation conditions.
