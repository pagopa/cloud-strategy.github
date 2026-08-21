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
  anti-scope, consolidated decisions and residual risks, the nearest owner and
  authority boundary, observable acceptance and validation path, and stop
  conditions. A user-accepted `Consolidated Analysis Spec` from
  `/internal-gateway-idea`, an approved design, a reviewed retained spec, or
  equivalent direct input is eligible only when all of those conditions are
  present. Producer identity does not substitute for any condition. Neither
  path authorizes plan execution, status creation, or Git mutation.
1. Capture the target, anti-scope, nearest owner, validation path, stop
   conditions, and observable acceptance. Build a control inventory before
   delegation: classify every task, acceptance criterion, and declared
   `manual_obligation` exactly once as `automatable-local`,
   `observable-runtime`, `external-capability`, `authority-or-scope`, or
   `genuine-human-judgment`. Require an explicit `- No Git mutation.` bullet
   under `## Global Constraints` and a compact `## Control Inventory` in every
   current plan. Completion: all six facts, the no-mutation rule, and one owner
   for every obligation are recorded before delegation.
2. Lock exactly one plan-owner-locked retained plan path under
    `tmp/superpowers/plans/` and its required structure before delegation:
    ordered actionable tasks, concrete file targets, focused validation, a
    compact `## Control Inventory`, an execution handoff, and one normative
   `## Execution Manifest` v2 fenced JSON object. The manifest owns targets,
    controls, validations, tasks, authority boundaries, retry posture, approval
   approval metadata, bootstrap metadata, and handoff. Imported
    `/superpowers-writing-plans` mechanics define plan structure only; they do
    not own approval eligibility or handoff. Each inventory row records a stable ID,
   preserved requirement, nearest owner, command or trigger, pass/fail signal,
   evidence, and safe fallback or authority boundary. Link local/runtime rows
   to `validations` and residual external/human rows to the existing contract
  fields; the inventory is traceability, not a second parser contract. Treat
  `genuine-human-judgment` rows as explicit offline review follow-up; they are
   reported after a successful `DONE` closeout and do not block completion.
   Treat external evidence that was unavailable without an observed material
   failure as the same kind of non-blocking follow-up. Authority and approval
   rows remain pre-execution gates. Completion: one
   plan exists at the retained path and contains those artifact properties plus
   one `## Execution Manifest` v2 fenced JSON object. New writer output uses
   `bootstrap.mode: manifest-only` and emits no legacy `## Execution Contract`.
   The current migration plan is the sole explicit compatibility projection;
   it is accepted only when its manifest metadata and Markdown projection bind
   exactly, and it retires at closeout.
  Classify each executable or evaluable task through `/internal-tdd`. Map
  every posture to focused and broad validation; require observed red-first
  evidence only for `mandatory-test-first`, while `feature-first` retains
  validation before production-ready completion.
  After eligibility, the control inventory, plan structure, locked decisions,
  and acceptance are complete, use local authoring as the default route:
  record `delegation.mode: none`, `worker: primary-owner`, and
  `result: not_applicable`; do not manufacture a brief, worker result,
  receipt, or retrospective delegation claim. Delegation is an exception only
  when the value gate proves that one autonomous, bounded, verifiable evidence
  package is materially more useful than a local operation and can remain off
  the critical path. Keep final synthesis parent-owned. Model or provider
  identity alone is not a routing reason. If delegation was explicitly chosen
  and the worker is unavailable, record the caller-owned lifecycle event and
  stop blocked; continue locally only after explicit caller authorization, then
  record the new local route as `delegation.mode: none` and `worker:
  primary-owner` with no synthetic worker artifacts.

  For the delegated route, fix the objective, value gate, bounded evidence,
  constraints, exact retained-plan write scope, expected output, acceptance,
  validation, and budgets. Then write one `DelegationBrief` v1 in `mode: plan`
  through `/internal-subagent-contract` before invoking
  `internal-luna-executor`. The brief binds the single retained-plan path as
  `write_scope` and `expected_output.path`, the required manifest and preflight
  acceptance, and exact focused validation. Record
  `worker: internal-luna-executor` in the plan authority boundary.

  Luna returns the semantic fields for one `WorkerResult` v1. The runtime
  adapter composes deterministic fields and a caller-owned
  `VerificationReceipt` v1; unobserved validation and budget data remain claims
  or `unavailable`. Caller acceptance binds the exact final artifact bytes and
  manifest semantic fingerprint. A material edit invalidates the result and
  receipt; route a material correction back to Luna under the retry contract
  instead of silently transferring authorship to the parent.

  The plan owner retains eligibility, control classification, routing,
  authority, lifecycle, retry choice, semantic review, independent `preflight`,
  final acceptance, handoff, and the no-Git-mutation boundary. Before critic
  output can expand scope, classify every finding exactly once as
  `blocking-now`, `acceptance-required`, `follow-up`, `separate-design`, or
  `rejected-with-reason`; untraceable findings are `separate-design`.
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
   `NEEDS_REVIEW` route. A user assertion cannot substitute for a technical gate. The
   contract must declare native authoritative validation
   commands and phases, equivalence policy, manual obligations, and authority
   boundaries. A local/runtime gate must fail when its requirement is violated;
   a warning or printout is not a gate. It must not predict runtime discovery
   results or recovery candidates. Completion: each review concern and control
   row is accepted or has a recorded revision.
  Delivery communication must keep `structure`, `semantic_review`,
  `artifact_provenance`, `source_baseline`, and `execution_readiness` as
  distinct verdict categories. Each category names its outcome, coverage, and
  limit; an aggregate green result requires every required category to be
  concluded and passed. The executor persists those categories in the YAML
   status sibling together with hash-free approval evidence, warnings, and deviations. A
  standalone `validated` flag is not a readiness claim.
