# Candidate, Review, and Acceptance

## Chat projection

Present one compact Candidate using these sections when they contain material:

1. `### 🧭 Decision` — active decision, state delta, and required choice.
2. `### ✅ Recommendation` — direction and fit with outcome and constraints.
3. `### 🔎 Evidence` — only decision-controlling evidence, grouped by implication.
4. `### ⚠️ Risks` — blockers, unknowns, acceptance conditions, and residuals.
5. `### ❓ Decisions needed` — one numbered block for eligible decisions.

Follow it with the seven-entry phase menu from `SKILL.md`. Do not duplicate
the spec, critical report, ledger, or recovery record in chat. Use at most one
Mermaid diagram, only when it clarifies at least three relationships. A
recommendation is not acceptance.

## Candidate Analysis Spec

Use one canonical subject. The spec contains `Decision focus`; `Desired outcome`
and `Success criteria`; `Scope` and `Anti-scope`; `Facts`, `Reports`,
`Assumptions`, `Unknowns`, and `Constraints`; `Resolved decisions`; `Options`;
`Recommendation`; `Rejected alternatives`; `Risks` and `Disconfirming signals`;
`Deferred questions`; and `Specific critical focus`.

## Critical review and realignment

Pass the Candidate and its `Specific critical focus` to
`/internal-gateway-critical-master`. Keep blocking or unresolved findings open
and require an explicit user choice before integrating any finding. On
realignment, incorporate supported findings, reject conflicts with evidence,
return unresolved decisions to `/grill-me`, and reopen only affected branches.

## Acceptance

Promote only after every finding is incorporated, rejected, accepted as risk,
or routed, and the user then selects `+spec` or `+plan`. Each action has the
scope defined in the `SKILL.md` unit lock; `+plan` may start from the Candidate
or from a retained plan-ready spec. `save` and `close` never promote.
