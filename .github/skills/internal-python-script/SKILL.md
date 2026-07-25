---
name: internal-python-script
description: Use when creating, modifying, or reviewing directly executed Python scripts, CLIs, automation, or small operator-facing toolkits rather than importable application behavior.
---

# Python Script Skill

## Referenced skills

- `internal-python-project`: route away when imported package, application, service, or framework behavior becomes the primary contract.

## When to use

- New standalone Python scripts.
- Existing Python scripts that need updates.
- CLI tools, one-off automation, data processing.
- Small multi-entrypoint toolkits whose primary contract is operator-facing execution rather than reusable package APIs.

## When not to use

- Package, application, service, or framework-owned behavior; use `internal-python-project`.
- Lambda-specific runtime behavior; combine the Lambda owner with the relevant Python owner.

## Boundary

- This skill covers standalone operational tools, CLI entrypoints, and small script toolkits whose primary contract is direct execution.
- A tool does not become application code just because it has multiple files, a `lib/` folder, or root-level tests.
- Move out of this lane only when the primary contract becomes imported behavior,
  service boundaries, or framework-owned flows; route those cases to
  `internal-python-project`.

## Script-specific guidance

- Standalone tools should default to a dedicated folder or toolkit root, not a loose top-level `.py` file.
- Keep entrypoints thin and importable: prefer a package `__main__.py`, importable `cli.py`, or declared `console_scripts` entrypoint; parse arguments, resolve paths, orchestrate helpers, and return an exit code through `main() -> int` plus `raise SystemExit(main())`.
- Keep script-owned configuration visible at the entrypoint boundary. In single-file scripts, place a clearly named `Configuration` section near the end of the file, after helper definitions and before `main()` or `raise SystemExit(main())`.
- Name configuration values by purpose, not by type: paths, file names, field lists, thresholds, defaults, mappings, filters, and output modes should explain what behavior they control.
- Do not hide script-specific configuration inside helper modules or libraries. Helpers should accept explicit parameters or a small typed settings object when several values travel together.
- Keep single-file scripts under 400 lines when possible. At 300 lines, review whether orchestration and helper boundaries stay clear; at 400 lines, split-or-justify is required.
- Place shared helper logic in local helper modules, preferably under `lib/` when the toolkit structure supports that layout.
- For operator-facing script work, crossing the 400-line threshold should move toward a toolkit or project structure according to the primary contract, not an ever-growing single entrypoint.
- Keep policy checks focused on maintained source; generated outputs and large fixture data are excluded unless directly edited.
- Prefer `argparse`, `pathlib.Path`, and small helper functions for operator-facing tools.
- Keep operator-facing console reporting centralized in a dedicated reporter, for example `ExecutionReporter`. Application logic should call semantic reporter methods instead of constructing styled strings or scattered `print()` calls.
- Use `rich` as the preferred console rendering library for polished human-facing CLI reports when the terminal experience is part of the contract. Keep it out of `--format json`, other machine-readable outputs, and reusable helper logic.
- Keep emoji, panels, tables, and color at human-facing boundaries such as banners, sections, success, warning, error, and summaries. Keep reusable helpers and machine-readable output paths free of decorative log formatting.
- When a tool can be called from subdirectories, resolve the repository root explicitly instead of assuming the current working directory.
- Use type hints on non-trivial public helpers and CLI-facing boundaries.
- Use `asyncio` only when the script truly coordinates multiple I/O-bound tasks.
- Reach for `pathlib`, context managers, and small helper functions before adding framework-like structure to a script.
- Add machine-readable output such as `--format json` only when the tool has a real automation consumer. Keep text output as the default operator path, and do not decorate machine-readable output with `rich`, emoji, color, or tables.
- When machine-readable output can become large and the script is agent-facing, add a bounded mode such as `--format compact` that preserves status, blocker or finding counts, key path evidence, and next action without dumping full detail.
- Keep full `--format json` available for durable audit/debug use; do not replace it with compact mode.
- When a script surfaces reusable project payloads, keep default reports summarized and defer raw payload dump policy to the project reporting boundary instead of embedding full bodies in shareable output.

