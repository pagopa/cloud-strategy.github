---
description: Python standards for both scripts and application code with DDD boundaries, guard clauses, and pytest defaults.
applyTo: "**/*.py"
---

# Python Instructions

## Mandatory rules
- Use emoji logs for key execution states.
- Prefer early return and clear guard clauses.
- Keep code explicit and readable.
- For new Python scripts, explicitly evaluate the standard library versus mature third-party libraries before implementation; `stdlib-first` is not an absolute default.
- Prefer a mature, well-maintained, widely used third-party library when it materially reduces boilerplate, edge cases, or custom logic in the final code.
- Keep the standard library only when the final implementation is genuinely simpler, more readable, and safer.
- Do not reinvent common parsing, validation, CLI handling, serialization, HTTP, retry, date handling, table rendering, Excel/CSV processing, or formatting behavior when a standard-library or mature third-party solution is clearer.
- Prefer simple, readable, and easily modifiable code over clever abstractions.
- Accept additional lines or mild redundancy when it improves clarity, maintainability, and safe future changes.
- Unit tests are required for testable logic.
- Apply these rules for both create and modify operations.
- For Python template tasks, use Jinja templates named `<file-name>.<extension>.j2`.
- Keep template content complete and externalize only values intentionally passed by the caller.

## Application code (non-script)
- For non-trivial features, keep business logic separated from I/O and infrastructure concerns.
- Keep module boundaries clear: business rules in one place, external integrations in another.
- Use clear, domain-relevant naming in classes, methods, and errors.

## Script code
- Start scripts with a module docstring containing purpose and usage examples.
- Keep CLI parsing and orchestration explicit.
- Avoid embedding domain rules that belong to reusable application modules.
- Before writing a new script, produce a short dependency decision note with candidate libraries, the final choice, and the reason for the choice.
- Optimize for the simplest final script, not for the smallest dependency list.
- Standalone Python entry points that rely on external packages should have a sibling Bash launcher that bootstraps a local `.venv` and installs from the local hash-locked `requirements.txt`.
- For standalone Python automation, treat the Python entry point plus its adjacent lock file such as `requirements.txt` as the only supported dependency source of truth unless the user explicitly requests a different model.
- Do not add local vendored libraries, wheelhouses, copied site-packages, fallback dependency mirrors, or deprecated alternate install paths for Python dependencies unless the user explicitly requests them.
- Standalone Python entry points that use only the standard library should be invoked directly with `python3 <script>.py` or an executable shebang path, not through a Bash wrapper.

## Style
- Follow PEP8.
- Use type hints in function signatures.
- Keep line length <= 120.

## Output language
- Docstrings, logs, exceptions, and CLI output must be in English.

## Dependencies
- Standardize on `requirements.txt` as the Python dependency lock artifact in this baseline.
- For new scripts, evaluate stdlib versus third-party options explicitly before coding and record that choice in the dependency decision note.
- If external libraries are introduced, prefer a compiled `requirements.txt` with exact `==` pins, full transitive dependency closure, and `--hash` entries for every locked requirement.
- Keep a short comment above each introduced dependency block so the pinned version is readable without parsing the full hash line.
- Keep the launcher and the lock file aligned as one canonical dependency path; do not keep fallback or deprecated alternatives in parallel.
- Recommend third-party libraries when they materially reduce custom parsing, validation, HTTP, CLI, serialization, retry, date handling, table rendering, Excel/CSV, or formatting code.
- If the dependency decision note selects external libraries, create or update the local `requirements.txt` accordingly.
- Do not force third-party libraries over the standard library when the standard library is simpler, clearer, or safer in the final implementation.
- Avoid marginal dependencies whose setup cost exceeds their practical simplification value.

## Dependency example
```text
# requests 2.32.3
requests==2.32.3 \
    --hash=sha256:<hash1> \
    --hash=sha256:<hash2>
```

- Generate the locked file with `pip-compile --generate-hashes` or an equivalent workflow that captures the full dependency closure.

## Testing defaults
- Use `pytest` as default unit-test framework.
- Keep tests under `tests/` with deterministic behavior.
- For modify tasks with existing tests: edit code first, run existing tests, then update tests only if behavior changes are intentional.

## Cross-references
- For structured application code, use `.github/skills/internal-project-python/SKILL.md`.
- For standalone scripts and CLI-oriented automation, use `.github/skills/internal-script-python/SKILL.md`.

## Minimal skeleton
```python
#!/usr/bin/env python3
"""Purpose: Explain what this script does.

Usage examples:
  python3 ./script.py --help
"""
```

## Minimal test example
```python
def test_example() -> None:
    assert 1 + 1 == 2
```
