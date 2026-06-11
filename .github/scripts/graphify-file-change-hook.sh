#!/usr/bin/env bash
#
# Purpose: keep graphify outputs fresh after local Git state changes.
# Usage examples:
#   ./.github/scripts/graphify-file-change-hook.sh post-commit
#   ./.github/scripts/graphify-file-change-hook.sh post-checkout <old> <new> <flag>

set -Eeuo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
EVENT="${1:-unknown}"
shift || true

cd "$REPO_ROOT"

if ! command -v graphify >/dev/null 2>&1; then
    exit 0
fi

if [ ! -d "$REPO_ROOT/graphify-out" ]; then
    exit 0
fi

TMP_ROOT="${TMPDIR:-/tmp}"
STATE_DIR="$TMP_ROOT/graphify-hook"
mkdir -p "$STATE_DIR"

REPO_ID="$(printf '%s\n' "$REPO_ROOT" | tr '/: ' '___')"
LOCK_DIR="$STATE_DIR/$REPO_ID.lock"
LOG_FILE="$STATE_DIR/$REPO_ID.log"
NEEDS_UPDATE_FILE="$REPO_ROOT/graphify-out/needs_update"

if ! mkdir "$LOCK_DIR" 2>/dev/null; then
    exit 0
fi
trap 'rmdir "$LOCK_DIR" 2>/dev/null || true' EXIT

is_doc_like_path() {
    case "$1" in
        ""|.git/*|graphify-out/*|tmp/*)
            return 1
            ;;
        *.md|*.mdx|*.rst|*.adoc|*.txt|*.pdf|*.png|*.jpg|*.jpeg|*.webp|*.svg|*.gif)
            return 0
            ;;
        docs/*|raw/*)
            return 0
            ;;
    esac
    return 1
}

is_relevant_path() {
    case "$1" in
        ""|.git/*|graphify-out/*|tmp/*)
            return 1
            ;;
    esac
    return 0
}

list_changed_paths() {
    case "$EVENT" in
        post-commit)
            if git rev-parse --verify HEAD^ >/dev/null 2>&1; then
                git diff-tree --no-commit-id --name-only -r HEAD
            else
                git ls-tree -r --name-only HEAD
            fi
            ;;
        post-checkout)
            local old_ref="${1:-}"
            local new_ref="${2:-}"
            if [ -n "$old_ref" ] && [ -n "$new_ref" ] \
                && git rev-parse --verify "$old_ref" >/dev/null 2>&1 \
                && git rev-parse --verify "$new_ref" >/dev/null 2>&1; then
                git diff --name-only "$old_ref" "$new_ref"
            fi
            ;;
        post-merge)
            git diff-tree --no-commit-id --name-only -r HEAD
            ;;
        *)
            return 0
            ;;
    esac
}

code_changes=0
doc_changes=0

while IFS= read -r path; do
    if ! is_relevant_path "$path"; then
        continue
    fi
    if is_doc_like_path "$path"; then
        doc_changes=1
    else
        code_changes=1
    fi
done < <(list_changed_paths "$@" || true)

if [ "$doc_changes" -eq 1 ]; then
    touch "$NEEDS_UPDATE_FILE"
fi

if [ "$code_changes" -ne 1 ]; then
    exit 0
fi

if ! graphify update . >>"$LOG_FILE" 2>&1; then
    touch "$NEEDS_UPDATE_FILE"
    printf '[graphify-hook] update failed; see %s\n' "$LOG_FILE" >&2
fi
