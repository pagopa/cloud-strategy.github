---
name: internal-gateway-writing-plans
description: Use when repository-owned work needs an approved implementation plan written from an approved design or reviewed retained spec.
---

# Internal Gateway Writing Plans

Write one retained implementation plan that
`/internal-gateway-execute-plans` can execute.

## When to use

- Use after the user approves implementation-plan writing from an approved
  design or reviewed retained spec.

## When not to use

- Retained-spec writing stays in the brainstorming lane.
- Route same-chat work, plan review, plan execution, and imported
  `superpowers-*` maintenance to their existing owners.

## Referenced skills

- `/superpowers-writing-plans`: imported plan-structure mechanics only; this
  gateway owns eligibility, retained-plan requirements, review, and handoff.
- `/internal-tdd`: posture classification for executable or evaluable tasks.
- `/internal-gateway-execute-plans`: required next owner after human review and
  explicit execution approval.

## Workflow

### 1. Establish writing eligibility

Check each condition before any implementation-plan writing:

- Eligibility requires a current explicit request to write an implementation
  plan, a verifiable approval state for that writing, the target and
  anti-scope, consolidated decisions and residual risks, the nearest owner and
  authority boundary, observable acceptance and validation path, and stop
  conditions. Producer identity does not substitute for any condition.
- Eligible source inputs are a user-accepted `Consolidated Analysis Spec` from
  `/internal-gateway-idea`, an approved design, a reviewed retained spec, or
  equivalent direct input, only when all eligibility conditions are present.
  A verified retained spec from `/internal-gateway-idea` with
  `plan_authoring_ready: true`, combined with the user's later explicit
  `+plan` selection, satisfies source readiness and the current plan-writing
  request; continue without another discovery or approval round.
- `implementation_permission: false` is expected because plan authoring is not
  implementation; it must not block writing eligibility. The handoff still
  needs the target, anti-scope, decisions, risks, acceptance, validation, and
  authority facts required above.
- Neither an eligible source input nor the writing request authorizes plan
  execution, status creation, or Git mutation.

Select the authorization mode from execution intent:

- A user who asks for a plan in order to apply it — the normal case — receives
  an `execution-ready` plan whose intended targets carry `modify` or `create`
  states and whose `Authorization:` line quotes the user's plan request.
  Source-spec markers such as `implementation_permission: false` describe
  idea-stage boundaries only; they never force `authoring-only` or `inspect`
  targets on a plan the user wants applied.
- Reserve `authoring-only` with `inspect` targets for a genuinely blocking
  condition — an unsafe target, a missing authority decision, or unresolved
  material ambiguity — or for an explicitly requested analysis-only plan.
  When such a condition exists, stop at writing time and name it; never hand
  the executor a plan that was never meant to be executable. Non-blocking
  review concerns become `Risk` lines, never a lower plan mode.

### 2. Capture scope and controls

Capture the target, anti-scope, nearest owner, validation path, stop
conditions, and observable acceptance. Build a control inventory before
delegation: classify every task, acceptance criterion, and declared
`manual_obligation` exactly once as `automatable-local`,
`observable-runtime`, `external-capability`, `authority-or-scope`, or
`genuine-human-judgment`. Require an explicit `- No Git mutation.` bullet
under `## Global Constraints` and a compact `## Control Inventory` in every
current plan.

**Complete when:** all six facts, the no-mutation rule, and one owner for
every obligation are recorded before delegation.

### 3. Author the retained plan

**Structure.** Lock exactly one plan-owner-locked retained plan path under
`tmp/superpowers/plans/` and its required structure before delegation:
ordered actionable tasks, concrete file targets, focused validation, a compact
`## Control Inventory`, an execution handoff, and one normative
`## Execution Manifest` fenced JSON object under the exact heading text with
no suffix. The manifest owns targets, controls, validations, tasks, authority
boundaries, retry posture, approval metadata, bootstrap metadata, and handoff.
Imported `/superpowers-writing-plans` mechanics define plan structure only;
they do not own approval eligibility or handoff.

**Markdown binding.** Author the Markdown exactly as
`references/manifest-v3.md` binds it:

- exact heading texts, and one fenced JSON code block only inside the
  manifest section;
- the canonical `## Repository Preflight` with its four bold fields;
- one `## Task N:` heading per task, numbered in manifest order with ids `T1`
  through `T<N>`;
- Control Inventory IDs bijective with the `manifest.controls` map keys.

Each inventory row records a stable ID, preserved requirement, nearest owner,
command or trigger, pass/fail signal, evidence, and safe fallback or authority
boundary. Link local/runtime rows to `validations` and residual external/human
rows to the existing contract fields; the inventory is traceability, not a
second parser contract. `genuine-human-judgment` rows are explicit offline
review follow-up, reported after a successful `DONE` closeout and never
blocking completion; external evidence unavailable without an observed
material failure is the same non-blocking follow-up. Authority and approval
rows remain pre-execution gates.

