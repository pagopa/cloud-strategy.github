---
applyTo: "**/*.js,**/*.cjs,**/*.mjs,**/*.ts,**/*.tsx"
---

# Node.js Instructions

## Mandatory rules
- Treat work as project-oriented (modules/services/handlers), not script-oriented.
- Add a concise purpose comment for new/changed core modules when intent is not obvious.
- Use emoji logs for key runtime states when logging is touched.
- Prefer early return and guard clauses.
- Keep code readable with straightforward control flow.
- Add unit tests for testable logic.

## Testing defaults
- Use built-in `node:test` + `node:assert/strict`.
- Prefer BDD-like structure (`describe`/`it` where available).
- Keep tests deterministic and isolated.

## Reference implementation
- For module and test examples, use `.github/skills/project-nodejs/SKILL.md`.
