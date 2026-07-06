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

Use this skill as the repository-owned owner for coding changes with executable behavior. Keep the test strategy risk-driven, keep the loop focused on observable behavior, and explain briefly when no new test is useful.

## When to use

- Features, bugfixes, or intentional behavior changes with an executable seam.
- Public-interface changes, adapters, tools, modules, validators, or structured outputs whose behavior can be checked through a stable boundary.
- Prompt, agent, or LLM-output drift when the change has an executable or evaluable contract with concrete failure examples.
- Any coding change where the main failure mode should be identified before implementation and guarded with the lightest useful test-first slice.

## When not to use

- Prose-only, prompt-only, skill-only, inventory-only, generated-only, formatting-only, or governance-only edits with no executable or evaluable contract.
- Review-only work; use the review lane separately when the job is defect-first review rather than implementation.
- Mechanical realignment with no behavior change and no credible executable seam.

## Applicability Levels

| Level | Use when | Required posture |
| --- | --- | --- |
| Mandatory | The change adds or changes executable behavior, or the user explicitly asks for TDD. | Identify the main failure mode, choose the lightest useful guardrail, and write or update the focused failing test first unless no new test is useful. |
| Recommended | The change touches public boundaries, adapters, modules, structured outputs, or evaluable prompt behavior with meaningful risk. | Prefer contract tests at public boundaries and keep the slice small and reviewable. |
| Not suitable | The change is prose-only, prompt-only, skill-only, inventory-only, generated-only, formatting-only, or governance-only with no executable or evaluable contract. | Do not manufacture tests; explain briefly why no new test is useful and use the closest validator or review gate instead. |

## Workflow

1. Identify the main failure mode before implementation.
2. Choose the lightest useful guardrail for the active risk.
3. Write or update a focused failing test first for new or changed behavior.
4. Add the regression test before the bug fix when the task is a bugfix.
5. Prefer contract tests at public boundaries over tests of private implementation details.
6. Use small, reviewable golden or snapshot tests only when they are the clearest guardrail.
7. For prompt, agent, or LLM-output drift, define concrete eval examples or failure cases before changing the implementation.
8. Finish with the closest broader validation and do not weaken, delete, skip, or rewrite tests just to pass.

## Test Shape Rules

- Test behavior, not implementation details.
- Prefer public APIs, CLIs, generated outputs, or stable validator entrypoints.
- Mock only external boundaries or expensive collaborators when the real path would make the test slow, flaky, unsafe, or unavailable.
- Keep test names in the repository's domain language when one exists.

## Support Skills

- `superpowers-test-driven-development`: core red-green-refactor execution when an executable test-first slice is selected.
- `internal-debugging`: root-cause diagnosis before the regression test when the failure is not yet understood.
- `superpowers-verification-before-completion`: evidence gate before claiming coverage, fix completion, or red-green-refactor success.

## Validation

- The failing test failed before the fix, or the explicit seam gap is recorded.
- The test exercises a public or stable interface.
- The implementation is the smallest behavior needed for the active slice.
- Focused tests and the closest broader validation pass.
- No speculative tests or features were added beyond the requested behavior.
- Use `superpowers-verification-before-completion` before claiming red-green-refactor completion or that a regression is covered.
