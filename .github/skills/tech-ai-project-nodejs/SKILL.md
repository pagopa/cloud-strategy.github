---
name: TechAIProjectNodejs
description: Create or modify Node.js/TypeScript project modules with purpose comments and BDD-like unit tests. Use when building Express services, TypeScript libraries, Node.js APIs, middleware patterns, async handlers, or module scaffolding.
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
- For modify tasks: edit implementation first, run existing tests, then update tests only for intentional behavior changes.

## Minimal test example
```javascript
const test = require("node:test");
const assert = require("node:assert/strict");

test("given missing id when building profile then throws", () => {
  assert.throws(() => buildUserProfile({}), /id is required/);
});
```

## Common mistakes

| Mistake | Why it matters | Instead |
|---|---|---|
| Mixing async/sync without `await` | Unhandled promise rejections, silent failures | Always `await` async calls; use `async` on the function |
| Business logic inside route handlers | Untestable, coupled to Express/framework | Extract to service modules, inject dependencies |
| Using `var` instead of `const`/`let` | Hoisting bugs, scope confusion | Use `const` by default, `let` only when reassignment is needed |
| Bare `catch(err) {}` that swallows errors | Silent failures, impossible to debug | Log the error and rethrow, or handle specifically |
| No input validation on API boundaries | Runtime crashes on malformed input | Validate and fail fast at handler entry |
| Callback-style code in modern Node.js | Hard to read, callback hell | Use async/await with Promises |

## Cross-references
- **TechAICodeReview** (`.github/skills/tech-ai-code-review/SKILL.md`): for reviewing Node.js code (see `references/anti-patterns-nodejs.md`).
- **TechAIDocker** (`.github/skills/tech-ai-docker/SKILL.md`): for containerizing Node.js apps.

## Validation
- Run tests: `node --test` or `npm test`.
- Lint: `npx eslint .` when configured.
- Type check: `npx tsc --noEmit` for TypeScript projects.
