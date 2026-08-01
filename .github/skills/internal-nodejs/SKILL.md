---
name: internal-nodejs
description: Use when reviewing localized JavaScript or TypeScript changes, changing Node.js package metadata, runtime configuration, dependencies, or editing a single module within established application boundaries.
---

# Internal Node.js

## Referenced files

- `references/review-anti-patterns.md`: load for evidence-based,
  Node.js-specific code review depth.

## When to use

- Review localized JavaScript or TypeScript changes for language, runtime,
  dependency, async, module-system, and resource-lifecycle defects.
- Change `package.json`, `tsconfig.json`, supported lockfiles, scripts,
  dependencies, or runtime configuration.
- Create, fix, or refactor a single module whose application boundaries and
  validation path are already clear.

## When not to use

- Do not use for application-wide changes spanning services, APIs, handlers,
  modules, adapters, or tests across multiple application boundaries.
- Route frontend design, generic JSON, Docker, workflows, and infrastructure
  to their domain owners.

## Responsibility boundary

- Own Node.js and TypeScript runtime correctness, package and compiler
  configuration, dependency intent, and localized module quality.
- Do not own application decomposition, cross-boundary behavior, transport
  orchestration, or application-wide test strategy.

## Baseline

- Follow the repository's local conventions for package manager, module system,
  runtime, compiler, and test stack before choosing defaults.
- Keep package metadata, scripts, dependency intent, lockfiles, and runtime
  configuration explicit and reproducible.
- Preserve the existing module system and package conventions unless the task
  explicitly changes them.
- Keep strict TypeScript boundary types and justify unavoidable `any` usage.
- Centralize runtime configuration and keep domain invariants in code rather
  than environment toggles.
- Bound async resources and outbound work with timeouts, cancellation, and
  cleanup where the execution path requires them.
- Run the repository-native validation nearest to the changed metadata or
  localized module.

## Validation

- Use the repository's established package, compiler, and test commands for
  the changed surface.
