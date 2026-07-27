---
name: internal-python-script
description: Use when Python direct execution covers directly executed scripts, CLIs, automation entrypoints, and small operator-facing toolkits, while routing imported behavior to internal-python-project.
---

# Python Script Skill

## Boundary and routing

This skill owns Python direct execution: scripts, CLIs, automation entrypoints,
and small operator-facing toolkits. Importable packages, libraries,
applications, services, and framework-owned flows belong to
`internal-python-project`. The shared `internal-python` baseline is not a required preload; use it only when a cross-cutting concern or unresolved ownership question remains.

## When to use

- New or changed standalone scripts, CLIs, automation, or data-processing
  entrypoints whose primary contract is direct execution.
- Small multi-entrypoint toolkits that remain operator-facing even when they
  have tests, a `lib/` folder, or several maintained files.

## Script contract

- Follow the repository's existing layout, runner, dependency manager, test
  naming, and validation commands before adding structure.
- Keep entrypoints thin and importable. Parse arguments, resolve paths,
  orchestrate helpers, and return an exit code through `main() -> int` plus
  `raise SystemExit(main())`.
- Keep argument parsing and script-owned configuration at the entrypoint
  boundary without prescribing a fixed physical section. Helpers accept
  explicit parameters or a small typed settings object.
- Add a dedicated tool folder or toolkit root only when a standalone tool owns
  dependencies, assets, configuration, or multiple maintained files. Put shared
  helpers under `lib/` when the repository's existing toolkit layout supports it.
- Use `rich` only when polished human terminal output is part of the accepted
  contract. Keep JSON and other machine-readable output plain, and add a format
  only when a real automation consumer needs it.
- Add `run.sh` only when external packages need a launcher and no existing
  repository runner owns the setup. Keep setup or dependency installation out
  of ordinary execution unless the declared runner explicitly owns bootstrap.
- Use `argparse`, `pathlib`, type hints, and `asyncio` only when the tool's
  inputs, boundaries, or I/O workload justify them.

## Compact Python baseline

- Prefer explicit control flow, clear names, small helpers, and repository-
  declared runtime selection.
- Keep comments, docstrings, logs, exceptions, and CLI output in English.
- Keep dependency changes in the declared dependency manager and its canonical
  lock artifact. Do not vendor libraries or fallback dependency mirrors.

## Dependency policy

Preserve the repository-declared dependency manager. For pip requirements, keep
exact pins and hashes in the owning requirements file. For another declared
dependency manager, update its canonical lock artifact and use its frozen or
locked validation command.

For pip requirements, generate the lock output with
`pip-compile --generate-hashes` and validate it with
`pip install --require-hashes -r requirements.txt`.

Keep a short dependency decision note when choosing between stdlib and an
external library. Record the decision once at a shared toolkit lock boundary
when several entrypoints use the same dependency set.

## References

Load `references/layout-and-templates.md` for a repository-aligned layout,
importable entrypoint, hash-locked requirements, or launcher guidance.

Load `references/reporting.md` when human-facing output, `rich`, redaction,
diagnostics, or final summaries are part of the tool contract.

## Testing and validation

- Follow repository pytest defaults and cover the public CLI or stable helper
  seam for changed behavior.
- Keep human-facing rendering separate from reusable helpers and machine data.
- Use the declared interpreter or shared runner for focused tests and syntax
  checks. Run `py_compile` or `compileall` only over changed source paths.
