# Node.js Project Examples

## Boundary service example

The service validates application input, calls an injected external adapter,
and returns a stable domain result without transport objects.

```javascript
export function createProfileService(profileAdapter) {
  return async function getProfile(input) {
    if (!input?.id) {
      throw new Error("id is required");
    }

    const profile = await profileAdapter.load(input.id);
    return {
      id: profile.id,
      name: profile.name ?? "unknown",
    };
  };
}
```

## Boundary behavior test

This is a minimal illustrative fixture using `node:test`; execution follows
the repository's established test stack.

```javascript
import { test } from "node:test";
import assert from "node:assert/strict";

test("rejects a profile request without an id", async () => {
  const service = createProfileService({
    load: async () => ({ id: "unused" }),
  });

  await assert.rejects(() => service({}), /id is required/);
});
```
