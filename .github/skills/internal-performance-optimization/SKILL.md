---
name: internal-performance-optimization
description: Use when performance is the primary problem, such as profiling slowness, reducing latency, improving throughput, or preventing regressions across frontend, backend, or database layers.
---

# Internal Performance Optimization

Use this skill when performance is the primary constraint. Start from measured
evidence, not intuition.

## When to use

- The user already has profiling evidence, benchmark data, query plans, or trace data pointing to a real bottleneck.
- The user has an explicit performance goal such as lower latency, higher throughput, or regression prevention that can be measured.

## When not to use

- The request is generic debugging with no evidence that performance is the dominant problem.
- The request is network-path specific and the main need is topology, connectivity, or transport tuning rather than application or database behavior.

## Workflow

1. Define the performance question, target, and acceptable regression budget.
2. Establish a baseline with a profiler, benchmark, timing harness, trace,
	query plan, or existing telemetry before changing behavior.
3. Locate the hottest path and rank falsifiable performance hypotheses.
4. Change one variable at a time and remove wasted work before adding caching or
	concurrency.
5. Validate the fix with before/after evidence from the same measurement path.
6. Protect the gain with a benchmark, budget, query-plan check, regression test,
	or monitoring threshold.

## Core Rules

- Do not optimize blind or claim a gain without a baseline.
- Fix the dominant bottleneck first.
- Prefer simpler code paths before micro-optimizations.
- Avoid broad caching until query shape, render flow, or algorithm choice is understood.
- Treat database, network, and serialization costs as first-class suspects.
- Keep measurement probes scoped and remove temporary timing or profiling code
	before completion unless it becomes an intentional diagnostic surface.

## Frontend Checks

- Re-render frequency
- Bundle size and lazy loading
- DOM churn and expensive layout work
- Image, font, and asset weight
- Request waterfalls and client caching

## Backend Checks

- N+1 patterns
- Avoidable I/O round-trips
- Unbounded concurrency
- Slow serialization or parsing
- Inefficient algorithms or data structures

## Database Checks

- Execution plan shape and row-estimate mismatches
- Missing or badly ordered indexes
- Functions on indexed columns in predicates
- Over-fetching
- Offset pagination on large tables
- Repeated aggregations that should be consolidated

## PostgreSQL-Specific Checks

- `EXPLAIN ANALYZE` and `pg_stat_statements`
- JSONB with GIN indexes only when the workload truly benefits
- Partial and expression indexes for selective predicates
- Full-text search when text filtering outgrows `LIKE`
- Extension choices only when they are explicit, justified, and operationally supportable

## Memory and CPU

- High allocation churn
- Duplicate object creation
- Work that should be streamed or batched
- Work happening on the critical path that can move off it

## Regression Prevention

After a fix, add at least one of:

- Benchmark or load-test coverage
- Performance budget
- Query-plan validation
- Monitoring or alert threshold
- Before/after evidence attached to the change record when automated protection
	is not practical

## Cross-references

- Use `internal-debugging` when the first problem is still root-cause isolation
	rather than a confirmed performance bottleneck.
- Use `superpowers-systematic-debugging` when the performance symptom is flaky
	or the reproduction loop is the hard part.
- Use `antigravity-network-engineer` when latency, packet flow, DNS, load-balancer behavior, or network topology is the primary bottleneck.

## Anti-Patterns

- Premature optimization before profiling
- Timing with a different harness before and after the fix
- Using `SELECT *` in hot paths
- Adding cache layers to hide broken query shapes
- Using JSONB as a catch-all when relational modeling is clearer
- Adopting PostgreSQL extensions or indexes without plan evidence and write-cost awareness
- Optimizing cold code because it is easy to touch
- Claiming performance gains without measurements
