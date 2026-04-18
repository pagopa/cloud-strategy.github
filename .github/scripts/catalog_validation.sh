#!/usr/bin/env bash
#
# Purpose: Simulate the catalog-validation GitHub Actions workflow locally.
# Usage examples:
#   ./catalog_validation.sh
#   ./.github/scripts/catalog_validation.sh
#   ./.github/scripts/catalog_validation.sh --skip-token-risks
#   ./.github/scripts/catalog_validation.sh --token-risks-only

set -Eeuo pipefail

log_info() {
    printf 'ℹ️  %s\n' "$*"
}

log_success() {
    printf '✅ %s\n' "$*"
}

log_warn() {
    printf '⚠️  %s\n' "$*"
}

log_error() {
    printf '❌ %s\n' "$*" >&2
}

usage() {
    cat <<'EOF'
Usage:
  ./catalog_validation.sh
  ./.github/scripts/catalog_validation.sh
  ./.github/scripts/catalog_validation.sh --skip-token-risks
  ./.github/scripts/catalog_validation.sh --token-risks-only
EOF
}

run_required_target() {
    local target="$1"

    log_info "Running make $target"
    make "$target"
    log_success "Completed make $target"
}

run_optional_target() {
    local target="$1"

    log_info "Running make $target"
    if make "$target"; then
        log_success "Completed make $target"
        return
    fi

    log_warn "make $target reported findings; continuing to match .github/workflows/catalog-validation.yml"
}

parse_args() {
    while (($# > 0)); do
        case "$1" in
            --skip-token-risks)
                RUN_TOKEN_RISKS=false
                ;;
            --token-risks-only)
                RUN_REQUIRED_TARGETS=false
                RUN_TOKEN_RISKS=true
                ;;
            -h|--help)
                usage
                exit 0
                ;;
            *)
                log_error "Unknown argument: $1"
                usage >&2
                exit 1
                ;;
        esac
        shift
    done
}

main() {
    parse_args "$@"
    cd "$REPO_ROOT"

    if [[ "$RUN_REQUIRED_TARGETS" == true ]]; then
        run_required_target catalog-lint
        run_required_target test
        run_required_target skill-lint
        run_required_target catalog-check
    fi

    if [[ "$RUN_TOKEN_RISKS" == true ]]; then
        run_optional_target token-risks
    fi
}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
RUN_REQUIRED_TARGETS=true
RUN_TOKEN_RISKS=true

main "$@"
