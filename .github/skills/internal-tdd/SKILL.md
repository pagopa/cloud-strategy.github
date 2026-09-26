---
name: internal-tdd
description: Use when modifying code with executable or evaluable behavior, including features, bugfixes, refactors, public-interface changes, regression tests, or prompt and LLM-output drift with concrete failure cases.
---

# Internal TDD

Repository-owned owner for coding changes with executable or evaluable
behavior. Select one test posture, name the lightest guardrail that proves it,
and hand `mandatory-test-first` sequencing to
`/superpowers-test-driven-development`. Test quality and recovery mechanics
belong to that core skill.

## Referenced skills

This index lists every other skill that this file asks the agent to load, route to, compare against, or delegate to.

- `superpowers-test-driven-development`: red-green-refactor loop for `mandatory-test-first`.
- `superpowers-verification-before-completion`: evidence gate before completion, passing, or coverage claims.
- `internal-subagent-contract`: brief, result, and receipt protocol for optional delegation.
- `internal-debugging`: root-cause owner when a bug's cause is not yet known.
- `internal-skill-creator`: owner for skill-bundle prose, metadata, and eval packs.
- `internal-review-code`: owner for review-only work.

## When to use

- Features, diagnosed bugfixes, refactors, or intentional behavior changes
  with an executable seam.
- Public interfaces, adapters, tools, modules, validators, scripts, CLIs,
  parsers, sync automation, generators, reports, or structured outputs whose
  behavior can be checked through a stable boundary.
- Prompt, agent, or LLM-output drift with concrete failure examples or an
  evaluable contract.

## When not to use

- Bugs whose root cause is unknown: route to `/internal-debugging`, then
  return here for the regression check.
- Prose-only, prompt-only, inventory-only, generated-only, formatting-only, or
  governance-only edits with no executable or evaluable contract.
- Skill-bundle prose or metadata: route to `/internal-skill-creator`. Scripts
  inside a bundle stay here.
- Review-only work: route to `/internal-review-code`.
- Mechanical realignment with no behavior change and no credible executable
  seam.

## Test postures

| Posture | Use when | Required posture |
| --- | --- | --- |
| `mandatory-test-first` | The work is a reproducible bug fix, regression, behavior-preserving refactor, established public contract, or involves security, authorization, secrets, persistent state, migration, destructive behavior, or another high-impact failure mode. | Load `/superpowers-test-driven-development` before writing the first test and follow its test-quality reference. For new or corrected behavior, observe a failure caused by the missing or incorrect behavior before changing production code. For a behavior-preserving refactor, first pin current behavior with a passing characterization check at the chosen boundary, then refactor under it. |
| `feature-first` | The work is a new, exploratory, reversible capability and changes no established contract. | Implementation may precede the durable regression check. Completion requires fresh focused validation and the closest applicable broader validation. |
| `prototype-unverified` | The work is an explicit learning artifact with declared scope, risk, and missing validation. | Never present it as production-ready; report the missing evidence. |
| `validation-only` | No useful executable or evaluable seam exists. | Name the seam gap and alternate validator before editing. |

Selection rules:

- The postures are mutually exclusive. Select exactly one before
  implementation.
- When one task mixes postures, split it into slices with one posture each.
- Risk and delivery stage control the choice. A new-feature label alone never
  grants `feature-first`.
- Finished production work never moves to `prototype-unverified` to obtain a
  completion label.
- Reading instructional source and asserting its wording does not create an
  evaluable seam.

Use the nearest native validator for the property it can establish. For
deterministic configuration or infrastructure-template edits where the owning
format provides a native validator, such as `terraform validate` and
`terraform test`, that native validator is the selected validation seam;
recording it satisfies the posture requirement. A formatter such as
`terraform fmt` proves formatting only. Use `validation-only` only when
the task has no useful executable or evaluable seam. Do not pre-classify all
prompt or skill work as `validation-only`, and do not require an additional
wording test, harness, or manufactured TDD ceremony for such edits. Selecting
a command is not execution evidence. Formatting or schema validation does not
establish behavioral correctness. Do not manufacture a failing test for a
formatting-only change. For a semantic change, select a behavioral check or
report the unverified property.

## Execution contract

1. Identify the observable behavior, risk, or evaluable contract, and select
   the posture.
2. Choose the nearest owner, stable boundary, native test layout, established
   runner, local command, and CI trigger. Use an external-language harness only
   for a real cross-language boundary such as a CLI, plan JSON, filesystem,
   protocol, or remote API; Python is not a universal harness.
3. When the task creates, moves, merges, deletes, or replaces tests, or moves
   them across a language boundary, record the behavior, owner, test level,
   native location, runner or trigger, duplication evidence, and decision.
   Other tasks do not need this record.
4. Apply the posture's required action from the table. For prompt, agent, or
   LLM-output drift, define concrete evaluation examples or failure cases
   before changing behavior.
5. Delegation is optional. After the parent locks the posture, boundary,
   artifact shape, write scope, acceptance, and validation, it may delegate
   through `/internal-subagent-contract` with one `DelegationBrief` v1 and
   follow its result, receipt, and lifecycle protocol. The parent retains
   posture and boundary choice, routing, authority, lifecycle, retry choice,
   red or characterization proof, refactor, independent validation, and final
   verification.
6. Run the focused check, then the closest applicable broader validation.
   Load `/superpowers-verification-before-completion` before any positive
   claim.

## Completion

| State | Required evidence |
| --- | --- |
| `test-first-validated` | The `mandatory-test-first` loop has observed red evidence, or passing characterization evidence for a behavior-preserving refactor only, plus fresh focused and broader passing validation. |
| `feature-first-validated` | The `feature-first` work has fresh focused validation and the closest applicable broader validation. |
| `prototype-unverified` | Scope, risk, and missing validation remain explicit; the artifact is not production-ready. |
| `validation-only` | The seam gap and alternate validation are recorded. |
| `blocked` | A required in-scope check could not be observed or does not pass; the failing or missing check and the next action are recorded. |

When the broader check fails outside the task scope, show the same failure on
the base state and record it as pre-existing in `gaps`; the validated state
remains available and the implementation is not reopened for it. When the
broader check is unavailable, report the verified scope and the missing
evidence; never imply complete validation.
A red run that fails from an import, syntax, collection, or environment error
is not red evidence.

Tests or checks added after implementation are not TDD. Classify them honestly
under the selected posture; do not reconstruct existing implementation solely
to manufacture a test-first history.

## Posture record

Report one record per task, in this order:

1. `posture`: the selected posture and the risk or stage that decided it.
   For `mandatory-test-first`, state whether the change is `behavior` or
   `refactor`.
2. `boundary`: the observable behavior and the native test location.
3. `checks`: each focused and broader command with its observed result,
   including red or characterization evidence when required.
4. `state`: one completion state.
5. `gaps`: missing evidence and the next action, or `none`.

When the record is stored as a file, follow
[`references/posture-record.md`](references/posture-record.md) and run
`scripts/check_posture_record.py` from this bundle.
