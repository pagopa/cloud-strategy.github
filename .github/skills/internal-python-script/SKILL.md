---
name: internal-python-script
description: Use when creating or changing directly executed Python, such as standalone scripts and CLIs, automation or CI entrypoints, standalone data jobs, small operator toolkits, or their tests. Route package code and its CLI adapters to /internal-python-project, and mixed or unclear ownership to /internal-python.
---

# Python Script Skill

## When to use

This skill owns Python work whose primary contract is direct execution:

- new or changed standalone scripts, CLIs, automation, or data-processing
  entrypoints;
- small multi-entrypoint toolkits whose primary contract is direct execution,
  even when they have tests, a `lib/` folder, or several maintained files.

It applies the complete script baseline itself. Route reusable imported
behavior in a package, library, application, service, or framework-owned flow,
including a thin CLI adapter over package code, to `/internal-python-project`.
Route a mixed change whose primary contract is still unresolved to
`/internal-python`.

## Workflow

1. **Confirm the contract.** Identify the entrypoints, arguments, exit codes,
   outputs, and runner that operators or automation depend on. **Complete
   when:** the execution contract and its consumers are named.
2. **Apply the script contract.** Follow the rules below and the repository's
   existing layout. **Complete when:** each changed entrypoint and helper
   satisfies every contract rule, applying repository conventions only where
   a rule defers to them.
3. **Validate.** Run the checks in
   [Testing and validation](#testing-and-validation). **Complete when:** each
   check has an observed result or a named evidence gap.

## Script contract

- Follow the repository's existing layout, runner, test naming, and validation
  commands before adding structure.
- Keep entrypoints thin and importable. Parse arguments, resolve paths,
  orchestrate helpers, and return an exit code through `main() -> int` plus
  `raise SystemExit(main())`.
- Keep argument parsing and script-owned configuration at the entrypoint
  boundary without prescribing a fixed physical section. Helpers accept
  explicit parameters or a small typed settings object.
- Add a dedicated tool folder or toolkit root only when a standalone tool owns
  dependencies, assets, configuration, or multiple maintained files. Put shared
  helpers under `lib/` when the repository's existing toolkit layout supports it.
- Keep human-facing rendering out of reusable helpers. Use `rich` only when
  polished human terminal output is part of the accepted contract. Keep JSON
  and other machine-readable output plain, and add a format only when a real
  automation consumer needs it.
- Add `run.sh` only when external packages need a launcher and no existing
  repository runner owns the setup. Keep setup or dependency installation out
  of ordinary execution unless the declared runner explicitly owns bootstrap.
- Use `argparse`, `pathlib`, type hints, and `asyncio` only when the tool's
  inputs, boundaries, or I/O workload justify them.

## Compact Python baseline

- Prefer explicit control flow, clear names, small helpers, and repository-
  declared runtime selection.
- Keep comments, docstrings, logs, exceptions, and CLI output in English.

## Dependency policy

Preserve the repository-declared dependency manager, and do not vendor
libraries or fallback dependency mirrors. For pip requirements, keep exact pins
and hashes in the owning requirements file. For another declared dependency
manager, update its canonical lock artifact and use its frozen or locked
validation command.

For pip requirements, generate the lock output with
`pip-compile --generate-hashes` and validate it with
`pip install --require-hashes -r requirements.txt`.

Keep a short dependency decision note when choosing between stdlib and an
external library. Record the decision once at a shared toolkit lock boundary
when several entrypoints use the same dependency set.

## References

Load `references/layout-and-templates.md` for a repository-aligned layout,
importable entrypoint, hash-locked requirements, or launcher guidance.

Load `references/reporting.md` when a direct-execution tool contract includes
human lifecycle output, bounded diagnostics, redaction, or final summaries.

## Testing and validation

- Follow repository pytest defaults and cover the public CLI or stable helper
  seam for changed behavior.
- Use the declared interpreter or shared runner for focused tests and syntax
  checks. Run `py_compile` or `compileall` only over changed source paths.
