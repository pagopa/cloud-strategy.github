---
name: internal-review-code
description: Use when reviewing a branch, pull request, work-in-progress diff, or code-focused change before merge or follow-up action.
---

# Internal Review Code

## Referenced skills

- `/addyosmani-code-review-and-quality`: complete and sole code-review engine,
  including its review reasoning, severity, categories, and approval standard.
- `/awesome-copilot-security-review`: security-specialist depth only when the
  user explicitly asks for it.
- `addyosmani-code-simplification`: on-demand remediation owner for an
  explicitly approved, behavior-preserving simplification follow-up; never
  part of the review pass.

## When to use

Use for a branch, pull request, work-in-progress diff, or code-focused change
that needs defect-first review before merge or a separate follow-up decision.

## Repository wrapper

Use `/addyosmani-code-review-and-quality` as the complete review engine. This
wrapper owns only repository preflight, target boundaries, escalation rules,
the detailed-to-chat projection, and final validation. It must not restate the
engine's review axes, procedure, approval standard, finding categories, or
remediation workflow.

The core owns review reasoning and severity. This wrapper owns the public chat projection.
The projection may reorder and compress supported evidence, but it
must not introduce another review axis, severity model, approval standard, or
remediation workflow.

## Boundaries

- Resolve a concrete, non-empty diff or explicit read-only code target before
  review; state the evidence gap when the target, fixed point, or context is
  missing.
- Read the spec, task, and tests before implementation when those sources
  exist. Review only the requested code surface and immediate evidence.
- Do not edit files, apply fixes, author plans, or delegate to peer agents.
- Load `/awesome-copilot-security-review` only on explicit user request.
- Name `addyosmani-code-simplification` only as a separate simplification
  follow-up for a concrete readability or complexity finding.
- Do not load or execute `addyosmani-code-simplification` during the review pass.
- Project the result through the shared `🔎`, `📌`, `🧪`, and `👉` semantics.

## Completion criteria

The review is complete only when the target is resolved and non-empty, core
categories are used without a second severity scale, claims are source-backed
or marked as explicit evidence gaps, every blocking and important finding is
preserved, and the report contains one boundary-safe next action.

## Public projection

Start with exactly four fields in this order:

- `🔎`: localized verdict and counts by severity.
- `📌`: one sentence explaining why that verdict follows.
- `🧪`: reviewed scope, completed validation, and material evidence gaps.
- `👉`: one user action and the consequence of accepting it.

For each material finding, preserve `Location`, `Evidence`, `Impact`,
`Correction`, and `Expected verification` when closure is not obvious. Map the
engine's categories to `B`, `I`, and `S` identifiers, show every blocking and
important finding, consolidate equivalent findings, and mark uncertainty inline
as `to confirm`.

Keep internal review details hidden unless they alter the verdict. State that
no changes were applied, and offer remediation only as a separate follow-up.

## Validation

Before reporting, verify the completion criteria, source evidence, target scope,
security escalation boundary, and separate simplification follow-up. Keep
no-findings or merge-readiness claims behind
`/superpowers-verification-before-completion`.
