---
description: Analyze repository changes and generate a structured Markdown report with errors, improvements, doubts, blind spots, and architecture advice
name: TechAIPairArchitectAnalysis
agent: TechAIPairArchitect
argument-hint: target=<branch|folder|file_list> [output=ANALYSIS_REPORT.md] [depth=full|quick] [mode=standard|devil]
---

# Change Analysis

## Context
Perform a deep, cross-cutting analysis of repository changes. Goes beyond line-level code review to evaluate domain design, architectural impact, operational readiness, and unconsidered aspects. Generates a self-contained Markdown report.

## Required inputs
- **Target**: ${input:target}
- **Output file**: ${input:output:ANALYSIS_REPORT.md}
- **Depth**: ${input:depth:full,quick}
- **Mode**: ${input:mode:standard,devil}

## Instructions

1. Read `.github/skills/tech-ai-pair-architect/SKILL.md` and use it as the complete analysis framework (dimensions, severity mappings, health score, report template, modes, validation).
2. If `.github/skills/tech-ai-code-review/SKILL.md` exists, use it as anti-pattern reference for the Errors section.
3. Identify changed files from `target` (branch diff, folder, or file list) and auto-detect languages.
4. Follow the skill workflow: gather context, analyze, compute health score, populate risk matrix, write report.
5. Apply depth and mode parameters as defined in the skill.
6. Write the report to `${input:output}` at repository root.

## Post-analysis

After generating the report:
- Print the summary statistics and health score to the conversation.
- If Critical errors exist, recommend concrete remediation steps.
- If the change set is clean, state it explicitly.

## Minimal example
- Input: `target=HEAD~3..HEAD output=ANALYSIS_REPORT.md depth=full mode=devil`
- Expected output:
  - `ANALYSIS_REPORT.md` written at repository root.
  - Health score, verdict, and severity-ordered findings backed by concrete file references.
  - A clear next-step recommendation for remediation or peer review.

## Validation
- Keep `.github/skills/tech-ai-pair-architect/SKILL.md` as the referenced analysis framework.
- Generate a valid Markdown report with all mandatory sections required by that skill.
- Cite concrete file paths and line numbers for every finding.
