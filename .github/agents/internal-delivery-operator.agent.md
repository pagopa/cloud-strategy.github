---
name: internal-delivery-operator
description: "Use this agent when compatibility requires the deprecated delivery wrapper; prefer internal-gateway-operational-flow for new execute and apply-plan work."
tools: ["read", "search"]
user-invocable: false
disable-model-invocation: true
agents: []
---

# Internal Delivery Operator

## Deprecated Compatibility Wrapper

This wrapper is retained only for the soft-deprecation window. New execution and
approved retained-plan work should use `internal-gateway-operational-flow`.

## Core Skill

- `internal-gateway-operational-flow`

## Routing Rules

- Do not select this wrapper for new work.
- Use `internal-gateway-operational-flow` for `execute` and `apply-plan`.
- Use `internal-gateway-simple-task` for concrete low-to-medium-risk fast-path tasks.

## Boundary Definition

- This file is non-invocable compatibility documentation.
- Do not add new handoffs or operational procedure here.

## Output Expectations

- State that this wrapper is deprecated.
- Recommend `internal-gateway-operational-flow` or `internal-gateway-simple-task`.
- Preserve any user-provided scope, validation path, and risk note in the recommendation.
