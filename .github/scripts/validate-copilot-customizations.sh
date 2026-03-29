#!/usr/bin/env bash

# Purpose: Validate core Copilot customization invariants for this repository.
# Usage examples:
#   bash .github/scripts/validate-copilot-customizations.sh
#   bash .github/scripts/validate-copilot-customizations.sh --scope root --mode strict

set -euo pipefail

scope="root"
mode="strict"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --scope)
      scope="${2:-}"
      shift 2
      ;;
    --mode)
      mode="${2:-}"
      shift 2
      ;;
    *)
      echo "Unknown argument: $1" >&2
      exit 2
      ;;
  esac
done

if [[ "$scope" != "root" ]]; then
  echo "Unsupported scope: $scope" >&2
  exit 2
fi

if [[ "$mode" != "strict" && "$mode" != "basic" ]]; then
  echo "Unsupported mode: $mode" >&2
  exit 2
fi

python3 - <<'PY'
from pathlib import Path
import re
import sys

root = Path(".")
errors: list[str] = []

required_paths = [
    Path("AGENTS.md"),
    Path(".github/copilot-instructions.md"),
    Path(".github/security-baseline.md"),
]
for path in required_paths:
    if not path.exists():
        errors.append(f"Missing required file: {path}")

if Path(".github/AGENTS.md").exists():
    errors.append("Legacy .github/AGENTS.md exists; root AGENTS.md must be canonical.")

for skill_dir in sorted((root / ".github/skills").iterdir()):
    if not skill_dir.is_dir():
        continue
    skill_file = skill_dir / "SKILL.md"
    if not skill_file.exists():
        errors.append(f"Missing skill file: {skill_file}")
        continue
    text = skill_file.read_text(encoding="utf-8", errors="ignore")
    match = re.search(r"^name:\s*(.+)$", text, re.M)
    if not match:
        errors.append(f"Missing frontmatter name: {skill_file}")
        continue
    name = match.group(1).strip().strip("\"'")
    if name != skill_dir.name:
        errors.append(f"Skill name mismatch: {skill_dir.name} != {name}")

for prompt_file in sorted((root / ".github/prompts").glob("*.prompt.md")):
    text = prompt_file.read_text(encoding="utf-8", errors="ignore")
    match = re.search(r"^name:\s*(.+)$", text, re.M)
    if not match:
        errors.append(f"Missing frontmatter name: {prompt_file}")
        continue
    name = match.group(1).strip().strip("\"'")
    expected = prompt_file.name[:-len(".prompt.md")]
    if name != expected:
        errors.append(f"Prompt name mismatch: {expected} != {name}")

for agent_file in sorted((root / ".github/agents").glob("*.agent.md")):
    text = agent_file.read_text(encoding="utf-8", errors="ignore")
    match = re.search(r"^name:\s*(.+)$", text, re.M)
    if not match:
        errors.append(f"Missing frontmatter name: {agent_file}")
        continue
    name = match.group(1).strip().strip("\"'")
    expected = agent_file.name[:-len(".agent.md")]
    if name != expected:
        errors.append(f"Agent name mismatch: {expected} != {name}")

inventory_lines = []
inside_inventory = False
for raw_line in Path("AGENTS.md").read_text(encoding="utf-8", errors="ignore").splitlines():
    if raw_line.startswith("## Repository Inventory"):
        inside_inventory = True
        continue
    if not inside_inventory:
        continue
    if raw_line.startswith("- `") and raw_line.endswith("`"):
        inventory_lines.append(raw_line[3:-1])

for relative in inventory_lines:
    if not (root / relative).exists():
        errors.append(f"Inventory path missing on disk: {relative}")

if errors:
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    sys.exit(1)

print("Validation passed.")
PY
