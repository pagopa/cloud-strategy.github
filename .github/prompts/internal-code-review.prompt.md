---
description: Perform an exhaustive, nit-level code review on Python, Bash, or Terraform files
name: internal-code-review
agent: agent
argument-hint: target=<file_or_folder> [language=<python|bash|terraform|auto>] [strictness=<strict|moderate>]
---

# Strict Code Review

## Context
Perform a thorough, opinionated code review using per-language anti-pattern catalogs. Catches everything from security flaws to style nits.

## Required inputs
- **Target**: ${input:target}
- **Language**: ${input:language:auto,python,bash,terraform}
- **Strictness**: ${input:strictness:strict,moderate}

## Instructions

1. Use the skill in `.github/skills/internal-code-review/SKILL.md` as the anti-pattern reference catalog.
2. Auto-detect language from file extensions when `language=auto` (default).
3. For multi-language targets, apply all relevant checklists in a single pass.
4. Cross-reference findings with the matching instruction files:
   - Python: `.github/instructions/internal-python.instructions.md`
   - Bash: `.github/instructions/internal-bash.instructions.md`
   - Terraform: `.github/instructions/internal-terraform.instructions.md`
5. Apply `security-baseline.md` controls as minimum baseline.
6. When `strictness=strict` (default):
   - Flag every anti-pattern from the catalog, including `Nit` level.
   - Escalate repeated violations (3+ of the same kind) one severity level.
   - Treat any deviation from instruction files as at minimum a `Nit`.
7. When `strictness=moderate`:
   - Skip `Nit` level findings.
   - Report only `Critical`, `Major`, and `Minor` findings.
8. Include file path and line reference for every finding.
9. Suggest a concrete fix or reference the catalog's "good" examples for each finding.

## Output format

```
## Review Summary
Files reviewed: <count>
Languages: <list>
Findings: <critical> Critical | <major> Major | <minor> Minor | <nit> Nit

## Critical
### [CRITICAL] <ID>: <title>
- File: <path>#L<line>
- Rule: <catalog anti-pattern ID>
- Issue: <description>
- Fix: <suggestion>

## Major
...

## Minor
...

## Nit
...

## Notes
...
```

## Minimal example
- Input: `target=src/service/utils.py language=auto strictness=strict`
- Expected output:
  - All Python anti-patterns checked against the file.
  - Findings grouped by severity with file/line references.
  - Concrete fix suggestions for each finding.

## Validation
- Verify all findings reference actual code from the target.
- Verify severity assignments match the catalog rules.
