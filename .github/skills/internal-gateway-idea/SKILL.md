---
name: internal-gateway-idea
description: Use when the user explicitly selects a conversation-first workflow to turn an early or unclear idea into a decision-ready analysis before any plan is requested.
---

# Internal Gateway Idea

## When to use

Use this skill only when the user explicitly selects it. Turn an early,
unclear, or anchored idea into a decision-ready analysis while keeping the
working material in the conversation by default. Do not infer invocation from
an idea-shaped request.

## Analysis unit lock

At the start of each analysis unit, record:

- `Subject`: one canonical subject for the analysis and any optional critical review;
- `Decision focus`: the decision the analysis must make possible;
- `Mode`: the current analysis mode;
- `Desired artifact`: none or the one Markdown artifact the user explicitly requests;
- `Implementation permission`: whether later implementation or execution has
  been explicitly requested;
- `Plan authoring readiness`: whether a retained spec is complete enough for a
  later explicit `+plan` selection.

The latest explicit subject or mode instruction wins. On a `subject-change` or
`mode-change`, park the prior unit with its capsule, start the new unit, and do
not silently reuse open decisions. In `analysis-only` mode, do not invoke
`/internal-tdd`, `/internal-gateway-writing-plans`, or
`/internal-gateway-execute-plans` before
the user explicitly selects a `+spec` or `+plan` Candidate acceptance action.
A `+spec` action authorizes only the selected spec artifact and records it as
`plan_authoring_ready: true` after verification. A later `+plan` action
authorizes only the plan-authoring handoff. `Implementation permission: false`
does not block plan authoring because neither action authorizes implementation
or execution.

## Autonomous route contract

This gateway owns one explicit, conversation-first route. Its owner is
`/internal-gateway-idea` and its default mode is `analysis-only`. The gateway
owns the analysis unit, evidence classification, decision eligibility,
recovery record, Candidate lifecycle, critical-review gate, finding
disposition, artifact selection, and authority envelope. A bounded interview
utility or critical-review procedure may provide its own mechanics, but
neither may replace this gateway's lifecycle, state, authority, acceptance, or
handoff decisions.

Before the user explicitly accepts a Candidate with `+spec` or `+plan`, do not
route to implementation-oriented design, TDD, plan authoring, or execution.
After `+plan` acceptance, the caller owns the separate plan-authoring handoff;
after explicit execution approval, `/internal-gateway-execute-plans` is the
sole execution handoff. The public `route_contract` projection must remain
aligned with these boundaries and may not introduce an alternate dependency,
route, invocation, or handoff.

## Global gates

This lifecycle has exactly two global gate types: `GRILL-ME` and `CRITICAL
REVIEW`. Recommendation, `save`, realignment, status, recovery, and the
four-option acceptance choice are actions or projections, not additional gate
types.

`GRILL-ME` is mandatory immediately after setup. Route every material doubt,
ambiguity, missing decision, or user-input question through `/grill-me`; do not
ask a material question in an ad-hoc route. A later round is allowed only when
new material decisions become eligible. Do not invent a repeat round for a
trivial or already-covered question, and do not impose a fixed question cap.
Record the gate event, the eligible decision IDs, and the question IDs in the
canonical recovery record. Interview mechanics and concrete phrasing remain
owned by `/grill-me`.

`CRITICAL REVIEW` is required before `close`, `+spec`, or `+plan`. The gateway
records completion as a structural review record, while review procedure and
report mechanics remain owned by `/internal-gateway-critical-master`. A review
is complete only when its record contains exactly three lenses, including one
lateral lens of type `analogy` or `reverse-assumption`, every finding has one
classification, and a non-empty conclusion is recorded. Use the approved
finding classes `blocking-now`, `acceptance-required`, `follow-up`,
`separate-design`, and `rejected-with-reason`.

An override must be explicit, name exactly one action, and record that action
as `accepted-risk`. It may bypass only the named action. Preserve every other
gate and authority boundary; an override never becomes a global bypass.
Findings require explicit disposition as `integrate`, `reject`,
`accept-risk`, or `route`; never integrate them automatically.

## Canonical recovery record

