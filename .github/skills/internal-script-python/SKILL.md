---
name: internal-script-python
description: Create or modify standalone Python scripts with purpose docstring, emoji logs, and pinned dependencies. Use for automation scripts, CLI tools, data processing scripts, or any Python helper that is NOT part of a larger application.
---

# Python Script Skill

## When to use
- New standalone Python scripts.
- Existing Python scripts that need updates.
- CLI tools, one-off automation, data processing.

## Boundary with TechAIProjectPython
- **This skill**: standalone scripts (`scripts/`, CLI tools, automation). Single-file or small utility scope.
- **TechAIProjectPython**: application components (services, use cases, adapters) inside a structured project with package layout.

## Mandatory rules
- Module docstring must include purpose and usage examples.
- Use emoji logs for execution states.
- Prefer early return and guard clauses.
- Keep implementation explicit and readable.
- Add unit tests for testable behavior.
- New standalone tools should default to a dedicated folder, not a loose top-level `.py` file.
- The folder should include the Python entry point, a `run.sh` launcher, and `tests/` when test scope applies. Add a local `requirements.txt` only when external packages are used.
- If external packages are used, keep them in the local `requirements.txt` with exact pins, full transitive dependency closure, `--hash` entries, and short comment lines that make pinned versions readable.
- Recommend third-party libraries when they materially simplify parsing, validation, HTTP, CLI, serialization, or retry behavior; do not replace a simpler standard-library solution just to satisfy the preference.
- Make new `run.sh` launchers executable, and make them install from `requirements.txt` only when that file exists.
- For Python template tasks, use Jinja templates named `<file-name>.<extension>.j2`.

## Default layout
```text
{script_name}/
├── requirements.txt  # only when external packages are used
├── run.sh
├── {script_name}.py
└── tests/
```

## Minimal Python entry point
```python
#!/usr/bin/env python3
"""Purpose: {description}

Usage examples:
  ./run.sh --help
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
```bash
#!/usr/bin/env bash
#
# Purpose: Run the {script_name} standalone Python tool.
# Usage examples:
#   ./run.sh --help

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"
PYTHON_BIN="${PYTHON_BIN:-python3}"
REQUIREMENTS_FILE="$SCRIPT_DIR/requirements.txt"

if [[ ! -d "$VENV_DIR" ]]; then
  "$PYTHON_BIN" -m venv "$VENV_DIR"
fi

# Install exactly the locally locked dependencies before execution when needed.
if [[ -f "$REQUIREMENTS_FILE" ]]; then
  "$VENV_DIR/bin/pip" install --require-hashes -r "$REQUIREMENTS_FILE"
fi

exec "$VENV_DIR/bin/python" "$SCRIPT_DIR/{script_name}.py" "$@"
```

## Testing
- Put tests under `tests/`.
- Use `pytest` as default test framework.
- Keep tests deterministic and isolated.
- For modify tasks: edit implementation first, run existing tests, then update tests only for intentional behavior changes.

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
| Shipping a loose `.py` file with undocumented setup steps | Users must guess how to create the environment and run the tool | Generate a self-contained folder with `run.sh` and add `requirements.txt` only when external packages are needed |

## Cross-references
- **TechAIProjectPython** (`.github/skills/tech-ai-project-python/SKILL.md`): for structured application code.
- **TechAICodeReview** (`.github/skills/tech-ai-code-review/SKILL.md`): for reviewing Python code (see `references/anti-patterns-python.md`).

## Validation
- `python -m py_compile <script_name>.py` (syntax check)
- `bash -n run.sh` (launcher syntax check)
- `pytest tests/` (run tests)
- `python -m compileall <changed_paths>` (batch syntax check)
