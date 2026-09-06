---
name: internal-gateway-writing-plans
description: Use when repository-owned work needs an approved implementation plan written from an approved design or reviewed retained spec.
---

# Internal Gateway Writing Plans

## Referenced skills

- `/superpowers-writing-plans`: imported plan-structure mechanics only; this gateway
  owns eligibility, retained-plan requirements, review, and handoff.
- `/internal-gateway-execute-plans`: required next owner after human review and
  explicit execution approval.

## When to use

- Use after the user approves implementation-plan writing from an approved
  design or reviewed retained spec.

## When not to use

- Retained-spec writing stays in the brainstorming lane.
- Route same-chat work, plan review, plan execution, and imported
  `superpowers-*` maintenance to their existing owners.

## Contract

0. Establish writing eligibility before any implementation-plan writing.
   Eligibility requires a current explicit request to write an implementation
   plan, a verifiable approval state for that writing, the target and
   anti-scope, consolidated decisions and residual risks, the nearest owner
   and authority boundary, observable acceptance and validation path, and
   stop conditions. A user-accepted `Consolidated Analysis Spec` from
   `/internal-gateway-idea`, an approved design, a reviewed retained spec, or
   equivalent direct input is eligible only when all of those conditions are
   present; producer identity does not substitute for any condition. Neither
   path authorizes plan execution, status creation, or Git mutation. A
   verified retained spec from `/internal-gateway-idea` with
   `plan_authoring_ready: true`, combined with the user's later explicit
   `+plan` selection, satisfies source readiness and the current
   plan-writing request; continue without another discovery or approval
   round. `implementation_permission: false` is expected because plan
   authoring is not implementation; it must not block writing eligibility.
   The handoff still needs the target, anti-scope, decisions, risks,
   acceptance, validation, and authority facts required above.
1. Capture the target, anti-scope, nearest owner, validation path, stop
   conditions, and observable acceptance. Build a control inventory before
   delegation: classify every task, acceptance criterion, and declared
   `manual_obligation` exactly once as `automatable-local`,
   `observable-runtime`, `external-capability`, `authority-or-scope`, or
   `genuine-human-judgment`. Require an explicit `- No Git mutation.` bullet
   under `## Global Constraints` and a compact `## Control Inventory` in
   every current plan. Completion: all six facts, the no-mutation rule, and
   one owner for every obligation are recorded before delegation.
