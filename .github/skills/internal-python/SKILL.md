---
name: internal-python
description: Use when editing Python files that need lightweight runtime, typing, testing, dependency, or readability guidance before script or project depth is needed.
---

# Internal Python

## Referenced skills

Treat the referenced skills below as on-demand owners. Do not preload them for
every Python edit; load them only when the task proves script or project depth.

- `internal-python-script`: standalone Python scripts, CLIs, and operator-facing toolkits when dependency bootstrap, launcher behavior, or direct execution becomes the main concern.
- `internal-python-project`: Python packages, application code, service boundaries, and framework-owned flows when importable behavior or service structure becomes the main concern.

## When to use

- `.py` changes where the first need is the shared Python baseline.
- Lightweight reviews of typing, guard clauses, tests, runtime version, imports, or dependencies.
- Small Python fixes where it is not yet clear whether script or project depth is needed.

## When not to use

- Standalone CLIs, automation scripts, or operator-facing toolkits; use `internal-python-script`.
- Package, application, service, or framework-owned behavior; use `internal-python-project`.
- Lambda-specific runtime behavior; combine the Lambda owner with the relevant Python owner.

## Baseline

- Prefer early returns, guard clauses, clear names, and readable control flow.
- Add type hints on public or non-trivial function signatures.
- Treat 300 lines as a review threshold for cohesive Python files.
- Treat 400 lines as a split-or-justify threshold: split repeated decisions into focused modules or document why a single file remains clearer.
- Apply pragmatic DRY: extract repeated decision logic, but do not force abstractions for one-off control flow.
- Keep comments, docstrings, logs, exceptions, and CLI output in English.
- Use the repository-declared runtime before falling back to ambient `python3`.
- When a test must modify `sys.path` before importing a standalone script, keep the affected import after that setup and mark only that import with `# noqa: E402`; remove truly unused imports or variables instead of suppressing them.
- Add or update tests for testable logic.
- Do not vendor libraries, wheelhouses, copied site-packages, or fallback dependency mirrors.
- If external packages are introduced, keep exact pins and hashes in the owning requirements file.

## Dependency And Runtime Depth

Use `internal-python-script` when dependency bootstrap, launcher behavior, local virtual environments, or direct operator execution is the main concern.

Use `internal-python-project` when importable behavior, service boundaries, application tests, or framework flows are the main concern.

## Validation

- Run the nearest focused `pytest` command when behavior changes.
- Run `python -m py_compile <file>` or `python -m compileall <path>` for syntax-only changes.
- Use the repository wrapper or runtime selector when one exists.
