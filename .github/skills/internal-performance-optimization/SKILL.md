---
name: internal-performance-optimization
description: Performance profiling, latency reduction, throughput tuning, rendering efficiency, memory control, SQL/query tuning, caching strategy, and regression prevention. Use when the task is to diagnose slowness, optimize runtime behavior, improve responsiveness, or design performance-focused changes across frontend, backend, or database layers.
---

# Internal Performance Optimization

Use this skill when performance is the primary constraint. Start from evidence, not intuition.

## Workflow

1. Measure the problem.
2. Locate the hottest path.
3. Remove wasted work.
4. Validate with before/after evidence.
5. Protect the gain with tests, benchmarks, or budgets.

## Core Rules

- Do not optimize blind.
- Fix the dominant bottleneck first.
- Prefer simpler code paths before micro-optimizations.
- Avoid broad caching until query shape, render flow, or algorithm choice is understood.
- Treat database, network, and serialization costs as first-class suspects.

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

- Missing or badly ordered indexes
- Functions on indexed columns in predicates
- Over-fetching
- Offset pagination on large tables
- Repeated aggregations that should be consolidated

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

## Anti-Patterns

- Premature optimization before profiling
- Using `SELECT *` in hot paths
- Adding cache layers to hide broken query shapes
- Optimizing cold code because it is easy to touch
- Claiming performance gains without measurements