4. Report the plan through the writer-specific compact projection below. Keep
  plan details in the retained artifact. Do not invoke execution, create a
  status sibling, or offer an imported execution owner before explicit
  approval. Completion: every line of the projection is present, the material
  gap is visible, and execution has not started without approval.

## Writer communication

Use exactly five short lines after plan authoring or review:

```text
Plan: <retained path> | <ready, blocked, or needs review>
Scope: <one-line target and anti-scope>
Evidence: structure=<...>; semantic=<...>; provenance=<...>; baseline=<...>; execution=<...>
Risk: <one material risk or none>
Next: <one owner and action; execution owner only after explicit approval>
```

Do not copy tasks, the control inventory, or the manifest into chat. The five
evidence categories remain distinct; a missing category keeps readiness
inconclusive. Put acceptance conditions and residual gaps in `Risk` or
`Next`, not in a second narrative. Use a Mermaid diagram only when the plan's
task dependency or handoff cannot be understood clearly from the five lines;
the diagram is supplementary, never a replacement for them.

## Command Portability

- Write every baseline, focused, and final validation command in directly
  executable native form. The command recorded in the plan is the
  authoritative command and evidence label.
- Do not make `graphify` or another optional accelerator a prerequisite or
  command prefix unless the task's actual subject is that tool.
- Executor-side optimization may accelerate an invocation, but must not alter
  the recorded authoritative command or its validation meaning.
- Before handoff, run an existence probe for every `validations[].command`.
  Probe the executable or path with `command -v` or the native path check before
  running the validation. Distinguish command-not-found from a validation
  failure. Exit 127 is a missing-tool condition: record an unambiguous native
  equivalent and its deviation, or retain the residual obligation and stop.
- Order tasks so non-blocking discovery and availability checks come first,
  implementation work stays in the middle, and environment-dependent
  verification runs after implementation.

The executor owns the single mechanical plan validator. Do not add a
writer-local validator, a second implementation-plan writing lifecycle, or a
duplicate parser contract. The executor validates one normative Execution
Manifest v2. There is no dual v1/v2 parser. A legacy `## Execution Contract`
is never a standalone plan schema and requires writer-side regeneration.
Before handoff, the parent gateway MUST resolve the executor's loaded physical
bundle and run its `scripts/run.sh preflight` independently against the written
current plan, then confirm zero blocking findings. The command is:
`bash <physical-executor-bundle>/scripts/run.sh preflight <plan> --format compact`.
Explicitly
`legacy/imported` material is the only reconstruction path; it is not a current
plan exemption and requires refreshed approval as Manifest v2. Plans
without the versioned manifest are not actionable. Do not leave an automatable
obligation as narrative-only evidence or downgrade it to a manual obligation
to make preflight or closeout pass.

## Normative Manifest v2 Contract

The following is the shared producer-consumer contract. It is an authoring
checklist, not a second parser. The executor's `plan_execution.py` and
`scripts/run.sh preflight` are the sole mechanical authority; if this text and
the parser differ, the parser wins.

A current Manifest v2 has exactly these top-level fields, with no additions or
omissions:

`schema_version`, `manifest_version`, `plan_id`, `repository_root`,
`authority_boundaries`, `delegation`, `targets`, `controls`, `validations`,
`manual_obligations`, `tasks`, `retry_policy`, `approval`,
`bootstrap`, `rollout`, and `handoff`.

There is no v1/v2 parser compatibility mode. Imported or legacy plans must be
regenerated by the writer route as Manifest v2, then approved and preflighted.

Use these exact nested shapes and values:

- `authority_boundaries` has exactly `normative_owner`, `execution_owner`,
  `worker`, `caller_owns`, `protected_paths`, and `no_git_mutation`. The last
  value is `true`.
