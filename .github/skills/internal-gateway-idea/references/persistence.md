# Pause and Persistence

Conversation-only analysis is the default. On pause, return this compact state:

## ⏸️ Resume from here

- `❓ Active decision block`
- `🔎 Key unknown`
- `➡️ Next branch`
- `🔒 Closed decisions`

The pause view is a readable projection of the current state capsule. Rebuild
it from the capsule after context compaction, a subject change, or a mode
change. If a field cannot be recovered, mark the affected decision `open`.
Carry the current `Authorized paths` and `Authorized actions` with the resume
projection as an authority boundary, not as a new state-capsule decision. A
pause, continuation, or recovery never expands that envelope, and a protected
status never supplies user authority.

The state capsule, decision ledger, authority envelope, and canonical
communication projection must be stored and recovered as one canonical
recovery record. The resume view is only a projection of that record. Before
continuing or authoring, verify the unit lock, stable decision IDs and states,
evidence anchors, exact authority sets, next action, and communication fields:
material deltas, outcome, up to three controlling evidence items, principal
risk, active choice, blockers, unknowns, acceptance conditions, residual
risks, and diagnostic word count. If any required projection is missing or
conflicting, fail closed, preserve the last valid record, and leave affected
decisions `open`; do not infer a path, action, decision, or acceptance.

The same recovery record also carries the gate and menu projection:

- `global_gates`: exactly `GRILL-ME` and `CRITICAL REVIEW`;
- `grill_me`: the post-setup gate event, eligible decision IDs, question IDs,
  route owner, and any repeat-round eligibility evidence;
- `critical_review`: `pending` or `completed`, its exactly three lens records,
  lateral lens type, classified findings, conclusion, and explicit
  disposition state;
- `gate_override`: absent unless one named action is explicitly recorded as
  `accepted-risk`, with all other gates preserved;
- `menu`: the same seven numbered entries, their positions, availability, and
  short lock reasons for the current phase.

The gate state is structural recovery data, not a second report or transcript.
On reconstruction, reject a missing or contradictory gate/menu projection and
preserve the last valid record. Never infer that a recommendation, checkpoint,
status, or recovery event completed a gate.

Create an analysis file only when the user explicitly selects `💾 Save the
analysis`, selects the `+ spec` acceptance action, or asks to continue in
another conversation. Write at most one Markdown artifact at the supplied
path. When no path is supplied for the analysis artifact, use
`tmp/superpowers/specs/YYYY-MM-DD-<topic>-analysis.md`, disclose that `tmp/` is
disposable, and update that same file in place.

`Save the analysis` is a non-promoting checkpoint and may occur before or
after critical review. A pre-review checkpoint records
`critical_review: pending` in this same canonical projection. Saving does not
make `+spec` or `+plan` available, does not dispose of findings, does not close
the review gate, and does not authorize implementation or execution.

The artifact must contain the current Candidate or Consolidated Analysis Spec,
its state capsule, evidence anchors, next action, and the one canonical
communication projection: material deltas, one outcome, up to three controlling
evidence items, one principal risk, active choice, blockers, unknowns,
acceptance conditions, and residual risks. It must also preserve the gate
state, menu locks, finding classifications, and any named-action
`accepted-risk` override. This keeps planning replay lossless without the
transcript. Do not create a separate critical report or transcript and do not
save twice as separate artifacts. A `+ plan` acceptance action uses
the single retained plan path locked by `/internal-gateway-writing-plans`;
this gateway does not create or structure that plan directly.

After `+ spec` acceptance, state that implementation-oriented design, planning,
and execution remain separate explicitly requested actions. After `+ plan`
acceptance, state that execution remains a separate action requiring explicit
approval. In both cases, do not invoke execution or imply that artifact
acceptance authorizes it.
