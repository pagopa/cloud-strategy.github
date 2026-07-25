---
name: internal-agent-support-lane-change-engine
description: Use when a repository-owned internal agent needs a consistent user-visible lane-change response after the selected lane no longer fits.
---

# Internal Agent Support Lane Change Engine

## Referenced skills

- `internal-gateway-idea`: source lane when planning or scope definition is needed; target lane when planning or scope definition dominates.
- `internal-gateway-critical-master`: source lane when assumption pressure-testing dominates; target lane when assumption pressure-testing dominates.
- `internal-gateway-execute-plans`: target lane when approved retained-plan execution is the next step.

Use this skill as the shared lane-mismatch engine for repository-owned internal
agents.

## When to use

- A repository-owned internal agent no longer fits the real work.
- The current owner must stop and recommend one better visible owner.

## Goals

- Stop before doing off-lane work.
- Explain the concrete mismatch.
- Recommend exactly one better owner when the next lane is clear.
- Fail safe to `internal-gateway-idea` when the next lane is still ambiguous.

## Recommendation Matrix

| Current agent | When the boundary breaks | Recommend |
| --- | --- | --- |
| `internal-gateway-critical-master` | The next step is planning | `internal-gateway-idea` |
| `internal-gateway-idea` | An approved retained plan is ready for execution | `internal-gateway-execute-plans` |