- Current `delegation` has exactly `schema_version`, `mode`, `worker`,
  `result`, `receipt`, and `acceptance`. Local authoring uses
  `schema_version: 1`, `mode: none`, `worker: primary-owner`, and
  `result: not_applicable`, with `receipt` and `acceptance` set to `null`.
  Manifest v2 does not manufacture delegated worker provenance.
- Each `targets` item has `id`, `path`, and `state`; `condition` is the only
  optional target field. `state` is `create`, `modify`, or `inspect`, and no
  target may be inside `.git`.
- `controls` is a non-empty map. Each value has exactly `class`, `owner`, and
  `binding`; `class` is `automatable-local`, `observable-runtime`,
  `external-capability`, `authority-or-scope`, or `genuine-human-judgment`.
- Each `validations` item has exactly `id`, `command`, `owner`, `pass_signal`,
  and `phases`; `equivalence` is the only optional validation field. Phases
  are `baseline`, `focused`, or `final`; equivalence is `exact-only` or
  `allowed-if-admissible`. `pass_signal`, not `success`, is the field name.
  Commands must be directly executable and must not mutate Git.
- Each `manual_obligations` item has exactly `id`, `kind`, `required`, and
  `acceptance`; `kind` is `human` or `external`. The list may be empty.
- Each `tasks` item has exactly `id`, `order`, `posture`, `objective`,
  `depends_on`, `target_ids`, `validation_ids`, `manual_obligation_ids`,
  `acceptance`, and `stop_conditions`. `posture` is
  `mandatory-test-first`, `feature-first`, `prototype-unverified`, or
  `validation-only`; task reference lists must contain only existing IDs.
- `retry_policy` has exactly `initial_attempts`, `max_context_refills`,
  `max_corrective_retries`, `caller_may_lower`, `repeat_progress_status`,
  and `minor_or_cosmetic_reopens`. Use `1`, `1`, `1`, `true`, `stalled`, and
  `false` respectively.
- `approval` has exactly `editorial_content_change` and
   `normative_manifest_change`; both fields are non-empty strings.
- `bootstrap` has exactly `mode`, `compatibility_projection`,
  `projection_binding`, `legacy_only`, and `retirement_evidence`. Current
  output uses `mode: manifest-only`, an empty compatibility projection, the
  exact bindings `manifest.controls`, `manifest.tasks`, `manifest.validations`,
  and `manifest.authority_boundaries`, and `legacy_only: reject`. The
  `explicit-single-plan` mode is reserved for the named migration plan and
  must project the legacy `Execution Contract` exactly.
- `rollout` is a non-empty list of strings. `handoff` has exactly
  `next_owner`, `requires`, `status_sibling`, and `git_mutation`; its owner is
  `/internal-gateway-execute-plans`, its requirements include human approval,
   exact Manifest v2 review, and zero blocking preflight findings, and
  it declares `status_sibling: none` and `git_mutation: prohibited`.

The Markdown projection must also bind exactly: Control Inventory IDs equal
`manifest.controls` keys; ordered Task headings equal `manifest.tasks` IDs;
task references resolve to manifest targets, validations, manual obligations,
and tasks; and manifest-only plans contain no `## Execution Contract`.

Keep plan metadata separate from runtime state. The plan does not contain
`approval_evidence`, `delivery_verdicts`, `completed_task_ids`,
`remaining_task_ids`, `last_validation`, `next_action`, `warnings`, or
`deviations`. After approval, the executor creates one YAML status sibling
with exactly `schema_version`, `status`, `plan`, `approval_evidence`,
`delivery_verdicts`, `completed_task_ids`, `remaining_task_ids`,
`last_validation`, `next_action`, `warnings`, and `deviations`; schema version
is `2`, and both successful terminal statuses require all five delivery categories to pass:
`structure`, `semantic_review`, `artifact_provenance`, `source_baseline`, and
`execution_readiness`.

Before handoff, the writer resolves the physical executor bundle and runs its
`scripts/run.sh preflight <plan> --format compact` independently, with zero
blocking findings. The writer never creates the status sibling or claims
execution approval. After explicit approval, the executor repeats preflight,
records hash-free approval evidence, and only then creates state and permits
the first task edit.

## Repository Preflight

Every current retained plan must contain this heading and concrete values for
each field below. The writer documents these fields; the executor parses and
enforces the retained plan.

- **Baseline Validation:** Run the manifest's baseline validation before edits and record the result.
- **Recovery Policy:** Allow only one distinct, task-local correction implied by the approved acceptance.
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
- Confirm the handoff names `/internal-gateway-execute-plans` and waits for
  explicit approval.
- Confirm the executor will record approval evidence and the five delivery
  verdicts in its YAML status sibling before terminal closeout.
- Run `git diff --check` and confirm no Git mutation occurred.
