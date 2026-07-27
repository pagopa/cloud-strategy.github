---
name: internal-python
description: Use when Python work needs a shared Python baseline for ownership routing; the shared baseline handles cross-cutting concerns when the primary contract is still unclear and decisions between imported behavior and directly executed tooling.
---

# Internal Python

## Owner routing

- Use this shared Python baseline when ownership is still unclear or a concern
  crosses imported code and direct execution boundaries.
- Route importable packages, libraries, applications, services, and framework
  flows to `internal-python-project`.
- Route directly executed scripts, CLIs, automation, and operator-facing
  toolkits to `internal-python-script`.
- This baseline is an uncertainty and review fallback; it is not a required
  preload after the primary contract becomes clear.

## Review reference

Load `references/review-anti-patterns.md` for evidence-based Python review
findings when a review-oriented caller needs defect depth. Defer formatter- and
linter-owned diagnostics to the configured tooling.

## When to use

- Cross-cutting Python concerns involving control flow, typing, configuration,
  runtime, dependencies, tests, or output boundaries.
- Lightweight reviews or small fixes where direct operator-facing execution
  versus importable application behavior is not yet clear.
- `.py` changes that need the shared baseline before a narrower owner is chosen.

## Cross-cutting baseline

- Prefer explicit control flow, early returns, guard clauses, clear names, and
  public or non-trivial type hints.
- Keep reusable logic explicit about its inputs. Put environment-specific and
  operator-tuned values at a configuration or composition boundary rather than
  scattering them through implementation code.
- Use the repository-declared runtime and declared dependency manager. For
  pip-managed requirements, preserve exact pins and hashes in the owning lock
  artifact; use the other manager's canonical frozen or locked validation when
  applicable.
- Do not vendor libraries, wheelhouses, copied site-packages, or fallback
  dependency mirrors.
- Add focused `pytest` coverage for new or changed behavior and use the nearest
  repository-owned syntax or runtime check for syntax-only changes.
- Keep human-facing console reporting separate from reusable logging and
  machine-readable output. Human output belongs at an execution boundary;
  JSON and other data outputs stay plain and neutral.

## Validation

- Use the repository wrapper or declared runtime before ambient `python3`.
- Run the nearest focused `pytest` command for behavior changes.
- Keep compile and test scope narrow; exclude virtual environments, caches,
  exports, generated outputs, and dependency trees from broad sweeps.
