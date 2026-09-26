---
name: internal-gateway-idea
description: Use when the user explicitly selects a conversation-first workflow to turn an early or unclear idea into a decision-ready analysis before any plan is requested.
---

# Internal Gateway Idea

Turn an early, unclear, or anchored idea into a decision-ready analysis while
keeping the working material in the conversation by default.

## When to use

- Use this skill only when the user explicitly selects it.
- Do not infer invocation from an idea-shaped request.

## Analysis unit lock

At the start of each analysis unit, record `Subject` (one canonical subject
for the analysis and any critical review), `Decision focus` (the decision the
analysis must make possible), `Mode` (only `analysis-only` is defined),
`Desired artifact` (none or the one explicitly requested Markdown artifact),
and `Implementation permission` (whether later implementation or execution
was explicitly requested).

The latest explicit subject or mode instruction wins. On a `subject-change` or
`mode-change`, park the prior unit with its capsule, start a new unit, and do
not silently reuse open decisions.

In `analysis-only` mode, do not invoke `/internal-tdd`,
`/internal-gateway-writing-plans`, `/internal-gateway-execute-plans`, or
implementation-oriented design before the user explicitly selects `+spec` or
`+plan`. `+spec` authorizes only the selected spec artifact and records
`plan_authoring_ready: true` after verification. A later `+plan` authorizes
only the plan-authoring handoff. `Implementation permission: false` does not
block plan authoring; neither action authorizes implementation or execution.

## Autonomous route contract and ownership

`/internal-gateway-idea` owns one explicit, conversation-first
`analysis-only` route: the analysis unit and lifecycle, evidence
classification, decision state and eligibility, the recovery record, option
comparison, recommendation, the Candidate and one canonical Analysis Spec, the
critical-review gate, finding disposition, artifact selection, and the
authority envelope.

It does not own interview mechanics (`/grill-me`), critical-review procedure
or report shape (`/internal-gateway-critical-master`), implementation-oriented
design (a separate user-selected route), or planning and execution. A utility
may supply mechanics but never replaces this gateway's lifecycle, state,
authority, acceptance, or handoff decisions. After `+plan`, the caller owns the
plan-authoring handoff; after explicit execution approval,
`/internal-gateway-execute-plans` is the sole execution handoff. The public
`route_contract` must match these boundaries and add no alternate route,
dependency, or handoff.

## Global gates

There are exactly two global gate types: `GRILL-ME` and `CRITICAL REVIEW`.
Recommendation, `save`, realignment, status, recovery, and menu choices are
actions or projections, not gates.

`GRILL-ME` is mandatory immediately after setup. Route every material doubt,
ambiguity, missing decision, or user-input question through `/grill-me`; never
ask a material question ad hoc. Run a later round only when new material
decisions become eligible; do not repeat trivial or already-covered questions,
and impose no fixed question cap. Record the gate event, eligible decision IDs,
and question IDs in the recovery record.

`CRITICAL REVIEW` is required before `close`, `+spec`, or `+plan`. It is
complete only when its record has at least three lenses with a lateral third
(`analogy` or `reverse-assumption`), one class per finding, and a non-empty
conclusion. Finding classes are `blocking-now`, `acceptance-required`,
`follow-up`, `separate-design`, and `rejected-with-reason`. Each finding needs
an explicit disposition, `integrate`, `reject`, `accept-risk`, or `route`, and
never integrates automatically.

An override must be explicit, name exactly one action, and be recorded as
`accepted-risk`. It bypasses only that action; every other gate and authority
boundary stays in force.

## Recovery record and state capsule

Keep exactly one canonical recovery record for the active unit, with the
projections `unit_lock`, `state_capsule`, `decision_ledger`,
`authority_envelope`, and `communication_projection`. Pause views,
continuation input, compaction handoffs, and artifact replays are projections
of it, never extra records or transcripts.

The state capsule holds `Subject`, `Mode`, decision focus; accepted, rejected,
deferred, and accepted-risk decision IDs; eligible-now IDs; blocked-later IDs
with prerequisites; evidence anchors; and the next action. Update the ledger
and capsule before and after `/grill-me`, on pause, compaction,
`subject-change`, or `mode-change`, and before presenting a Candidate. In
ordinary turns, show only state deltas and the current decision block.

Before continuation, promotion, authoring, or recovery, verify that all
projections exist and agree on subject and decision IDs. Otherwise fail closed:
mark affected decisions `open` visibly, preserve the last valid record, do not
treat the recommendation as resolved, and add no path, action, artifact,
route, or handoff to repair the gap.

## Mutation authority envelope