New writer output uses `bootstrap.mode: manifest-only` and emits no legacy
`## Execution Contract`. The current migration plan is the sole explicit
compatibility projection, accepted only when its manifest metadata and
Markdown projection bind exactly, and retired at closeout.

**Completeness sections.** Current plans also carry the sections bound by the
same reference:

- `## Target Census` with raw `file:line` hits;
- `## Execution Authorization` with exactly one `Mode:` line;
- `## Completeness Audit` with literal commands and raw evidence;
- an optional generated `## Task Graph` aligned with manifest `depends_on`.

`## Execution Authorization` is the single authorization carrier: it owns the
mode, the quoted `Authorization:` line for `execution-ready`, and the
writer/executor handoff pairing. Global Constraints carry no execution-gating
prose and no scope-limiting bullet that contradicts a declared `modify`
target.

**Test posture.** Classify each executable or evaluable task through
`/internal-tdd`. Map every posture to focused and broad validation; require
observed red-first evidence only for `mandatory-test-first` (characterization
for its behavior-preserving refactors), while `feature-first` retains
validation before production-ready completion.

**Authoring route.** After eligibility, the control inventory, plan
structure, locked decisions, and acceptance are complete, use local authoring
as the default route:

- Record `delegation.mode: none`, `worker: primary-owner`, and
  `result: not_applicable`. Do not manufacture a brief, worker result,
  receipt, or retrospective delegation claim.
- Current Manifest v3 accepts only that local tuple. A worker may provide a
  bounded evidence or draft package only when the final retained artifact
  keeps it and the caller-owned receipt remains separate; never ask a worker
  to emit an unsupported delegated Manifest tuple.
- Delegation is an exception only when the value gate proves that one
  autonomous, bounded, verifiable evidence package is materially more useful
  than a local operation and can remain off the critical path. Keep final
  synthesis parent-owned. Model or provider identity alone is not a routing
  reason.
- If delegation was explicitly chosen and the worker is unavailable, record
  the caller-owned lifecycle event and stop blocked; continue locally only
  after explicit caller authorization, then record the new local route with
  no synthetic worker artifacts.
- Load [`references/delegation.md`](references/delegation.md) for worker
  preflight, brief, receipt, retry, and plan-owner retention before invoking
  any worker.

**Critic findings.** Before critic output can expand scope, classify every
finding exactly once as `blocking-now`, `acceptance-required`, `follow-up`,
`separate-design`, or `rejected-with-reason`; untraceable findings are
`separate-design`.

**Acceptance gate.** Before any ready verdict or handoff, run on the exact
final plan bytes, in order:

1. The writer structural check, with exit code zero:
   `python3 <writer-bundle>/scripts/check_plan_structure.py <plan> --format compact`.
2. The physical executor preflight, with exit code zero and zero blocking
   findings:
   `bash <physical-executor-bundle>/scripts/run.sh preflight <plan> --format compact`.
3. The bundle-local pytest suite.

Cite both gate compact outputs together at every OK report. Offer the
`/internal-gateway-execute-plans` handoff only for `execution-ready` plans;
`authoring-only` plans stay retained with the writer as next owner. A
completion claim without that fresh evidence for all three is invalid; repair
the plan and rerun every gate instead of describing the expected result.

### 4. Review the plan

Perform human review for task actionability, approved scope, focused
validation, control coverage, safety, and handoff quality:

- Every `automatable-local` or `observable-runtime` row must map to a required
  executable validation.
- An `external-capability` row must have an explicit probe and safe fallback,
  or a declared residual external obligation. An external capability must be
  probed, but unavailable evidence without an observed material failure is
  follow-up rather than an automatic `NEEDS_REVIEW` route.
- `authority-or-scope` and `genuine-human-judgment` rows must remain explicit
  authority or human obligations. Human judgment is verified offline after
  successful execution, while authority and approval remain pre-execution
  gates.
- A user assertion cannot substitute for a technical gate.
- The contract must declare native authoritative validation commands and
  phases, equivalence policy, manual obligations, and authority boundaries.
- The handoff names `/internal-gateway-execute-plans`, and `handoff.requires`
  uses the exact canonical strings `human approval`,
  `exact Manifest v3 review`, and `zero blocking preflight findings`.
- A local/runtime gate must fail when its requirement is violated; a warning
  or printout is not a gate. It must not predict runtime discovery results or
  recovery candidates.

Delivery communication must keep `structure`, `semantic_review`,
`artifact_provenance`, `source_baseline`, and `execution_readiness` as
distinct verdict categories. Each category names its outcome, coverage, and
limit; an aggregate green result requires every required category to be
concluded and passed. The executor persists those categories in the YAML
status sibling together with externally computed semantic approval evidence,
including the current Manifest `semantic_fingerprint`, warnings, and
deviations. A standalone `validated` flag is not a readiness claim.

