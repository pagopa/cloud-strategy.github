---
name: internal-gateway-idea
description: Use when the user explicitly selects a conversation-first workflow to turn an early or unclear idea into a decision-ready analysis before any plan is requested.
---

# Internal Gateway Idea

## When to use

Use this skill only when the user explicitly selects it. Turn an early,
unclear, or anchored idea into a decision-ready analysis while keeping the
working material in the conversation by default.

## Ownership boundary

This gateway owns the analysis lifecycle, evidence discipline, option
comparison, recommendation, and one canonical Analysis Spec. It does not own:

- interview mechanics or question formatting, which belong to `/grill-me`;
- critical-review procedure or report shape, which belong to
  `/internal-gateway-critical-master`;
- implementation-oriented design and design-spec writing, which belong to the
  separately selected `superpowers-brainstorming` skill;
- implementation planning or execution.

## Analysis posture

Begin by naming the decision the analysis should make possible. Keep the depth
proportional to the uncertainty and the user's desired outcome. Recover facts
from named local evidence before asking for them.

Classify working material as `Facts`, `Reports`, `Assumptions`, `Unknowns`, or
`Constraints`. Preserve those labels through every revision. A report's
recommendation remains an option until the user resolves the decision.

## Workflow

Work through these branches in order. Reopen only a branch changed by new
evidence, a user decision, or a supported critical finding.

1. **Orient.** Name the decision focus, desired outcome, audience, time
   horizon, success criteria, scope, and anti-scope.
2. **Map the fog.** Separate the five evidence classes. Identify decision-
   changing unknowns, the evidence that could resolve them, and the constraints
   that must remain true.
3. **Reframe and diverge.** For an anchored proposal, change at least one actor,
   mechanism, constraint, or causal assumption. Produce a compact set of
   options with genuinely contrasting mechanisms.
4. **Resolve decisions.** When a user decision remains, invoke `/grill-me` with
   the current evidence map, active branch, and unresolved dependencies. Let it
   own the interview and return the resolved decision summary. Do not ask the
   user for facts recoverable from evidence.
5. **Converge.** Compare the options against the desired outcome, success
   criteria, evidence quality, constraints, and anti-scope. Recommend one
   direction and record why credible alternatives were rejected.
6. **Stress-test.** Record material risks, dependencies, disconfirming signals,
   deferred questions, and the evidence that would change the recommendation.
7. **Normalize.** Produce a Candidate Analysis Spec only when the analysis is
   decision-ready. Otherwise continue the branch that can resolve the gap.

Completion criterion: the recommendation is traceable to resolved decisions
and labeled evidence, and every material uncertainty is resolved, deferred, or
accepted as a visible residual risk.

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

Present the candidate before offering the next action:

- `🔄 Continue the analysis`
- `🧠 Invoke /internal-gateway-critical-master`
- `✅ Accept as the Consolidated Analysis Spec`
- `💾 Save the analysis`
- `⏹️ Close without a file or plan`

Without a critical review, promote the Candidate Analysis Spec to the
Consolidated Analysis Spec only when the user explicitly accepts it.

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

Do not realign automatically. When the user selects realignment, treat the
critical report as new evidence: incorporate supported findings, reject
conflicting suggestions with evidence, return unresolved user decisions to
`/grill-me`, and reopen the affected analysis branch. Update the same canonical
spec. It becomes the Consolidated Analysis Spec only when every material
finding has been incorporated, rejected with evidence, accepted as residual
risk, or routed to a resolvable branch.

## Pause and persistence

Conversation-only analysis is the default. On pause, return this compact state:

### ⏸️ Resume from here

- `❓ Active decision`
- `🔎 Key unknown`
- `➡️ Next branch`
- `🔒 Closed decisions`

Create a file only when the user explicitly asks to save or continue in another
conversation. Write at most one Markdown artifact at the supplied path. When
no path is supplied, use
`tmp/superpowers/specs/YYYY-MM-DD-<topic>-analysis.md`, disclose that `tmp/` is
disposable, and update that same file in place. Do not create a separate
critical report or transcript.

After the Consolidated Analysis Spec is accepted, state that implementation-
oriented design, planning, and execution remain separate explicitly requested
actions.
