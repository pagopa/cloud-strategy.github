# Authoring and Proportional Evaluation

## Intent contract

Recover known answers from the request and repository evidence before asking
for input. Confirm the capability, invocation conditions, expected output,
constraints, dependencies, success criteria, validation path, and anti-scope.

## Bundle anatomy

Keep ordered actions and completion criteria in `SKILL.md`. Put branch-specific
facts and procedures behind explicit context pointers in `references/`. Add a
script only for deterministic or repeated work. Add an asset only when the
skill must reuse it in produced output. Keep `agents/openai.yaml` aligned with
the skill purpose.

## Evaluation selection

Classify each candidate branch as applicable, skipped, or blocked. Objective
file transformations, structured extraction, generated code, and fixed
workflows should use executable or assertion-based checks. Subjective writing,
design, and judgment work should use human review. Do not invent quantitative
assertions for subjective quality.

Use two or three realistic prompts when examples can expose behavior. Cover
the main path, one boundary or edge case, and one competing-owner or retrieval
case when relevant.

## Baselines

For a new skill, compare against the same task without the skill when the
runtime supports an isolated run. For a material revision, compare against a
snapshot of the previous version. If isolation is unavailable, record the gap
and use the closest focused validator plus human review.

## Evidence and human review

For each applicable branch, record the prompt or fixture, expected behavior,
observed result, validator or review method, and pass, fail, or blocked status.
Capture timing or token measurements only when the decision depends on them.
Present subjective outputs to the user before revising them from agent
judgment alone.

Generalize feedback into a reusable rule. Do not optimize only for the sampled
prompts. When multiple runs repeat the same deterministic work, consider a
bundle-local script instead of repeating instructions.

## Description trigger checks

Test realistic should-trigger prompts and difficult near-miss prompts that
share vocabulary but belong to another owner. Keep distinct branches
represented. When enough cases exist for tuning, reserve a holdout set and
select wording using holdout performance rather than training performance.
Record an explicit gap when the current runtime cannot measure invocation.

## Iteration stop conditions

Stop when the accepted prompts and validators pass, the user accepts subjective
outputs, or another iteration produces no decision-relevant improvement.
Remain blocked when required evidence cannot be produced; do not translate a
validation gap into success.

## Intentionally retired capabilities

This repository contract does not provide a Claude CLI trigger optimizer, HTML
review viewer, generic skill packager, full benchmark schema suite, or bundled
blind-comparison agents. Add any such capability only after a repository-owned
requirement identifies its owner, interface, test, and maintenance path.
