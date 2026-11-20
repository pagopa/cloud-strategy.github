# Testing Recipes For Imported Python Contracts

Use the declared framework and native layout. The runnable example in
[Project examples](examples.md) uses pytest; it does not require migrating an
existing suite. Keep tests near the component that owns the public behavior.

## Design useful cases

| Contract | Cases to consider | Observable assertion |
| --- | --- | --- |
| Pure decision | Meaningful branches and boundary values | Hand-derived result |
| Validation | Valid, malformed, empty, ambiguous inputs | Accepted result or specific error type |
| Stateful service | Allowed transition, refusal, repeated request | State and invariants after each operation |
| Persistence or adapter | Success, failure, partial response | Public result and intended or forbidden effects |

Select rows from the actual contract. A retry rule, rounding rule, duplicate
policy, or idempotency rule needs its own meaningful boundaries; a percentage
coverage target does not select them. Parameter IDs should explain the case.

## Test level and doubles

Call imported decisions directly; avoid a subprocess for each pure branch.
Keep internal collaborators real. Use boundary fakes or mocks for actual network,
clock, random, or persistence dependencies when isolation requires them.

A double must represent relevant complete response shapes and failure behavior.
Check request arguments when they constitute the actual adapter contract. A fake
that accepts any request cannot establish request correctness. Retain a focused
actual integration check when correctness depends on a driver or wire format.

Control time and randomness through existing boundaries. For async behavior,
use the repository's declared async runner and synchronization events instead
of sleeps. Avoid introducing test-only hooks in production code.

## Fixtures and independence

- Use temporary files for filesystem behavior and explicit cleanup for resources.
- Prefer function-local mutable fixtures. Share immutable expensive setup only
  with measured benefit; reset state between cases and workers.
- Keep fixture construction visible and representative. Extract repeated domain
  setup rather than building a generic factory framework for a single test.
- Test stable outcomes. Private renaming or rearrangement should preserve tests.
- Assert that rejected input leaves protected state unchanged when required.

## Example and defect proof

The project example tests blank identifier rejection and both lock decisions
with literal expectations. Removing validation or always returning `locked`
would break those tests. Execute both the contract and its test block; successful
compilation alone does not prove the assertions detect those defects.

Use a small controlled defective variant when a test's sensitivity is disputed.
Keep it in test fixtures or temporary output. Do not introduce a mandatory
mutation or property-testing dependency. Property-based tests are useful when
an actual invariant and input domain warrant them and the framework is available.

## Validation and speed

Run the focused case, then the component suite, relevant integration, and declared
compatibility. Use the declared interpreter and configured syntax and lint checks.
Report unavailable integration explicitly; a fake is not proof of a live service.

Measure slow tests before changing fixture scope or adding parallelism. Record
the same command, runtime, environment, case set, and setup policy before and
after optimization. With pytest, `--durations=10` helps identify expensive cases.
Compare repeated runs when timing is noisy; preserve the risky behavior coverage.
Keep intermittent failures visible and diagnose their state or timing cause.
