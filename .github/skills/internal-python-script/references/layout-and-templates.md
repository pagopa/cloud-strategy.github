# Python Script Layout And Templates

Load this reference when a direct-execution tool needs a layout, importable
entrypoint, pip-managed lock, or launcher. Follow the repository-declared
environment and existing runner before using these illustrative shapes.

## Repository-aligned layouts

Use an existing script folder first. A standalone tool may use:

```text
repo-root/
├── {script_path}/
│   ├── {script_name}.py
│   ├── requirements.txt  # only for pip-managed external packages
│   └── run.sh            # only when a launcher contract requires it
└── tests/
    └── {script_path}/
        └── test_{script_name}.py
```

For several operator-facing entrypoints with shared dependencies, follow the
repository's existing toolkit layout. One common shape is:

```text
repo-root/
├── .github/scripts/
│   ├── run.sh
│   ├── requirements.txt  # shared pip lock
│   ├── {tool_a}.py
│   ├── {tool_b}.py
│   └── lib/
│       ├── __init__.py
│       ├── shared.py
│       └── {helper_module}.py
└── tests/
    └── test_{toolkit_behavior}.py
```

Keep entrypoints thin and mirror coverage under repository-root `tests/`.

## Minimal importable entrypoint

```python
#!/usr/bin/env python3
"""Purpose: {description}"""

import argparse


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", required=True)
    args = parser.parse_args()
    # Resolve, orchestrate, and report at this boundary.
    return 0 if args.target else 1


if __name__ == "__main__":
    raise SystemExit(main())
```

## Hash-locked dependencies

```text
# requirements.in — illustrative input; generate requirements.txt before use
# Dependency decision note
# Candidates: standard library only, PyYAML, python-frontmatter
# Final choice: PyYAML
# Why: explicit YAML parsing without a heavier content wrapper.
PyYAML==6.0.3
```

Generate and validate the full lock with:

```bash
pip-compile --generate-hashes requirements.in
python -m pip install --require-hashes -r requirements.txt
```

Do not copy partial real hashes into a reusable template; valid wheel hashes
vary by release and platform support.

## Launcher boundary

Use a launcher only when the tool contract or repository runner requires it.
It must invoke the repository-declared environment without silently creating a
virtual environment or installing dependencies on every execution.

```bash
#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3}"

# The repository-declared environment or shared runner owns setup.
exec "$PYTHON_BIN" "$SCRIPT_DIR/{script_name}.py" "$@"
```

For a shared toolkit, use a thin wrapper that delegates to the existing
`run.sh`; do not clone its environment bootstrap into each entrypoint.
