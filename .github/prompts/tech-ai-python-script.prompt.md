---
description: Create or modify repository-agnostic Python scripts with explicit interfaces and deterministic tests
name: TechAIPythonScript
agent: agent
argument-hint: action=<create|modify> script_name=<name> purpose=<purpose> [target_path=<path>] [target_file=<path>] [test_scope=<none|unit>]
---

# TechAI Python Script

## Context
Create or modify a standalone Python script while keeping interfaces explicit, behavior deterministic, and the delivery package self-contained.

## Required inputs
- **Action**: ${input:action:create,modify}
- **Script name**: ${input:script_name}
- **Purpose**: ${input:purpose}
- **Target path**: ${input:target_path:.github/scripts}
- **Target file (when modifying)**: ${input:target_file}
- **Test scope**: ${input:test_scope:unit,none}

## Instructions
1. Use `.github/skills/tech-ai-script-python/SKILL.md`.
2. Reuse existing repository patterns before introducing new structure.
3. Keep module purpose/usage clear, public interfaces explicit, comments/logs in English, and control flow easy to follow.
4. If `action=modify` and tests already exist, run the existing tests before editing them.
5. Add or update deterministic tests only for intentional behavior changes or uncovered new behavior when `test_scope=unit`.
6. Use Jinja templates named `<file-name>.<extension>.j2` when the task includes Python-managed templates.
7. For new standalone scripts, prefer a dedicated folder at `<target_path>/<script_name>/` instead of a loose single `.py` file.
8. The standalone script folder should contain the Python entry point, a local `requirements.txt` with exact pins and hashes when external packages are used, and a `run.sh` launcher that bootstraps or reuses `.venv`, installs dependencies, and invokes the Python entry point.
9. Keep a short comment above each introduced requirement block so pinned package versions are easy to read.
10. External libraries are recommended when they materially simplify the script, but they are not mandatory if the standard library is simpler.
11. Follow `.github/instructions/python.instructions.md` for dependency locking.
12. Make new `run.sh` launchers executable.

## Minimal example
- Input: `action=modify script_name=inventory_report purpose="Summarize customization assets" target_file=.github/scripts/inventory_report.py test_scope=unit`
- Expected output:
  - Updated standalone Python script package with explicit CLI behavior, local dependency lock data, a Bash launcher, and focused deterministic tests.

## Validation
- Run `python -m compileall <changed_python_paths>`.
- Run `pytest` for the changed script/tests when present.
- Run `bash -n` on generated or modified launcher scripts.
- Run `bash .github/scripts/validate-copilot-customizations.sh --scope root --mode strict` when changing Copilot assets.
