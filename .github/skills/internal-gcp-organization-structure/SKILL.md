---
name: internal-gcp-organization-structure
description: Use when the user needs Google Cloud control-plane or platform-structure guidance for org or folder layout, billing-account model, project segmentation, Shared VPC host and service project topology, environment segmentation, platform-level network structure, or other layout decisions that shape how GCP is organized before implementation.
---

# Internal GCP Organization Structure

Use this skill when the next need is to design or review how GCP is structured at org and platform level.

This skill owns GCP layout decisions, not generic strategy and not detailed IAM or monitoring implementation. It helps translate a platform goal into org, folder, project, Shared VPC, topology, and rollout structure.

## When to use

- The user is shaping or reviewing GCP org or folder hierarchy.
- The user needs billing-account or project-model guidance.
- The user is deciding Shared VPC host and service project topology.
- The user needs platform-level network or regional structure guidance.
- The user needs rollout-scope guidance for structural GCP change.

## When not to use

- The question is mainly IAM, service account, workload identity, or Org Policy logic.
- The task is mainly monitoring, backup, reporting, or post-rollout validation.
- The user only needs generic strategic comparison with no concrete structure question.
- The task is already implementation-focused.

## Main domains covered

- org hierarchy
- folder layout
- billing-account placement and ownership split
- project model and project purpose
- Shared VPC host and service project topology
- environment segmentation
- platform-level network structure
- regional structure and residency placement when relevant
- rollout unit and blast radius for structural change

## Working model

- Keep org and folder hierarchy decisions separate from project-level governance decisions.
- Separate structure decisions from governance decisions:
  - structure decides where capabilities live
  - governance decides what controls and permissions apply
- Make billing ownership explicit when it differs from platform ownership.
- Name the smallest safe rollout unit for structural change: folder, project set, or region set.

## Research and current facts

Use current Google Cloud documentation when the answer depends on current Shared VPC behavior, project constraints, org hierarchy guidance, billing-account limits, or region-sensitive platform capabilities.

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
- what should move next to `internal-gcp-governance` or `internal-gcp-operations`

## Relationship to adjacent skills

- `internal-gcp-strategic`
  Use first when the user still needs broader decision framing or lens selection.
- `internal-gcp-governance`
  Use when the structural decision is accepted and the next need is IAM, workload identity federation, Org Policy, or guardrail definition.
- `internal-gcp-operations`
  Use when the structure is accepted and the next need is validation, monitoring, backup, inventory, or operational evidence.

## Anti-patterns

- proposing org or project layouts without a rollout scope
- mixing Shared VPC placement and IAM design into one vague answer
- treating billing layout as an afterthought when it changes ownership or blast radius
- using structure answers to sneak in Org Policy or IAM design without separating the concerns
- ignoring region or residency implications when they materially shape layout
