---
name: internal-agent-support-lane-change-engine
description: Use when a repository-owned internal agent needs a consistent user-visible lane-change response after the selected lane no longer fits.
---

# Internal Agent Support Lane Change Engine

## Referenced skills

- `internal-gateway-review`: source lane when review findings leave a local fix, planning gap, or assumption challenge.
- `internal-gateway-simple-task`: source or target lane for concrete local follow-up work.
- `internal-gateway-idea-brainstorming`: target lane when planning or scope definition is needed.
- `internal-gateway-critical-master`: target lane when assumption pressure-testing dominates.
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
- Fail safe to `internal-gateway-idea-brainstorming` when the next lane is still ambiguous.

## Recommendation Matrix

| Current agent | When the boundary breaks | Recommend |
| --- | --- | --- |
| `internal-gateway-review` | Findings now leave only a concrete local fix | `internal-gateway-simple-task` |
| `internal-gateway-review` | Findings reopen planning or scope definition | `internal-gateway-idea-brainstorming` |
| `internal-gateway-review` | Assumption pressure-testing becomes dominant | `internal-gateway-critical-master` |
| `internal-gateway-simple-task` | Planning or governance becomes dominant | `internal-gateway-idea-brainstorming` |
| `internal-gateway-simple-task` | Defect-first analysis becomes dominant | `internal-gateway-review` |
| `internal-gateway-simple-task` | Assumption pressure-testing becomes dominant | `internal-gateway-critical-master` |
| `internal-gateway-critical-master` | The next step is planning | `internal-gateway-idea-brainstorming` |
| `internal-gateway-critical-master` | The next step is evidence-first review | `internal-gateway-review` |
| `internal-gateway-idea-brainstorming` | A retained `compact` plan is approved for execution | `internal-gateway-simple-task` |
| `internal-gateway-idea-brainstorming` | A retained `extended` plan is approved for execution | `internal-gateway-execute-plans` |
