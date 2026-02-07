#!/usr/bin/env bash
#
# Purpose: Validate Copilot customization files under .github.
# Usage examples:
#   ./.github/scripts/validate-copilot-customizations.sh
#   bash .github/scripts/validate-copilot-customizations.sh
#

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
readonly ROOT_DIR

PROMPTS_DIR="${ROOT_DIR}/.github/prompts"
INSTRUCTIONS_DIR="${ROOT_DIR}/.github/instructions"
SKILLS_DIR="${ROOT_DIR}/.github/skills"
WORKFLOWS_DIR="${ROOT_DIR}/.github/workflows"

FAILURES=0

log_info() { echo "ℹ️  $*"; }
log_warn() { echo "⚠️  $*"; }
log_error() { echo "❌ $*" >&2; }
log_success() { echo "✅ $*"; }

frontmatter() {
  awk '
    NR == 1 && $0 == "---" { in_fm = 1; next }
    in_fm && $0 == "---" { exit }
    in_fm { print }
  ' "$1"
}

has_key() {
  local file="$1"
  local key="$2"
  frontmatter "$file" | grep -Eq "^${key}:[[:space:]]*.+$"
}

check_required_keys() {
  local file="$1"
  shift
  local missing=()

  for key in "$@"; do
    if ! has_key "$file" "$key"; then
      missing+=("$key")
    fi
  done

  if [[ "${#missing[@]}" -gt 0 ]]; then
    log_error "Missing frontmatter keys (${missing[*]}): ${file}"
    FAILURES=$((FAILURES + 1))
  fi
}

validate_prompts() {
  while IFS= read -r file; do
    check_required_keys "$file" description name agent
    if frontmatter "$file" | grep -Eq '^mode:[[:space:]]*'; then
      log_error "Legacy key 'mode' is not allowed: ${file}"
      FAILURES=$((FAILURES + 1))
    fi
  done < <(find "${PROMPTS_DIR}" -type f -name "*.prompt.md" | sort)
}

validate_instructions() {
  while IFS= read -r file; do
    check_required_keys "$file" applyTo
  done < <(find "${INSTRUCTIONS_DIR}" -type f -name "*.instructions.md" | sort)
}

validate_skills() {
  while IFS= read -r file; do
    check_required_keys "$file" name description
  done < <(find "${SKILLS_DIR}" -type f -name "SKILL.md" | sort)
}

validate_workflow_pinning() {
  if [[ ! -d "${WORKFLOWS_DIR}" ]]; then
    log_warn "No .github/workflows directory found; skipping action pinning check."
    return
  fi

  if rg -n "uses:[[:space:]]*[^[:space:]]+@v[0-9]+" "${WORKFLOWS_DIR}" >/dev/null 2>&1; then
    log_error "Workflow action tags (@v*) found. Pin actions to full-length SHAs."
    rg -n "uses:[[:space:]]*[^[:space:]]+@v[0-9]+" "${WORKFLOWS_DIR}" || true
    FAILURES=$((FAILURES + 1))
  fi
}

main() {
  log_info "🚀 Starting Copilot customization validation"

  if [[ ! -d "${PROMPTS_DIR}" || ! -d "${INSTRUCTIONS_DIR}" || ! -d "${SKILLS_DIR}" ]]; then
    log_error "Expected .github prompts/instructions/skills directories are missing."
    return 1
  fi

  validate_prompts
  validate_instructions
  validate_skills
  validate_workflow_pinning

  if [[ "${FAILURES}" -gt 0 ]]; then
    log_error "Validation failed with ${FAILURES} issue(s)."
    return 1
  fi

  log_success "🏁 Copilot customization validation passed."
}

main "$@"
