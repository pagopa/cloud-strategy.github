---
name: internal-nodejs
description: Use when creating, editing, or reviewing JavaScript, Node.js, TypeScript, package.json, tsconfig.json, or package-manager lockfile work before project depth is needed.
---

# Internal Node.js

## Referenced skills

Treat the referenced skill below as an on-demand owner. Do not preload it for
every Node.js or TypeScript edit; load it only when application structure,
package architecture, or deterministic test design becomes the real issue.

- `internal-nodejs-project`: Node.js or TypeScript services, APIs, middleware, modules, and deterministic tests when project-level architecture becomes the main concern.

## When to use

- `.js`, `.cjs`, `.mjs`, `.ts`, `.tsx`, `package.json`, `tsconfig.json`, or Node.js package-manager lockfile changes.
- Lightweight Node.js or TypeScript reviews focused on readability, boundary hygiene, dependency intent, scripts, engines, or compiler options.
- Small module edits where the target package and validation path are concrete.

## When not to use

- Service, API, middleware, package architecture, or test design is the main concern; use `internal-nodejs-project`.
- Generic JSON formatting is the only concern and the file is not Node.js project metadata.
- Frontend design or browser UI behavior is the dominant task.

## Baseline

- Keep business logic in focused modules, separate from transport adapters and infrastructure wiring.
- Prefer early returns, clear domain names, and straightforward control flow.
- Treat 300 lines as a review threshold for cohesive JavaScript and TypeScript files.
- Treat 400 lines as a split-or-justify threshold and move repeated decision logic into focused modules.
- Apply pragmatic DRY: extract repeated decision paths and shared adapters, but avoid speculative abstractions.
- Use `node:test` and `node:assert/strict` unless the repository already standardizes on another test framework.
- Keep `package.json` scripts, engines, and dependency intent explicit.
- Keep dependency delivery reproducible: no vendored packages, commit the lockfile, and use `npm ci` for deterministic installs.
- Keep comments, JSDoc, logs, thrown errors, and operator-facing output in English.
- Centralize runtime configuration and keep domain invariants in code rather than environment toggles.
- Keep strict `tsconfig.json` settings enabled, avoid drift toward `any`, and type external boundaries explicitly.
- Preserve the existing module system and package conventions unless the task explicitly changes them.

## Validation

- Run the nearest `npm`, `pnpm`, `yarn`, or `node --test` command already used by the repository.
- Run TypeScript checking when `tsconfig.json` or typed source changes.
