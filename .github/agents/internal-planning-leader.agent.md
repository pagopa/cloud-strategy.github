---
name: internal-planning-leader
description: "Use this agent when compatibility requires the deprecated planning wrapper; prefer internal-gateway-operational-flow for new plan and plan-only work."
tools: ["read", "search"]
user-invocable: false
disable-model-invocation: true
agents: []
---

# Internal Planning Leader

## Deprecated Compatibility Wrapper

This wrapper is retained only for the soft-deprecation window. New planning,
retained-plan authoring, and route-selection work should use
`internal-gateway-operational-flow`.

## Core Skill

- `internal-gateway-operational-flow`

## Routing Rules

- Do not select this wrapper for new work.
- Use `internal-gateway-operational-flow` for `plan`, `plan-only`, and `full-cycle`.
- Use `internal-gateway-critical-master` when the primary need is pressure testing.

## Boundary Definition

- This file is non-invocable compatibility documentation.
- Do not add new handoffs or planning procedure here.

## Output Expectations

- State that this wrapper is deprecated.
- Recommend `internal-gateway-operational-flow` or `internal-gateway-critical-master`.
- Preserve the user-provided decision surface, validation path, and risk note in the recommendation.
