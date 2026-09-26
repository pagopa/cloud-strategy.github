# Pause and Persistence

Conversation-only analysis is the default.

## Recovery record

Store and recover these projections together as the one canonical recovery
record:

- `unit_lock`: `Subject`, `Mode`, `Decision focus`, `Desired artifact`, and
  `Implementation permission`;
- `state_capsule`: accepted, rejected, deferred, and accepted-risk decision
  IDs; eligible-now IDs; blocked-later IDs with prerequisites; evidence
  anchors; and the next action;
- `decision_ledger`: each stable `Decision ID` with state, basis, reopen
  condition, and dependencies;
- `authority_envelope`: the exact `Authorized paths` and `Authorized actions`
  plus the unchanged continuation boundary;
- `communication_projection`: material deltas, one outcome, up to three
  controlling evidence items, one principal risk, active choice, blockers,
  unknowns, acceptance conditions, residual risks, and diagnostic word count.

The record also carries the gate and menu projection:

- `global_gates`: exactly `GRILL-ME` and `CRITICAL REVIEW`;
- `grill_me`: the post-setup gate event, eligible decision IDs, question IDs,
  route owner, and any repeat-round eligibility evidence;
- `critical_review`: `pending` or `completed`, its lens records, classified
  findings, conclusion, and disposition state;
- `gate_override`: absent unless one named action is recorded as
  `accepted-risk`;
- `menu`: the seven entries with positions, availability, and lock reasons.

Gate state is structural recovery data, not a second report or transcript.
Never infer that a recommendation, checkpoint, status, or recovery event
completed a gate. A missing or contradictory projection triggers the
fail-closed rule in `SKILL.md`.

## Pause view

On pause, return this projection of the state capsule and carry the authority
envelope unchanged:

```markdown
## ⏸️ Resume from here

- `❓ Active decision block`
- `🔎 Key unknown`
- `➡️ Next branch`
- `🔒 Closed decisions`
```

Rebuild it from the capsule after compaction, a subject change, or a mode
change. Mark the decision of any unrecoverable field `open`.

## Artifact

Create an analysis file only when the user selects `save` or `+spec`, or asks
to continue in another conversation. Write at most one Markdown artifact at the
supplied path. Without a path, use
`tmp/superpowers/specs/YYYY-MM-DD-<topic>-analysis.md`, disclose that `tmp/` is
disposable, and update that same file in place. Saving does not close the
review gate.

The artifact holds the current Candidate or Consolidated Analysis Spec and the
full recovery record, including finding classifications and any named-action
`accepted-risk` override, so planning replay is lossless without the
transcript. Never create a separate critical report, transcript, or second
analysis artifact.

After a verified `+spec`, record `plan_authoring_ready: true` and state that
plan authoring stays available through a later explicit `+plan`. `+plan` uses
the retained spec and the single plan path locked by
`/internal-gateway-writing-plans`; this gateway does not create or structure
that plan. After `+plan`, state that execution is a separate action that needs
explicit approval.