2. Lock exactly one plan-owner-locked retained plan path under
   `tmp/superpowers/plans/` and its required structure before delegation:
   ordered actionable tasks, concrete file targets, focused validation, a
   compact `## Control Inventory`, an execution handoff, and one normative
   `## Execution Manifest` fenced JSON object under the exact heading text
   with no suffix. The manifest owns targets, controls, validations, tasks,
   authority boundaries, retry posture, approval metadata, bootstrap
   metadata, and handoff. Imported `/superpowers-writing-plans` mechanics
   define plan structure only; they do not own approval eligibility or
   handoff.
   Author the Markdown exactly as `references/manifest-v3.md` binds it: exact heading texts,
   one fenced JSON code block only inside the manifest section, the canonical
   `## Repository Preflight` with its four bold fields, one `## Task N:` heading per task
   numbered in manifest order with ids `T1` through `T<N>`, and Control Inventory IDs
   bijective with the `manifest.controls` map keys. Each inventory row records a stable ID,
   preserved requirement, nearest owner, command or trigger, pass/fail signal, evidence, and
   safe fallback or authority boundary. Link local/runtime rows to `validations` and residual
   external/human rows to the existing contract fields; the inventory is traceability, not a
   second parser contract. `genuine-human-judgment` rows are explicit offline review
   follow-up, reported after a successful `DONE` closeout and never blocking completion;
   external evidence unavailable without an observed material failure is the same
   non-blocking follow-up. Authority and approval rows remain pre-execution gates. New
   writer output uses `bootstrap.mode: manifest-only`, emits no legacy
   `## Execution Contract`, and treats the current migration plan as the sole explicit
   compatibility projection, accepted only when its manifest metadata and Markdown
   projection bind exactly, and retired at closeout.
   Classify each executable or evaluable task through `/internal-tdd`. Map
   every posture to focused and broad validation; require observed
   red-first evidence only for `mandatory-test-first`, while
   `feature-first` retains validation before production-ready completion.
   After eligibility, the control inventory, plan structure, locked decisions, and acceptance
   are complete, use local authoring as the default route: record `delegation.mode: none`,
   `worker: primary-owner`, and `result: not_applicable`; do not manufacture a brief, worker
   result, receipt, or retrospective delegation claim. Current Manifest v3 accepts only that
   local tuple; a worker may provide a bounded evidence or draft package only when the final
   retained artifact keeps it and the caller-owned receipt remains separate; never ask a
   worker to emit an unsupported delegated Manifest tuple. Delegation is an exception only
   when the value gate proves that one autonomous, bounded, verifiable evidence package is
   materially more useful than a local operation and can remain off the critical path. Keep
   final synthesis parent-owned. Model or provider identity alone is not a routing reason. If
   delegation was explicitly chosen and the worker is unavailable, record the caller-owned
   lifecycle event and stop blocked; continue locally only after explicit caller
   authorization, then record the new local route with no synthetic worker artifacts.

   Before invoking any worker, materialize the exact retained-plan skeleton and output path
   with the final Manifest tuple. Resolve the physical executor bundle from its loaded runner
   and run
   `bash <physical-executor-bundle>/scripts/run.sh preflight <skeleton> --format compact`.
   A nonzero result or any blocking finding, including `delegation-not-supported`, prevents
   dispatch and requires local authoring or a corrected route.

   For an explicitly chosen delegated route, fix the objective, value gate, bounded evidence,
   constraints, exact retained-plan write scope, expected output, acceptance, validation, and
   budgets; write one `DelegationBrief` v1 in `mode: plan` through
   `/internal-subagent-contract` before invoking `internal-luna-executor`, binding the single
   retained-plan path as `write_scope` and `expected_output.path` with the required manifest
   and preflight acceptance plus exact focused validation, and record
   `worker: internal-luna-executor` in the plan authority boundary. Luna returns the semantic
   fields for one `WorkerResult` v1; the runtime adapter composes deterministic fields and a
   caller-owned `VerificationReceipt` v1, and unobserved validation or budget data stay
   claims or `unavailable`. Caller acceptance binds the exact final artifact bytes and
   manifest semantic fingerprint; a material edit invalidates the result and receipt and
   routes one new evidence-bound corrective brief to Luna under the retry contract instead of
   silently transferring authorship to the parent. Caller-authorized local continuation
   begins a fresh local route with the local tuple and no inherited worker artifacts.
   Preserve the final-byte physical preflight requirement on either branch.

   The plan owner retains eligibility, control classification, routing,
   authority, lifecycle, retry choice, semantic review, independent
   `preflight`, final acceptance, handoff, and the no-Git-mutation boundary.
   Before critic output can expand scope, classify every finding exactly
   once as `blocking-now`, `acceptance-required`, `follow-up`,
   `separate-design`, or `rejected-with-reason`; untraceable findings are
   `separate-design`.

   Acceptance gate: before any ready verdict or handoff, run the physical
   preflight against the exact final plan bytes and require exit code zero
   with zero blocking findings. A completion claim without that fresh
   preflight evidence is invalid; repair the plan and rerun the preflight
   instead of describing the expected result.
3. Perform human review for task actionability, approved scope, focused
   validation, control coverage, safety, and handoff quality. Every
   `automatable-local` or `observable-runtime` row must map to a required
   executable validation. An `external-capability` row must have an explicit
   probe and safe fallback, or a declared residual external obligation.
   `authority-or-scope` and `genuine-human-judgment` rows must remain explicit
   authority or human obligations; human judgment is verified offline after
   successful execution, while authority and approval remain pre-execution
   gates. An external capability must be probed, but unavailable evidence
   without an observed material failure is follow-up rather than an automatic
   `NEEDS_REVIEW` route. A user assertion cannot substitute for a technical
   gate. The contract must declare native authoritative validation commands
   and phases, equivalence policy, manual obligations, and authority
   boundaries. Verify the handoff names `/internal-gateway-execute-plans` and
   that `handoff.requires` uses the exact canonical strings
   `human approval`, `exact Manifest v3 review`, and
   `zero blocking preflight findings`. A local/runtime gate must fail when
   its requirement is violated; a warning or printout is not a gate. It must
   not predict runtime discovery results or recovery candidates. Completion:
   each review concern and control row is accepted or has a recorded
   revision.
   Delivery communication must keep `structure`, `semantic_review`,
   `artifact_provenance`, `source_baseline`, and `execution_readiness` as
   distinct verdict categories. Each category names its outcome, coverage,
   and limit; an aggregate green result requires every required category to
   be concluded and passed. The executor persists those categories in the
   YAML status sibling together with externally computed semantic approval
   evidence, including the current Manifest `semantic_fingerprint`,
   warnings, and deviations. A standalone `validated` flag is not a
   readiness claim.
