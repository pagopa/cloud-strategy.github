---
description: Go review checks for error handling, context use, concurrency safety, API contracts, and dependency scope.
applyTo: "**/*.go,**/go.mod,**/go.sum"
excludeAgent: "cloud-agent"
---

# Go Review Checks

This file is optimized for Copilot code review and should produce only evidenced findings on matching changed files.

- Verify error handling is explicit and no critical errors are silently ignored.
- Flag context misuse in I/O or network paths that can leak goroutines.
- Check exported APIs for clear contracts, naming, and package boundaries.
- Verify tests cover changed behavior and avoid flaky timing assumptions.
- Report data races, shared-state hazards, or unsafe concurrency patterns.
- Check dependency updates in `go.mod` and `go.sum` for unnecessary scope creep.
- Flag logging or panic usage that can expose sensitive operational details.
