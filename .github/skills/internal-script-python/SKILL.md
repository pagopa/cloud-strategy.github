---
name: internal-script-python
description: Create or modify standalone Python scripts with purpose docstring, emoji logs, pinned dependencies, and pragmatic runtime choices. Use for automation scripts, CLI tools, data processing scripts, or any Python helper that is NOT part of a larger application.
---

# Python Script Skill

## When to use
- New standalone Python scripts.
- Existing Python scripts that need updates.
- CLI tools, one-off automation, data processing.

## Boundary with internal-project-python
- **This skill**: standalone scripts (`scripts/`, CLI tools, automation). Single-file or small utility scope.
- **internal-project-python**: application components (services, use cases, adapters) inside a structured project with package layout.

## Mandatory rules
- Module docstring must include purpose and usage examples.
- Use emoji logs for execution states.
- Prefer early return and guard clauses.
- Keep implementation explicit and readable.
- Use type hints on non-trivial public helpers and CLI-facing boundaries.
- Add unit tests for testable behavior.
- Standalone tools should default to a dedicated folder, not a loose top-level `.py` file.
- The tool folder should include the Python entry point. Put matching tests under the repository-root `tests/` tree when test scope applies. Add a local `requirements.txt` and a `run.sh` launcher only when external packages are used.
- Mirror the tool source path under the repository-root `tests/` tree so the owning script is obvious from the test path.
- Existing standalone Python entry points should keep a sibling Bash launcher only when that launcher is needed to bootstrap external packages or an isolated local environment.
- When a Bash launcher exists, `./run.sh` must work without parameters by using documented defaults, and optional flags or environment variables may override those defaults.
- Stdlib-only standalone Python entry points should be documented and invoked directly with `python3 <script>.py` or an executable shebang path.
- For new scripts, do an explicit dependency decision before implementation; do not assume `stdlib-first` as the automatic default.
- Prefer mature, well-maintained, widely used third-party libraries when they clearly reduce boilerplate, edge cases, or custom logic in the finished script.
- Keep the standard library only when the final code is genuinely simpler, more readable, and safer than the third-party alternative.
- Optimize for less bespoke code and a simpler final script, not for the fewest possible dependencies.
- If external packages are used, keep them in the local `requirements.txt` with exact pins, full transitive dependency closure, `--hash` entries, and short comment lines that make pinned versions readable.
- Recommend third-party libraries when they materially simplify parsing, validation, CLI handling, serialization, HTTP, retry behavior, date handling, table rendering, Excel/CSV processing, or formatting; do not replace a simpler standard-library solution just to satisfy the preference.
- Avoid weak or marginal dependencies; every package should have a clear value-versus-setup justification.
- Make new `run.sh` launchers executable, and make them install from `requirements.txt` only when that file exists.
- For Python template tasks, use Jinja templates named `<file-name>.<extension>.j2`.

## Dependency decision note
Before writing a new script, include a short dependency decision note such as:

```text
Dependency decision note
- Candidates: argparse (stdlib), click, typer
- Final choice: typer
- Why: cleaner CLI structure, less boilerplate, better help output, and less custom parsing code than argparse for this script.
```

- Keep the note short and task-specific.
- Compare the standard library with realistic third-party candidates.
- If the final choice uses external libraries, create or update the local `requirements.txt` before finishing the task.

## Default layout
```text
repo-root/
├── {script_path}/
│   ├── {script_name}.py
│   ├── requirements.txt  # only when external packages are used
│   └── run.sh            # only when external packages are used
└── tests/
    └── {script_path}/
        └── test_{script_name}.py
```

## Minimal Python entry point
```python
#!/usr/bin/env python3
"""Purpose: {description}

Usage examples:
  python3 ./{script_name}.py --help
"""
import argparse
import sys


def log_info(msg: str) -> None:
    print(f"ℹ️  {msg}")


def log_error(msg: str) -> None:
    print(f"❌ {msg}", file=sys.stderr)


def log_success(msg: str) -> None:
    print(f"✅ {msg}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", required=True, help="Target to process")
    args = parser.parse_args()

    log_info(f"Processing {args.target}")
    # ... logic ...
    log_success("Done")


if __name__ == "__main__":
    main()
```

## Minimal requirements example
```text
# requests 2.32.3
requests==2.32.3 \
    --hash=sha256:<hash1> \
    --hash=sha256:<hash2>
```

Generate `requirements.txt` with `pip-compile --generate-hashes` or an equivalent workflow that locks the full dependency closure.

## Minimal launcher example
Use a launcher only when the tool depends on external packages.

```bash
#!/usr/bin/env bash
#
# Purpose: Run the {script_name} standalone Python tool.
# Usage examples:
#   ./run.sh
#   ./run.sh --help
#   ./run.sh --config ./config/custom.yaml

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"
PYTHON_BIN="${PYTHON_BIN:-python3}"
REQUIREMENTS_FILE="$SCRIPT_DIR/requirements.txt"
DEFAULT_CONFIG="$SCRIPT_DIR/config/default.yaml"
CONFIG_PATH="$DEFAULT_CONFIG"
PASSTHROUGH_ARGS=()

if [[ ! -d "$VENV_DIR" ]]; then
  "$PYTHON_BIN" -m venv "$VENV_DIR"
fi

# Install exactly the locally locked dependencies before execution when needed.
if [[ -f "$REQUIREMENTS_FILE" ]]; then
  "$VENV_DIR/bin/pip" install --require-hashes -r "$REQUIREMENTS_FILE"
fi

while [[ $# -gt 0 ]]; do
  case "$1" in
    --config)
      CONFIG_PATH="${2:?❌ --config requires a value}"
      shift 2
      ;;
    --help)
      PASSTHROUGH_ARGS+=("--help")
      shift
      ;;
    --)
      shift
      PASSTHROUGH_ARGS+=("$@")
      break
      ;;
    *)
      PASSTHROUGH_ARGS+=("$1")
      shift
      ;;
  esac
done

exec "$VENV_DIR/bin/python" "$SCRIPT_DIR/{script_name}.py" --config "$CONFIG_PATH" "${PASSTHROUGH_ARGS[@]}"
```

## Testing
- Put tests under the repository-root `tests/` tree.
- Mirror the source path under `tests/`. Example: `tools/reporting/sync_accounts.py` maps to `tests/tools/reporting/test_sync_accounts.py`.
- Use `pytest` as default test framework.
- Keep tests deterministic and isolated.
- Use coverage reports to inspect missing behavior on touched code, not to force blanket 100% coverage.
- For modify tasks: edit implementation first, run existing tests, then update tests only for intentional behavior changes.

## Runtime guidance
- Evaluate stdlib and third-party options explicitly for each new script instead of defaulting blindly to stdlib.
- Prefer mature third-party packages when they clearly produce a smaller, safer, easier-to-maintain script than a custom stdlib-based implementation.
- Keep stdlib when it wins on simplicity, clarity, and safety in the final result.
- Reach for libraries instead of custom logic when they solve parsing, validation, CLI handling, serialization, HTTP, retry, date handling, table rendering, Excel/CSV, or formatting better.
- Use `asyncio` only when the script truly coordinates multiple I/O-bound tasks.
- Reach for `pathlib`, context managers, and small helper functions before adding framework-like structure to a script.

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