Maintain exactly one canonical recovery record for the active analysis unit.
The pause view, continuation input, compaction handoff, and any artifact
replay are projections of this record; they are not additional recovery
records or transcripts. The record must contain these projections together:

- `unit_lock`: `Subject`, `Mode`, `Decision focus`, `Desired artifact`, and
  `Implementation permission`;
- `state_capsule`: accepted, rejected, deferred, and accepted-risk decision
  IDs; eligible-now IDs; blocked-later IDs with prerequisites; evidence
  anchors; and the next action;
- `decision_ledger`: each stable `Decision ID`, state, basis, reopen condition,
  and dependencies;
- `authority_envelope`: the exact `Authorized paths` and `Authorized actions`,
  plus the unchanged continuation boundary;
- `communication_projection`: material deltas, outcome, up to three
  controlling evidence items, principal risk, active choice, blockers,
  unknowns, acceptance conditions, residual risks, and diagnostic word count.

Before continuation, promotion, artifact authoring, or recovery, verify that
all five projections are present and agree on the same subject and decision
IDs. If any projection is missing, contradictory, or cannot be reconstructed,
fail closed: mark affected decisions `open`, preserve the last valid record,
do not treat the recommendation as resolved, and do not add an authority path,
action, artifact, route, or handoff to repair the gap.

## Mutation authority envelope

Record two explicit sets for each unit: `Authorized paths` and `Authorized
actions`; an absent item is not authorized. The default is analysis-only:
reads, evidence recovery, non-mutating checks, and disposable temporary output
do not expand the grant, and writes are limited to the one explicitly selected
artifact path. This gateway has no standing grant for implementation, planning,
execution, or unrelated paths.

`continue`, `finish`, pause, compaction, and recovery preserve both sets and
may not add a path or action. Protected workflow status is separate from user
authority and cannot authorize a mutation. A requested item outside the sets is
blocked with outcome `authority-or-scope` until the user explicitly accepts the
scope delta; continuity, a resumed capsule, and a status marker are not
acceptance. `AUTH-03` depends on preserved `AUTH-01` authority.

Copy the authority envelope unchanged into every continuation and recovery
projection. A status marker, resumed capsule, or recovered decision does not
grant mutation authority.

## Ownership boundary

This gateway owns the analysis lifecycle, evidence discipline, option
comparison, recommendation, decision state, and one canonical Analysis Spec.
It does not own:

- interview mechanics or question formatting, which belong to `/grill-me`;
- critical-review procedure or report shape, which belong to
  `/internal-gateway-critical-master`;
- implementation-oriented design and design-spec writing, which require a
  separate explicit user-selected route;
- implementation planning or execution.

## Evidence posture

Begin by naming the decision the analysis should make possible. Keep the depth
proportional to the uncertainty and the user's desired outcome. Recover facts
from named local evidence before asking for them. Classify working material as
`Facts`, `Reports`, `Assumptions`, `Unknowns`, or `Constraints`, and preserve
those labels through every revision. A report's recommendation remains an
option until the user resolves the decision.

## Decision ledger and eligibility

Load [`references/decision-ledger.md`](references/decision-ledger.md) before building or updating the ledger; it owns states, priority, batching, and reopen rules.

## State capsule

Maintain one compact state capsule with exactly:

`Subject`; `Mode` and decision focus; accepted, rejected, deferred, and
accepted-risk IDs; eligible-now IDs; blocked-later IDs with prerequisites;
evidence anchors; and next action.

Update the ledger and capsule before and after `/grill-me`, on pause, context
compaction, `subject-change`, or `mode-change`, and before presenting a
Candidate. During ordinary turns, show only state deltas and the current
decision block. If reconstruction fails, mark affected decisions `open`
visibly and recover them before treating them as resolved.

## Workflow

Work through these branches in order. Reopen only a branch changed by new
evidence, a user decision, or a supported critical finding.

1. **Orient.** Set the analysis unit lock. Name the desired outcome, audience,
   time horizon, success criteria, scope, and anti-scope.
2. **Map the fog.** Separate the five evidence classes. Identify decision-
   changing unknowns, the evidence that could resolve them, and the constraints
   that must remain true.
