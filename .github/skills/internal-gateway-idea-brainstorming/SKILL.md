---
name: internal-gateway-idea-brainstorming
description: Use when a repository-owned request starts with a vague idea, unclear goal, unresolved option set, or needs substantive definition, convergence, critical challenge, and retained planning in the same conversation.
---

# Internal Gateway Idea Brainstorming

## Referenced skills

Load these skills by name only when the active phase requires them. This list is
an on-demand dependency index. Do not preload them; load only the owner proved
by the active uncertainty or next checkpoint.

- `grill-me`: guided decision interview.
- `internal-gateway-critical-master`: mandatory critical challenge owner.
- `internal-writing-plans`: retained-plan authoring after a confident critical outcome.
- `internal-agent-support-next-step`: next-step package formatting.

Portable skill-first idea gateway. This skill now owns substantive idea work
through retained-plan creation. It stops before execution.

## When to use

- The user brings a vague idea, unclear goal, or unresolved option set.
- Brainstorming, clarification, or success criteria are needed before planning.

## When not to use

- The target state and validation path are already concrete; use `internal-gateway-simple-task`.
- The primary request is defect-first review; use `internal-gateway-review`.
- A retained plan folder is already approved for execution; route to `internal-gateway-simple-task` for `compact` or `internal-executing-plans` for `extended`.

## Core Invariants

- Same-conversation support-skill loading is not a lane change.
- Idea Gate 0 remains mandatory.
- Use `internal-gateway-critical-master` before finalizing any substantive definition.
- After a confident critical outcome, load `internal-writing-plans`, create the retained plan, and stop before execution.

## Flow

1. Discover
2. Converge
3. Critical
4. Plan
5. Stop before execution

## Validation

- The gateway keeps `idea -> critical -> retained plan` in one conversation.
- `internal-writing-plans` owns profile selection.
- Execution stays a manual boundary after plan creation.
