---
name: internal-nodejs-project
description: Use when creating or modifying Node.js or TypeScript project code such as services, APIs, middleware, or modules, and the main concern is application code rather than Docker, workflows, or infrastructure.
---

# Node.js Project Skill

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

## Project-specific guidance

- Follow the existing module system and runtime constraints before introducing ESM/CJS or build-tool changes.
- Validate inputs at API or function boundaries and keep async error handling explicit.
- Keep framework wiring thin and move request-shaping logic out of transport handlers when reuse or testing would improve.

Load `references/examples.md` when you need a minimal module or test example.

## Test stack

- Follow the repository test-stack defaults.
- If the repository already uses Jest, stay with local Jest conventions instead of introducing mixed test stacks.
- For modify tasks: edit implementation first, run existing tests, then update tests only for intentional behavior changes.

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
