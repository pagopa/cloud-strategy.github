# Authoring and Proportional Evaluation

## Intent contract

Recover known answers from the request and repository evidence. Capture the
capability, invocation conditions, expected output, constraints, dependencies,
success criteria, validation path, and anti-scope.

## Bundle evidence

For a bundle change, inspect every existing sibling under `references/`,
`scripts/`, `assets/`, and `agents/openai.yaml`, or record why a sibling is
intentionally unaffected. Checked-clean surfaces are evidence, not findings.

## Consumption and ownership

Distinguish a file's existence from selection or consumption through routing,
cross-skill calls, validators, tests, inventory, or sync. Keep generic
analysis-only review outside this creator.

## Lifecycle and retirement

Check compatibility, periodic maintenance, replacement, propagation, and
retirement readiness when the change affects them. Retirement must leave no
hollow references or unmanaged catalog fallout.

## Propagation and proof

Name each affected inventory, sync, validator, and test surface. Prefer the
smallest deterministic proof and record unavailable proof as a gap.

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
