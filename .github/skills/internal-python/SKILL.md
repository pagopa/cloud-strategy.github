---
name: internal-python
description: Use when Python work needs a lightweight shared baseline or its primary contract is still unclear, including small fixes and reviews before script or application ownership is established.
---

# Internal Python

## Referenced files

- `references/review-anti-patterns.md`: Python review anti-pattern catalog with ID-tagged patterns, severity, rationale, and examples. Load when `internal-review-code` or a review-oriented caller needs Python-specific defect depth.

## When to use

- `.py` changes where the first need is the shared Python baseline or the
  primary contract is still unclear.
- Lightweight reviews of typing, guard clauses, tests, runtime version, imports, or dependencies.
- Small Python fixes where it is not yet clear whether direct operator-facing
  execution or importable application behavior is the primary contract.

## When not to use

- Lambda-specific runtime behavior; combine the Lambda owner with the relevant Python owner.

## Baseline

- Prefer early returns, guard clauses, clear names, and readable control flow.
- Keep functions small enough to read without tracing hidden state. Prefer explicit inputs over module-level lookups inside reusable logic.
- Add type hints on public or non-trivial function signatures.
- Treat 300 lines as a review threshold for cohesive Python files.
- Treat 400 lines as a split-or-justify threshold: split repeated decisions into focused modules or document why a single file remains clearer.
- Apply pragmatic DRY: extract repeated decision logic, but do not force abstractions for one-off control flow.
- Centralize behavioral configuration instead of scattering magic values through implementation code. Use clear names for paths, field lists, thresholds, defaults, mappings, feature switches, and external endpoint values.
- Do not confuse domain invariants with configuration. Stable rules that belong to the domain may stay near the domain code; environment-specific or operator-tuned values belong at an entrypoint, settings module, adapter, or composition boundary.
- Keep comments, docstrings, logs, exceptions, and CLI output in English.
- Use the repository-declared runtime before falling back to ambient `python3`.
- If a local `.venv` or declared runtime exists, use it first for
  `py_compile`, `pytest`, and validator runs instead of ambient Python.
- Before opening large modules, use `rg` to find owner functions, classes,
  entrypoints, tests, and runtime selectors, then read only the needed blocks.
- When Ruff is configured for the target repository, let `ruff format` own formatting and use Ruff diagnostics for import order and simple style cleanup. Do not create manual formatting churn that fights the configured formatter.
- When a test must modify `sys.path` before importing a standalone script, keep the affected import after that setup and mark only that import with `# noqa: E402`; remove truly unused imports or variables instead of suppressing them.
- Add or update tests for testable logic.
- Do not vendor libraries, wheelhouses, copied site-packages, or fallback dependency mirrors.
- Preserve the repository-declared dependency manager. For pip requirements, keep exact pins and hashes in the owning requirements file; for another declared dependency manager, update its canonical lock artifact and use its frozen or locked validation command.
- Keep human-facing console reporting separate from reusable Python logging and machine-readable output. Script or CLI adapter boundaries may use `rich`; project/package internals and JSON-style output paths should stay neutral, structured, or plain data.

## Validation

- Run the nearest focused `pytest` command when behavior changes.
- Run the nearest runtime-owned `py_compile` or `compileall` command for
  syntax-only changes.
- Keep compile and test scope narrow. Exclude `.venv`, `__pycache__`, exports,
  generated outputs, and dependency trees from broad sweeps.
- Use the repository wrapper or runtime selector when one exists.
