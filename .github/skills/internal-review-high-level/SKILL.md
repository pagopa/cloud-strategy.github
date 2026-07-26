---
name: internal-review-high-level
description: Use when a user needs evidence-first, high-level review of non-code artifacts or changes for system fit, cross-cutting impact, risk, ownership, validation gaps, or orientation rather than code-level correctness.
---

# Internal Review High Level

## Purpose

Review non-code targets at system and contract level. Remain report-only: do
not apply remediation.

## Scope

Review documentation, policy, governance, plans, specifications, decisions,
skills, prompts, instructions, processes, and declarative artifacts when the
question is system-level. Assess system fit, cross-cutting impact, risk,
ownership, validation gaps, and orientation.

Exclude code-level correctness, syntax, format validation, executable behavior,
and code-level correctness checks. For mixed targets, use this skill only when
code is not the primary review subject.

## When to use

Use this skill when the question concerns system fit or contract impact in a
non-code target.

## Review method

1. Resolve the target, intent, scope, and review limits.
2. Choose only the dimensions relevant to the question.
3. Inspect the target and its immediate consumers.
4. Test the strongest contrary explanation.
5. Separate findings from evidence gaps.
6. Report the smallest useful next action.

Support material conclusions with evidence. Keep recommendations report-only
and make ownership or validation limits visible.

## Optional depth

Load `references/analysis-dimensions.md` for system or orientation depth.
Load `references/review-lenses.md` when findings need severity or confidence.
Use only the questions that fit the target.

## Public projection

Use `🔎` for the result, `📌` for the reason, `🧪` for evidence or a gap, and
`👉` for the next action. Omit an anchor when it adds no information. Add
detailed findings only when evidence supports them.

A material finding contains `Evidence`, `Impact`, `Recommendation`, and
`Expected verification`. State uncertainty with the confidence vocabulary in
`references/review-lenses.md`.

## Completion

Every material conclusion is evidence-backed or marked as an evidence gap.
Scope and validation limits are visible. No remediation was applied.
