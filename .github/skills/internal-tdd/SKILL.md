---
name: internal-tdd
description: Use when coding changes have executable behavior, including features, bugfixes, behavior changes, public-interface changes, regression tests, contract seams, or risk-driven test-first guardrails.
---

# Internal TDD

## Referenced skills

This index lists every other skill that this file asks the agent to load, route to, compare against, or delegate to.

- `internal-debugging`: root-cause diagnosis before regression tests when the failure is not yet understood.
- `superpowers-test-driven-development`: strict red-green-refactor execution when an executable test-first slice is selected.
- `superpowers-verification-before-completion`: evidence gate before claiming coverage, fix completion, or red-green-refactor success.

Use this skill as the repository-owned owner for coding changes with executable
behavior. Keep the test strategy risk-driven, keep the loop focused on
observable behavior, and make any no-test path explicit before implementation.

## When to use

- Features, bugfixes, or intentional behavior changes with an executable seam.
- Public-interface changes, adapters, tools, modules, validators, scripts,
  CLIs, parsers, sync automation, generators, reports, or structured outputs
  whose behavior can be checked through a stable boundary.
- Prompt, agent, or LLM-output drift when the change has an executable or evaluable contract with concrete failure examples.
- Any coding change where the main failure mode should be identified before implementation and guarded with the lightest useful test-first slice.

## When not to use

- Prose-only, prompt-only, skill-only, inventory-only, generated-only, formatting-only, or governance-only edits with no executable or evaluable contract.
- Review-only work; use the review lane separately when the job is defect-first review rather than implementation.
- Mechanical realignment with no behavior change and no credible executable seam.

## Applicability Levels

| Level | Use when | Required posture |
| --- | --- | --- |
| Mandatory | The change adds or changes executable behavior, or the user explicitly asks for TDD. | Identify the main failure mode, choose the lightest useful guardrail, and write or update the focused failing test before the first implementation edit unless a pre-code exception is recorded. |
| Recommended | The change touches public boundaries, adapters, modules, structured outputs, or evaluable prompt behavior with meaningful risk. | Prefer contract tests at public boundaries and keep the slice small and reviewable. |
| Not suitable | The change is prose-only, prompt-only, skill-only, inventory-only, generated-only, formatting-only, or governance-only with no executable or evaluable contract. | Do not manufacture tests; explain briefly why no new test is useful and use the closest validator or review gate instead. |

## Core Contract

- `test-first` means the test or check is written or updated before the first
  implementation edit.
- An implementation edit is any change to an artifact that creates, changes, or
  removes executable or evaluable behavior.
- Tests or checks added after implementation are regression coverage only; do
  not describe them as test-first work.
- For changes without a practical stable seam, record a TDD exception note
  before implementation. Name the seam gap, the alternate validation path, and
  why a focused failing check is not practical.
- If the gate was skipped, stop, disclose the violation, load this contract,
  and recover without claiming a retroactive red-green-refactor cycle.

## Workflow

1. Identify the main failure mode before implementation.
2. Choose the lightest useful guardrail for the active risk.
3. Write or update a focused failing test or check before the first
   implementation edit for new or changed behavior.
4. Add the regression test before the bug fix when the task is a bugfix.
5. Prefer contract tests at public boundaries over tests of private implementation details.
6. Use small, reviewable golden or snapshot tests only when they are the clearest guardrail.
7. For prompt, agent, or LLM-output drift, define concrete eval examples or failure cases before changing the implementation.
8. Finish with the closest broader validation and do not weaken, delete, skip, or rewrite tests just to pass.

## Test Shape Rules

- Test behavior, not implementation details.
- Prefer public APIs, CLIs, generated outputs, stable validator entrypoints, or
  machine-readable output contracts.
- Mock only external boundaries or expensive collaborators when the real path would make the test slow, flaky, unsafe, or unavailable.
- Keep test names in the repository's domain language when one exists.

## Completion States

- `red-green-refactor`: a focused failing check existed before implementation,
  the implementation made it pass, and the closest broader validation ran or
  the gap was named.
- `exception-based`: a pre-code TDD exception note exists, and the named
  alternate validation ran or the gap was reported.
- `regression-only`: tests or checks were added after implementation. Report
  this honestly and do not claim test-first work.

## Support Skills

- `superpowers-test-driven-development`: core red-green-refactor execution when an executable test-first slice is selected.
- `internal-debugging`: root-cause diagnosis before the regression test when the failure is not yet understood.
- `superpowers-verification-before-completion`: evidence gate before claiming coverage, fix completion, or red-green-refactor success.

## Validation

- The failing test or check failed before the implementation edit, or the
  pre-code TDD exception note is recorded.
- The test exercises a public or stable interface.
- The implementation is the smallest behavior needed for the active slice.
- Focused tests and the closest broader validation pass.
- No speculative tests or features were added beyond the requested behavior.
- Completion declares whether the cycle was `red-green-refactor`,
  `exception-based`, or `regression-only`.
- Use `superpowers-verification-before-completion` before claiming red-green-refactor completion or that a regression is covered.
