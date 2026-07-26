---
name: internal-debugging
description: Use when a bug, test failure, build failure, validator drift, sync failure, or unexpected behavior needs a reproducible root-cause diagnosis before a fix.
---

# Internal Debugging

## Referenced skills

This index lists every other skill that this file asks the agent to load, route to, compare against, or delegate to.
Treat the referenced skills below as on-demand supports. Do not preload them
for every failure loop; load only the owner proved by the active diagnosis,
next claim, or validated handoff.

- `internal-review-code`: defect-first review when diagnosis exposes unsafe code or missing tests.
- `internal-performance-optimization`: performance owner when measured slowness or throughput is primary.
- `internal-tdd`: regression-test owner after the root cause is understood.
- `superpowers-systematic-debugging`: stricter diagnosis discipline for hard, flaky, or guess-prone failures.
- `superpowers-verification-before-completion`: evidence gate before claiming the original loop is fixed.

Use this skill as the repository-owned owner for root-cause diagnosis. Build a
feedback loop before changing behavior, then use evidence to narrow the cause.

When an unexpected failure appears, stop adjacent feature work, preserve the current evidence, and diagnose that failure loop before resuming unrelated changes.

## When to use

- A test, build, validator, script, sync run, or workflow is failing.
- The user reports a bug, unexpected behavior, or inconsistent output.
- A catalog refresh, generated inventory, or governance check drifted from its
  expected result.
- A review finding needs a reproducible failure loop before the fix is safe.

## When not to use

- Use `internal-performance-optimization` when slowness or throughput is the
  primary problem and a measurable performance question exists.
- Use `internal-review-code` when the task is review-only and no diagnosis loop
  is needed.
- Use `internal-tdd` when the main job is test-first delivery of new executable
  behavior, not diagnosing a current failure.
- Do not force this skill onto Markdown-only, prompt-only, agent-only, or
  governance prose edits unless a validator or generated artifact is actually
  failing.

## Diagnostic Loop

1. Build the fastest credible pass/fail loop before changing code or policy.
   Prefer the closest existing validator, test, CLI invocation, fixture replay,
   generated artifact check, or minimal harness that reproduces the symptom.
2. Reproduce the user's exact failure, including the error text, wrong output,
   stale path, or drift signal. Do not fix a nearby different failure.
3. Rank three to five falsifiable hypotheses. Each hypothesis must predict what
   will change if it is true.
4. Probe one variable at a time. Use temporary instrumentation only where it
   distinguishes hypotheses, tag it with a unique `DEBUG-` marker, and remove it
   before completion.
5. Minimize the reproducer until the root cause is visible. If the failure is
   flaky, raise the reproduction rate with controlled repetition or narrowed
   timing before guessing.
6. Add or update a regression test at the correct seam when executable behavior
   changed. Use `internal-tdd` for the red-green-refactor loop when the seam is
   meaningful.
7. Apply the root-cause fix, rerun the original loop, rerun the regression test
   or validator, and confirm all temporary probes are gone.

## Support Skills

- `superpowers-systematic-debugging`: stricter diagnosis discipline when the
  failure is hard, flaky, or tempting to guess at.
- `superpowers-verification-before-completion`: evidence gate before claiming
  that the bug, failing loop, or drift signal is resolved.
- `internal-tdd`: regression tests and public-interface test seams after the
  root cause is understood.
- `internal-review-code`: defect-first review when the diagnosis exposes a code
  smell, missing test, or unsafe fix.
- Runtime-specific internal skills: language, workflow, Terraform, GitHub
  Actions, or script owners for idiomatic fixes and validation.

## Completion Requirements

- Name the feedback loop and the exact failure it reproduced.
- State the root cause, the winning hypothesis, and the change that fixed it.
- Show the validation evidence that the original loop now passes.
- Show the regression test, validator, or explicit seam gap.
- Confirm temporary instrumentation, throwaway fixtures, and debug-only files
  were removed or intentionally retained with a clear route.
- Use `superpowers-verification-before-completion` before claiming the bug,
  original loop, or drift signal is fixed.

## Common mistakes

- Patching the symptom before reproducing it.
- Testing only the guessed fix path instead of the original failure.
- Adding broad logs or broad refactors instead of one-variable probes.
- Leaving temporary instrumentation behind.
- Claiming a root cause when the evidence only proves correlation.
