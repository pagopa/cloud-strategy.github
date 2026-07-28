#!/usr/bin/env bash
#
# Purpose: install repository-owned Git hooks that keep graphify current.
# Usage examples:
#   ./.github/scripts/install-graphify-hooks.sh

set -Eeuo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

cd "$REPO_ROOT"
git config core.hooksPath .github/hooks

HOOKS_DIR="$REPO_ROOT/.github/hooks"
HOOK_MARKER="# graphify-hook: managed delegate"
mkdir -p "$HOOKS_DIR"

install_hook() {
    local hook_name="$1"
    local hook_path="$HOOKS_DIR/$hook_name"
    local original_path="$hook_path.graphify-original"
    local temporary_path

    if [ -L "$hook_path" ]; then
        printf 'Preserved foreign symlink hook: %s\n' "$hook_path"
        return 0
    fi

    if [ -f "$hook_path" ] && ! grep -Fq "$HOOK_MARKER" "$hook_path"; then
        if [ -e "$original_path" ] || [ -L "$original_path" ]; then
            printf 'Preserved foreign hook with existing backup: %s\n' "$hook_path"
            return 0
        fi
        mv "$hook_path" "$original_path"
    fi

    if [ -f "$hook_path" ] && grep -Fq "$HOOK_MARKER" "$hook_path"; then
        return 0
    fi

    temporary_path="$(mktemp "$HOOKS_DIR/.${hook_name}.XXXXXX")"
    # The generated hook must expand these variables when it runs, not while it is written.
    # shellcheck disable=SC2016
    {
        printf '%s\n' '#!/usr/bin/env bash'
        printf '%s\n' "$HOOK_MARKER"
        printf '%s\n' 'set -Eeuo pipefail'
        printf '%s\n' 'SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"'
        printf 'ORIGINAL_HOOK="$SCRIPT_DIR/%s.graphify-original"\n' "$hook_name"
        printf '%s\n' 'original_status=0'
        printf '%s\n' 'if [ -f "$ORIGINAL_HOOK" ]; then'
        printf '%s\n' '    set +e'
        printf '%s\n' '    if [ -x "$ORIGINAL_HOOK" ]; then'
        printf '%s\n' '        "$ORIGINAL_HOOK" "$@"'
        printf '%s\n' '    else'
        printf '%s\n' '        bash "$ORIGINAL_HOOK" "$@"'
        printf '%s\n' '    fi'
        printf '%s\n' '    original_status=$?'
        printf '%s\n' '    set -e'
        printf '%s\n' 'fi'
        printf '%s\n' 'set +e'
        printf '%s ' '"$SCRIPT_DIR/../scripts/graphify-file-change-hook.sh"'
        printf '%s ' "$hook_name"
        printf '%s\n' '"$@"'
        printf '%s\n' 'delegate_status=$?'
        printf '%s\n' 'set -e'
        printf '%s\n' 'if [ "$original_status" -ne 0 ]; then'
        printf '%s\n' '    exit "$original_status"'
        printf '%s\n' 'fi'
        printf '%s\n' 'exit "$delegate_status"'
    } >"$temporary_path"
    chmod 755 "$temporary_path"
    mv "$temporary_path" "$hook_path"
}

for hook_name in post-commit post-checkout post-merge; do
    install_hook "$hook_name"
done

printf 'Installed Git hooks path: %s\n' '.github/hooks'