Record two explicit sets per unit: `Authorized paths` and
`Authorized actions`; anything absent is not authorized. Reads, evidence
recovery, non-mutating checks, and disposable temporary output do not expand
the grant, and writes are limited to the one explicitly selected artifact
path. There is no standing grant for implementation, planning, execution, or
unrelated paths.

`continue`, `finish`, `save`, `close`, pause, compaction, and recovery
preserve both sets and never add to them; copy the envelope unchanged into
every continuation and recovery projection. A request outside the sets is
blocked as `authority-or-scope` until the user explicitly accepts the scope
delta. Continuity, a resumed capsule, a recovered decision, and a protected
workflow status never grant authority.

## Evidence posture

Name the decision the analysis must enable, and keep depth proportional to the
uncertainty and desired outcome. Recover facts from named local evidence
before asking. Classify working material as `Facts`, `Reports`,
`Assumptions`, `Unknowns`, or `Constraints`, and keep those labels through
every revision. A report's recommendation stays an option until the user
resolves the decision.

## Workflow

Work through these branches in order. Reopen a branch only on new evidence, a
user decision, or a supported critical finding.

1. **Orient.** Set the unit lock. Name the desired outcome, audience, time
   horizon, success criteria, scope, and anti-scope.
2. **Map the fog.** Separate the five evidence classes. Identify
   decision-changing unknowns, the evidence that could resolve them, and the
   constraints that must hold.
3. **Resolve evidence and roots.** Load
   [`references/decision-ledger.md`](references/decision-ledger.md), which owns
   states, priority, batching, and reopen rules. Build the ledger, mark roots
   and dependents, recover sufficient facts, and collect the current
   `eligible-now` decisions.
4. **Challenge the anchor.** Always challenge one actor, mechanism,
   constraint, or causal assumption internally. Show alternatives only when at
   least two evidence-supported mechanisms stay credible; otherwise converge
   directly. Record any credible rejected alternative.
5. **Route unresolved decisions.** Invoke `/grill-me` once per round with one
   numbered bulk block holding one packet per eligible decision: `Decision ID`,
   `Open decision`, `Material impact`, `Evidence checked`, `Remaining gap`, and
   `Prerequisites`. `/grill-me` owns phrasing, recommendations, defaults,
   ordering, follow-ups, and the resolved summary. Keep each decision open
   until its resolved summary returns; accept a default only when that summary
   explicitly returns it. Collect later eligible decisions into the next
   numbered block, even a one-item block.
6. **Converge.** Compare options against the outcome, success criteria,
   evidence quality, constraints, and anti-scope. Recommend one direction and
   record why credible alternatives were rejected.
7. **Stress-test.** Record material risks, dependencies, disconfirming
   signals, deferred questions, accepted risks, and the evidence that would
   change the recommendation.
8. **Present the Candidate** only when every material assumption is resolved,
   visibly deferred, or accepted as risk, and the recommendation traces to
   accepted decisions and labeled evidence.

**Complete when** the recommendation traces to resolved decisions and labeled
evidence, every material uncertainty is resolved, deferred, or accepted as
visible risk, and the state capsule is current.

## Phase menu and gate

After setup and after every named phase, show the same seven numbered entries
in the same positions. Keep locked entries visible with a short reason; never
remove, renumber, or silently unlock one:

1. `🔄 continue`
2. `🔍 critical review`
3. `🧩 realign when findings exist`
4. `📝 +spec`
5. `🗺️ +plan`
6. `💾 save`
7. `⏹️ close`

Before `CRITICAL REVIEW` completes, lock `+spec`, `+plan`, and `close` with
the reason `critical review is pending`, unless one named-action override is
recorded. Lock `realign` when no findings exist. After review, entries 4 to 7
are the acceptance actions; explain any remaining lock, including a pending
finding disposition. Only `+spec` and `+plan` promote the Candidate. The menu
does not replace the `GRILL-ME` gate, and no menu action grants
implementation or execution.

`save` is a non-promoting checkpoint, available before or after review. A
pre-review save records `critical_review: pending`. Save never unlocks
`+spec` or `+plan`, closes a finding, or creates a second artifact.

## References by phase

Load only the reference the current action needs:

| Action | Reference |
| --- | --- |
| Present a Candidate, run critical review, realign, or accept | [`candidate-and-persistence.md`](references/candidate-and-persistence.md) |
| Pause, `save`, compaction, recovery, or cross-chat continuation | [`persistence.md`](references/persistence.md) |
| Author the artifact after `+spec` or `+plan` | [`artifact-authoring.md`](references/artifact-authoring.md) |
