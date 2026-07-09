---
name: internal-review-code
description: Use when reviewing a branch, pull request, work-in-progress diff, or code changes since a fixed point against repository standards and an originating spec.
---

# Internal Review Code

## Referenced skills

- `addyosmani-code-review-and-quality`: operating core for the fixed-point Standards and Spec review.

## When to use

Use for a branch, pull request, work-in-progress diff, or code change that must
be reviewed against repository standards and its originating spec.

## Core contract

Use `addyosmani-code-review-and-quality` as the complete review engine and follow its
process end to end. This wrapper provides the stable repository-owned entrypoint
and the local context below; it does not redefine the core's axes, process, or
output.

## Repository context

- Treat `AGENTS.md` and any narrower owner instructions that govern the changed
  files as Standards sources.
- Apply repository precedence when standards conflict: direct user instructions,
  then the nearest owner, then broader repository policy.
- If `docs/agents/issue-tracker.md` is absent, do not assume an issue-tracker
  integration. Continue through the core's other Spec sources, then use its
  no-spec path when none is available.
- Keep Standards and Spec findings separate as required by the core.

## Boundaries

- Review the diff; do not apply fixes unless the user asks in a separate step.
- Do not load implementation-language skills or systems-level review skills
  merely because their file types or topics appear in the diff.
- Do not add another severity model, review lens set, workflow, or output
  template around the core.
- If the fixed point is missing, invalid, or produces an empty diff, stop at the
  core preflight.
- If no spec exists, follow the core's no-spec path and state the evidence gap.

## Validation

Before reporting the review, confirm that:

- the fixed point resolved and the reviewed diff is the intended non-empty diff;
- each Standards finding cites the governing repository rule or is labelled as
  a judgement-call smell;
- each Spec finding cites its source, or the report states that no spec was
  available;
- the two core axes remain separate in the final report.
