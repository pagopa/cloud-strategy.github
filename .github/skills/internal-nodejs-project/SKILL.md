---
name: internal-nodejs-project
description: Use when creating, modifying, reviewing, or refactoring Node.js or TypeScript application behavior and structure across services, APIs, handlers, modules, adapters, or tests. Route localized changes, package metadata, and dependencies to /internal-nodejs.
---

# Internal Node.js Project

## When to use

- Create, modify, review, or refactor application behavior across services,
  APIs, handlers, modules, adapters, or tests.
- Change boundaries between transport, domain logic, and infrastructure.
- Design or revise application-level error handling, concurrency, validation,
  or test seams.

This skill owns application composition, cross-boundary behavior,
transport-to-domain flow, infrastructure adapters, and application-level test
seams. Supporting package or runtime changes stay in scope only when the
application change requires them.

## When not to use

- Metadata-only, toolchain, dependency, compiler, or lockfile work, and other
  localized changes; route them to `/internal-nodejs`.
- Frontend design, Docker, workflows, and infrastructure; route them to their
  domain owners.

## Boundaries and errors

- Keep machine-readable payloads stable and undecorated at data boundaries,
  and keep human-friendly formatting at CLI or UI boundaries only.
- Keep logs structured and do not mix log streams with stdout payloads
  consumed by other tools.
- Validate external input with schema checks at API and module boundaries
  before domain logic runs.
- Classify operational failures at transport and infrastructure boundaries
  and handle them through one central async error path instead of ad-hoc
  per-handler response logic.
- Let programmer errors fail fast and stay visible.

## Application behavior

- Keep framework wiring thin and move request-shaping logic out of transport
  handlers when reuse or testing would improve.
- Keep async boundaries explicit between transport handlers, domain modules,
  and infrastructure adapters.
- Keep the event loop non-blocking; move CPU-heavy work to worker threads,
  queues, or external services.
- Observe intentional async outcomes, including fire-and-forget work whose
  ownership, failure handling, and lifecycle are explicit.

## Concurrency and resource lifecycle

- Use concurrency primitives only when their dependency assumptions are clear.
- Bound outbound work and clean up streams, timers, listeners, and other owned
  resources at the application boundary.

## Test design

- Follow the repository's established test stack and keep tests focused on
  observable module, API, adapter, or boundary behavior.
- Mock external boundaries while keeping internal modules real where practical.
- Cover changed branches and boundary failure paths with the smallest meaningful
  focused test set.

## Validation

- Run the repository-native tests and the closest configured validation for the
  changed application boundary.

## References

- [`references/common-mistakes.md`](references/common-mistakes.md): load for
  the full mistake table.
- [`references/examples.md`](references/examples.md): load when you need a
  minimal module or test example.
