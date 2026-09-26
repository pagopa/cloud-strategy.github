---
name: internal-python
description: Use when Python work has no single primary contract, such as shared modules changed together with independently executed scripts, cross-cutting typing, dependency, test, or runtime concerns, or unclear ownership. Route package code to /internal-python-project, standalone scripts to /internal-python-script, and diff or PR reviews to /internal-review-code.
---

# Internal Python

## When to use

This skill owns Python work without one clear primary contract:

- mixed changes that touch both importable modules and independently executed
  entrypoints, not thin CLI adapters over package code or a toolkit's private
  helpers;
- cross-cutting control flow, typing, configuration, runtime, dependency, test,
  or output concerns;
- single-file fixes whose contract cannot be inferred from importers,
  entrypoints, or packaging metadata;
- Python-specific review depth requested by a review owner.

It completes mixed and cross-cutting work itself. When repository evidence
shows one primary contract, route reusable imported behavior to
`/internal-python-project` and direct execution to `/internal-python-script`.
Route a whole diff, branch, or pull-request review to `/internal-review-code`.

## Workflow

1. **Classify the primary contract.** Inspect entrypoints, import sites,
   packaging metadata, and tests. Decide from importers: code imported only by
   its own entrypoints is direct execution; code imported outside its toolkit
   or published as a package is imported; a change touching both is mixed. For
   new files, use packaging metadata or the consumer named in the request.
   **Complete when:** the change is labeled imported, direct-execution, or
   mixed, and the deciding evidence is named.
2. **Route or apply the baseline.** Route a clear contract to its owner. For
   mixed or cross-cutting work, apply the baseline below to every changed file.
   **Complete when:** each changed file satisfies every baseline rule, or the
   owner skill is loaded and receives the classification evidence.
3. **Validate.** Run the checks in [Validation](#validation). **Complete
   when:** each check has an observed result or a named evidence gap.

## Review reference

Load `references/review-anti-patterns.md` for evidence-based Python review
findings when a review-oriented caller needs defect depth. Defer formatter- and
linter-owned diagnostics to the configured tooling.

## Cross-cutting baseline

- Prefer explicit control flow, early returns, guard clauses, clear names, and
  public or non-trivial type hints.
- Keep reusable logic explicit about its inputs. Put environment-specific and
  operator-tuned values at a configuration or composition boundary rather than
  scattering them through implementation code.
- Place each Python test in the native test location of the component that
  owns the behavior, such as a real CLI, subprocess, filesystem, protocol,
  JSON, or wrapper contract. Use a shared repository-level test directory only
  for behavior that crosses component boundaries. Reading another technology's
  source or configuration alone does not establish a Python test boundary.
- Preserve the repository-declared dependency manager and its canonical lock
  artifact. Do not vendor libraries, wheelhouses, copied site-packages, or
  fallback dependency mirrors.
- Keep machine-readable output plain data and keep human-facing rendering at an
  entrypoint or adapter boundary.
- Keep comments, docstrings, logs, exceptions, and CLI output in English.
- Add focused `pytest` coverage for new or changed behavior and use the nearest
  repository-owned syntax or runtime check for syntax-only changes.

## Validation

- Use the repository wrapper or declared runtime before ambient `python3`.
- Run the nearest focused `pytest` command for behavior changes.
- Keep imports minimal and backed by actual usage while writing Python. Before
  handoff, run the repository's declared static-analysis or lint check against
  every changed `.py` file. Resolve unused or otherwise dead-import diagnostics
  by removing the imports; do not suppress them with `noqa` or broaden
  exclusions.
- Keep compile and test scope narrow; exclude virtual environments, caches,
  exports, generated outputs, and dependency trees from broad sweeps.
