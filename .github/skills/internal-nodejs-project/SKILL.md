---
name: internal-nodejs-project
description: Use when creating, modifying, or refactoring Node.js or TypeScript application behavior and structure across services, APIs, handlers, modules, adapters, or tests; use /internal-nodejs for metadata-only, toolchain, or lightweight file-level work.
---

# Node.js Project Skill

## Referenced skills

- `/internal-nodejs`: Node.js and TypeScript review, package metadata,
  dependencies, runtime configuration, compiler settings, and localized module
  work.

## When to use

- Create, modify, or refactor application behavior across services, APIs,
  handlers, modules, adapters, or tests.
- Change boundaries between transport, domain logic, and infrastructure.
- Design or revise application-level error handling, concurrency, validation,
  or test seams.

## When not to use

- For metadata-only, toolchain, dependency, compiler, lockfile, review-only, or
  lightweight file-level work, use `/internal-nodejs`.
- Route frontend design, Docker, workflows, and infrastructure to their domain
  owners.

## Application boundaries

- Keep machine-readable payloads stable and undecorated at data boundaries, and keep human-friendly formatting at CLI or UI boundaries only.
- Keep logs structured and do not mix log streams with stdout payloads consumed by other tools.
- Classify operational errors at boundaries and handle them centrally; let programmer errors fail fast.
- Validate external input with schema checks at API and module boundaries before domain logic runs.

## Application behavior

- Keep framework wiring thin and move request-shaping logic out of transport handlers when reuse or testing would improve.
- Keep async boundaries explicit between transport handlers, domain modules, and infrastructure adapters.
- Use a central async error handler path instead of ad-hoc per-handler response logic.
- Keep the event loop non-blocking; move CPU-heavy work to worker threads, queues, or external services.
- Observe intentional async outcomes, including fire-and-forget work whose
  ownership, failure handling, and lifecycle are explicit.

## Concurrency and resource lifecycle

- Use concurrency primitives only when their dependency assumptions are clear.
- Bound outbound work and clean up streams, timers, listeners, and other owned
  resources at the application boundary.

## Error handling

- Validate inputs before domain logic runs and classify operational failures at
  transport and infrastructure boundaries.
- Keep programmer errors visible while handling expected operational failures
  through the application's central error path.

Load `references/examples.md` when you need a minimal module or test example.

## Test design

- Follow the repository's established test stack and keep tests focused on
  observable module, API, adapter, or boundary behavior.
- Mock external boundaries while keeping internal modules real where practical.
- Cover changed branches and boundary failure paths with the smallest meaningful
  focused test set.

## Common mistakes

Load `references/common-mistakes.md` for the full mistake table.

## Validation

- Run the repository-native tests and the closest configured validation for the
  changed application boundary.
