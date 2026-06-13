---
name: internal-python-script
description: Use when creating or modifying standalone Python scripts, CLIs, or small operator-facing toolkits whose primary contract is direct execution rather than reusable package or application code.
---

# Python Script Skill

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
- Move out of this lane only when the primary contract becomes imported behavior, service boundaries, or framework-owned flows.

## Script-specific guidance

- Standalone tools should default to a dedicated folder or toolkit root, not a loose top-level `.py` file.
- Keep entrypoints thin: parse arguments, resolve paths, orchestrate helpers, and return an exit code through `main() -> int` plus `raise SystemExit(main())`.
- Prefer `argparse`, `pathlib.Path`, and small helper functions for operator-facing tools.
- Keep emoji logs at operator-facing boundaries such as start, success, warning, and failure states; keep reusable helpers free of decorative log formatting.
- When a tool can be called from subdirectories, resolve the repository root explicitly instead of assuming the current working directory.
- Use type hints on non-trivial public helpers and CLI-facing boundaries.
- Use `asyncio` only when the script truly coordinates multiple I/O-bound tasks.
- Reach for `pathlib`, context managers, and small helper functions before adding framework-like structure to a script.
- Add machine-readable output such as `--format json` only when the tool has a real automation consumer. Keep text output as the default operator path.
- When machine-readable output can become large and the script is agent-facing, add a bounded mode such as `--format compact` that preserves status, blocker or finding counts, key path evidence, and next action without dumping full detail.
- Keep full `--format json` available for durable audit/debug use; do not replace it with compact mode.

## Compact Python baseline

- Prefer early returns, guard clauses, clear names, and readable control flow.
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
- If several entrypoints share the same lock file, record the decision once at the shared toolkit `requirements.txt` rather than repeating it in every script.

## Layout and templates

Load `references/layout-and-templates.md` when you need the default folder layout, a repo-aligned multi-tool toolkit layout, a minimal entry point, a hash-locked `requirements.txt`, or the launcher pattern.

Keep these rules visible while drafting:

- Use a dedicated tool folder or toolkit root rather than a loose top-level `.py` file.
- Add `requirements.txt` and `run.sh` only when external packages are actually needed.
- Generate `requirements.txt` with `pip-compile --generate-hashes` or an equivalent locked workflow.
- Reuse an existing shared runner such as `.github/scripts/run.sh` instead of cloning bootstrap logic into every entrypoint.
- Mirror script or toolkit coverage under the repository-root `tests/` tree; do not create ad-hoc test folders beside the tool.

## Testing

- Follow the repository pytest defaults.
- Use coverage reports to inspect missing behavior on touched code, not to force blanket 100% coverage.
- For modify tasks: edit implementation first, run existing tests, then update tests only for intentional behavior changes.
- Prefer existing repository commands such as `make lint`, `make test`, or a shared script runner before inventing a one-off validation path.

## Runtime guidance

- Prefer direct, readable orchestration over framework-like structure.
- Keep shared helpers local to the toolkit, not promoted into application-style layering without a real need.
- Centralize repeated environment bootstrap in one shared runner instead of copying `.venv` and `pip install` logic into every wrapper.

## Common mistakes

Load `references/common-mistakes.md` for the full mistake table.

## Validation

- `python -m py_compile <script_name>.py` (syntax check)
- `bash -n run.sh` (launcher syntax check, only when `run.sh` exists)
- `pytest tests/` (run tests)
- `python -m compileall <changed_paths>` or the repository's canonical shared runner when the tool already lives inside a maintained toolkit
