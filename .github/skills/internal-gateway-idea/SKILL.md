---
name: internal-gateway-idea
description: Use when the user explicitly selects a conversation-first workflow to turn an early or unclear idea into a decision-ready analysis before any plan is requested.
---

# Internal Gateway Idea

## When to use

Use this skill only when the user explicitly selects it. It turns an early,
unclear, or anchored idea into a decision-ready analysis while keeping the
working discussion in the conversation by default.

This is the canonical repository-owned idea-analysis gateway. It does not
create an implementation plan or execution handoff.
`grill-me` owns interview decisions and the resolved decision summary.
`internal-gateway-critical-master` is an optional critical-strategy owner that
the user must select explicitly. Planning is a separate user-requested action
after the analysis is accepted.

## Invocation and posture

Begin by stating the decision the analysis should make possible. Keep the
analysis proportional to the uncertainty and the user's desired outcome.
Recover facts from named local evidence before asking for them. Label the
working material as `Facts`, `Reports`, `Assumptions`, `Unknowns`, or
`Constraints`; preserve the distinction through every revision.

## Workflow

Work through these branches in order, revisiting only a branch changed by new
evidence or a user decision.

1. **Orient.** Name the decision focus, desired outcome, audience, time horizon,
   and what a useful decision would unlock. State the current scope and
   anti-scope.
2. **Map the fog.** Separate the five evidence labels. Identify the unknowns
   that could change the recommendation, the evidence that would resolve them,
   and the constraints that must remain true. Do not promote a report or
   assumption to a fact.
3. **Reframe.** For an anchored proposal, offer at least one materially
   different framing by changing the actor, mechanism, constraint, or causal
   assumption before polishing the initial proposal.
4. **Diverge.** Generate a compact set of contrasting options. A simple idea
   still gets a mechanism-level contrast; keep exploration small when the
   uncertainty is small and broaden it only when the decision warrants it.
5. **Interview.** When a user decision remains, use `/grill-me` with the
   current map and the active branch. Let it own recommendations, accepted
   defaults, question batching, dependent follow-ups, and the resolved decision
   summary. Do not ask the user to resolve facts recoverable from evidence.
6. **Converge.** Compare options against the desired outcome, success criteria,
   evidence quality, constraints, and anti-scope. Select a recommendation,
   record resolved decisions, and explain rejected alternatives with the reason
   each was declined.
7. **Stress-test.** Record material risks, dependencies, disconfirming signals,
   and deferred questions. State what new evidence would change the
   recommendation and which uncertainty remains acceptable as residual risk.
8. **Normalize.** Produce a Candidate Analysis Spec only when the focus,
   outcome, scope, evidence, options, recommendation, and critical focus are
   decision-ready. If they are not ready, continue the branch that can resolve
   the gap instead of manufacturing a candidate spec.

## Candidate Analysis Spec

Use one canonical subject for the analysis and any later optional review. The
Candidate Analysis Spec contains:

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

Present the candidate spec to the user before offering the next choice. Offer
only: continue analysis; invoke `/internal-gateway-critical-master` in this
conversation; save the analysis for another conversation; or close without a
file or plan.

## Optional critical review

Invoke `/internal-gateway-critical-master` only after the user selects that
choice. Pass the Candidate Analysis Spec as the canonical subject and pass
earlier conversation only as supporting evidence. Use this semantic handoff:

> Challenge the Candidate Analysis Spec below as the canonical subject for a
> pre-plan critical review. Use earlier conversation only as supporting
> evidence. Do not create an implementation plan.

The critical owner supplies its own procedure, lenses, report shape, and
finding logic. Keep those contracts with that owner; `/grill-me` remains the
interview owner.

## Counter-validation and consolidation

Counter-validate every material critical finding separately against intent,
evidence, constraints, success criteria, and anti-scope.

- Incorporate a supported finding into the same Candidate Analysis Spec.
- Reject an unsupported or conflicting suggestion with concise evidence.
- Return a finding that needs a user decision to `/grill-me`.
- Reopen framing, evidence, alternatives, or convergence when that branch can
  resolve the finding.
- Accept a supported remaining risk only when its impact and disconfirming
  signal are explicit.

Do not rerun unchanged analysis or critical review. Present the
`Consolidated Analysis Spec` only after every material finding is resolved,
rejected with evidence, accepted as residual risk, or routed to the branch
that can resolve it. The consolidated spec updates the same canonical document;
it is not a second report.

## Pause, continuation, and persistence

Conversation-only analysis is the default. If the user pauses, provide a
`Resume from here` section containing the active question, key unknown, next
branch, and decisions that remain closed. A later turn continues from that
context without restarting settled work.

On an explicit request to continue in another conversation or to save the
analysis, create at most one Markdown analysis artifact at the supplied path.
When no path is supplied, use
`tmp/superpowers/specs/YYYY-MM-DD-<topic>-analysis.md`; disclose that `tmp/`
is disposable and the file must move to a durable repository path for long-term
retention or versioned review. Update that same file in place. Never create a
separate critical report or transcript.

After the Consolidated Analysis Spec is accepted, state that planning remains
a separate explicitly requested action. Close without a file or plan when the
user selects close.
