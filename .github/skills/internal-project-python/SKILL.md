---
name: internal-project-python
description: Use when creating or modifying Python package or application code whose primary contract is imported behavior, service boundaries, or framework-owned flows rather than operator-facing scripts.
---

# Python Project Skill

## When to use

- Services, use cases, adapters, packages, and modules in Python applications.
- Refactoring or extending existing Python application components.
- Reusable Python code whose primary contract is imported behavior rather than operator-facing execution.
- Python application code that should keep logging neutral or framework-native; operator-facing emoji output belongs to CLI, script, or delivery boundaries instead.

## When not to use

- Standalone CLIs, automation scripts, or operator-facing toolkits; use `internal-script-python`.
- Lambda-specific runtime behavior; combine the Lambda owner with the relevant Python owner.

## Boundary

- This skill covers structured package, library, or application components whose primary contract is reusable domain, service, or framework behavior.
- Small operator-facing tools remain out of scope even when they have multiple files or tests.
- A `lib/` folder, root-level tests, or multiple entrypoints alone do not make a tool application code.

## Compact Python baseline

- Prefer early returns, guard clauses, clear names, and readable control flow.
- Add type hints on public or non-trivial function signatures.
- Keep comments, docstrings, logs, exceptions, and CLI output in English.
- Use the repository-declared runtime before falling back to ambient `python3`.
- Do not vendor libraries, wheelhouses, copied site-packages, or fallback dependency mirrors.
- If external packages are introduced, keep exact pins and hashes in the owning requirements file.

## Application-specific guidance

- Use type hints on public APIs and keep data contracts explicit.
- Choose async only when the workload is I/O-bound and the surrounding stack supports it cleanly.
- Keep request or transport models, domain logic, and persistence concerns in separate modules.
- Keep reusable module and service logs neutral or structured; reserve emoji log formatting for outer operator-facing entrypoints.

Load `references/examples.md` when you need a minimal module or test example.

## Testing

- Follow the repository pytest defaults.
- BDD-like names: `given_when_then` style.
- Prefer fixtures, parameterization, and mocking only when they reduce duplication or isolate real external boundaries.
- Use coverage reports to close meaningful behavioral gaps, not as a blanket 100% doctrine.
- For modify tasks: edit implementation first, run existing tests, then update tests only for intentional behavior changes.

## Architecture and framework guidance

- Follow the repository's existing framework before introducing FastAPI, Flask, Django, or a new dependency stack.
- Use dataclasses or typed DTOs for internal contracts, and boundary-validation models where the framework already expects them.
- Keep async flows end-to-end; do not mix blocking libraries into async request paths without an explicit bridge.

## Test-shape guidance

- Use parameterized tests for behavior that varies across a small, explicit input matrix.
- Mock network, filesystem, database, or queue boundaries; do not mock internal business logic seams by default.
- Use property-based testing only when the input space is large enough to justify it.
- Prefer targeted coverage growth on changed code and risk-heavy branches over chasing untouched lines.

## Common mistakes

Load `references/common-mistakes.md` for the full mistake table.

## Validation

- `python -m compileall <paths>` (syntax check)
- `pytest tests/` (run tests)
- Lint with project's configured linter.
