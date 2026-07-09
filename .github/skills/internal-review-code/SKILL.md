---
name: internal-review-code
description: Use when reviewing a branch, pull request, work-in-progress diff, or code-focused change before merge or follow-up action.
---

# Internal Review Code

## Referenced skills

- `addyosmani-code-review-and-quality`: complete five-axis review core, approval standard, and finding categories.
- `awesome-copilot-security-review`: security-specialist depth only when the user explicitly asks for it.

## When to use

Use for a branch, pull request, work-in-progress diff, or code-focused change
that needs defect-first review before merge or before a follow-up patch
decision.

## Core contract

Use `addyosmani-code-review-and-quality` as the complete review engine and
follow its process end to end. This wrapper provides the stable
repository-owned entrypoint and the local boundaries below. It must not
redefine the core's five axes, review order, approval standard, finding
categories, structural remedies, or verification posture.

## Boundaries

- Review only the requested code surface and the supporting tests, spec, task,
  or validation evidence needed to judge it.
- Review tests before implementation when tests are present because that order
  belongs to the core contract.
- Do not apply fixes unless the user asks in a separate step.
- Do not load implementation-language skills or systems-level review skills
  merely because their file types or topics appear in the diff. Load a narrower
  owner only when the file type, runtime, or defect pattern would materially
  change the review.
- Do not load `awesome-copilot-security-review` automatically. Use it only when
  the user explicitly asks for security-specialist depth.
- Do not add another severity model, review lens set, workflow, or output
  template around the core.
- If the requested fixed point, diff, or code target is missing, invalid, or
  empty, stop at the core preflight and state the evidence gap.
- If no spec or task context exists, follow the core no-spec path and state the
  evidence gap.

## Validation

Before reporting the review, confirm that:

- the reviewed surface resolved to the intended non-empty diff or explicit
  read-only code target;
- tests were reviewed before implementation when tests were present;
- findings use the core finding categories consistently and do not add a second
  local severity scale;
- correctness and security issues lead the report before lower-leverage
  comments;
- any spec, task, or repository-standard claim cites its source, or the report
  states the evidence gap;
- security-specialist escalation was used only on explicit user request.
