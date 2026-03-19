# Python Standalone Script Policy Design

**Context**

This repository defines GitHub Copilot customization assets that are propagated to consumer repositories. We want stronger defaults for Python dependency management everywhere, while adding stricter packaging guidance only for standalone Python scripts.

**Goals**

- Require hash-locked Python dependencies when external packages are introduced.
- Keep external libraries as a recommended simplification tool, not a mandatory rule.
- Make standalone Python scripts self-contained so consumers do not need to manually manage virtual environments or invocation details.

**Policy Split**

1. Global Python policy:
   - When external dependencies are introduced, prefer a compiled `requirements.txt` with `--hash` entries.
   - Keep a short comment above each dependency block to make the pinned version readable for humans.
   - Recommend third-party libraries when they materially reduce complexity or custom parsing/validation/HTTP/CLI code.
   - Do not require third-party libraries when the standard library remains simpler and safer.

2. Standalone script policy:
   - New standalone Python scripts should default to a dedicated folder instead of a loose single `.py` file.
   - The folder should contain the Python entry point, `requirements.txt`, a Bash launcher, and tests when applicable.
   - The Bash launcher should bootstrap or reuse `.venv`, install dependencies from the hash-locked requirements file, and execute the Python script with passed arguments.

**Why Not Stronger**

- Requiring third-party libraries in all cases would increase supply-chain risk and maintenance churn.
- Requiring the standalone-script folder layout for all Python code would be harmful for application modules and libraries.
- Adding validator enforcement now would likely be premature. Instructional guidance is the right first move.

**Files To Update**

- `.github/copilot-instructions.md`
- `.github/instructions/python.instructions.md`
- `.github/instructions/bash.instructions.md`
- `.github/prompts/tech-ai-python.prompt.md`
- `.github/prompts/tech-ai-python-script.prompt.md`
- `.github/skills/tech-ai-script-python/SKILL.md`
- `.github/CHANGELOG.md`
