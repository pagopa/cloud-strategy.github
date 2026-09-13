# Candidate And Persistence

## Chat Projection

Present one compact Candidate using these sections when they contain material:

1. `### 🧭 Decision` — active decision, state delta, and required choice.
2. `### ✅ Recommendation` — direction and fit with outcome and constraints.
3. `### 🔎 Evidence` — only decision-controlling evidence, grouped by implication.
4. `### ⚠️ Risks` — blockers, unknowns, acceptance conditions, and residuals.
5. `### ❓ Decisions needed` — one numbered block for eligible decisions.

Keep the seven gateway menu entries in their fixed positions with lock reasons.
Do not duplicate the spec, critical report, ledger, or recovery record in chat.
Use at most one Mermaid diagram when it clarifies at least three relationships.
A recommendation is not acceptance.

## Candidate Analysis Spec

Use one canonical subject. The spec contains `Decision focus`; `Desired outcome`
and `Success criteria`; `Scope` and `Anti-scope`; `Facts`, `Reports`,
`Assumptions`, `Unknowns`, and `Constraints`; `Resolved decisions`; `Options`;
`Recommendation`; `Rejected alternatives`; `Risks` and `Disconfirming signals`;
`Deferred questions`; and `Specific critical focus`.

Present the Candidate before acceptance. After critical review, show exactly:

1. `✅ Accept as the Consolidated Analysis Spec + spec`
2. `✅ Accept as the Consolidated Analysis Spec + plan`
3. `💾 Save the analysis`
4. `⏹️ Close without a file or plan`

Only options 1 and 2 promote the Candidate. Option 1 authorizes only the
consolidated spec artifact and records `plan_authoring_ready: true` after
verification. Option 2 authorizes only the plan-authoring handoff, either from
the Candidate or a retained plan-ready spec. `Implementation permission: false`
does not block option 2. Neither option authorizes implementation or execution.

## Artifact Authoring

After `+ spec` or `+ plan`, load and apply
[`artifact-authoring.md`](artifact-authoring.md). It owns conditional delegation
admission and retained owner responsibilities for the selected artifact.

## Critical Review Integration

The `CRITICAL REVIEW` gate is mandatory before close or promotion. Pass the
Candidate and `Specific critical focus` to `/internal-gateway-critical-master`.
Keep blocking or unresolved findings open. Require an explicit user choice
before integrating findings. On realignment, incorporate supported findings,
reject conflicts with evidence, return unresolved decisions to `/grill-me`, and
reopen only affected branches. Promote only after every finding is incorporated,
rejected, accepted as risk, or routed, followed by option 1 or 2.

## Persistence

Conversation-only analysis remains the default. On pause, save, cross-chat
continuation, or accepted artifact creation, load and apply
[`persistence.md`](persistence.md). It owns the resume projection,
single-artifact rule, default path, and post-acceptance handoff.
