---
name: internal-critical-master
description: "Use this agent when compatibility requires the deprecated critical wrapper; prefer internal-gateway-critical-master for new pressure-test work."
tools: ["read", "search"]
user-invocable: false
disable-model-invocation: true
agents: []
---

# Internal Critical Master

## Deprecated Compatibility Wrapper

This wrapper is retained only for the soft-deprecation window. New pressure-test
and critical challenge work should use `internal-gateway-critical-master`.

## Core Skill

- `internal-gateway-critical-master`

## Routing Rules

- Do not select this wrapper for new work.
- Use `internal-gateway-critical-master` for pre-mortems, assumption tests, and failure-mode analysis.
- Use `internal-gateway-operational-flow` when the next step is planning, execution, or review.

## Boundary Definition

- This file is non-invocable compatibility documentation.
- Do not add new handoffs or critical challenge procedure here.

## Output Expectations

- State that this wrapper is deprecated.
- Recommend `internal-gateway-critical-master` or `internal-gateway-operational-flow`.
- Preserve the challenged artifact, outcome, validation path, and residual risk in the recommendation.
