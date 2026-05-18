---
name: internal-tdd
description: Use when executable behavior should be delivered test-first, including red-green-refactor feature work, bugfix regression tests, public-interface test design, or validation seams.
---

# Internal TDD

Use this skill as the repository-owned meta-owner for test-first delivery. Keep
the loop focused on observable behavior through public interfaces.

## When to use

- The user asks for TDD, red-green-refactor, test-first work, or integration
  tests before implementation.
- A bugfix has a meaningful executable seam and needs a regression test before
  the fix.
- A script, validator, reusable module, or application path changes behavior
  that can be checked through a stable interface.
- A risky behavior change benefits from one small vertical slice at a time.

## When not to use

- Do not force TDD onto Markdown-only, prompt-only, agent-only, skill-only,
  instruction-only, inventory-only, or governance-only edits.
- Do not use TDD as the default gate for mechanical formatting, catalog
  rebuilds, generated inventory, or text realignment with no executable seam.
- Do not write a bulk suite before implementation. Use one behavior at a time.

## Applicability Levels

| Level | Use when | Required posture |
| --- | --- | --- |
| Mandatory | The user explicitly asks for TDD, or a bugfix changes executable behavior with a credible regression seam. | Write the failing test before the fix. |
| Recommended | The change touches domain logic, scripts, validators, APIs, or workflow behavior with meaningful edge cases. | Start with the most valuable public-interface behavior. |
| Not suitable | The change is repository-owned prose, prompt, agent, skill, instruction, inventory, or governance text with no executable contract. | Use review, validator, or catalog checks instead. |

## Workflow

1. Identify the public interface or operator-facing command that should carry
   the behavior.
2. Pick one behavior for the first vertical slice. Avoid testing implementation
   shape, private helpers, or imagined future branches.
3. Write one failing test and confirm it fails for the intended reason.
4. Implement the smallest correct change that makes that test pass.
5. Repeat one behavior at a time. Let each passing slice inform the next test.
6. Refactor only while green, and rerun the focused tests after each refactor.
7. Finish by running the closest broader validation that covers the changed
   behavior.

## Test Shape Rules

- Test behavior, not implementation details.
- Prefer public APIs, CLIs, generated outputs, or stable validator entrypoints.
- Mock only external boundaries or expensive collaborators when the real path
  would make the test slow, flaky, unsafe, or unavailable.
- Keep test names in the repository's domain language when one exists.
- Use stack-specific internal skills for idiomatic test layout, fixtures, and
  framework conventions.

## Support Skills

- `superpowers-test-driven-development`: strict red-green-refactor execution
  when the user explicitly asks for a TDD workflow.
- `internal-debugging`: root-cause diagnosis before the regression test when the
  failure is not yet understood.
- `internal-project-python`, `internal-project-nodejs`, `internal-project-java`,
  and other stack owners: idiomatic test placement, fixtures, and assertions.
- `internal-code-review`: defect-first review of test quality, coverage gaps,
  and false-confidence seams.

## Validation

- The failing test failed before the fix, or the explicit seam gap is recorded.
- The test exercises a public or stable interface.
- The implementation is the smallest behavior needed for the active slice.
- Focused tests and the closest broader validation pass.
- No speculative tests or features were added beyond the requested behavior.
