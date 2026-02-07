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

FAILURES=0

log_info() {
  echo "ℹ️  $*"
}

log_success() {
  echo "✅ $*"
}

log_warn() {
  echo "⚠️  $*"
}

log_error() {
  echo "❌ $*" >&2
}

frontmatter() {
  local file="$1"
  awk '
    NR == 1 && $0 == "---" { in_fm = 1; next }
    in_fm && $0 == "---" { exit }
    in_fm { print }
  ' "$file"
}

has_frontmatter_key() {
  local file="$1"
  local key="$2"
  if frontmatter "$file" | grep -Eq "^${key}:[[:space:]]*.+$"; then
    return 0
  fi
  return 1
}

validate_prompt_file() {
  local file="$1"
  local missing=()

  for key in description name agent; do
    if ! has_frontmatter_key "$file" "$key"; then
      missing+=("$key")
    fi
  done

  if [[ "${#missing[@]}" -gt 0 ]]; then
    log_error "Prompt missing frontmatter keys (${missing[*]}): ${file}"
    FAILURES=$((FAILURES + 1))
  fi

  if frontmatter "$file" | grep -Eq '^mode:[[:space:]]*'; then
    log_error "Legacy frontmatter key 'mode' is not allowed in: ${file}"
    FAILURES=$((FAILURES + 1))
  fi
}

validate_instruction_file() {
  local file="$1"
  if ! has_frontmatter_key "$file" "applyTo"; then
    log_error "Instruction missing 'applyTo' frontmatter: ${file}"
    FAILURES=$((FAILURES + 1))
  fi
}

validate_skill_file() {
  local file="$1"
  local missing=()

  for key in name description; do
    if ! has_frontmatter_key "$file" "$key"; then
      missing+=("$key")
    fi
  done

  if [[ "${#missing[@]}" -gt 0 ]]; then
    log_error "Skill missing frontmatter keys (${missing[*]}): ${file}"
    FAILURES=$((FAILURES + 1))
  fi
}

validate_no_version_tags_in_workflows() {
  local workflows_dir="${ROOT_DIR}/.github/workflows"
  if [[ ! -d "${workflows_dir}" ]]; then
    log_warn "No .github/workflows directory found; skipping action pinning check."
    return
  fi

  if rg -n "uses:[[:space:]]*[^[:space:]]+@v[0-9]+" "${workflows_dir}" >/dev/null 2>&1; then
    log_error "Workflow action tags (@v*) found. Pin actions to full-length SHAs."
    rg -n "uses:[[:space:]]*[^[:space:]]+@v[0-9]+" "${workflows_dir}" || true
    FAILURES=$((FAILURES + 1))
  fi
}

main() {
  log_info "🚀 Starting Copilot customization validation"

  if [[ ! -d "${PROMPTS_DIR}" || ! -d "${INSTRUCTIONS_DIR}" || ! -d "${SKILLS_DIR}" ]]; then
    log_error "Expected .github prompts/instructions/skills directories are missing."
    return 1
  fi

  while IFS= read -r file; do
    validate_prompt_file "$file"
  done < <(find "${PROMPTS_DIR}" -type f -name "*.prompt.md" | sort)

  while IFS= read -r file; do
    validate_instruction_file "$file"
  done < <(find "${INSTRUCTIONS_DIR}" -type f -name "*.instructions.md" | sort)

  while IFS= read -r file; do
    validate_skill_file "$file"
  done < <(find "${SKILLS_DIR}" -type f -name "SKILL.md" | sort)

  validate_no_version_tags_in_workflows

  if [[ "${FAILURES}" -gt 0 ]]; then
    log_error "Validation failed with ${FAILURES} issue(s)."
    return 1
  fi

  log_success "🏁 Copilot customization validation passed."
  return 0
}

main "$@"
