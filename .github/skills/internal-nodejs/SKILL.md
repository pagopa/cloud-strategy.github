---
name: internal-nodejs
description: Use when reviewing localized JavaScript or TypeScript changes, changing Node.js package metadata, runtime configuration, dependencies, or editing a single module within established application boundaries. Route application or service structure, adapters, and cross-module behavior to /internal-nodejs-project.
---

# Internal Node.js

## When to use

- Review localized JavaScript or TypeScript changes for language, runtime,
  dependency, async, module-system, and resource-lifecycle defects.
- Change `package.json`, `tsconfig.json`, supported lockfiles, scripts,
  dependencies, or runtime configuration.
- Create, fix, or refactor a single module whose application boundaries and
  validation path are already clear.

This skill owns Node.js and TypeScript runtime correctness, package and
compiler configuration, dependency intent, and localized module quality.

## When not to use

- Application decomposition, cross-boundary behavior, transport
  orchestration, application-wide test strategy, or changes spanning services,
  APIs, handlers, modules, adapters, or tests across multiple application
  boundaries. Route application/service structure, adapters, and cross-module
  behavior to `/internal-nodejs-project`.
- Frontend design, generic JSON, Docker, workflows, and infrastructure; route
  them to their domain owners.

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

## Validation

- Run the repository's established package, compiler, and test commands
  nearest to the changed metadata or localized module.

## References

- [`references/review-anti-patterns.md`](references/review-anti-patterns.md):
  load for evidence-based, Node.js-specific code review depth.
