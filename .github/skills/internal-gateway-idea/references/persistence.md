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

`save` is a non-promoting analysis checkpoint. Write at most one Markdown
artifact when the user selects `save` or explicitly authorizes a continuation
checkpoint at the supplied path. Without a path, use
`tmp/superpowers/specs/YYYY-MM-DD-<topic>-analysis.md`, disclose disposable
`tmp/`, and update that file in place. It holds the Candidate and recovery
record, including classifications and `accepted-risk`.
Saving does not close the review gate.

`+spec` is a separate specialist handoff. It does not create or update the
analysis checkpoint or authorize another path/action. The specialist owns the
work spec and tracker publication. Bind its spec reference and accepted
decision IDs in the existing recovery record's artifact event; persist only
when its authority envelope allows it. No report, transcript, recovery record,
state, gate, or second artifact.

When the producer exposes content identity or version, bind and recheck it on
replay or `+plan`. Otherwise compare observable accepted contents with the
active unit and decision IDs; record only that comparison, never an invented
identity, hash, or strong guarantee. Unavailable or uncomparable content is
not-ready until reverified. After verified `+spec`, record
`plan_authoring_ready: true`; later explicit `+plan` uses the retained spec
and the single path returned by `/internal-gateway-writing-plans`. This
gateway does not create that plan, and execution still needs explicit
approval.