4. Report the plan through the writer-specific compact projection below.
   Keep plan details in the retained artifact. Do not invoke execution,
   create a status sibling, or offer an imported execution owner before
   explicit approval. The `Evidence:` line records `execution=` as the
   executed preflight command with its zero-blocking result on the final
   plan bytes; without that fresh evidence the readiness verdict stays
   `blocked` or `needs review`, never `ready`. Completion: every line of
   the projection is present, the material gap is visible, and execution
   has not started without approval.

## Writer communication

Use exactly five short lines after plan authoring or review:

```text
Plan: <retained path> | <ready, blocked, or needs review>
Scope: <one-line target and anti-scope>
Evidence: structure=<...>; semantic=<...>; provenance=<...>; baseline=<...>; execution=<...>
Risk: <one material risk or none>
Next: <one owner and action; execution owner handoff requires no re-confirmation>
```

Do not copy tasks, the control inventory, or the manifest into chat. The five
evidence categories remain distinct; a missing category keeps readiness
inconclusive. Put acceptance conditions and residual gaps in `Risk` or
`Next`, not in a second narrative. Use a Mermaid diagram only when the plan's
task dependency or handoff cannot be understood clearly from the five lines;
the diagram is supplementary, never a replacement for them.

## Command Portability

Before writing validation commands or handing off a plan, load
[`references/command-portability.md`](references/command-portability.md). It
owns native command form, availability probes, missing-tool handling, task
ordering, and the executor preflight boundary.

## Manifest Contract Loading

Load the bundle-local `references/manifest-v3.md` only for Manifest v3 authoring
or review. It is the detailed producer-consumer checklist for exact Manifest
v3 fields, nested values, projection bindings, task references, approval and
status separation, bootstrap, handoff, retry posture, and no-Git rules.
The executor parser and `scripts/run.sh preflight` remain the sole mechanical
authority; the parser wins if prose and implementation differ. Keep the
always-loaded route focused on eligibility, producer readiness, acceptance,
preflight, and handoff. Do not create a second parser or a shared cross-bundle
dependency.

## Repository Preflight

Every current retained plan must contain this heading and concrete values for
each field below. The writer documents these fields; the executor parses and
enforces the retained plan.

- **Baseline Validation:** Run the manifest's baseline validation before edits and record the result.
- **Recovery Policy:** Use the finite per-task corrective budget; each recovery must be distinct, task-local, safe, and implied by the approved acceptance.
- **Escalation Conditions:** Stop for authority, scope, safety, or unresolved task-local failures.
- **User-Facing Report:** Report the plan path, scope, five evidence categories, one risk, and one next action.

### Producer readiness boundary

The writer owns producer-side readiness: it may prove the control inventory,
ordered task projection, manifest-only shape, and handoff ownership from the
plan it emits. These checks use parsed structure and do not import
`internal-gateway-execute-plans` or any executor-private module. Producer
readiness is writer-owned and structural. The executor bundle remains the
only owner of retained-plan mechanical preflight, loaded bundle resolution,
state, and execution validation.

## No-Commit Rule

- Never run `git add`, `git commit`, `git push`, or another Git mutation while
  writing or handing off a plan. This boundary also applies to any plan-writing
  or execution subagent. Retained artifacts stay uncommitted for user review
  unless the user explicitly requests commit help.
- Do not put Git mutation steps or default commit advice in the produced plan.

## Validation

- Confirm the delegated plan has ordered tasks, concrete file targets, focused
  validation, clear scope and safety boundaries, and no duplicate owner.
- Confirm the handoff names `/internal-gateway-execute-plans`, uses the exact
  canonical `handoff.requires` strings, and requires no runtime
  re-confirmation of the approved plan.
- Confirm the executor will record approval evidence and the five delivery
  verdicts in its YAML status sibling before terminal closeout.
- Run the bundle-local pytest suite and the executor physical preflight
  against the exact final plan bytes; record the zero-blocking preflight
  result as the `execution=` evidence in the writer projection.
- Run `git diff --check` and confirm no Git mutation occurred.
