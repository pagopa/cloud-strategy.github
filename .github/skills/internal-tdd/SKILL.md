---
name: internal-tdd
description: Use when modifying code with executable or evaluable behavior, including features, bugfixes, behavior changes, public-interface changes, regression tests, contract seams, or risk-driven test-first guardrails.
---

# Internal TDD

## Referenced skills

This index lists every other skill that this file asks the agent to load, route to, compare against, or delegate to.

- `superpowers-test-driven-development`: core red-green-refactor loop after this wrapper selects a mandatory-test-first slice.
- `superpowers-verification-before-completion`: evidence gate before completion, passing, or coverage claims.

Use this skill as the repository-owned owner for coding changes with executable
or evaluable behavior. It classifies the local seam, names the lightest useful
guardrail, and then delegates mandatory-test-first execution to
`/superpowers-test-driven-development`.

This wrapper does not redefine test quality or recovery mechanics. Those belong
to the core skill. It selects the risk- and stage-based posture that controls
whether the core skill owns sequencing.

## When to use

- Features, diagnosed bugfixes, or intentional behavior changes with an executable seam.
- Public-interface changes, adapters, tools, modules, validators, scripts,
  CLIs, parsers, sync automation, generators, reports, or structured outputs
  whose behavior can be checked through a stable boundary.
- Prompt, agent, or LLM-output drift with concrete failure examples or an
  evaluable contract.
- Coding work that needs a repository-local decision about which test posture is
  appropriate.

## When not to use

- Prose-only, prompt-only, skill-only, inventory-only, generated-only,
  formatting-only, or governance-only edits with no executable or evaluable
  contract.
- Review-only work where the job is defect-first review rather than
  implementation.
- Mechanical realignment with no behavior change and no credible executable
  seam.

## Test Postures

| Posture | Use when | Required posture |
| --- | --- | --- |
| `mandatory-test-first` | The work is a reproducible bug fix, regression, behavior-preserving refactor, established public contract, or involves security, authorization, secrets, persistent state, migration, destructive behavior, or another high-impact failure mode. | Choose the observable behavior, establish red evidence, then load `/superpowers-test-driven-development` for the implementation loop. |
| `feature-first` | The work is a new, exploratory, reversible capability and changes no established contract. | Implementation may precede the durable regression check, but focused and broader validation must be reachable before `feature-first-validated` completion. |
| `prototype-unverified` | The work is an explicit learning artifact with declared scope, risk, and missing validation. | Never present it as production-ready; report the missing evidence. |
| `validation-only` | No useful executable or evaluable seam exists. | Name the seam gap and alternate validator before editing. |

The postures are mutually exclusive. A new-feature label alone never grants
`feature-first`; risk and delivery stage control the choice. Reading
instructional source and asserting its wording does not create an evaluable
seam.

## Execution Contract

1. Identify the observable behavior, risk, or evaluable contract and select
   exactly one posture before implementation.
2. Choose the nearest owner, stable boundary, native test layout, established
   runner, local command, and CI trigger. Use an external-language harness only
   for a real cross-language boundary such as a CLI, plan JSON, filesystem,
   protocol, or remote API; Python is not a universal harness.
3. For `mandatory-test-first`, establish red evidence and delegate the
   implementation loop to `/superpowers-test-driven-development` rather than
   reproducing it locally.
4. For prompt, agent, or LLM-output drift, define concrete evaluation examples
   or failure cases before changing behavior.
5. After the parent locks the posture, boundary, artifact shape, write scope,
   and validation, it may invoke `internal-luna-executor` for the specified
   work. The parent retains boundary choice, red proof, refactor, and final
   verification.
6. Run the focused check and closest broader validation, then load
   `/superpowers-verification-before-completion` before positive claims.

## Completion

| State | Required evidence |
| --- | --- |
| `test-first-validated` | The `mandatory-test-first` loop has observed red evidence plus fresh focused and broader passing validation. |
| `feature-first-validated` | The `feature-first` work has fresh focused validation and reachable broader validation. |
| `prototype-unverified` | Scope, risk, and missing validation remain explicit; the artifact is not production-ready. |
| `validation-only` | The seam gap and alternate validation are recorded. |

Tests or checks added after implementation are not TDD. Classify them honestly
under the selected posture; do not reconstruct existing implementation solely
to manufacture a test-first history.