3. **Resolve evidence and roots.** Build the ledger, mark roots and
   dependents, recover sufficient facts, and collect the current set of
   `eligible-now` decisions using the priority heuristic.
4. **Challenge the anchor.** Always challenge one actor, mechanism, constraint,
   or causal assumption internally. Show alternatives only when that challenge
   yields at least two materially credible mechanisms supported by evidence. If
   evidence and accepted constraints determine one feasible direction, converge
   directly. Record a credible rejected alternative whenever one exists.
5. **Route unresolved decisions.** When one or more eligible user decisions
   remain, invoke `/grill-me` once for the current round with exactly one of
   these packets per decision, in one numbered bulk question block:

   - `Decision ID`;
   - `Open decision`;
   - `Material impact`;
   - `Evidence checked`;
   - `Remaining gap`;
   - `Prerequisites`.

   `/grill-me` owns concrete phrasing, recommendations, defaults, ordering,
   follow-ups, and the resolved summary. Do not duplicate its interview
   contract. Keep every decision open until its returned resolved summary is
   available; accept a default only when that summary explicitly returns it.
   Later decisions that become eligible are collected into a subsequent
   numbered block, including a numbered one-item block when only one remains.
6. **Converge.** Compare options against the desired outcome, success criteria,
   evidence quality, constraints, and anti-scope. Recommend one direction and
   record why credible alternatives were rejected.
7. **Stress-test.** Record material risks, dependencies, disconfirming signals,
   deferred questions, accepted risks, and the evidence that would change the
   recommendation.
8. **Present the Candidate.** Do so only when every material assumption is
   resolved, visibly deferred, or explicitly accepted as risk, and the
   recommendation is traceable to accepted decisions and labeled evidence.

### Post-Candidate menu and gate

After setup and after every named analysis phase, present the same seven
numbered semantic entries in the same positions. Keep locked entries visible
and give a short reason; do not remove, renumber, or silently unlock an entry:

1. `🔄 continue`
2. `🔍 critical review`
3. `🧩 realign when findings exist`
4. `📝 +spec`
5. `🗺️ +plan`
6. `💾 save`
7. `⏹️ close`

Before `CRITICAL REVIEW` completes, lock `+spec`, `+plan`, and `close` with
the reason `critical review is pending`. Lock `realign` when no findings
exist. Keep `continue`, `save`, and the applicable gate action visible. After
review, retain all seven positions and explain any remaining lock, including
an explicit finding disposition requirement. The post-setup menu does not
replace the mandatory `GRILL-ME` gate.

Critical review must complete before `+spec`, `+plan`, or `close` is
available, except for one explicit named-action override recorded as
`accepted-risk`. Findings never integrate automatically; require explicit
choice to incorporate, reject with evidence, accept as residual risk, or
route each material finding. No menu action grants implementation or
execution, and `continue`, `finish`, `save`, and `close` preserve the
authority envelope.

`save` is a non-promoting checkpoint and remains available before or after
critical review. A pre-review save must record `critical_review: pending` in
the one canonical recovery/artifact projection. Save never makes `+spec` or
`+plan` available, closes a finding, authorizes implementation or execution,
or creates a second artifact.

Completion criterion: the recommendation is traceable to resolved decisions and labeled evidence, every material uncertainty is resolved/deferred/accepted as visible risk, and the latest state capsule is current.

## Chat layout

Before presenting a Candidate, opening acceptance, running critical review,
authoring an accepted artifact, or persisting state, load
[`references/candidate-and-persistence.md`](references/candidate-and-persistence.md).
It owns the compact chat projection, stable Analysis Spec fields, acceptance
gate, review integration, artifact handoff, and persistence route.

## Candidate Analysis Spec

Use the field set and promotion rules in
`references/candidate-and-persistence.md`; the Candidate remains unaccepted
until critical review and an explicit promotion choice complete.

## Critical review procedure

Invoke `/internal-gateway-critical-master` with the Candidate as canonical
subject. Apply the disposition and realignment rules in
`references/candidate-and-persistence.md`; this gateway retains lifecycle and
authority ownership.

## Pause and persistence

Use the persistence route in `references/candidate-and-persistence.md` for
pause, save, cross-chat continuation, or accepted artifact creation.
