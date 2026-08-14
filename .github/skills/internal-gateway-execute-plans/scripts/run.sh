#!/usr/bin/env bash

set -Eeuo pipefail

fail() {
    printf 'BLOCKED: %s\n' "$*" >&2
    exit 1
}

resolve_loaded_script() {
    local candidate="$1"
    while [[ -L "$candidate" ]]; do
        [[ -e "$candidate" ]] || fail "Loaded runner is a stale symlink: $candidate; next action: repair the bundle link."
        local target
        target="$(readlink "$candidate")" || fail "Unable to read loaded runner link: $candidate"
        if [[ "$target" == /* ]]; then
            candidate="$target"
        else
            candidate="$(dirname "$candidate")/$target"
        fi
    done
    [[ -f "$candidate" ]] || fail "Loaded runner is unavailable: $candidate; next action: load the executor bundle."
    local directory
    directory="$(cd -P -- "$(dirname "$candidate")" && pwd)" || fail "Unable to resolve loaded runner directory."
    printf '%s/%s\n' "$directory" "$(basename "$candidate")"
}

SCRIPT_PATH="$(resolve_loaded_script "${BASH_SOURCE[0]}")"
BUNDLE_ROOT="$(cd -P -- "$(dirname "$SCRIPT_PATH")/.." && pwd)"
SKILL_FILE="$BUNDLE_ROOT/SKILL.md"
ENTRYPOINT="$BUNDLE_ROOT/scripts/plan_execution.py"
LOCK_FILE="$BUNDLE_ROOT/scripts/requirements.txt"

[[ -f "$SKILL_FILE" ]] || fail "Loaded executor bundle is missing SKILL.md; next action: repair the bundle."
[[ -f "$ENTRYPOINT" ]] || fail "Loaded executor bundle is missing plan_execution.py; next action: repair the bundle."
[[ -f "$LOCK_FILE" ]] || fail "Loaded executor bundle is missing its dependency lock; next action: restore requirements.txt."
grep -Eiq '^pyyaml==[0-9]' "$LOCK_FILE" || fail "Dependency lock does not pin PyYAML; next action: regenerate requirements.txt with hashes."
grep -Eq -- '--hash=sha256:[0-9a-f]{64}' "$LOCK_FILE" || fail "Dependency lock is not hash-locked; next action: regenerate requirements.txt with hashes."

PYTHON_BIN="${PYTHON_BIN:-python3}"
command -v "$PYTHON_BIN" >/dev/null 2>&1 || fail "Missing Python runtime: $PYTHON_BIN; next action: install Python 3."
RUNTIME_DIR="${EXECUTOR_BUNDLE_RUNTIME_DIR:-$BUNDLE_ROOT/.runtime}"
RUNTIME_PYTHON="$RUNTIME_DIR/bin/python"

bootstrap_runtime() {
    if [[ ! -x "$RUNTIME_PYTHON" ]]; then
        "$PYTHON_BIN" -m venv "$RUNTIME_DIR" || fail "Unable to create the executor runtime: $RUNTIME_DIR"
    fi
    "$RUNTIME_PYTHON" -m pip install --disable-pip-version-check --require-hashes --no-deps -r "$LOCK_FILE" || \
        fail "Unable to provision the executor runtime; next action: inspect the locked dependency installation."
}

if [[ "${1:-}" == "--bootstrap" ]]; then
    shift
    bootstrap_runtime
    [[ "$#" -gt 0 ]] || exit 0
fi

[[ -x "$RUNTIME_PYTHON" ]] || fail "Executor runtime is not provisioned: $RUNTIME_DIR; next action: run $SCRIPT_PATH --bootstrap."
"$RUNTIME_PYTHON" -c 'import yaml' >/dev/null 2>&1 || \
    fail "Executor runtime is missing its locked dependencies; next action: run $SCRIPT_PATH --bootstrap."
exec "$RUNTIME_PYTHON" "$ENTRYPOINT" "$@"
