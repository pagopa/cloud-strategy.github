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
  A user-accepted `Consolidated Analysis Spec` supplied by
  `/internal-gateway-idea` authorizes implementation-plan writing only when
  the user explicitly requests it. A direct invocation of this gateway
  requires explicit user approval in the current conversation. Neither path
  authorizes plan execution, status creation, or Git mutation.
1. Capture the target, anti-scope, nearest owner, validation path, stop
   conditions, and observable acceptance. Build a control inventory before
   delegation: classify every task, acceptance criterion, and declared
   `manual_obligation` exactly once as `automatable-local`,
   `observable-runtime`, `external-capability`, `authority-or-scope`, or
   `genuine-human-judgment`. Require an explicit `- No Git mutation.` bullet
   under `## Global Constraints` and a compact `## Control Inventory` in every
   current plan. Completion: all six facts, the no-mutation rule, and one owner
   for every obligation are recorded before delegation.
2. Lock exactly one parent-supplied retained plan path under
    `tmp/superpowers/plans/` and its required structure before delegation:
    ordered actionable tasks, concrete file targets, focused validation, a
    compact `## Control Inventory`, an execution handoff, and one normative
    `## Execution Manifest` v1 fenced JSON object. The manifest owns targets,
    controls, validations, tasks, authority boundaries, retry posture, approval
    binding, bootstrap metadata, and handoff. Imported
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
   one `## Execution Manifest` v1 fenced JSON object. New writer output uses
   `bootstrap.mode: manifest-only` and emits no legacy `## Execution Contract`.
   The current migration plan is the sole explicit compatibility projection;
   it is accepted only when its manifest metadata and Markdown projection bind
   exactly, and it retires at closeout.
  Classify each executable or evaluable task through `/internal-tdd`. Map
  every posture to focused and broad validation; require observed red-first
  evidence only for `mandatory-test-first`, while `feature-first` retains
  validation before production-ready completion.
  After eligibility, the control inventory, plan structure, locked decisions,
  and acceptance are complete, the gateway MUST write one `DelegationBrief` v1
  in `mode: plan` through `/internal-subagent-contract` before invoking
  `internal-luna-executor`. The brief declares the single retained-plan path
  as `write_scope` and `expected_output.path`, the plan objective and evidence,
  the required manifest and preflight acceptance, and exact focused validation.
  Luna MUST return the semantic fields for one `WorkerResult` v1. The runtime
  adapter composes deterministic fields and a caller-owned `VerificationReceipt`
  v1; unobserved validation and budget data remain claims or `unavailable`.
  When delegation adds provenance value, caller acceptance must bind the exact
  final artifact bytes and the manifest semantic fingerprint. A material edit
  invalidates the prior result and receipt. When delegation adds no provenance
  value, the primary owner performs the work without manufacturing a worker
  chain or retrospective authorship claim.
  The writer independently verifies the result, receipt, and plan, then runs the
  executor-owned `preflight`; it may use only the one bounded refill and one
  corrective retry allowed by the brief. The parent gateway retains
  eligibility, control classification, routing, authority, lifecycle, retry
  choice, human review, final independent `preflight`, handoff, and the
  no-Git-mutation boundary. No caller-identity branch changes this contract.
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
  status sibling together with approval evidence bound to the plan hashes. A
  standalone `validated` flag is not a readiness claim.
4. Report the retained plan path, name `/internal-gateway-execute-plans` as
  the only next owner, and wait for explicit execution approval. Do not invoke
  execution, create a status sibling, or offer an imported execution owner
  before that approval. Completion: the path and next owner are reported and
  execution has not started without approval.

## Command Portability

- Write every baseline, focused, and final validation command in directly
  executable native form. The command recorded in the plan is the
  authoritative command and evidence label.
- Do not make `rtk`, `graphify`, or another optional accelerator a prerequisite
  or command prefix unless the task's actual subject is that tool.
- Executor-side optimization may accelerate an invocation, but must not alter
  the recorded authoritative command or its validation meaning.

The executor owns the single mechanical plan validator. Do not add a
writer-local validator, a second implementation-plan writing lifecycle, or a
duplicate parser contract. The executor validates one normative Execution
Manifest v1; a legacy `## Execution Contract` is accepted only as the exact
compatibility projection declared by the migration manifest, never as a
standalone plan schema.
Before handoff, the parent gateway MUST resolve the executor's loaded physical
bundle and run its `scripts/run.sh preflight` independently against the written
current plan, then confirm zero blocking findings. The command is:
`bash <physical-executor-bundle>/scripts/run.sh preflight <plan> --format compact`.
Explicitly
`legacy/imported` material is the only reconstruction path; it is not a current
plan exemption and requires refreshed approval and semantic fingerprint. Plans
without the versioned manifest are not actionable. Do not leave an automatable
obligation as narrative-only evidence or downgrade it to a manual obligation
to make preflight or closeout pass.

### Producer readiness boundary

The writer owns producer-side readiness: it may prove the control inventory,
ordered task projection, manifest-only shape, and handoff ownership from the
plan it emits. These checks use parsed structure and do not import
`internal-gateway-execute-plans` or any executor-private module. The executor
bundle remains the only owner of retained-plan mechanical preflight, loaded
bundle resolution, state, and execution validation.

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
