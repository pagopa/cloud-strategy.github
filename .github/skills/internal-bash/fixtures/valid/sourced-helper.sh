# Sourced helper: the caller owns the interpreter.

require_value() {
  if [ -z "${1:-}" ]; then
    printf '%s\n' 'missing value' >&2
    return 1
  fi
}
