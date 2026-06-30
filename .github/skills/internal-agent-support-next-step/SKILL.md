---
name: internal-agent-support-next-step
description: Use when a repository-owned agent or prompt needs to package an already-chosen next owner, scope, action, validation path, and risk note for a user-visible transition.
---

# Internal Agent Support Next Step

## Referenced skills

- `internal-gateway-idea-brainstorming`: source lane that may need a visible next-step transition.
- `internal-gateway-review`: source lane that may need a visible next-step transition.
- `internal-gateway-simple-task`: source lane that may need a visible next-step transition.
- `internal-gateway-execute-plans`: source lane that may need a visible next-step transition.
- `internal-gateway-critical-master`: source lane that may need a visible next-step transition.

Use this skill to format the next step after the next owner has already been
chosen or confirmed.

## When to use

- `internal-gateway-idea-brainstorming`, `internal-gateway-review`,
  `internal-gateway-simple-task`, `internal-gateway-execute-plans`, or
  `internal-gateway-critical-master` stop with a visible transition.

## Package Contract

- `Owner`
- `Scope`
- `Action`
- `Validation`
- `Risk`
- `Continuation`
- `User action required` when `Continuation` is `waiting`
