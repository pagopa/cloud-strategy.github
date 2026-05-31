---
name: internal-agent-support-next-step
description: Use when a repository-owned agent or prompt needs to package an already-chosen next owner, scope, action, validation path, and risk note for a user-visible transition.
---

# Internal Agent Support Next Step

Use this skill to format the next step after the next owner has already been chosen or confirmed. It keeps sequential workflows compact, explicit, and user-visible without turning Copilot wrappers or portable skill workflows into hidden routers.

## When to use

- `internal-gateway-operational-flow` ends a staged `plan`, `execute`, `apply-plan`, `review`, or critical phase with a visible transition.
- A Copilot wrapper recommends moving from planning, delivery, review, or critical challenge to a different owner.
- `internal-gateway-operational-flow` review mode finishes defect-first analysis and needs to route actionable findings to delivery, planning, critical challenge, or deferred follow-up.
- A prompt needs a consistent handoff package that survives surfaces where VS Code `handoffs:` buttons are not available.

## When not to use

- Do not use this skill to choose the next owner from scratch; use `internal-agent-support-lane-change-engine` when the lane no longer fits.
- Do not use it to dispatch another agent, auto-submit a handoff, or bypass user approval.
- Do not duplicate the lane-change recommendation matrix here.

## Package Contract

When a next step is needed, include this compact package:

- `Owner`: exact next agent or skill owner already selected.
- `Scope`: files, directories, artifacts, or decision surface in scope.
- `Action`: one concrete next action the next owner should take.
- `Validation`: command, review path, evidence, or explicit gap the next owner must address.
- `Risk`: residual risk, rollback note, or reason the transition should stay manual.
- `Continuation`: `continuing` when the current owner can safely keep going after
  the next slice, or `waiting` when user input, approval, or an external
  prerequisite must land first.
- `User action required`: mandatory when `Continuation` is `waiting`; say
  exactly what the user or operator must do next.

Keep the package short. Prefer one line per field unless the validation path or risk note genuinely needs more detail.

Use `references/decision-brief.md` when the next-step package must become a
Decision Brief for retained planning, execution handoff, or cross-surface
continuation.

## VS Code Handoffs

- Treat `handoffs:` buttons as the primary VS Code wrapper UX for sequential workflows.
- Keep `send: false` so the user reviews and approves the transition.
- Keep the text package in the response even when a button exists, because GitHub.com and other surfaces may ignore `handoffs:`.
- Use user-facing labels with `Next step:` or `Next action:`; keep `handoffs:` only as the technical frontmatter property.

## Review Fix Routing

For each actionable review finding, name one routing outcome:

- `delivery`: clear local fix with concrete validation.
- `planning`: larger design, ownership, or rollout decision required.
- `critical`: unresolved assumption or weak reasoning needs a pressure test.
- `defer`: intentionally delayed, with a reason and residual risk.

## Validation

- The next owner is already selected and exact.
- The package includes owner, scope, action, validation, and risk.
- The package includes `Continuation`, and includes `User action required` when
  `Continuation` is `waiting`.
- Decision Brief handoffs include target state, anti-scope, suggested owner,
  evidence source, validation path, known risks, and stop conditions.
- The transition remains user-visible and manual unless the user explicitly asked otherwise.
- The package does not restate the full lane-change matrix.
