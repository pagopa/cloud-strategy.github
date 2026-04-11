# Python Script Layout And Templates

Use this reference when you need the default folder layout, a starter entry point, a locked `requirements.txt`, or a `run.sh` launcher.

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

## Minimal Python Entry Point

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

## Minimal Requirements Example

```text
# requests 2.32.3
requests==2.32.3 \
    --hash=sha256:<hash1> \
    --hash=sha256:<hash2>
```

Generate `requirements.txt` with `pip-compile --generate-hashes` or an equivalent workflow that locks the full dependency closure.

## Minimal Launcher Example

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
