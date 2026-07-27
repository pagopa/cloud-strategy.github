# Java Review Defects

Primary owner: `internal-java`. Report a pattern only when repository evidence
shows that it creates a correctness, security, maintainability, or observable
boundary problem. Review cues are not universal mandates.

## Critical

| ID | Anti-pattern | Why |
| --- | --- | --- |
| JV-C01 | Hardcoded secrets, tokens, or passwords | Credential exposure risk |
| JV-C02 | Deserialization of untrusted data (`ObjectInputStream`) | Remote code execution risk |
| JV-C03 | SQL string concatenation instead of parameterized queries | SQL injection |

## Major

| ID | Anti-pattern | Why |
| --- | --- | --- |
| JV-M01 | Caught failure is swallowed or converted without preserving the required observable error | Silent or misleading failures |
| JV-M02 | Missing `try-with-resources` for `AutoCloseable` | Resource leak |
| JV-M03 | Shared mutable state crosses concurrent boundaries without a proven synchronization or ownership model | Race conditions |
| JV-M04 | Raw types or unchecked casts can accept an invalid value without a documented, checked boundary | Type-safety erosion |
| JV-M05 | Public or external input crosses a boundary without validation required by the contract | Invalid state or unsafe behavior |
| JV-M08 | `System.out.println` in application/library code | No log level control |

## Minor

| ID | Anti-pattern | Why |
| --- | --- | --- |
| JV-m01 | Unused imports | Dead code noise |
| JV-m02 | `@SuppressWarnings` or an equivalent escape hatch lacks an inline reason | Hides real issues |
| JV-m03 | Dead code, unreachable branches, or commented-out implementation remains in the changed path | Maintenance burden |
| JV-m04 | Mutable collections or internal state escape a public boundary where callers can violate invariants | Encapsulation leak |
| JV-m05 | Changed public behavior lacks a focused test for its observable contract or boundary failure | Regression risk |

## Review cues

- A large class, method, or constructor is a review cue when its actual
  responsibilities, branching, or collaborator set makes behavior hard to
  understand or test. Do not assign severity from a line-count threshold.
- Request documentation when a changed public type or method has non-obvious
  contract or intent. Do not require JavaDoc for every public symbol.
- Prefer the repository formatter and linter for naming, imports, braces, and
  whitespace; do not duplicate formatter policy here.

## Example

```java
// BAD (JV-M02): resource leak
public String readFile(Path path) throws IOException {
    BufferedReader reader = new BufferedReader(new FileReader(path.toFile()));
    return reader.readLine();
}

// GOOD: preserve the resource lifecycle
public String readFile(Path path) throws IOException {
    try (var reader = new BufferedReader(new FileReader(path.toFile()))) {
        return reader.readLine();
    }
}
```
