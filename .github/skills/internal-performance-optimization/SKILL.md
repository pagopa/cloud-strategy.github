---
name: internal-performance-optimization
description: Use when performance is the primary problem, such as profiling slowness, reducing latency, improving throughput, or preventing regressions across frontend, backend, or database layers.
---

# Internal Performance Optimization

Use this skill when performance is the primary constraint. Start from measured
evidence, not intuition.

## When to use

- The user already has profiling evidence, benchmark data, query plans, or
  trace data pointing to a real bottleneck.
- The user has an explicit performance goal such as lower latency, higher
  throughput, or regression prevention that can be measured.

## When not to use

- The request is generic debugging with no evidence that performance is the
  dominant problem.
- The request is network-path specific and the main need is topology,
  connectivity, or transport tuning rather than application or database
  behavior. Load `/antigravity-network-engineer` when latency, DNS,
  load-balancer behavior, or network topology is the primary bottleneck.

## Workflow

1. Define the performance question, target, and acceptable regression budget.
2. Establish a baseline with a profiler, benchmark, timing harness, trace,
   query plan, or existing telemetry before changing behavior.
3. Locate the hottest path and rank falsifiable performance hypotheses. Load
   [Optimization checklists](references/optimization-checklists.md)
   for the domain checklist matching the measured bottleneck.
4. Change one variable at a time and remove wasted work before adding caching
   or concurrency.
5. Validate the fix with before/after evidence from the same measurement path.
6. Protect the gain with at least one regression-prevention measure:
   - benchmark, load-test, or regression-test coverage;
   - performance budget;
   - query-plan validation;
   - monitoring or alert threshold;
   - before/after evidence attached to the change record when automated
     protection is not practical.

## Core rules

- Do not optimize blind or claim a gain without a baseline.
- Fix the dominant bottleneck first; do not optimize cold code because it is
  easy to touch.
- Prefer simpler code paths before micro-optimizations.
- Avoid broad caching until query shape, render flow, or algorithm choice is
  understood; do not add cache layers to hide broken query shapes.
- Treat database, network, and serialization costs as first-class suspects.
- Keep measurement probes scoped and remove temporary timing or profiling code
  before completion unless it becomes an intentional diagnostic surface.

## Database anti-patterns

- Using `SELECT *` in hot paths.
- Using JSONB as a catch-all when relational modeling is clearer.
- Adopting PostgreSQL extensions or indexes without plan evidence and
  write-cost awareness.

## Validation

- Baseline and after-change measurements use the same measurement path.
- The claimed gain is backed by fresh output, traces, telemetry, or benchmark
  evidence.
- Regression protection exists, or the explicit protection gap is recorded.
- Load `/superpowers-verification-before-completion` before claiming a
  performance gain.
