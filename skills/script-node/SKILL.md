---
name: script-node
description: Create Node.js scripts with purpose header, emoji logs, early return flow, and unit tests.
---

# Node.js Script Skill

## When to use
- Node.js CLI scripts.
- Small automation utilities.
- Data processing scripts in JavaScript/TypeScript.

## Mandatory rules
- Add a top comment block with purpose.
- Use emoji logs for key execution states.
- Prefer early return and guard clauses.
- Keep code readable and straightforward.
- Add unit tests for testable behavior.

## Template

```javascript
/**
 * Purpose: {description}
 */

function run(argv) {
  if (!argv.includes("--input")) {
    console.error("❌ Missing --input");
    return 1;
  }

  console.log("🚀 Starting {script_name}");
  // Implementation here
  console.log("✅ Completed");
  return 0;
}

if (require.main === module) {
  process.exit(run(process.argv.slice(2)));
}

module.exports = { run };
```

## Test template

Create `tests/{script_name}.test.js`:

```javascript
const test = require("node:test");
const assert = require("node:assert/strict");
const { run } = require("../{script_name}");

test("returns error when --input is missing", () => {
  assert.equal(run([]), 1);
});
```

## Checklist
- [ ] Purpose is documented at the top.
- [ ] Emoji logs are used for key states.
- [ ] Guard clauses use early return.
- [ ] Code is readability-first.
- [ ] Unit tests are included for testable behavior.
