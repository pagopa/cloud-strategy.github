---
name: internal-agent-next-step
description: Use when a repository-owned agent or prompt needs to package an already-chosen next owner, scope, action, validation path, and risk note for a user-visible transition.
---

# Internal Agent Next Step

Use this skill to format the next step after the next owner has already been chosen or confirmed. It keeps sequential workflows compact, explicit, and user-visible without turning canonical agents into hidden routers.

## When to use

- `internal-planning-leader` recommends moving from planning to delivery, review, or critical challenge.
- `internal-review-guard` finishes defect-first analysis and needs to route actionable findings to delivery, planning, critical challenge, or deferred follow-up.
- A prompt needs a consistent handoff package that survives surfaces where VS Code `handoffs:` buttons are not available.
- `internal-delivery-operator` or `internal-critical-master` wants optional support for a compact next-step recommendation after its own lane is complete.

## When not to use

- Do not use this skill to choose the next owner from scratch; use `internal-agent-lane-change-engine` when the lane no longer fits.
- Do not use it to dispatch another agent, auto-submit a handoff, or bypass user approval.
- Do not duplicate the lane-change recommendation matrix here.

## Package Contract

When a next step is needed, include this compact package:

- `Owner`: exact next agent or skill owner already selected.
- `Scope`: files, directories, artifacts, or decision surface in scope.
- `Action`: one concrete next action the next owner should take.
- `Validation`: command, review path, evidence, or explicit gap the next owner must address.
- `Risk`: residual risk, rollback note, or reason the transition should stay manual.

Keep the package short. Prefer one line per field unless the validation path or risk note genuinely needs more detail.

## VS Code Handoffs

- Treat `handoffs:` buttons as the primary VS Code UX for sequential workflows.
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
- The transition remains user-visible and manual unless the user explicitly asked otherwise.
- The package does not restate the full lane-change matrix.
