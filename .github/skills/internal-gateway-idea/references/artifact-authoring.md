# Artifact Authoring After Acceptance

The selected acceptance action controls one next artifact and does not change
domain ownership. Authoring consumes the one canonical recovery record without
creating a parallel record, transcript, or critical-review artifact. If its
projections disagree, stop and preserve the last valid record. The exact
`Authorized paths` and `Authorized actions` remain unchanged; a new path or
action is `authority-or-scope` until explicitly accepted.

## `+spec`

Build one handoff from the recovery record containing the accepted decisions,
labeled evidence, subject and decision focus, scope, anti-scope, critical-review
dispositions, and exact authority envelope. Before invoking, require exact
authority for the tracker destination, publication, and `ready-for-agent`
label; otherwise block as `authority-or-scope`. Invoke `/mattpocock-to-spec`
directly; if it is not loaded, stop and ask the user to mention it. The
specialist owns the template, tracker, and label; do not
duplicate output or ask a new design question.

When the specialist returns, verify that the spec reference points to the
active unit. If it exposes a content identity or version, bind and recheck it
against accepted decisions. Otherwise compare observable accepted contents
with the unit and decision IDs, recording only that comparison; never invent
an identity, hash, or stronger guarantee. Unavailable or uncomparable content
is not ready. Record the binding or comparison in the existing recovery event.
Replay and `+plan` repeat this check; changed or unavailable content does not
inherit `plan_authoring_ready: true`.

Pass accepted Testing Decisions and boundaries directly to
`/mattpocock-to-spec`; do not repeat an interview. A materially new test or
specification decision returns through existing `/grill-me` eligibility and
reevaluation before accepting the work spec. This adds no gate.

Only after that verification record `plan_authoring_ready: true` and wait for a
later explicit `+plan`. This action never authorizes implementation or
execution.

## `+plan`

Route to `/internal-gateway-writing-plans`. It wraps
`/addyosmani-planning-and-task-breakdown`, which owns task decomposition,
template, checkpoints, and planning quality. Pass the verified spec binding,
accepted decisions, evidence, target, anti-scope, repository deltas, and
authority unchanged. The writer returns the exact retained plan path and the
actual task target; unresolved source or task references block the handoff.
This gateway never starts execution. Only the user invokes
`/internal-gateway-execute-plans`.
