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
AGENTS_DIR="${ROOT_DIR}/.github/agents"
WORKFLOWS_DIR="${ROOT_DIR}/.github/workflows"

FAILURES=0

log_info() { echo "ℹ️  $*"; }
log_warn() { echo "⚠️  $*"; }
log_error() { echo "❌ $*" >&2; }
log_success() { echo "✅ $*"; }

search_pattern() {
  local pattern="$1"
  local target="$2"

  if command -v rg >/dev/null 2>&1; then
    rg -n "$pattern" "$target"
    return $?
  fi

  grep -R -nE "$pattern" "$target"
}

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

has_heading() {
  local file="$1"
  local heading="$2"
  grep -Eq "^${heading}$" "$file"
}

has_any_heading() {
  local file="$1"
  shift
  local heading

  for heading in "$@"; do
    if has_heading "$file" "$heading"; then
      return 0
    fi
  done

  return 1
}

check_required_keys() {
  local file="$1"
  shift
  local missing=()
  local key

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

validate_prompt_skill_references() {
  local file="$1"
  local refs=()
  local ref

  while IFS= read -r ref; do
    refs+=("$ref")
  done < <(grep -oE '\.github/skills/[A-Za-z0-9._/-]+/SKILL\.md' "$file" | sort -u || true)

  if [[ "${#refs[@]}" -eq 0 ]]; then
    log_error "Prompt must reference at least one skill: ${file}"
    FAILURES=$((FAILURES + 1))
    return
  fi

  for ref in "${refs[@]}"; do
    if [[ ! -f "${ROOT_DIR}/${ref}" ]]; then
      log_error "Prompt references missing skill path '${ref}' in ${file}"
      FAILURES=$((FAILURES + 1))
    fi
  done
}

validate_prompts() {
  local file

  while IFS= read -r file; do
    check_required_keys "$file" description name agent argument-hint

    if frontmatter "$file" | grep -Eq '^mode:[[:space:]]*'; then
      log_error "Legacy key 'mode' is not allowed: ${file}"
      FAILURES=$((FAILURES + 1))
    fi

    if ! has_heading "$file" '## Instructions'; then
      log_error "Prompt missing '## Instructions' section: ${file}"
      FAILURES=$((FAILURES + 1))
    fi

    if ! has_heading "$file" '## Validation'; then
      log_error "Prompt missing '## Validation' section: ${file}"
      FAILURES=$((FAILURES + 1))
    fi

    if ! has_heading "$file" '## Minimal example'; then
      log_error "Prompt missing '## Minimal example' section: ${file}"
      FAILURES=$((FAILURES + 1))
    fi

    validate_prompt_skill_references "$file"
  done < <(find "${PROMPTS_DIR}" -type f -name "*.prompt.md" | sort)
}

validate_instructions() {
  local file

  while IFS= read -r file; do
    check_required_keys "$file" applyTo

    if ! grep -Eq '^# ' "$file"; then
      log_error "Instruction missing top heading: ${file}"
      FAILURES=$((FAILURES + 1))
    fi
  done < <(find "${INSTRUCTIONS_DIR}" -type f -name "*.instructions.md" | sort)
}

validate_skill_directories() {
  local dir

  while IFS= read -r dir; do
    if [[ ! -f "${dir}/SKILL.md" ]]; then
      log_error "Skill directory missing SKILL.md: ${dir}"
      FAILURES=$((FAILURES + 1))
    fi
  done < <(find "${SKILLS_DIR}" -mindepth 1 -maxdepth 1 -type d | sort)
}

validate_skills() {
  local file

  validate_skill_directories

  while IFS= read -r file; do
    check_required_keys "$file" name description

    if ! has_heading "$file" '## When to use'; then
      log_error "Skill missing '## When to use' section: ${file}"
      FAILURES=$((FAILURES + 1))
    fi

    if ! has_any_heading "$file" '## Validation' '## Checklist' '## Testing' '## Test stack'; then
      log_error "Skill missing validation/testing section: ${file}"
      FAILURES=$((FAILURES + 1))
    fi
  done < <(find "${SKILLS_DIR}" -type f -name "SKILL.md" | sort)
}

validate_agents() {
  local file
  local agent_count=0

  if [[ ! -d "${AGENTS_DIR}" ]]; then
    log_warn "No .github/agents directory found; skipping agent validation."
    return
  fi

  while IFS= read -r file; do
    agent_count=$((agent_count + 1))
    check_required_keys "$file" name description tools

    if ! grep -Eq '^# ' "$file"; then
      log_error "Agent missing top heading: ${file}"
      FAILURES=$((FAILURES + 1))
    fi

    if ! has_heading "$file" '## Objective'; then
      log_error "Agent missing '## Objective' section: ${file}"
      FAILURES=$((FAILURES + 1))
    fi

    if ! has_heading "$file" '## Restrictions'; then
      log_error "Agent missing '## Restrictions' section: ${file}"
      FAILURES=$((FAILURES + 1))
    fi
  done < <(find "${AGENTS_DIR}" -type f -name "*.agent.md" | sort)

  if [[ "${agent_count}" -eq 0 ]]; then
    log_warn "No custom agents found under .github/agents."
  fi
}

validate_unreferenced_skills() {
  local skill
  local skill_ref

  while IFS= read -r skill; do
    skill_ref="${skill#"${ROOT_DIR}"/}"
    if ! grep -R -q "${skill_ref}" "${PROMPTS_DIR}"; then
      log_warn "Unreferenced skill (consider using in prompts): ${skill_ref}"
    fi
  done < <(find "${SKILLS_DIR}" -type f -name "SKILL.md" | sort)
}

validate_workflow_pinning() {
  local pattern='uses:[[:space:]]*[^[:space:]]+@v[0-9]+'

  if [[ ! -d "${WORKFLOWS_DIR}" ]]; then
    log_warn "No .github/workflows directory found; skipping action pinning check."
    return
  fi

  if search_pattern "$pattern" "${WORKFLOWS_DIR}" >/dev/null 2>&1; then
    log_error "Workflow action tags (@v*) found. Pin actions to full-length SHAs."
    search_pattern "$pattern" "${WORKFLOWS_DIR}" || true
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
  validate_agents
  validate_unreferenced_skills
  validate_workflow_pinning

  if [[ "${FAILURES}" -gt 0 ]]; then
    log_error "Validation failed with ${FAILURES} issue(s)."
    return 1
  fi

  log_success "🏁 Copilot customization validation passed."
}

main "$@"
