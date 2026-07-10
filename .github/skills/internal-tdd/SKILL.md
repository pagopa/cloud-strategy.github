---
name: internal-tdd
description: Use when modifying code with executable or evaluable behavior, including features, bugfixes, behavior changes, public-interface changes, regression tests, contract seams, or risk-driven test-first guardrails.
---

# Internal TDD

## Referenced skills

This index lists every other skill that this file asks the agent to load, route to, compare against, or delegate to.

- `superpowers-test-driven-development`: core red-green-refactor loop after this wrapper selects a mandatory test-first slice.
- `superpowers-verification-before-completion`: evidence gate before completion, passing, or coverage claims.

Use this skill as the repository-owned owner for coding changes with executable
or evaluable behavior. It classifies the local seam, names the lightest useful
guardrail, and then delegates mandatory TDD execution to
`superpowers-test-driven-development`.

This wrapper does not redefine red, green, refactor, test quality, or recovery
mechanics. Those belong to the core skill.

## When to use

- Features, bugfixes, or intentional behavior changes with an executable seam.
- Public-interface changes, adapters, tools, modules, validators, scripts,
  CLIs, parsers, sync automation, generators, reports, or structured outputs
  whose behavior can be checked through a stable boundary.
- Prompt, agent, or LLM-output drift with concrete failure examples or an
  evaluable contract.
- Coding work that needs a repository-local decision about whether TDD is
  mandatory, recommended, or not useful.

## When not to use

- Prose-only, prompt-only, skill-only, inventory-only, generated-only,
  formatting-only, or governance-only edits with no executable or evaluable
  contract.
- Review-only work where the job is defect-first review rather than
  implementation.
- Mechanical realignment with no behavior change and no credible executable
  seam.

## Applicability Levels

| Level | Use when | Required posture |
| --- | --- | --- |
| Mandatory | The change adds or changes executable behavior, or the user explicitly asks for TDD. | Name the observable behavior or risk, choose the smallest useful stable check, then load `superpowers-test-driven-development`. |
| Recommended | The change touches public boundaries, adapters, modules, structured outputs, or evaluable prompt behavior with meaningful risk. | Prefer a public-boundary check and keep the slice small. |
| Not suitable | The change has no practical executable or evaluable contract. | Do not manufacture tests; name the seam gap and use the closest validator or review gate. |

## Core Contract

- Delegate mandatory red-green-refactor work to
  `superpowers-test-driven-development`; do not run a local copy of its loop.
- Before implementation, record one of three routing outcomes:
  `mandatory`, `recommended`, or `not suitable`.
- For `mandatory`, load the core skill before changing behavior.
- For `recommended`, keep the check at the most meaningful public or stable
  boundary.
- When adding tests, keep them under repository-root `tests/` and choose paths
  that make the covered owner or checked behavior obvious. Use the nearest
  owner for deeper layout conventions.
- For `not suitable`, name the seam gap and the alternate validation path before
  implementation.
- Tests or checks added after implementation are regression coverage only. Do
  not describe them as test-first work.

## Workflow

1. Identify the observable behavior, risk, or evaluable contract.
2. Pick the closest public or stable boundary that can prove it.
3. Choose `mandatory`, `recommended`, or `not suitable`.
4. Load `superpowers-test-driven-development` only for mandatory TDD execution.
5. For prompt, agent, or LLM-output drift, define concrete eval examples or
   failure cases before changing behavior.
6. Finish with the focused check, the closest broader validation, and
   `superpowers-verification-before-completion` before positive claims.

## Completion States

- `red-green-refactor`: the core skill owned the loop and fresh evidence shows
  the focused check plus broader validation passed.
- `exception-based`: the seam gap was named before implementation and the
  alternate validation ran or its gap was reported.
- `regression-only`: tests or checks were added after implementation. Report
  this honestly and do not claim test-first work.

## Validation

- The wrapper chose `mandatory`, `recommended`, or `not suitable` before
  implementation.
- Mandatory slices loaded `superpowers-test-driven-development`.
- Not-suitable slices named the seam gap and alternate validation path.
- Focused checks and the closest broader validation ran, or the gap was
  reported.
- Completion declares whether the work was `red-green-refactor`,
  `exception-based`, or `regression-only`.
- Final claims passed through `superpowers-verification-before-completion`.
