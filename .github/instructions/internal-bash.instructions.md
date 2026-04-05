---
description: Bash scripting standards for safe execution, guard clauses, and consistent runtime logs.
applyTo: "**/*.sh"
---

<!-- Core Knowledge Source: awesome-copilot-shell.instructions.md -->
<!-- This internal instruction extends the external with governance-specific rules. -->
<!-- Do not duplicate content from the core source; reference it instead. -->

# Bash Instructions

## Mandatory rules
- Use Bash only: `#!/usr/bin/env bash`.
- Add a header comment with purpose and usage examples.
- Use emoji logs (`ℹ️ ✅ ⚠️ ❌`) for runtime visibility.
- Prefer early return and simple, readable functions.
- Apply these rules for both create and modify operations.

## Standard skeleton
```bash
#!/usr/bin/env bash
#
# Purpose: Explain what this script does.
# Usage examples:
#   ./script.sh --help
#   ./script.sh --input data.json
#   ./script.sh --input <file content>


set -euo pipefail
```

## Best practices
- Quote variables (`"$var"`).
- Use `[[ ... ]]` and `$(...)`.
- Check dependencies with `command -v`.
- Keep functions short and focused.
- Keep logs informative and consistent.
- Use `getopts` for argument parsing.
- Keep logic simple and avoid unnecessary complexity.
- Validate inputs and handle errors gracefully.
- When the Bash script is a launcher for a standalone Python tool, resolve its own directory, create or reuse a sibling `.venv`, install from the local `requirements.txt` when it exists, and execute the sibling Python entry point.
- When modifying an existing standalone Python entry point, add or preserve the sibling Bash launcher and treat that launcher as the documented entry point in usage examples, prompts, and workflow notes.

## Validation
- `bash -n <script>.sh`
- `shellcheck -s bash <script>.sh` (if available)
