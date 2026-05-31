---
name: internal-nodejs
description: Use when creating, editing, or reviewing JavaScript, Node.js, TypeScript, package.json, or tsconfig.json work before project depth is needed.
---

# Internal Node.js

## Referenced skills

- `internal-project-nodejs`: Node.js or TypeScript services, APIs, middleware, modules, and deterministic tests.

## When to use

- `.js`, `.cjs`, `.mjs`, `.ts`, `.tsx`, `package.json`, or `tsconfig.json` changes.
- Lightweight Node.js or TypeScript reviews focused on readability, boundary hygiene, dependency intent, scripts, engines, or compiler options.
- Small module edits where the target package and validation path are concrete.

## When not to use

- Service, API, middleware, package architecture, or test design is the main concern; use `internal-project-nodejs`.
- Generic JSON formatting is the only concern and the file is not Node.js project metadata.
- Frontend design or browser UI behavior is the dominant task.

## Baseline

- Keep business logic in focused modules, separate from transport adapters and infrastructure wiring.
- Prefer early returns, clear domain names, and straightforward control flow.
- Use `node:test` and `node:assert/strict` unless the repository already standardizes on another test framework.
- Keep `package.json` scripts, engines, and dependency intent explicit.
- Prefer strict `tsconfig.json` settings unless a documented compatibility reason exists.
- Preserve the existing module system and package conventions unless the task explicitly changes them.

## Validation

- Run the nearest `npm`, `pnpm`, `yarn`, or `node --test` command already used by the repository.
- Run TypeScript checking when `tsconfig.json` or typed source changes.
