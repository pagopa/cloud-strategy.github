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
`/internal-gateway-writing-plans`, or `/internal-gateway-execute-plans`.
Implementation permission never implies any of those routes.

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
count or a normative multi-branch scheduler. Ask only about a material
`eligible-now` decision, and map each question to exactly one such decision.
Reopen a decision only when new evidence, an explicit user change, or a
supported critical finding matches its declared reopen condition.

## State capsule

Maintain one compact state capsule with exactly:

- `Subject`;
- `Mode` and decision focus;
- accepted, rejected, deferred, and accepted-risk IDs;
- eligible-now IDs;
- blocked-later IDs with prerequisites;
- evidence anchors;
- next action.

Update the ledger and capsule before and after `/grill-me`, on pause, context
compaction, `subject-change`, or `mode-change`, and before presenting a
Candidate. During ordinary turns, show only state deltas and the next decision.
If reconstruction fails, mark affected decisions `open` visibly and recover
them before treating them as resolved.

## Workflow

Work through these branches in order. Reopen only a branch changed by new
evidence, a user decision, or a supported critical finding.

1. **Orient.** Set the analysis unit lock. Name the desired outcome, audience,
   time horizon, success criteria, scope, and anti-scope.
2. **Map the fog.** Separate the five evidence classes. Identify decision-
   changing unknowns, the evidence that could resolve them, and the constraints
   that must remain true.
3. **Resolve evidence and roots.** Build the ledger, mark roots and
   dependents, recover sufficient facts, and choose the next `eligible-now`
   decision using the priority heuristic.
4. **Challenge the anchor.** Always challenge one actor, mechanism, constraint,
   or causal assumption internally. Show alternatives only when that challenge
   yields at least two materially credible mechanisms supported by evidence. If
   evidence and accepted constraints determine one feasible direction, converge
   directly. Record a credible rejected alternative whenever one exists.
5. **Route unresolved decisions.** When an eligible user decision remains,
   invoke `/grill-me` with exactly this packet for each decision:

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
6. **Converge.** Compare options against the desired outcome, success criteria,
   evidence quality, constraints, and anti-scope. Recommend one direction and
   record why credible alternatives were rejected.
7. **Stress-test.** Record material risks, dependencies, disconfirming signals,
   deferred questions, accepted risks, and the evidence that would change the
   recommendation.
8. **Present the Candidate.** Do so only when every material assumption is
   resolved, visibly deferred, or explicitly accepted as risk, and the
   recommendation is traceable to accepted decisions and labeled evidence.

Completion criterion: the recommendation is traceable to resolved decisions
and labeled evidence; every material uncertainty is resolved, deferred, or
accepted as a visible residual risk; and the latest state capsule is current.

## Chat layout

Use these compact headings when their section has material content:

- `### 🧭 Decision`
- `### 🔎 Evidence`
- `### 🔀 Options`
- `### ✅ Recommendation`
- `### ⚠️ Risks`
- `### ❓ Decisions needed`

Use emoji as navigation, not decoration. Do not prefix every paragraph or
bullet with one. Keep the stable Analysis Spec field names unchanged.

## Candidate Analysis Spec

Use one canonical subject for the analysis and any optional critical review.
The Candidate Analysis Spec contains:

- `Decision focus`
- `Desired outcome` and `Success criteria`
- `Scope` and `Anti-scope`
- `Facts`, `Reports`, `Assumptions`, `Unknowns`, and `Constraints`
- `Resolved decisions`
- `Options` with their contrasting mechanisms
- `Recommendation`
- `Rejected alternatives` and evidence-based reasons
- `Risks` and `Disconfirming signals`
- `Deferred questions`
- `Specific critical focus`

Present the Candidate before offering the next action. Require an explicit
numbered user choice; do not treat a displayed recommendation as acceptance:

- `🔄 Continue the analysis`
- `🧠 Invoke /internal-gateway-critical-master`
- `✅ Accept as the Consolidated Analysis Spec`
- `💾 Save the analysis`
- `⏹️ Close without a file or plan`

Without a critical review, promote the Candidate Analysis Spec to the
Consolidated Analysis Spec only after the user explicitly chooses its numbered
acceptance action. The Candidate remains the Candidate until then.

## Optional critical review

Invoke `/internal-gateway-critical-master` only when the user selects it. Pass
the Candidate Analysis Spec as the canonical subject, its `Specific critical
focus`, and earlier conversation only as supporting evidence. The critical
owner supplies its own intake, lenses, procedure, findings, and report.

After presenting the critical report, offer:

- `🔍 Examine a specific finding`
- `🔄 Realign the analysis with supported critical findings`
- `🧠 Run another critical review`, only when a material finding remains
  unresolved or new evidence arrived
- `✅ Accept the analysis`, only when no blocking finding remains
- `💾 Save the analysis`
- `⏹️ Close without a file or plan`

Do not realign automatically. Require the user's explicit numbered choice
before integrating critical findings. When the user selects realignment, treat
the critical report as new evidence: incorporate supported findings, reject
conflicting suggestions with evidence, return unresolved user decisions to
`/grill-me`, and reopen the affected analysis branch. Update the same canonical
state and spec. It becomes the Consolidated Analysis Spec only when every
material finding has been incorporated, rejected with evidence, accepted as
residual risk, or routed to a resolvable branch, and the user explicitly
accepts the resulting analysis.

## Pause and persistence

Conversation-only analysis is the default. On pause, return this compact state:

### ⏸️ Resume from here

- `❓ Active decision`
- `🔎 Key unknown`
- `➡️ Next branch`
- `🔒 Closed decisions`

The pause view is a readable projection of the current state capsule. Rebuild
it from the capsule after context compaction, a subject change, or a mode
change; if a field cannot be recovered, mark the affected decision `open`.

Create a file only when the user explicitly asks to save or continue in another
conversation. Write at most one Markdown artifact at the supplied path. When
no path is supplied, use
`tmp/superpowers/specs/YYYY-MM-DD-<topic>-analysis.md`, disclose that `tmp/` is
disposable, and update that same file in place. The artifact must contain the
current Candidate or Consolidated Analysis Spec, its state capsule, evidence
anchors, and next action so planning replay works without the transcript. Do
not create a separate critical report or transcript, and do not save twice as
separate artifacts.

After the Consolidated Analysis Spec is accepted, state that implementation-
oriented design, planning, and execution remain separate explicitly requested
actions. Do not invoke those owners from `analysis-only` mode.
