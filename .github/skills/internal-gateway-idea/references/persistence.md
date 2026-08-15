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

Create an analysis file only when the user explicitly selects `💾 Save the
analysis`, selects the `+ spec` acceptance action, or asks to continue in
another conversation. Write at most one Markdown artifact at the supplied
path. When no path is supplied for the analysis artifact, use
`tmp/superpowers/specs/YYYY-MM-DD-<topic>-analysis.md`, disclose that `tmp/` is
disposable, and update that same file in place.

The artifact must contain the current Candidate or Consolidated Analysis Spec,
its state capsule, evidence anchors, next action, and the one canonical
communication projection: material deltas, one outcome, up to three controlling
evidence items, one principal risk, active choice, blockers, unknowns,
acceptance conditions, and residual risks. This keeps planning replay lossless
without the transcript. Do not create a separate critical report or transcript
and do not save twice as separate artifacts. A `+ plan` acceptance action uses
the single retained plan path locked by `/internal-gateway-writing-plans`;
this gateway does not create or structure that plan directly.

After `+ spec` acceptance, state that implementation-oriented design, planning,
and execution remain separate explicitly requested actions. After `+ plan`
acceptance, state that execution remains a separate action requiring explicit
approval. In both cases, do not invoke execution or imply that artifact
acceptance authorizes it.
