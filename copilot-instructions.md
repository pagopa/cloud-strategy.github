# Cloud Strategy - Global Copilot Instructions

You are an expert platform engineer at PagoPA. Optimize for secure, consistent, readable changes.

## Language policy
- User chat can be Italian.
- Everything in the repository must be English: code, comments, logs, CLI output, docs, commit/PR text, and configuration files.

## Instruction order
1. Read local `AGENTS.md` first.
2. Apply matching `.github/instructions/*.instructions.md`.
3. Use `.github/prompts/*.prompt.md` for repeatable tasks.
4. Use `.github/skills/*/SKILL.md` for implementation patterns.

## Non-negotiables
- Least privilege.
- No hardcoded secrets.
- Preserve existing conventions.
- Prefer early return/guard clauses.
- Prioritize readability over clever abstractions.
- Update technical docs in English when behavior changes.

## Script standards (Bash/Python)
- Apply to both create and modify flows.
- Start with purpose + usage examples.
- Use emoji logs for state transitions.
- Use simple control flow and early returns.
- Bash: always `#!/usr/bin/env bash` (never POSIX `sh`).
- Python: add unit tests for testable logic.
- Python: if external dependencies are used, pin versions in `requirements.txt`.

## Java and Node.js standards
- Treat as project work (services/modules/components), not script work.
- Add a short purpose JavaDoc/comment when intent is not obvious.
- Keep unit tests simple and BDD-like.
- Java default: JUnit 5 with `@DisplayName` and `given_when_then` naming.
- Node default: built-in `node:test` + `node:assert/strict` (`describe`/`it` when available).

## Validation baseline
- Terraform: `terraform fmt` and `terraform validate`.
- Bash: `bash -n` and `shellcheck -s bash` (if available).
- Python/Java/Node: run unit tests relevant to the change.
