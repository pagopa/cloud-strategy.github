#!/usr/bin/env bash
#
# Purpose: Bootstrap Copilot customization files from a source `.github` folder into a target repository.
# Usage examples:
#   ./.github/scripts/bootstrap-copilot-config.sh --target /path/to/repo
#   ./.github/scripts/bootstrap-copilot-config.sh --target /path/to/repo --apply
#   ./.github/scripts/bootstrap-copilot-config.sh --target /path/to/repo --apply --clean
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEFAULT_SOURCE_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

SOURCE_DIR="${DEFAULT_SOURCE_DIR}"
TARGET_REPO=""
DRY_RUN=true
CLEAN_SYNC=false

log_info() { echo "ℹ️  $*"; }
log_warn() { echo "⚠️  $*"; }
log_error() { echo "❌ $*" >&2; }
log_success() { echo "✅ $*"; }

usage() {
  cat <<'USAGE'
Usage: bootstrap-copilot-config.sh --target <repo-path> [--source <.github-path>] [--apply] [--clean]

Options:
  --target   Target repository path (required)
  --source   Source `.github` directory path (default: sibling .github directory)
  --apply    Apply changes (default is dry-run)
  --clean    Remove files in target `.github` that are not in source (requires --apply)
  -h, --help Show help
USAGE
}

require_dependencies() {
  if ! command -v rsync >/dev/null 2>&1; then
    log_error "Missing dependency: rsync"
    return 1
  fi
}

parse_args() {
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --target)
        TARGET_REPO="${2:-}"
        shift 2
        ;;
      --source)
        SOURCE_DIR="${2:-}"
        shift 2
        ;;
      --apply)
        DRY_RUN=false
        shift
        ;;
      --clean)
        CLEAN_SYNC=true
        shift
        ;;
      -h|--help)
        usage
        exit 0
        ;;
      *)
        log_error "Unknown argument: $1"
        usage
        return 1
        ;;
    esac
  done

  if [[ -z "$TARGET_REPO" ]]; then
    log_error "--target is required"
    return 1
  fi

  if [[ "$CLEAN_SYNC" == true && "$DRY_RUN" == true ]]; then
    log_error "--clean requires --apply"
    return 1
  fi
}

validate_paths() {
  if [[ ! -d "$SOURCE_DIR" ]]; then
    log_error "Source directory not found: $SOURCE_DIR"
    return 1
  fi

  if [[ "$(basename "$SOURCE_DIR")" != ".github" ]]; then
    log_warn "Source path does not end with .github: $SOURCE_DIR"
  fi

  if [[ ! -d "$TARGET_REPO" ]]; then
    log_error "Target repository not found: $TARGET_REPO"
    return 1
  fi
}

run_sync() {
  local target_github_dir="${TARGET_REPO}/.github"
  local rsync_args=(-a --exclude '.git/')

  if [[ "$CLEAN_SYNC" == true ]]; then
    rsync_args+=(--delete)
  fi

  if [[ "$DRY_RUN" == true ]]; then
    rsync_args+=(--dry-run)
  fi

  mkdir -p "$target_github_dir"

  log_info "📦 Source: ${SOURCE_DIR}"
  log_info "🎯 Target: ${target_github_dir}"
  log_info "🧪 Mode: $([[ "$DRY_RUN" == true ]] && echo dry-run || echo apply)"

  rsync "${rsync_args[@]}" "${SOURCE_DIR}/" "${target_github_dir}/"

  if [[ "$DRY_RUN" == true ]]; then
    log_success "Dry-run completed. Re-run with --apply to persist changes."
    return 0
  fi

  log_success "Copilot customization bootstrap completed."
  return 0
}

main() {
  require_dependencies || return 1
  parse_args "$@" || return 1
  validate_paths || return 1
  run_sync
}

main "$@"
