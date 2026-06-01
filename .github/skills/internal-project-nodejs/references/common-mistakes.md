# Common Mistakes For Node.js Projects

| Mistake | Why it matters | Instead |
| --- | --- | --- |
| Mixing async/sync without `await` | Unhandled promise rejections, silent failures | Always `await` async calls; use `async` on the function |
| Business logic inside route handlers | Untestable, coupled to Express/framework | Extract to service modules, inject dependencies |
| Using `var` instead of `const`/`let` | Hoisting bugs, scope confusion | Use `const` by default, `let` only when reassignment is needed |
| Bare `catch(err) {}` that swallows errors | Silent failures, impossible to debug | Log the error and rethrow, or handle specifically |
| No input validation on API boundaries | Runtime crashes on malformed input | Validate and fail fast at handler entry |
| Callback-style code in modern Node.js | Hard to read, callback hell | Use async/await with Promises |
| Mixing Jest and `node:test` in the same project without reason | Duplicated conventions and confusing tooling | Follow the test stack already used by the repository |
| Changing module system casually | Breaks tooling, imports, and runtime behavior | Stay with the existing ESM/CJS choice unless the migration is explicit |
| Using `Promise.all` on dependent work | Masks ordering assumptions and makes failures harder to interpret | Keep dependent async steps sequential |
