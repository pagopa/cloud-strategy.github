---
name: internal-debugging
description: Use when a bug, test, build, validator, sync, workflow, or catalog-drift failure needs a reproducible root-cause diagnosis before a fix. This repository-owned wrapper applies a self-contained diagnosis baseline, uses /mattpocock-diagnosing-bugs as optional technique depth, and routes measured slowness or throughput to /internal-performance-optimization.
---

# Internal Debugging

Use this skill as the repository-owned owner for root-cause diagnosis. The
baseline below is self-contained and applies on its own.
`mattpocock-diagnosing-bugs` adds optional technique depth. This file is a
wrapper-owned contract; it cannot govern a session that loads the core without
this skill.

When an unexpected failure appears, stop adjacent work, preserve the current
evidence, and diagnose that failure before resuming unrelated changes.

## Referenced skills

This index lists every other skill that this file asks the agent to load,
route to, or delegate to. Load only the owner that the active diagnosis, next
claim, or validated handoff needs.

- `mattpocock-diagnosing-bugs`: optional depth for loop construction,
  tightening, flaky-rate raising, minimisation, instrumentation, seam
  analysis, and post-mortem.
- `internal-performance-optimization`: owner when measured slowness or
  throughput is primary.
- `internal-tdd`: regression-test workflow when a meaningful seam exists.
- `superpowers-verification-before-completion`: optional evidence gate before
  a fixed claim.
- Runtime-specific internal skills: language, workflow, Terraform, GitHub
  Actions, or script owners for idiomatic fixes and validation.

## When to use

- A test, build, validator, script, sync run, or workflow is failing.
- The user reports a bug, unexpected behavior, or inconsistent output.
- A catalog refresh, generated inventory, or governance check drifted from its
  expected result.
- A review finding needs a reproducible failure loop before the fix is safe.

## When not to use

- Use `/internal-performance-optimization` when slowness or throughput is the
  primary problem and a measurable performance question exists.
- Use `/internal-tdd` when the main job is test-first delivery of new executable
  behavior, not diagnosing a current failure.
- Do not force this skill onto Markdown-only, prompt-only, agent-only, or
  governance prose edits unless a validator or generated artifact is actually
  failing.

## Baseline

1. **Loop.** Before changing code or policy, name one command that drives the
   failing path and asserts the user's exact symptom: error text, wrong
   output, stale path, or drift signal. Prefer the closest existing validator,
   test, CLI invocation, fixture replay, or generated-artifact check. Run it at
   least once and show the redacted invocation and output. Do not fix a nearby
   different failure.
2. **Reliability.** Record the reproduction rate. For a flaky failure, raise
   the rate with controlled repetition or narrowed timing until it is
   debuggable, and record the repetition count.
3. **No loop.** If you cannot build a loop, stop. List what you tried and ask
   for environment access, a redacted artifact, or permission for temporary
   instrumentation. Do not hypothesise without a loop.
4. **Hypotheses.** Rank three to five falsifiable hypotheses, each with the
   prediction it makes. Probe one variable at a time. Do not fix before the
   evidence identifies the root cause.
5. **Probes.** Tag temporary instrumentation with a unique `DEBUG-` marker.
6. **Regression before fix.** When a correct seam exists, make the regression
   check fail on the bug, apply the root-cause fix, and watch the check pass.
   When no correct seam exists, record the seam gap as a finding.
7. **Close.** Rerun the original loop at the repetition count from step 2. One
   green run does not prove a flaky fix. Remove every `DEBUG-` probe.
8. **Redact.** Replace every secret with `<REDACTED>` in shown commands,
   output, and artifacts. Keep credentials in the environment.

## Technique depth

Load `/mattpocock-diagnosing-bugs` when the loop is hard to build, slow, or
flaky, or when minimisation, instrumentation, or seam analysis needs more
depth. If it is unavailable, continue with the baseline and report the gap. If
it no longer describes a feedback-loop discipline, do not use it; the baseline
still applies.

## Repository overrides

When the core text conflicts with this file, follow this file regardless of
load order:

- **Commits:** create no commit. State the winning hypothesis in the final
  report instead of a commit or PR message.
- **Performance:** route measured slowness or throughput to
  `/internal-performance-optimization` instead of the core performance branch.
- **Regression tests:** use `/internal-tdd` for the red-green-refactor loop
  when the seam is meaningful. Baseline step 6 still applies without it.
- **Context:** read `CONTEXT-MAP.md`, `docs/`, and `docs/adr/` instead of a
  `CONTEXT.md` file.
- **Architecture follow-ups:** report them as findings. Hand off only on user
  request.

## Completion requirements

- Name the loop, the exact failure it reproduced, and the reproduction rate.
- State the root cause, the winning hypothesis, and the change that fixed it.
- Show the regression check failing before the fix and passing after it, or
  the explicit seam gap.
- Show the original loop passing at the recorded repetition count.
- Confirm temporary instrumentation, throwaway fixtures, and debug-only files
  were removed or intentionally retained with a clear route.
- Optionally use `/superpowers-verification-before-completion` before claiming
  the bug, original loop, or drift signal is fixed. The requirements above
  apply without it.

## Common mistakes

- Patching the symptom before reproducing it.
- Testing only the guessed fix path instead of the original failure.
- Adding broad logs or broad refactors instead of one-variable probes.
- Declaring a flaky failure fixed after one green run.
- Leaving temporary instrumentation behind.
- Claiming a root cause when the evidence only proves correlation.
