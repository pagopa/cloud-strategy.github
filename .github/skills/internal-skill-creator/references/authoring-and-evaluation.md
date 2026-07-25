# Authoring and Proportional Evaluation

## Intent contract

Recover known answers from the request and repository evidence. Capture the
capability, invocation conditions, expected output, constraints, dependencies,
success criteria, validation path, and anti-scope.

## Evaluation selection

Classify each candidate branch as applicable, skipped, or blocked. Objective
file transformations and fixed workflows use executable checks. Subjective
writing, design, and judgment work use human review.

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
