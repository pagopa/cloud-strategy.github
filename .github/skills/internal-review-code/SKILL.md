---
name: internal-review-code
description: Use when reviewing a branch, pull request, work-in-progress diff, or code-focused change before merge or follow-up action.
---

# Internal Review Code

## Review engine

Use `/addyosmani-code-review-and-quality` as the complete and sole review
engine. The core owns review reasoning and severity. This wrapper owns the public chat projection,
repository preflight, target boundaries, escalation rules, and final validation. It must not restate the engine's review axes,
procedure, approval standard, or finding categories.

## Conditional domain contributors

When the read-only target includes `.github/workflows/**`, conditionally load
`/internal-github-actions` as a domain contributor. When it includes
`.github/actions/**/action.y*ml`, conditionally load
`/internal-github-action-composite`. When both surfaces are present, load both;
unrelated code activates neither. Use
[the contributor protocol](references/actions-contributor-protocol.md) for the
activation boundary and record shape.

Contributors are bounded observers inside this review flow. They may return
domain observations, changed contract surfaces, execution-chain probes,
applicable validations, compatibility risks, and evidence gaps. The wrapper
passes those observations into the one Addy review and retains ownership of
target preflight, provenance, differential sequence, coverage counter-analysis,
severity projection, and the exact public verdicts. Contributors do not emit a
verdict, severity, approval, merge decision, remediation plan, or replacement
review procedure.

For workflow and composite targets, inspect linked static evidence from the
event through the workflow, reusable workflow or job permissions/environment,
composite action, repository script, artifact, or external-system boundary
when those links are present. Static review does not establish live runner
health or runtime behavior; route that evidence to the appropriate operations
owner and record the gap.

## When to use

Use when reviewing a code-focused branch, pull request, work-in-progress diff,
or explicit read-only code target before merge or a separately authorized
follow-up.

## Review preflight

Before substantive review, resolve the concrete target and fully load the
declared review engine from its resolved source. Record the target identity,
target fingerprint, engine identity, and source. If the target is empty or the
engine identity or resolved source cannot be confirmed, stop with
`REVIEW BLOCKED` and name the missing evidence.

The review is report-only. Planning, remediation, and other state-changing
follow-ups require a separate explicit request outside the current review.

## Ordered repository review

Run this sequence after the review preflight:

1. Resolve the fixed point or explicit read-only target once. Fail on a bad
   reference or empty target, and record target identity.
2. Record the target fingerprint, commit list when applicable, requested code
   surface, and impacted-validation surface.
3. Discover repository Standards sources and the originating Spec sources or
   task source. Cite them or record `to confirm`.
4. Run the Addy engine without restating its five review axes.
5. Compare the diff against missing/partial requirements, wrong implementation,
   and scope creep.
6. Derive concrete adversarial probes from the changed contracts, assumptions,
   boundaries, and observed evidence.
7. Apply green-test anchoring: treat green tests as evidence only and ask
   which defect classes they would fail to catch.
8. Run a final coverage counter-analysis before approval and project severity
   to `BLOCKER`, `IMPORTANT`, and `SUGGESTION`.

The wrapper owns the repository-specific differential sequence; Addy owns the
substantive review standard. Security stays inside the engine's security axis
for the whole review pass. A readability or complexity correction may be
proposed, but no separate simplification runtime is loaded.

## Boundaries

- Resolve a concrete, non-empty diff or explicit read-only code target before
  review; state the evidence gap when the target, fixed point, or context is
  missing.
- Read the spec, task, and tests before implementation when those sources
  exist. Review only the requested code surface and immediate evidence.
- During the review pass, do not edit files, apply fixes, or author plans.
- Keep the review pass report-only. Planning or remediation requires a
  separate explicit request and remains outside the current review.

## Completion criteria

The review is complete only when the target is resolved and non-empty, the
engine's categories are used without a second severity scale, claims are
source-backed or marked as explicit evidence gaps, every blocking and
important finding is preserved, and the report contains one boundary-safe next
action.

## Public projection

Start with exactly four fields in this order:

- `🔎`: localized verdict and counts by severity.
- `📌`: one sentence explaining why that verdict follows.
- `🧪`: reviewed scope, completed validation, and material evidence gaps.
- `👉`: one user action and the consequence of accepting it.

For each material finding, preserve `Location`, `Evidence`, `Impact`,
`Correction`, and `Expected verification` when closure is not obvious. Map the
engine category using this table, show every blocking and important finding,
consolidate equivalent findings, and mark uncertainty inline as `to confirm`.
The localized verdict in `🔎` must be exactly one of `MERGE READY`,
`CHANGES REQUIRED`, or `REVIEW BLOCKED`. Use `MERGE READY` for an approval
result, `CHANGES REQUIRED` when blocking findings remain, and `REVIEW BLOCKED`
when the preflight evidence is insufficient to conduct the review. Number
public finding identifiers by label, such as `BLOCKER-1`, `IMPORTANT-1`, and
`SUGGESTION-1`.

| Engine category | Projection label | Rule |
| --- | --- | --- |
| Critical | `BLOCKER` | Blocking finding. |
| Required change | `BLOCKER` | Blocking required change by default. |
| Optional / Consider | `SUGGESTION` | Non-blocking suggestion. |
| Nit | `SUGGESTION` | Non-blocking suggestion. |
| FYI | — | Omit unless it changes the verdict. |

Use `IMPORTANT` for a correction or follow-up that does not independently
block merge. It is not a third undefined severity scale.

This mapping depends on the imported engine's categories; after an engine
refresh, rerun the review-engine contract before relying on this projection.

Keep internal review details hidden unless they alter the verdict. State that
no changes were applied. For request-changes results, invite the user to
manually select named finding IDs for a separately authorized plan-only
follow-up. Approval results state that no user action is required.

## Validation

Before reporting, verify the completion criteria, source evidence, target scope,
the review escalation boundary, and the separate follow-up boundary.
