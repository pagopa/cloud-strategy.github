# Testing Recipes For Mixed Python Work

Use this reference when authoring or reorganizing tests across imported code,
entrypoints, or real cross-language boundaries. Preserve the declared runner,
framework, naming, and native component test locations.

## Contract map

Before editing, name the behavior, consumer, test level, owner, native location,
and focused command. For moved tests, record why the old location duplicates
coverage or assigns the wrong owner. A shell subprocess contract may have Python
assertions; reading shell or configuration source does not create that boundary.

| Boundary | Fastest useful check | Broader evidence |
| --- | --- | --- |
| Imported decision | Call real public behavior in process | Actual adapter or consumer when changed |
| Python entrypoint | Call importable decisions with explicit inputs | Documented invocation, status and outputs |
| Shell helper | Execute declared shell with a fixed invocation snippet | Declared shell implementations |
| Filesystem or external command | Isolated real file effects or boundary double | Required actual integration |

## Case selection and assertions

- Start with a meaningful success case, an error case, and a boundary case.
  Add empty, malformed, duplicate, or repeated inputs only when the contract
  distinguishes them. Cover changed decisions rather than multiplying examples.
- Name the realistic defect each test detects. Use literal or hand-checked
  expectations. A helper from the implementation must not compute the oracle.
- Assert observable values, stable diagnostics, exit codes, and intended or
  forbidden file effects. Exact wording matters only when consumers depend on it.
- Keep decisions real. Replace only actual external I/O or nondeterminism; assert
  arguments and ordering only when they are part of the boundary contract.
- Verify independence: each case owns its mutable state and cleanup. A private
  refactor preserving the contract should not require changing assertions.

## Isolation and fixtures

Use the framework's temporary workspace and cleanup facilities. Control relevant
home, configuration, locale, timezone, and command discovery for process tests;
retain required platform variables explicitly. Never point destructive cases at
real operator directories. Use explicit arguments, cwd, environment, capture,
and a bounded subprocess timeout with useful failure diagnostics.

Keep fixtures local, explicit, and small. Share immutable expensive setup only
when measurement justifies it. Reset mutable resources for every case. Keep
fixture dependencies shallow; add a shared helper only for repeated semantics.

## Feedback and proof

1. Follow the repository's test-first posture. Run the focused native case.
2. Run the owning component suite and relevant actual integration separately.
3. Exercise declared runtime compatibility, or report exactly what is unavailable.
4. Review whether representative wrong results, missing validation, and missing
   effects would fail the tests. Use a small disposable defect check where useful;
   a full mutation-testing dependency is optional and needs a measured benefit.
5. For speed work, record command, runtime, environment, selected cases, setup
   cost, and comparable before/after timings. Keep defect coverage intact.

Measure slow cases with the declared runner; pytest supports `--durations=10`.
Parallel execution requires independent resources and justified measured benefit.
Do not hide intermittent failures with blanket retries; reproduce and remove
uncontrolled state, timing, or environment dependence.

Bundle validation proves structure and executable examples only. Claims about
agent-generated test quality need separately observed evaluation outcomes.
