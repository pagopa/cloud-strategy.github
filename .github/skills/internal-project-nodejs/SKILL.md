---
name: internal-project-nodejs
description: Create or modify Node.js/TypeScript project modules with purpose comments, async/runtime judgment, and repository-aligned test strategy. Use when building Express services, TypeScript libraries, Node.js APIs, middleware patterns, async handlers, or module scaffolding.
---

# Node.js Project Skill

## When to use
- Services, handlers, adapters, and utility modules.
- Refactoring or extending existing Node.js components.

## Mandatory rules
- Keep business logic in focused modules, separate from transport and infrastructure.
- Use clear, domain-relevant naming for core modules and errors.
- Add a concise top purpose comment for new/changed core modules when intent is not obvious.
- Use emoji logs for key runtime states when logging is touched.
- Prefer early return and guard clauses.
- Keep code readable and straightforward.
- Follow the existing module system and runtime constraints before introducing ESM/CJS or build-tool changes.
- Validate inputs at API or function boundaries and keep async error handling explicit.
- Add unit tests for testable logic.

## Minimal module example
```javascript
/** Purpose: Build a user profile response. */
function buildUserProfile(input) {
  if (!input?.id) {
    throw new Error("❌ id is required");
  }
  return { id: input.id, name: input.name ?? "unknown" };
}
```

## Test stack
- Built-in `node:test` + `node:assert/strict`.
- BDD-like grouping (`describe`/`it`) when available.
- If the repository already uses Jest, stay with local Jest conventions instead of introducing mixed test stacks.
- For modify tasks: edit implementation first, run existing tests, then update tests only for intentional behavior changes.

## Minimal test example
```javascript
const test = require("node:test");
const assert = require("node:assert/strict");

test("given missing id when building profile then throws", () => {
  assert.throws(() => buildUserProfile({}), /id is required/);
});
```

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

| Mistake | Why it matters | Instead |
|---|---|---|
| Mixing async/sync without `await` | Unhandled promise rejections, silent failures | Always `await` async calls; use `async` on the function |
| Business logic inside route handlers | Untestable, coupled to Express/framework | Extract to service modules, inject dependencies |
| Using `var` instead of `const`/`let` | Hoisting bugs, scope confusion | Use `const` by default, `let` only when reassignment is needed |
| Bare `catch(err) {}` that swallows errors | Silent failures, impossible to debug | Log the error and rethrow, or handle specifically |
| No input validation on API boundaries | Runtime crashes on malformed input | Validate and fail fast at handler entry |
| Callback-style code in modern Node.js | Hard to read, callback hell | Use async/await with Promises |
| Mixing Jest and `node:test` in the same project without reason | Duplicated conventions and confusing tooling | Follow the test stack already used by the repository |
| Changing module system casually | Breaks tooling, imports, and runtime behavior | Stay with the existing ESM/CJS choice unless the migration is explicit |
| Using `Promise.all` on dependent work | Masks ordering assumptions and makes failures harder to interpret | Keep dependent async steps sequential |

## Cross-references
- **internal-code-review** (`.github/skills/internal-code-review/SKILL.md`): for reviewing Node.js code (see `.github/skills/internal-code-review/references/anti-patterns-nodejs.md`).
- **internal-docker** (`.github/skills/internal-docker/SKILL.md`): for containerizing Node.js apps.

## Validation
- Run tests: `node --test` or `npm test`.
- Lint: `npx eslint .` when configured.
- Type check: `npx tsc --noEmit` for TypeScript projects.
