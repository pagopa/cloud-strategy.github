---
name: internal-script-python
description: Create or modify standalone Python scripts with purpose docstring, emoji logs, pinned dependencies, and pragmatic runtime choices. Use for automation scripts, CLI tools, data processing scripts, or any Python helper that is NOT part of a larger application.
---

# Python Script Skill

Follow `.github/instructions/internal-python.instructions.md` for the baseline Python rules. This skill adds standalone-script guidance only.

## When to use
- New standalone Python scripts.
- Existing Python scripts that need updates.
- CLI tools, one-off automation, data processing.

## Boundary with internal-project-python
- **This skill**: standalone scripts (`scripts/`, CLI tools, automation). Single-file or small utility scope.
- **internal-project-python**: application components (services, use cases, adapters) inside a structured project with package layout.

## Script-specific guidance
- Standalone tools should default to a dedicated folder, not a loose top-level `.py` file.
- The tool folder should include the Python entry point. Add a local `requirements.txt` and a `run.sh` launcher only when external packages are used.
- Existing standalone Python entry points should keep a sibling Bash launcher only when that launcher is needed to bootstrap external packages or an isolated local environment.
- Stdlib-only standalone Python entry points should be documented and invoked directly with `python3 <script>.py` or an executable shebang path.
- Use type hints on non-trivial public helpers and CLI-facing boundaries.
- Use `asyncio` only when the script truly coordinates multiple I/O-bound tasks.
- Reach for `pathlib`, context managers, and small helper functions before adding framework-like structure to a script.

## Dependency decision note
When the instruction owner requires a dependency decision note, keep it short, for example:

```text
Dependency decision note
- Candidates: argparse (stdlib), click, typer
- Final choice: typer
- Why: cleaner CLI structure, less boilerplate, better help output, and less custom parsing code than argparse for this script.
```

- Keep the note short and task-specific.
- Compare the standard library with realistic third-party candidates.
- If the final choice uses external libraries, create or update the local `requirements.txt` before finishing the task.

## Layout and templates

Load `references/layout-and-templates.md` when you need the default folder layout, a minimal entry point, a hash-locked `requirements.txt`, or the launcher pattern.

Keep these rules visible while drafting:

- Use a dedicated tool folder rather than a loose top-level `.py` file.
- Add `requirements.txt` and `run.sh` only when external packages are actually needed.
- Generate `requirements.txt` with `pip-compile --generate-hashes` or an equivalent locked workflow.
- Stdlib-only tools should run directly with `python3 <script>.py` or an executable shebang path.

## Testing
- Follow the repository pytest defaults from the instruction owner.
- Use coverage reports to inspect missing behavior on touched code, not to force blanket 100% coverage.
- For modify tasks: edit implementation first, run existing tests, then update tests only for intentional behavior changes.

## Runtime guidance
- Prefer direct, readable orchestration over framework-like structure.
- Reach for script-local helpers before introducing reusable application layering into a standalone tool.

## Common mistakes

| Mistake | Why it matters | Instead |
|---|---|---|
| Missing `if __name__ == "__main__":` guard | Script runs on import, breaks testing and reuse | Always guard the entry point |
| Using `print()` for errors | Errors go to stdout, mixed with normal output | Use `print(..., file=sys.stderr)` or `logging` |
| Bare `except:` or `except Exception:` at top level | Swallows all errors including KeyboardInterrupt | Catch specific exceptions; let unexpected ones propagate |
| Hardcoded file paths | Non-portable across machines | Use `argparse`, `pathlib`, or environment variables |
| No argument parsing | Caller has to modify script source to change behavior | Use `argparse` for any configurable parameter |
| Installing deps globally or without hash-locked version pinning | Non-reproducible environment and hidden setup drift | Keep dependencies in the local `requirements.txt` with exact pins and hashes |
| Adding an empty `requirements.txt` to a stdlib-only tool | Adds noise and implies missing setup steps | Omit `requirements.txt` when the script uses only the standard library |
| Wrapping a stdlib-only script in Bash | Adds setup indirection without solving a real dependency problem | Document direct `python3 <script>.py` execution and skip the wrapper |
| Shipping a loose `.py` file with undocumented setup steps | Users must guess how to run the tool safely | Generate a self-contained folder and add `run.sh` plus `requirements.txt` only when external packages are needed |
| Defaulting to stdlib without comparing mature libraries | Leaves avoidable boilerplate, edge cases, and custom parsing logic in the script | Write the dependency decision note first and choose the option that makes the final code simpler |
| Rejecting a useful dependency just to keep dependency count low | Optimizes the wrong thing and increases custom code | Optimize for simpler final code and justified value, not dependency minimization |
| Forcing async or framework abstractions into a simple tool | Raises complexity without improving the script | Keep the script synchronous and direct unless concurrency is essential |

## Cross-references
- **internal-project-python** (`.github/skills/internal-project-python/SKILL.md`): for structured application code.
- **internal-code-review** (`.github/skills/internal-code-review/SKILL.md`): for reviewing Python code (see `.github/skills/internal-code-review/references/anti-patterns-python.md`).

## Validation
- `python -m py_compile <script_name>.py` (syntax check)
- `bash -n run.sh` (launcher syntax check, only when `run.sh` exists)
- `pytest tests/` (run tests)
- `python -m compileall <changed_paths>` (batch syntax check)