**Complete when:** each review concern and control row is accepted or has a
recorded revision.

### 5. Report

Report the plan through the writer projection in
[Writer communication](#writer-communication). Keep plan details in the
retained artifact. Do not invoke execution, create a status sibling, or offer
an imported execution owner before explicit approval. The `Evidence:` line
records `structure=` as the executed writer structural check and `execution=`
as the executed preflight command, each with its zero-blocking result on the
final plan bytes; without those fresh results the status stays
`blocked — evidence incomplete`, never `ready to execute`.

**Complete when:** every line of the projection is present, the material gap
is visible, and execution has not started without approval.

## Writer communication

Use exactly six short lines after plan authoring or review, in the user's
conversation language, keeping the field labels canonical:

```text
Plan: <retained path>
Status: ready to execute | blocked — <one-line reason>
Scope: <one-line target and anti-scope>
Evidence: structure=<...>; semantic=<...>; provenance=<...>; baseline=<...>; execution=<...>
Risk: <one material residual risk or none>
Next: <ready: one execution instruction; blocked: the one decision that unblocks>
```

- `Status` has exactly two values. `ready to execute` requires an
  `execution-ready` mode and all five evidence categories passed on the final
  plan bytes; anything else is `blocked — <reason>` naming the single
  blocking condition.
- There is no middle review state: a review concern is either material,
  which blocks writing, or residual, which becomes a `Risk` line.
- For a ready plan, `Next` is one instruction such as: Say "execute" or
  invoke `/internal-gateway-execute-plans`; execution then proceeds without
  re-confirmation. For a blocked plan, `Next` names the one user decision or
  named-owner action that unblocks, never a procedure.
- The five evidence categories remain distinct, with the completeness audit
  status folded into `semantic=`; a missing category keeps the status
  `blocked — evidence incomplete`.
- Put acceptance conditions and residual gaps in `Risk` or `Next`, not in a
  second narrative. Do not copy tasks, the control inventory, or the manifest
  into chat.
- Use a Mermaid diagram only when the plan's task dependency or handoff
  cannot be understood clearly from the six lines; the diagram is
  supplementary, never a replacement for them.

## Command portability

Before writing validation commands or handing off a plan, load
[`references/command-portability.md`](references/command-portability.md). It
owns native command form, availability probes, missing-tool handling, task
ordering, the producer-readiness boundary, and the executor preflight boundary.

## Manifest contract loading

Load the bundle-local [`references/manifest-v3.md`](references/manifest-v3.md)
only for Manifest v3 authoring or review. It is the detailed producer-consumer
checklist for exact Manifest v3 fields, nested values, projection bindings,
task references, approval and status separation, bootstrap, handoff, retry
posture, and no-Git rules. The executor parser and `scripts/run.sh preflight`
remain the sole mechanical authority; the parser wins if prose and
implementation differ. Keep the always-loaded route focused on eligibility,
producer readiness, acceptance, preflight, and handoff. Do not create a second
parser or a shared cross-bundle dependency.

## Repository Preflight

Every current retained plan must contain this heading and concrete values for
each field below. The writer documents these fields; the executor parses and
enforces the retained plan.

- **Baseline Validation:** Run the manifest's baseline validation before
  edits and record the result.
- **Recovery Policy:** Use the finite per-task corrective budget; each
  recovery must be distinct, task-local, safe, and implied by the approved
  acceptance.
- **Escalation Conditions:** Stop for authority, scope, safety, or unresolved
  task-local failures.
- **User-Facing Report:** Report the plan path, two-state status, scope, five
  evidence categories, one risk, and one next action.

## No-Commit Rule

- Never run `git add`, `git commit`, `git push`, or another Git mutation while
  writing or handing off a plan. This boundary also applies to any plan-writing
  or execution subagent. Retained artifacts stay uncommitted for user review
  unless the user explicitly requests commit help.
- Do not put Git mutation steps or default commit advice in the produced plan.

## Validation

Before the final report, confirm each item:

- The retained plan has ordered tasks, concrete file targets, focused
  validation, clear scope and safety boundaries, and no duplicate owner.
- The handoff names `/internal-gateway-execute-plans`, uses the exact
  canonical `handoff.requires` strings, and requires no runtime
  re-confirmation of the approved plan.
- The executor will record approval evidence and the five delivery verdicts
  in its YAML status sibling before terminal closeout.
- All three acceptance-gate checks from step 3 pass against the exact final
  plan bytes with zero blocking findings; the structural and preflight
  results are recorded as the `structure=` and `execution=` evidence in the
  writer projection.
- `git diff --check` passes and no Git mutation occurred.
