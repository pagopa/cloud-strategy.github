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
`/superpowers-brainstorming`, `/internal-tdd`,
`/internal-gateway-writing-plans`, or `/internal-gateway-execute-plans` before
the user explicitly selects a `+spec` or `+plan` Candidate acceptance action.
A `+spec` action authorizes only the selected spec artifact; a `+plan` action
authorizes only the selected plan-authoring handoff. Neither action authorizes
implementation or execution.

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

## Ownership boundary

This gateway owns the analysis lifecycle, evidence discipline, option
comparison, recommendation, decision state, and one canonical Analysis Spec.
It does not own:

- interview mechanics or question formatting, which belong to `/grill-me`;
- critical-review procedure or report shape, which belong to
  `/internal-gateway-critical-master`;
- implementation-oriented design and design-spec writing, which belong to the
  separately selected `superpowers-brainstorming` skill;
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

After a Candidate, present this ordered menu as applicable: `continue`,
critical review, explicit `realign` when findings exist, `+spec`, `+plan`,
`save`, and `close`. Critical review must complete before `+spec` or `+plan` is available. Findings never integrate automatically; require explicit choice
to incorporate, reject with evidence, accept as residual risk, or route each
material finding. No menu action grants implementation or execution, and
`continue`, `finish`, `save`, and `close` preserve the authority envelope.

Completion criterion: the recommendation is traceable to resolved decisions and labeled evidence, every material uncertainty is resolved/deferred/accepted as visible risk, and the latest state capsule is current.

## Chat layout

Lead with the active decision block, recommendation, or next required choice.
Ordinary chat has one canonical Candidate view: material deltas, one outcome,
up to three controlling evidence items, one principal risk, and the active
choice. Preserve blockers, unknowns, acceptance conditions, and residual risks;
do not duplicate the view as a report or transcript. Word counts are diagnostic
only and must not hide content. Use at most one Mermaid, only for three or more
relationships, with the conclusion in adjacent prose; simple content stays
prose-only. A displayed recommendation is not acceptance.

Use these compact headings when material: `### 🧭 Decision`, `### 🔎 Evidence`,
`### 🔀 Options`, `### ✅ Recommendation`, `### ⚠️ Risks`, and
`### ❓ Decisions needed`.

Use emoji as navigation, not decoration. Do not prefix every paragraph or
bullet with one. For a non-trivial decision flow, dependency, ownership
relation, or option mechanism, use the one-diagram rule above only when at
least three relationships are clarified. Keep the controlling conclusion in
adjacent prose and skip decorative visuals.

Keep full evidence, decision history, and residual risks in the one
user-requested artifact; ordinary chat shows state deltas and the current
decision block. Do not introduce a new template, artifact, field, or automatic
save. Keep the stable Analysis Spec field names unchanged.

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

Without a critical review, promote the Candidate Analysis Spec to the
Consolidated Analysis Spec only after the user explicitly chooses option 1 or
2. Option 1 authorizes only authoring the consolidated analysis spec artifact;
option 2 authorizes only the implementation-plan authoring handoff. Neither
option authorizes implementation or execution. Options 3 and 4 do not promote
the Candidate. The Candidate remains the Candidate until option 1 or 2 is
explicitly selected.

### Artifact authoring after acceptance

After the user selects `+ spec` or `+ plan`, load and apply
[`references/artifact-authoring.md`](references/artifact-authoring.md). It owns
the conditional Luna route, the bounded delegation admission, and the retained
owner responsibilities for the selected artifact. Neither route starts
implementation or execution.

## Optional critical review

Invoke `/internal-gateway-critical-master` only when the user selects it. Pass
the Candidate Analysis Spec as the canonical subject, its `Specific critical
focus`, and earlier conversation only as supporting evidence. The critical
owner supplies its own intake, lenses, procedure, findings, and report.

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
