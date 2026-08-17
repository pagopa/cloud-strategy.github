---
name: internal-gateway-simple-task
description: Use when a concrete repository-owned low-to-medium-risk task can finish in one bounded session with a focused validation path.
---

# Internal Gateway Simple Task

Use this skill as the short, linear route for concrete repository work. It owns
scope selection, bounded execution, repair, validation, and the final report.

## Internal Execution Brief

For every concrete non-trivial task, this gateway owns one canonical Internal
Execution Brief. Capture the following task-instance fields before
implementation:

- **Request and observable outcome** — what was asked and what a reviewer can
  observe when it is complete.
- **Target scope, anti-scope, owner, and route** — the intended files or
  boundaries, explicit exclusions, nearest owner, and selected gateway.
- **Constraints, authority, assumptions, and open facts** — safety and
  approval boundaries, known assumptions, and facts still to resolve.
- **Local evidence, proposed direction, and rejected alternative** — the
  evidence that selects the direction and the credible alternative that was
  declined.
- **Acceptance, native validation, and pass/fail signal** — observable
  acceptance, the owning command or check, and what counts as pass or fail.
- **Stop conditions, dependencies, and handoff** — conditions that halt work,
  required local or external dependencies, and the next owner when work stops
  or is promoted.
- **State, evidence delta, and current decisions** — the current working state,
  what new evidence changed, and the decisions that currently govern the task.

The brief is task-instance working data. It is not a new skill format, design
or state machine, second implementation plan, or separate approval gate. Use
the self-contained `references/execution-brief-template.md` as a reusable
shape without turning it into persisted state or a competing contract.

Keep a same-session brief in working context. On pause or resume, materialize
at most one uncommitted disposable `tmp/briefs/<slug>.md`. When promotion
creates a retained implementation plan, authority transfers to
`/internal-gateway-writing-plans` and the brief retires as authority.
Supporting skills may contribute evidence, but may not create competing
briefs. `/internal-gateway-idea` owns conversation-first idea analysis and
`/internal-gateway-writing-plans` owns retained-plan work.

Before any live provider or external operation, require explicit authority.
Use a safe local fallback when the brief permits one; otherwise stop
fail-closed. Keep this boundary provider-neutral. Close out through one
canonical evidence ledger with fresh focused and broader validation evidence;
do not claim completion before those checks pass, and do not introduce numeric
tool-call or read thresholds.

## Scope

Use only when the target, intended outcome, anti-scope, and validation signal
are concrete enough to finish in one bounded session. This includes small code
changes, metadata or documentation edits, diagnosis, and focused validation.

Do not use this route for brainstorming, architecture selection, multi-phase
rollouts, production operations, approval-bound work, unsafe changes, or work
that cannot be checked locally. Route those requests to their named owner or
stop with the exact boundary and required decision.

## When to use

- The request is repository-owned and the target can be identified from local evidence.
- The smallest coherent action and its focused validation are clear.
- The work can finish without staged workflow changes or external coordination.

## Local evidence first

1. Inspect the nearest owner, target files, relevant callers, repository policy,
   current worktree state, and the closest executable validation.
2. Record the original request, emerged requirements, actual problem, proposed
   direction, hidden assumption, smaller move, alternative path, validation
   signal, and stop signal before choosing a route.
3. Recover missing facts from the repository before asking anyone. Use one
   bounded `/grill-me` block only when one unrecoverable material fact blocks
   the active route. If the answer creates a dependent clarification or changes
   scope, stop and request the required decision.

## Route decision

Classify the work as `trivial` or `non-trivial`.

- `trivial`: a local answer, tiny deterministic edit, focused read, or validator
  run whose implementation scope is small, whose contract is evident, and
  whose local validator evidence is evident, such as `terraform fmt` plus
  `terraform test` for Terraform or the owning format's equivalent. A small
  local deterministic edit qualifies even when it carries future operational
  risk, such as possible resource replacement; surface that risk in the report
  instead of escalating the classification. Execute directly and report the
  evidence.
- `non-trivial`: every other same-run task that still fits this route. Write the
  smallest clean action plan with target, anti-scope, dependencies, acceptance,
  validation, and stop conditions before implementation.

**Downgrade:** After classification, when recovered local evidence shows that
the task satisfies the trivial criteria, downgrade to `trivial` instead of
continuing the non-trivial route. This is permitted only when all three fences
hold: (a) a deterministic local validator is identified; (b) no contract or
consumer changes; and (c) the downgrade rationale is recorded in the Internal
Execution Brief. Always notify the user of the downgrade in the report. If the
downgrade would touch any contract or consumer, require explicit user
confirmation before execution.

