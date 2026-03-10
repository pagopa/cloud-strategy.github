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

1. Use the skill in `.github/skills/tech-ai-pair-architect/SKILL.md` as the analysis framework.
2. Identify changed files:
   - If `target` is a branch name, diff against the default branch.
   - If `target` is a folder or file list, analyze those files directly.
3. Auto-detect languages and load matching instruction files.
4. If `.github/skills/tech-ai-code-review/SKILL.md` exists, use it as anti-pattern reference for the Errors section.
5. When `depth=full` (default):
   - Analyze all five dimensions: correctness, DDD, architecture, blind spots, and lateral thinking.
   - Include all report sections with maximum detail.
   - Read dependency files beyond the immediate diff when needed.
6. When `depth=quick`:
   - Focus on Errors and Blind Spots only.
   - Skip Architecture Advisory section.
   - Limit analysis to changed files without dependency tracing.
7. When `mode=devil`:
   - Apply adversarial analysis: challenge at least 3 design assumptions.
   - Propose radically different alternatives with honest tradeoffs.
   - Add a dedicated `Devil's Advocate` section in the report.
8. When `mode=standard` (default):
   - Skip the Devil's Advocate section.
9. Read recent git history (`git log --oneline -20`) for project trajectory context.
10. Compute a health score (0-100) and populate a risk matrix for top findings.
11. Apply `security-baseline.md` controls as minimum baseline.
12. Write the report to `${input:output}` at repository root.

## Output format

The report follows the structure defined in the skill:
1. Executive Summary
2. Errors and Defects (with severity, explanation, and fix)
3. Improvement Opportunities (with category, effort, and rationale)
4. Doubts and Open Questions (with clarification requests)
5. Blind Spots and Unconsidered Aspects (with consequences and recommendations)
6. Architecture and Best Practices — Advisory (non-binding, with impact/effort)
7. Devil's Advocate (only when mode=devil)
8. Risk Matrix (probability/impact grid for top findings)
9. Summary Statistics (with health score and verdict)

## Post-analysis

After generating the report:
- Print the summary statistics and health score to the conversation.
- If Critical errors exist, recommend routing to `TechAIImplementer` for remediation.
- If the change set is clean, state it explicitly.

## Minimal example
- Input: `target=main..feature-branch depth=full mode=devil`
- Expected output:
  - `ANALYSIS_REPORT.md` at repository root with all sections populated.
  - Executive summary with overall assessment and health score.
  - Errors, improvements, doubts, blind spots, and architecture advice with file references.
  - Devil's Advocate section with 3+ design challenges.
  - Risk matrix with top findings placed on probability/impact grid.
  - Summary statistics table with health score and verdict.

## Validation
- Verify every finding references a concrete file and line number from the diff.
- Verify the report contains all mandatory sections, even if empty (state "No findings").
- Verify architecture recommendations include impact and effort assessment.
- Verify health score is computed and verdict matches the threshold table.
- Verify risk matrix contains the most impactful findings.
- If `mode=devil`, verify at least 3 Devil's Advocate challenges are present.

