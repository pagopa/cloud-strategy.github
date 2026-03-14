---
name: TechAIScriptPython
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
- For Python template tasks, use Jinja templates named `<file-name>.<extension>.j2`.

## Minimal template
```python
#!/usr/bin/env python3
"""Purpose: {description}

Usage examples:
  python {script_name}.py --help
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
| Installing deps globally without version pinning | Non-reproducible environment | Pin in `requirements.txt` or inline `pip install pkg==x.y.z` |

## Cross-references
- **TechAIProjectPython** (`.github/skills/tech-ai-project-python/SKILL.md`): for structured application code.
- **TechAICodeReview** (`.github/skills/tech-ai-code-review/SKILL.md`): for reviewing Python code (see `references/anti-patterns-python.md`).

## Validation
- `python -m py_compile script.py` (syntax check)
- `pytest tests/` (run tests)
- `python -m compileall <changed_paths>` (batch syntax check)
