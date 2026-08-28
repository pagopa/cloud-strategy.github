---
name: internal-python
description: Use when Python work is cross-cutting, spans imported and directly executed code, or ownership is unclear; do not use for work with one clear imported or direct-execution contract.
---

# Internal Python

## Boundary

This skill owns cross-cutting Python work and ambiguous mixed changes. It
provides a shared baseline when a task spans reusable imported behavior and
direct execution, or when repository evidence does not yet establish one
primary contract. It completes that work directly without delegating it.

## Review reference

Load `references/review-anti-patterns.md` for evidence-based Python review
findings when a review-oriented caller needs defect depth. Defer formatter- and
linter-owned diagnostics to the configured tooling.

## When to use

- Cross-cutting Python concerns involving control flow, typing, configuration,
  runtime, dependencies, tests, or output boundaries.
- Lightweight reviews or small fixes where direct operator-facing execution
  versus importable application behavior is not yet clear.
- `.py` changes that need the shared baseline before a narrower owner is chosen:
  `/internal-python-project` for reusable imported behavior and
  `/internal-python-script` for directly executed scripts.

## When not to use

- Do not use when the primary contract is clearly reusable imported code and no
  cross-cutting ownership decision remains.
- Do not use when the primary contract is clearly a direct-execution tool and
  no cross-cutting ownership decision remains.

## Cross-cutting baseline

- Prefer explicit control flow, early returns, guard clauses, clear names, and
  public or non-trivial type hints.
- Keep reusable logic explicit about its inputs. Put environment-specific and
  operator-tuned values at a configuration or composition boundary rather than
  scattering them through implementation code.
- Place a Python test under repository-root `tests/` when it verifies Python
  behavior or a real observable external contract such as CLI, subprocess,
  filesystem, protocol, JSON, or wrapper behavior. Reading another
  technology's source or configuration alone does not establish a Python test
  boundary.
- Baseline dependency and output rules are owned by the selected owner.
- Do not vendor libraries, wheelhouses, copied site-packages, or fallback
  dependency mirrors.
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
