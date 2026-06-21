---
name: internal-python-project
description: Use when creating or modifying Python package or application code whose primary contract is imported behavior, service boundaries, or framework-owned flows rather than operator-facing scripts.
---

# Python Project Skill

## Referenced skills

- `internal-python-script`: route CLI adapters, direct operator execution, and rich console reporting boundaries.
- `internal-tdd`: load for bugfixes, features, or project behavior changes with a meaningful public or service seam.

## When to use

- Services, use cases, adapters, packages, and modules in Python applications.
- Refactoring or extending existing Python application components.
- Reusable Python code whose primary contract is imported behavior rather than operator-facing execution.
- Python application code that should keep logging neutral or framework-native; operator-facing emoji output belongs to CLI, script, or delivery boundaries instead.

## When not to use

- Standalone CLIs, automation scripts, or operator-facing toolkits; use `internal-python-script`.
- Lambda-specific runtime behavior; combine the Lambda owner with the relevant Python owner.

## Boundary

- This skill covers structured package, library, or application components whose primary contract is reusable domain, service, or framework behavior.
- Small operator-facing tools remain out of scope even when they have multiple files or tests.
- A `lib/` folder, root-level tests, or multiple entrypoints alone do not make a tool application code.

## Compact Python baseline

- Prefer early returns, guard clauses, clear names, and readable control flow.
- Keep functions small enough to read without tracing hidden state. Prefer explicit inputs over module-level lookups inside reusable logic.
- Add type hints on public or non-trivial function signatures.
- Keep comments, docstrings, logs, exceptions, and CLI output in English.
- Use the repository-declared runtime before falling back to ambient `python3`.
- Centralize behavioral configuration instead of scattering magic values through services, adapters, or library modules. Put environment-specific and operator-tuned values in a settings module, application factory, CLI adapter, framework configuration, or composition root.
- Pass configuration into reusable project code through typed settings, constructor arguments, or function parameters. Domain and service code should not read environment variables, files, or deployment defaults directly unless that boundary is its explicit responsibility.
- Do not confuse domain invariants with configuration. Stable rules that belong to the domain may stay near the domain code; deployment-specific paths, endpoints, thresholds, defaults, and feature switches should live at the configuration boundary.
- Do not vendor libraries, wheelhouses, copied site-packages, or fallback dependency mirrors.
- If external packages are introduced, keep exact pins and hashes in the owning requirements file.

## Application-specific guidance

- Use type hints on public APIs and keep data contracts explicit.
- Choose async only when the workload is I/O-bound and the surrounding stack supports it cleanly.
- Keep request or transport models, domain logic, and persistence concerns in separate modules.
- Prefer a domain/service/adapter decomposition before adding generic catch-all modules.
- Keep reusable module and service logs neutral, structured, or framework-native. Log events should be parsable, searchable, and useful in production.
- Design professional reporting as a boundary concern: core project code returns typed results, events, or DTOs; adapters decide whether to render JSON, HTTP responses, framework logs, metrics, or human-facing CLI reports.
- No emoji or `rich` rendering inside importable domain, service, persistence, framework modules, or machine-readable output paths such as JSON. Use `rich` only in human-facing CLI adapter reporting.
- If a project exposes a CLI adapter, keep the CLI adapter thin and route its operator-facing reporting to the script boundary. A CLI adapter may use an `ExecutionReporter`; the core project code should not know that reporter exists.

Load `references/examples.md` when you need a minimal module or test example.

Load `references/logging-and-reporting.md` when project code needs a professional logging/reporting layout, structured log context, result DTOs, adapter-owned rendering, or JSON versus human-output boundaries.

## Testing

- Follow the repository pytest defaults.
- BDD-like names: `given_when_then` style.
- Prefer fixtures, parameterization, and mocking only when they reduce duplication or isolate real external boundaries.
- Use coverage reports to close meaningful behavioral gaps, not as a blanket 100% doctrine.
- For bugfixes, features, and intentional behavior changes, start test-first through the public API, service boundary, adapter contract, or framework-owned seam: add or update the failing test, confirm it fails for the intended reason, then implement the smallest fix.
- For refactors, prose-only updates, generated fixtures, or mechanical formatting with no executable behavior change, run existing focused tests and syntax validation instead of manufacturing speculative tests.

## Architecture and framework guidance

- Follow the repository's existing framework before introducing FastAPI, Flask, Django, or a new dependency stack.
- Use dataclasses or typed DTOs for internal contracts, and boundary-validation models where the framework already expects them.
- Keep async flows end-to-end; do not mix blocking libraries into async request paths without an explicit bridge.
- When Ruff is configured for the project, let `ruff format` own formatting and use `ruff check` before broader test runs. Avoid hand-formatting that creates churn against the configured formatter.

## Test-shape guidance

- Use parameterized tests for behavior that varies across a small, explicit input matrix.
- Mock network, filesystem, database, or queue boundaries; do not mock internal business logic seams by default.
- Use property-based testing only when the input space is large enough to justify it.
- Prefer targeted coverage growth on changed code and risk-heavy branches over chasing untouched lines.

## Common mistakes

Load `references/common-mistakes.md` for the full mistake table.

## Validation

- `python -m compileall <paths>` (syntax check)
- `pip install --require-hashes -r requirements.txt` (dependency integrity check, only when requirements change)
- `pytest tests/` (run tests)
- Lint with project's configured linter.
