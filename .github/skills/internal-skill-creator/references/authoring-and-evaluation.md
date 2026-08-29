# Authoring and Proportional Evaluation

## Intent contract

Recover known answers from the request and repository evidence. Capture the
capability, invocation conditions, expected output, constraints, dependencies,
success criteria, validation path, and anti-scope.

## Creator delegation matrix

Delegate only after the parent fixes the complete task-specific objective,
value gate, bounded evidence, constraints, write scope, expected output,
acceptance, validation, and budget.

| Creator task | Mode | Expected output | Write scope | Parent acceptance |
| --- | --- | --- | --- | --- |
| Multi-file inventory or consumer mapping | `read` | bounded analysis/evidence | empty | Every named path and consumer class is covered; no unresolved decision is silently inferred. |
| Evidence inventory across known sources | `read` | bounded analysis/evidence | empty | Evidence refs resolve and authority remains with the parent. |
| Draft after outline, metadata, acceptance, and validation are fixed | `plan` | one artifact at one exact path | one exact draft path | Parent reviews semantic content and applies or accepts it. |
| One bounded implementation artifact | `write` | one artifact | one exact file or artifact path | Parent runs independent validation and accepts the result. |
| Bounded validation set with multiple observable checks | `read` | validation evidence | empty | All declared checks and pass signals are present. |

A single command, one obvious edit, unresolved policy, boundary, authority, or
acceptance, incomplete acceptance, and unverifiable prose stay local or blocked.
A competing-owner request stays with its owner; a Copilot agent under
`.github/agents/` routes to `/internal-agent-creator`.

Use one worker, one brief, and one result. Default to one attempt. A corrective
retry requires new evidence and a concrete correction target, and it must carry
a changed brief. Cosmetic, punctuation, prose-only, and semantic disagreement do
not reopen the worker.
Direct worker writes are limited to one exact declared artifact; the parent
reviews and accepts it. The worker never edits the creator contract, inventory,
approval records, protected bundles, or broad directories.

## Bundle evidence

For a bundle change, inspect every existing sibling under `references/`,
`scripts/`, `assets/`, and `agents/openai.yaml`, or record why a sibling is
intentionally unaffected. Checked-clean surfaces are evidence, not findings.

## Consumption and ownership

Distinguish a file's existence from selection or consumption through routing,
cross-skill calls, validators, tests, inventory, or sync. Keep generic
analysis-only review outside this creator.

After the parent locks the required inventory, consumer map, outline, metadata
shape, or evaluation command, it may invoke `internal-luna-executor` through
`/internal-subagent-contract` with one `DelegationBrief` v1. The caller verifies
the adapter-composed `WorkerResult` v1 and caller-owned `VerificationReceipt`
v1; unobserved worker validation and budget data remain claims or unavailable
evidence. When timeout, interruption, executor unavailability, or missing
terminal output prevents a worker payload, the caller records a
`LifecycleRecord` and creates neither a synthetic `WorkerResult` nor a
`VerificationReceipt`. Trigger, boundary, policy, scope, retry choice,
independent validation, acceptance, semantic review, closeout, and subjective
authoring decisions remain with the parent.

## Lifecycle and retirement

Check compatibility, periodic maintenance, replacement, propagation, and
retirement readiness when the change affects them. Retirement must leave no
hollow references or unmanaged catalog fallout.

## Propagation and proof

Name each affected inventory, sync, validator, and test surface. A report or
output-contract change propagates to three surfaces: the SKILL.md contract,
`agents/openai.yaml`, and the paired `.github/agents/<name>.agent.md` when one
exists. A session started before the change keeps the previous snapshot; prove
the new contract from a newly started session. Prefer the smallest
deterministic proof and record unavailable proof as a gap.

## Self-review risk

When this skill revises its own contract, name the rationalization risk and
prefer evidence from external consumers and focused tests.

## Evaluation selection

Classify each candidate branch as applicable, skipped, or blocked. Objective
file transformations and fixed workflows use executable checks. Subjective
writing, design, and judgment work use human review.

| Change surface | Required evidence |
| --- | --- |
| Frontmatter, metadata, paths, references | Parsed structural validator |
| Script, CLI, parser, generator | Executable test with fixtures |
| Stable public output | Producer and consumer test |
| LLM routing or trigger | Executable resolver or concrete evaluation cases |
| Subjective instructional prose | Human review with an explicit evidence gap when runtime evaluation is unavailable |
| Editorial wording or reorganization | Markdown and token validation only |

Raw instructional wording is not an executable or evaluable seam. Do not
manufacture wording tests when a change has no parser, executable consumer,
public protocol, or concrete evaluation case.

## Baselines

For a material revision, compare with the previous version. For a new skill,
compare with the same task without it when isolation is available. Otherwise,
record the gap and use the closest focused validator plus human review.

## Evidence and human review

For each applicable branch, record the prompt or fixture, expected and observed
behavior, review method, and status. Present subjective outputs to the user
before changing them from agent judgment alone. Generalize feedback; do not
optimize only for sampled prompts.

## Description trigger checks

Test realistic should-trigger and near-miss prompts. Include the main branch
and a competing-owner case. When tuning against enough cases, reserve a holdout
set. Record a gap when the runtime cannot measure invocation.

## Iteration stop conditions

Stop when the accepted prompts and validators pass, the user accepts subjective
outputs, or another iteration adds no decision-relevant evidence. Keep required
evidence gaps blocked.

## Portability and invocation contract

`SKILL.md` frontmatter allows only `name`, `description`, `metadata`, `license`,
and `compatibility`. Invocation policy goes to `agents/openai.yaml` under
`policy.allow_implicit_invocation`. Provenance fields (`source`, `risk`,
`date_added`, and `revision`) go under `metadata`. The validator blocks
non-portable fields.

## Skill evaluation harness

A new skill requires at least three realistic scenario prompts, should-trigger
and should-not-trigger cases (including one competing-owner near-miss), and a
baseline comparison without the skill. A material revision re-runs trigger
checks only when the description changed.
