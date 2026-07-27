---
name: internal-nodejs
description: Use when reviewing JavaScript or TypeScript, or when creating or editing Node.js package metadata, runtime configuration, dependencies, or a small localized module; use /internal-nodejs-project when application structure or behavior is the main concern.
---

# Internal Node.js

## Referenced skills

- `/internal-nodejs-project`: application structure and behavior across
  services, APIs, handlers, modules, adapters, and tests.

## Referenced files

- `references/review-anti-patterns.md`: load for evidence-based,
  Node.js-specific code review depth.

## When to use

- Review JavaScript or TypeScript changes for language, runtime, dependency,
  async, module-system, and boundary defects.
- Change `package.json`, `tsconfig.json`, supported lockfiles, scripts,
  dependencies, or runtime configuration.
- Make a localized module change whose package, architecture, and validation
  path are already clear.

## When not to use

- When application structure or behavior across services, APIs, handlers,
  modules, adapters, or tests is the primary concern, use `/internal-nodejs-project`.
- Route frontend design, generic JSON, Docker, workflows, and infrastructure
  to their domain owners.

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
