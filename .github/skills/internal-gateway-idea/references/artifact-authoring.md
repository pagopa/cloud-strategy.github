# Artifact Authoring After Acceptance

The selected acceptance action controls exactly one next artifact and does not
change domain ownership. Before delegation, the caller fixes the objective,
value gate, bounded evidence, constraints, exact write scope, output,
acceptance, validation, and budgets. The authority envelope stays in force:
authoring writes only the selected artifact path, and any new path or action
is `authority-or-scope` until the user accepts it. Worker metadata, a protected
status, and continuity grant nothing.

Authoring consumes the one canonical recovery record without creating a
parallel record, transcript, or critical-review artifact. If the record is
incomplete or its projections disagree, stop and preserve the last valid
record.

## Delegation

Author locally by default: record `delegation.mode: none`,
`worker: primary-owner`, and `result: not_applicable`, with no delegation
brief, worker result, receipt, or retrospective worker claim. Delegate to
`internal-luna-executor` only when the caller's value gate proves that one
autonomous, bounded, verifiable evidence package is materially more useful
than local work. Then use one `DelegationBrief` through
`/internal-subagent-contract`, which owns brief and receipt shapes. The primary
owner keeps synthesis, independent result verification, acceptance, and
closeout.

If an explicitly selected worker is unavailable, record a caller-owned
`LifecycleRecord` and stop as blocked. Continue locally only with explicit
caller authorization, as a new route with `delegation.mode: none` and
`worker: primary-owner`; never keep worker metadata or fabricate a result or
receipt.

## `+spec`

The gateway keeps the spec's subject, field structure, scope, review,
validation, and final acceptance. After verification, record
`plan_authoring_ready: true` and wait for a later explicit `+plan`. Do not
invoke `/internal-gateway-writing-plans` before that selection.

## `+plan`

Route to `/internal-gateway-writing-plans`, which owns plan eligibility,
structure, review, validation, and handoff with the same local-first
delegation rule. The user's `+plan` selection is the caller's route choice. A
retained spec with `plan_authoring_ready: true` meets source readiness without
another discovery or approval round, but overrides no eligibility, review,
validation, or safety boundary. The plan owner keeps final acceptance and the
no-Git-mutation boundary. This gateway never starts execution; the caller keeps
the sole post-approval handoff to `/internal-gateway-execute-plans`.