Stop when the task becomes multi-phase, materially ambiguous, approval-bound,
unsafe, too costly for the session, or not locally verifiable.

## Critical challenge

Before non-trivial action, run `/internal-gateway-critical-master` with exactly
three lenses; the third lens must be lateral (`analogy` or
`reverse-assumption`). Challenge the plan's claims, constraints, success
criteria, anti-scope, and evidence gaps.

If the challenge rejects the plan, allow exactly one reformulation only when
new evidence changes the plan, then run the challenge once more. Otherwise
stop. The gateway retains scope, critique resolution, acceptance, repair,
validation, and final reporting.

## Execution posture

- Trivial work executes directly after local evidence is sufficient.
- Non-trivial work may use `internal-luna-executor` only after the caller's
  value gate, scope, authority, objective, expected output, acceptance, and
  validation are locked. Use `/internal-subagent-contract` for one
  `DelegationBrief` v1 and verify the adapter-composed `WorkerResult` v1 plus
  caller-owned `VerificationReceipt` v1 here. Treat worker validation and
  budget data as claims unless the receipt records runtime observation. This
  gateway, as the active primary owner, retains routing, scope, authority,
  lifecycle, retry choice, independent validation, acceptance, and closeout.
  Delegated worker evidence remains subordinate; do not branch on producer or
  model identity.
- Use one initial worker attempt, at most one context refill, and at most one
  corrective retry. A repeated progress signature is `stalled`; Minor,
  cosmetic, punctuation, and prose-only findings do not reopen a retry. If the
  worker times out, is interrupted, is unavailable, or emits no terminal
  payload, record a caller-owned `LifecycleRecord` and do not fabricate a
  `WorkerResult` or `VerificationReceipt`. Perform work locally only after the
  locked brief permits that fallback and the caller starts a new local route.
- For executable or evaluable behavior, load `/internal-tdd` before editing and
  record exactly one selected posture for the current task. For deterministic
  configuration or infrastructure-template edits where the owning format
  provides a native validator, such as `terraform fmt` and `terraform test`,
  that native validator is the selected validation seam; recording it in the
  brief satisfies the TDD posture requirement. Use `validation-only` only when
  that task has no useful executable or evaluable seam; record the seam gap and
  alternate validation. Do not pre-classify all prompt or skill work as
  `validation-only`, and do not require an additional wording test, harness,
  or manufactured TDD ceremony for such edits.
- Load `/addyosmani-code-simplification` only for an explicit simplification
  request or an already-approved simplification remediation, after a passing
  behavior baseline exists. Preserve behavior, local conventions, and scope.

## Execute and validate

Keep one coherent in-scope change per task. Do not add speculative machinery,
hidden routing, duplicate validators, or other structure that does not serve
the active outcome.

After each task, run its exact focused validation and record the fresh result in
the canonical evidence ledger. Check that every changed requirement has fresh
evidence. Classify failures as task-local, pre-existing, unrelated/external,
environmental, or unknown. Repair once only when the repair is safe, in scope,
and produces new evidence; rerun the authoritative command.

After successful validation, report these fields in this order:

- `Outcome` — what is complete and the controlling conclusion;
- `Changed` — the in-scope files or behavior delta;
- `Checks` — the focused and broader validation evidence;
- `Risks` — material residual risks, gaps, or unavailable evidence;
- `Next` — one required action or `none`.

Keep each field concise, include residual gaps, and do not repeat commentary.
Within `Outcome`, strongly prefer the smallest useful Mermaid diagram only
when the completed result spans a material multi-component relationship. Keep
the controlling conclusion in text; simple results remain prose-only.

Before any completion, passing, fixed, or no-gap claim, load
`/superpowers-verification-before-completion`, run the full required checks,
read their exit status and output, and compare the result with the baseline.
Record pending human judgment or unavailable external evidence as follow-up
only when no material feature failure remains.

## Exact stop reasons

Stop immediately for an unexpected consumer, out-of-scope path, owner conflict,
missing validation, unresolved material ambiguity, approval boundary, unsafe
continuation, inability to preserve conditional Luna delegation, or a failed
repair whose next action would cross scope or authority.

Use this form and keep it concise:

`Stop: <violated condition>. Evidence: <bounded fact or command result>. Next: <required authority, user decision, or named owner>.`

Do not continue by inventing facts, weakening a requirement into a manual
attestation, or replacing a missing validator with narrative confidence.
