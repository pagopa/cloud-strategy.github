---
description: Python standards for both scripts and application code with DDD boundaries, guard clauses, and pytest defaults.
applyTo: "**/*.py"
excludeAgent: "cloud-agent"
---

# Python Review Checks

This file is optimized for Copilot code review and should produce only evidenced findings on matching changed files.

- Verify guard clauses and error handling make failure modes explicit.
- Flag unsafe input handling, shell invocation, or filesystem side effects.
- Check function and module boundaries for readability and cohesion.
- Flag behavioral configuration buried in helpers, services, or library modules instead of centralized at the correct boundary: a script entrypoint, `Configuration` section, settings module, adapter, application factory, or composition root.
- Do not flag stable domain invariants merely because they are constants near domain code.
- Verify type hints and public interfaces stay consistent with call sites.
- Flag manual formatting churn that fights the repository formatter; when Ruff is configured, prefer `ruff format` and Ruff diagnostics over subjective style edits.
- Report dependency usage that is unpinned or unnecessary for the change.
- Flag vendored libraries, wheelhouses, copied site-packages, or fallback dependency mirrors.
- Flag new external dependencies that are missing hash-locked pins in the owning requirements file.
- Check tests for deterministic coverage of changed behavior.
- Flag logging or exception messages that may leak sensitive values.
