# Node.js / TypeScript Review Anti-Patterns

Baseline owner: `internal-nodejs`

## Evidence threshold

Report a finding only when the changed code demonstrates a concrete
correctness, security, compatibility, resource-lifecycle, or operability risk.
Leave naming, import order, semicolons, trailing newlines, unused symbols, and
other mechanically enforceable style checks to repository tooling.

## Critical

| ID | Anti-pattern | Report when the evidence shows |
| --- | --- | --- |
| ND-C01 | Hardcoded secrets, tokens, or passwords | A credential can be exposed through the changed code or artifact. |
| ND-C02 | `eval()` or `new Function()` on untrusted input | Input reaches dynamic code execution without a trusted, constrained source. |
| ND-C03 | User input in `child_process.exec()` | Input reaches a shell command without a demonstrated safe argument boundary. |

## Major

| ID | Anti-pattern | Report when the evidence shows |
| --- | --- | --- |
| ND-M01 | Unhandled async failure | A rejected promise can escape an owned execution path without an intentional failure policy. |
| ND-M02 | Blocking I/O on a latency-sensitive path | Synchronous file or child-process work can block request or event processing. |
| ND-M03 | Unbounded outbound I/O | Network work lacks a timeout, cancellation, or bounded retry where the path can outlive its owner. |
| ND-M04 | Unjustified boundary `any` | External data crosses a TypeScript boundary without a documented validation or compatibility reason. |
| ND-M05 | Missing stream or event-emitter error handling | An owned stream or emitter can emit `error` without an observer. |
| ND-M06 | Missing listener or resource cleanup | A changed lifecycle leaves listeners, timers, streams, or controllers retained beyond ownership. |
| ND-M07 | Module-system mismatch | Imports, exports, or package settings conflict with the repository's active runtime conventions. |
| ND-M08 | Unjustified suppression directive | `@ts-ignore` or equivalent suppresses a defect without a local compatibility explanation. |

## Review examples

### Unsafe command-execution boundary

```javascript
// Reportable: request input is interpolated into a shell command.
import { exec } from "node:child_process";

export function removeArtifact(name) {
  return exec(`rm -rf /srv/artifacts/${name}`);
}
```

```javascript
// Safer boundary: the command and arguments are separated from the shell.
import { execFile } from "node:child_process";

export function removeArtifact(name) {
  return execFile("rm", ["-rf", `/srv/artifacts/${name}`]);
}
```

### Bounded outbound I/O

```javascript
// Reportable: the request has no owner-controlled timeout or cancellation.
export async function fetchUser(id) {
  const response = await fetch(`/users/${id}`);
  return response.json();
}
```

```javascript
// Bounded: the request is cancelled after the owned time budget.
export async function fetchUser(id) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 5000);
  try {
    const response = await fetch(`/users/${id}`, {
      signal: controller.signal,
    });
    if (!response.ok) throw new Error(`User fetch failed: ${response.status}`);
    return response.json();
  } finally {
    clearTimeout(timeout);
  }
}
```