## Compact Python baseline

- Prefer early returns, guard clauses, clear names, and readable control flow.
- Keep script-owned configuration at the entrypoint boundary with simple descriptive names.
- Add type hints on public or non-trivial function signatures.
- Keep comments, docstrings, logs, exceptions, and CLI output in English.
- Use the repository-declared runtime before falling back to ambient `python3`.
- Do not vendor libraries, wheelhouses, copied site-packages, or fallback dependency mirrors.
- If external packages are introduced, keep exact pins and hashes in the owning requirements file.

## Dependency decision note

When the Python baseline requires a dependency decision note, keep it short, for example:

```text
Dependency decision note
- Candidates: argparse (stdlib), click, typer
- Final choice: typer
- Why: cleaner CLI structure, less boilerplate, better help output, and less custom parsing code than argparse for this script.
```

- Keep the note short and task-specific.
- Compare the standard library with realistic third-party candidates.
- If the final choice uses external libraries, create or update the local `requirements.txt` before finishing the task.
- Keep exact pins and current hashes in `requirements.txt`. Use `pip-compile --generate-hashes` or an equivalent repository-approved workflow, then validate with `pip install --require-hashes -r requirements.txt` when the requirements file changes.
- If several entrypoints share the same lock file, record the decision once at the shared toolkit `requirements.txt` rather than repeating it in every script.

## Layout and templates

Load `references/layout-and-templates.md` when you need the default folder layout, a repo-aligned multi-tool toolkit layout, a minimal entry point, a hash-locked `requirements.txt`, or the launcher pattern.

Load `references/reporting.md` when the script needs polished human-facing
output, `rich` rendering, status tables, redaction, verbose diagnostics, or a
final operator summary.

Keep these rules visible while drafting:

- Use a dedicated tool folder or toolkit root rather than a loose top-level `.py` file.
- Add `requirements.txt` and `run.sh` only when external packages are actually needed.
- Generate `requirements.txt` with `pip-compile --generate-hashes` or an equivalent locked workflow.
- Reuse an existing shared runner such as `.github/scripts/run.sh` instead of cloning bootstrap logic into every entrypoint.
- Mirror script or toolkit coverage under the repository-root `tests/` tree; do not create ad-hoc test folders beside the tool.

## Testing

- Follow the repository pytest defaults.
- Use coverage reports to inspect missing behavior on touched code, not to force blanket 100% coverage.
- For bugfixes, features, and intentional behavior changes, follow the repository test strategy for the task and keep the public CLI or stable helper seam covered by focused tests.
- For refactors, prose-only updates, generated fixtures, or mechanical formatting with no executable behavior change, run the existing focused tests plus `py_compile` or `compileall` instead of manufacturing speculative tests.
- When Ruff is configured, run `ruff format` for formatting-only Python edits and `ruff check` for lint feedback before wider test runs.
- Prefer existing repository commands such as `make lint`, `make test`, or a shared script runner before inventing a one-off validation path.
- Keep test execution reproducible: run through the declared interpreter or local virtualenv, reuse shared runners when they exist, and anchor pytest discovery with the repository rootdir or `testpaths` contract instead of ad-hoc shell state.

## Runtime guidance

- Prefer direct, readable orchestration over framework-like structure.
- Keep shared helpers local to the toolkit, not promoted into application-style layering without a real need.
- Centralize repeated environment bootstrap in one shared runner instead of copying `.venv` and `pip install` logic into every wrapper.

## Common mistakes

Load `references/common-mistakes.md` for the full mistake table.

## Validation

- `python -m py_compile <script_name>.py` (syntax check)
- `bash -n run.sh` (launcher syntax check, only when `run.sh` exists)
- `pip install --require-hashes -r requirements.txt` (dependency integrity check, only when requirements change)
- `pytest tests/` (run tests)
- `python -m compileall <changed_paths>` or the repository's canonical shared runner when the tool already lives inside a maintained toolkit
