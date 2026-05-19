---
name: internal-review-guard
description: "Use this agent when compatibility requires the deprecated review wrapper; prefer internal-gateway-operational-flow for new review work."
tools: ["read", "search"]
user-invocable: false
disable-model-invocation: true
agents: []
---

# Internal Review Guard

## Deprecated Compatibility Wrapper

This wrapper is retained only for the soft-deprecation window. New review,
merge-readiness, and correctness-evidence work should use
`internal-gateway-operational-flow` with the `review` entry point.

## Core Skill

- `internal-gateway-operational-flow`

## Routing Rules

- Do not select this wrapper for new work.
- Use `internal-gateway-operational-flow` for review mode and fix routing.
- Use `internal-gateway-critical-master` when the real need is pressure testing.

## Boundary Definition

- This file is non-invocable compatibility documentation.
- Do not add new handoffs or review procedure here.

## Output Expectations

- State that this wrapper is deprecated.
- Recommend `internal-gateway-operational-flow` review mode or `internal-gateway-critical-master`.
- Preserve the review subject, evidence gaps, and residual risk in the recommendation.
