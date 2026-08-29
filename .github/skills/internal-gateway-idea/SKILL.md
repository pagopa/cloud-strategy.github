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
- `Implementation permission`: whether a later design, planning, or execution action has been explicitly requested.

The latest explicit subject or mode instruction wins. On a `subject-change` or
`mode-change`, park the prior unit with its capsule, start the new unit, and do
not silently reuse open decisions. In `analysis-only` mode, do not invoke
`/internal-tdd`, `/internal-gateway-writing-plans`, or
`/internal-gateway-execute-plans` before
the user explicitly selects a `+spec` or `+plan` Candidate acceptance action.
A `+spec` action authorizes only the selected spec artifact; a `+plan` action
authorizes only the selected plan-authoring handoff. Neither action authorizes
implementation or execution.

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

Give every material decision a stable `Decision ID`. The compact ledger stores
only:

- `Decision ID`;
- decision or constraint;
- status;
- basis;
- reopen condition;
- dependencies.

Use these decision states:

- `eligible-now`: an open decision with no unresolved prerequisite;
- `blocked-later`: a decision whose prerequisite is still unresolved;
- `deferred`: visibly postponed by the user or by an explicit evidence limit;
- `resolved-from-evidence`: settled by sufficient local evidence;
- `accepted`: explicitly accepted by the user;
- `accepted-risk`: explicitly retained as a known risk;
- `rejected`: rejected by evidence, the user, or a supported comparison.

Use `open` only as a visible recovery marker when a decision cannot be
reconstructed; it is not a hidden substitute for a normal terminal state.
Root decisions have no unresolved prerequisites. Dependent decisions remain
`blocked-later` until their prerequisites resolve. Before asking, recover local
evidence and move any fact that is already sufficient to
`resolved-from-evidence`.

When several roots are open, prioritize authority or scope blockers, then
dependency impact, recommendation impact, material risk, and finally
non-blocking preference. This is a priority heuristic, not a fixed question
count or a normative multi-branch scheduler. Collect every currently known
material `eligible-now` decision for the current round and map each numbered
question to exactly one such decision. Do not split that set into one-question
turns. If the set contains only one decision, still send it as a numbered
one-item block. Reopen a decision only when new evidence, an explicit user
change, or a supported critical finding matches its declared reopen condition.

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

Use one compact Candidate projection, not a transcript or a second report.
Present these sections in this order when they contain information:

1. `### 🧭 Decision` — the active decision, current state delta, and the
  choice required from the user.
2. `### ✅ Recommendation` — the current direction and why it satisfies the
  accepted outcome and constraints.
3. `### 🔎 Evidence` — only evidence that controls this decision, grouped by
  implication instead of repeating the investigation.
4. `### ⚠️ Risks` — blockers, unknowns, acceptance conditions, and residual
  risks that could change the recommendation.
5. `### ❓ Decisions needed` — one numbered block for eligible decisions, or
  omit it when none remain.

Keep the seven gateway menu entries in their required positions, each as one
compact line with its lock reason. Do not repeat the Candidate Analysis Spec,
critical report, ledger, or recovery record in chat. The canonical record and
selected artifact retain full detail; chat must still name every material item
in the sections above or state that it is retained there. A recommendation is
not acceptance.

Use at most one Mermaid diagram only when it clarifies three or more decision,
dependency, ownership, or option relationships. Put the conclusion in adjacent
prose and keep simple decisions prose-only. Diagnostic word counts never
authorize dropping a blocker, unknown, acceptance condition, or residual risk.
Keep the stable Analysis Spec field names unchanged.

## Candidate Analysis Spec

Use one canonical subject for the analysis and any optional critical review.
The Candidate Analysis Spec contains `Decision focus`; `Desired outcome` and
`Success criteria`; `Scope` and `Anti-scope`; `Facts`, `Reports`, `Assumptions`,
`Unknowns`, and `Constraints`; `Resolved decisions`; `Options` with contrasting
mechanisms; `Recommendation`; `Rejected alternatives` and evidence-based
reasons; `Risks` and `Disconfirming signals`; `Deferred questions`; and
`Specific critical focus`.

Present the Candidate before opening acceptance. The user may explicitly ask
to continue the analysis or invoke `/internal-gateway-critical-master` instead
of accepting. When asking for acceptance, show exactly this numbered gate and
do not treat a displayed recommendation as acceptance:

1. `✅ Accept as the Consolidated Analysis Spec + spec`
2. `✅ Accept as the Consolidated Analysis Spec + plan`
3. `💾 Save the analysis`
4. `⏹️ Close without a file or plan`

After completed critical review, promote the Candidate Analysis Spec to the
Consolidated Analysis Spec only after the user explicitly chooses option 1 or
2. Option 1 authorizes only authoring the consolidated analysis spec artifact;
option 2 authorizes only the implementation-plan authoring handoff. Neither
option authorizes implementation or execution. Options 3 and 4 do not promote
the Candidate. The Candidate remains the Candidate until review is complete
and option 1 or 2 is explicitly selected.

### Artifact authoring after acceptance

After the user selects `+ spec` or `+ plan`, load and apply
[`references/artifact-authoring.md`](references/artifact-authoring.md). It owns
the conditional Luna route, the bounded delegation admission, and the retained
owner responsibilities for the selected artifact. Neither route starts
implementation or execution.

## Critical review procedure

The `CRITICAL REVIEW` gate is mandatory before close or promotion. Invoke
`/internal-gateway-critical-master` for its procedure when the review route is
selected or required by this lifecycle. Pass the Candidate Analysis Spec as
the canonical subject, its `Specific critical focus`, and earlier conversation
only as supporting evidence. The critical owner supplies its intake, lenses,
procedure, findings, and report; this gateway records only the structural
completion predicate and keeps ownership of lifecycle and authority.

While a blocking finding or a material unresolved finding remains, offer only
the applicable examination, realignment, or additional-review actions. When
no blocking finding remains and acceptance is available, show exactly the same
four-option acceptance gate:

1. `✅ Accept as the Consolidated Analysis Spec + spec`
2. `✅ Accept as the Consolidated Analysis Spec + plan`
3. `💾 Save the analysis`
4. `⏹️ Close without a file or plan`

Do not realign automatically. Require the user's explicit numbered choice
before integrating critical findings. When the user selects realignment, treat
the critical report as new evidence: incorporate supported findings, reject
conflicting suggestions with evidence, return unresolved user decisions to
`/grill-me`, and reopen the affected analysis branch. Update the same canonical
state and spec. It becomes the Consolidated Analysis Spec only when every
material finding has been incorporated, rejected with evidence, accepted as
residual risk, or routed to a resolvable branch, and the user explicitly
selects acceptance option 1 or 2. The selected artifact then follows
`references/artifact-authoring.md`. Do not realign or accept automatically.

## Pause and persistence

Conversation-only analysis remains the default. On pause, save, cross-chat
continuation, or accepted artifact creation, load and apply
[`references/persistence.md`](references/persistence.md). It owns the resume
projection, single-artifact rule, default path, and post-acceptance handoff.
