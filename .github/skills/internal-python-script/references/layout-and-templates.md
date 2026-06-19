# Python Script Layout And Templates

Use this reference when you need the default folder layout, a repo-aligned toolkit layout, a starter entry point, a locked `requirements.txt`, or a `run.sh` launcher.

## Default Layout

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

## Shared Toolkit Layout

Use this when several operator-facing entrypoints share one dependency set and local helper modules.

```text
repo-root/
├── .github/scripts/
│   ├── run.sh
│   ├── requirements.txt
│   ├── {tool_a}.py
│   ├── {tool_b}.py
│   └── lib/
│       ├── __init__.py
│       ├── shared.py
│       └── {helper_module}.py
└── tests/
    ├── conftest.py
    └── test_{toolkit_behavior}.py
```

- Keep each entrypoint thin and import reusable helpers from the local `lib/` package.
- Keep the dependency decision note and pinned hashes in the shared `requirements.txt`.

## Minimal Python Entry Point

```python
#!/usr/bin/env python3
"""Purpose: {description}

Usage examples:
  python3 ./{script_name}.py --help
"""
import argparse
import sys


class ExecutionReporter:
    def __init__(self, *, verbose: bool = False) -> None:
        self.verbose = verbose

    def _emit(self, message: str, *, error: bool = False) -> None:
        stream = sys.stderr if error else sys.stdout
        print(message, file=stream)

    def detail(self, message: str) -> None:
        if self.verbose:
            self._emit(f"ℹ️  {message}")

    def error(self, message: str) -> None:
        self._emit(f"❌ {message}", error=True)

    def step(self, message: str) -> None:
        self._emit(f"• {message}")

    def success(self, message: str) -> None:
        self._emit(f"✅ {message}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", required=True, help="Target to process")
    parser.add_argument("--verbose", action="store_true", help="Show technical details.")
    args = parser.parse_args()

    reporter = ExecutionReporter(verbose=args.verbose)
    reporter.step(f"Processing {args.target}")
    # ... logic ...
    reporter.success("Done")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

For richer operator-facing output, use `references/reporting.md` and replace this stdlib reporter with a `rich`-backed `ExecutionReporter` after recording the dependency decision.

## Repo-Aligned Toolkit Entry Point

Use this pattern when a repository-maintained toolkit exposes multiple entrypoints and a shared `lib/` package.

```python
#!/usr/bin/env python3
"""Purpose: {description}

Usage examples:
  python3 ./.github/scripts/{tool_name}.py --root .
  python3 ./.github/scripts/{tool_name}.py --root . --format json
"""

from __future__ import annotations

import argparse
from pathlib import Path

from lib.reporting import ExecutionReporter
from lib.shared import find_repo_root, render_json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="{description}")
    parser.add_argument("--root", default=".", help="Repository root or any path inside it.")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
  reporter = ExecutionReporter()
    root = find_repo_root(Path(args.root))
    payload = {"root": root.as_posix()}
    if args.format == "json":
        print(render_json(payload))
    else:
    reporter.detail(f"Resolved repository root: {root.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

## Minimal Requirements Example

```text
# Dependency decision note
# Candidates: standard library only, PyYAML, python-frontmatter
# Final choice: PyYAML
# Why: explicit YAML parsing without carrying a heavier content wrapper.

# requests 2.32.3
requests==2.32.3 \
    --hash=sha256:<hash1> \
    --hash=sha256:<hash2>
```

Generate `requirements.txt` with `pip-compile --generate-hashes` or an equivalent workflow that locks the full dependency closure.

## Minimal Launcher Example

Use a dedicated launcher only when one standalone tool depends on external packages.

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

## Thin Wrapper For A Shared Toolkit Runner

Use this when several tools share one local `.venv` and dependency lock file.

```bash
#!/usr/bin/env bash
#
# Purpose: Run the {tool_name} repository toolkit entrypoint.
# Usage examples:
#   ./.github/scripts/{tool_name}.sh --root .

set -Eeuo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

exec "$SCRIPT_DIR/run.sh" "{tool_name}" "$@"
```

- Prefer this thin wrapper pattern when the shared runner already owns `.venv`, dependency installation, and dispatch.
- Keep direct `python3` invocation documented for stdlib-only tools that do not need a runner.
