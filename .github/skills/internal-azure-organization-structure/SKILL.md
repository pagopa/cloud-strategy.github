---
name: internal-azure-organization-structure
description: Use when the user needs Azure control-plane or platform-structure guidance for tenant hierarchy, management groups, subscription models, landing-zone placement, environment segmentation, platform-level network topology, or other layout decisions that shape how Azure is organized before implementation.
---

# Internal Azure Organization Structure

Use this skill when the next need is to design or review how Azure is structured at tenant and platform level.

This skill owns Azure layout decisions, not generic strategy and not detailed RBAC or monitoring implementation. It helps translate a platform goal into management-group, subscription, landing-zone, topology, and rollout structure.

## When to use

- The user is shaping or reviewing Azure tenant hierarchy.
- The user needs management-group or subscription-model guidance.
- The user is deciding landing-zone placement or environment segmentation.
- The user needs platform-level network or regional structure guidance.
- The user needs rollout-scope guidance for structural Azure change.

## When not to use

- The question is mainly RBAC, PIM, managed identities, or Policy logic.
- The task is mainly monitoring, backup, reporting, or post-rollout validation.
- The user only needs generic strategic comparison with no concrete structure question.
- The task is already implementation-focused.

## Main domains covered

- tenant hierarchy
- management-group layout
- subscription model and subscription purpose
- landing-zone placement
- environment segmentation
- platform-level network topology
- regional structure and residency placement when relevant
- rollout unit and blast radius for structural change

## Working model

- Keep tenant-level hierarchy decisions separate from subscription-level governance decisions.
- Separate structure decisions from governance decisions:
  - structure decides where capabilities live
  - governance decides what controls and permissions apply
- Keep platform subscriptions separate from workload subscriptions when the operating model needs it.
- Name the smallest safe rollout unit for structural change: management group, subscription set, or region set.

## Research and current facts

Use current Microsoft documentation when the answer depends on current landing-zone guidance, management-group behavior, subscription constraints, Azure networking capabilities, or region-sensitive platform limits.

Load `references/topology-map.md` when the structure choice is ambiguous or when the user needs a deeper control-surface split.

## Output expectations

Keep outputs proportional to the question.

For narrow asks, return:

- recommended structure choice
- short reason
- main blast-radius or rollout note

For broader asks, return:

- structural objective
- candidate layouts
- recommended placement model
- smallest safe rollout unit
- main risks
- what should move next to `internal-azure-governance` or `internal-azure-operations`

## Relationship to adjacent skills

- `internal-azure-strategic`
  Use first when the user still needs broader decision framing or lens selection.
- `internal-azure-governance`
  Use when the structural decision is accepted and the next need is RBAC, managed identity, PIM/PAM, Policy, or guardrail definition.
- `internal-azure-operations`
  Use when the structure is accepted and the next need is validation, monitoring, backup, or operational evidence.

## Anti-patterns

- proposing hierarchy or subscription layouts without a rollout scope
- mixing landing-zone placement and RBAC design into one vague answer
- treating network topology as an operations concern instead of a structure concern
- using structure answers to sneak in Policy or RBAC design without separating the concerns
- ignoring region or residency implications when they materially shape layout
