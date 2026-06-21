---
name: internal-nodejs-project
description: Use when creating or modifying Node.js or TypeScript project code such as services, APIs, middleware, or modules, and the main concern is application code rather than Docker, workflows, or infrastructure.
---

# Node.js Project Skill

## Referenced skills

Treat the referenced skill below as an on-demand owner. Do not preload it for
every project edit; load it when baseline Node.js or TypeScript metadata rules
are the primary concern.

- `internal-nodejs`: baseline Node.js and TypeScript guidance for package metadata, lockfiles, scripts, and compiler settings.

## When to use

- Services, handlers, adapters, and utility modules.
- Refactoring or extending existing Node.js components.

## When not to use

- Generic JSON formatting is the only concern and the file is not Node.js project metadata.
- Frontend design or browser UI behavior is the dominant task.

## Compact Node.js baseline

- Keep business logic in focused modules, separate from transport adapters and infrastructure wiring.
- Prefer early returns, clear domain names, and straightforward control flow.
- Use `node:test` and `node:assert/strict` unless the repository already standardizes on another test framework.
- Keep `package.json` scripts, engines, and dependency intent explicit.
- Prefer strict `tsconfig.json` settings unless a documented compatibility reason exists.
- Preserve the existing module system and package conventions unless the task explicitly changes them.

## Boundary

- Keep machine-readable payloads stable and undecorated at data boundaries, and keep human-friendly formatting at CLI or UI boundaries only.
- Keep logs structured and do not mix log streams with stdout payloads consumed by other tools.
- Classify operational errors at boundaries and handle them centrally; let programmer errors fail fast.
- Validate external input with schema checks at API and module boundaries before domain logic runs.

## Project-specific guidance

- Follow the existing module system and runtime constraints before introducing ESM/CJS or build-tool changes.
- Validate inputs at API or function boundaries and keep async error handling explicit.
- Keep framework wiring thin and move request-shaping logic out of transport handlers when reuse or testing would improve.
- Keep async boundaries explicit between transport handlers, domain modules, and infrastructure adapters.
- Use a central async error handler path instead of ad-hoc per-handler response logic.
- Keep the event loop non-blocking; move CPU-heavy work to worker threads, queues, or external services.
- Centralize environment-aware config loading and keep domain invariants out of env parsing.

Load `references/examples.md` when you need a minimal module or test example.

## Test stack

- Follow the repository test-stack defaults.
- If the repository already uses Jest, stay with local Jest conventions instead of introducing mixed test stacks.
- For behavior changes or bug fixes, write or update the failing test first, then implement and re-run.
- For pure refactors, run existing tests before and after while keeping public behavior unchanged.
- Prefer parameterized table-style tests when many input/output cases exercise one behavior.
- Mock only external boundaries and keep internal modules real where practical.
- Focus coverage on changed branches and boundary failure paths.

## Runtime and async guidance

- Prefer `async`/`await` over promise chains unless streaming or concurrency composition clearly benefits from lower-level primitives.
- Use `Promise.all` only for independent work; use `Promise.allSettled` when partial failure is acceptable.
- Keep CPU-heavy work off request paths or move it to worker threads or an external service.
- Choose framework and runtime patterns from the repository first; do not switch to Fastify, NestJS, Bun, or another stack without an explicit reason.
- Default to the current module system. Use ESM for new projects only when the repo and toolchain already support it cleanly.

## Testing guidance

- Prefer unit tests and narrow integration tests over broad end-to-end coverage for every module change.
- In Jest repos, use focused mocks and reset them between tests; do not introduce Jest where the project already standardizes on `node:test`.
- Keep async tests explicit with `await`, `assert.rejects`, or the framework-native async helpers.

## Common mistakes

Load `references/common-mistakes.md` for the full mistake table.

## Validation

- Run tests: `node --test` or `npm test`.
- Lint: `npx eslint .` when configured.
- Type check: `npx tsc --noEmit` for TypeScript projects.
