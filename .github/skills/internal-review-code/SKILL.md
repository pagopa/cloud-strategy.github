---
name: internal-review-code
description: Use when review evidence needs line-level or language-specific defect checks for Python, Bash, Terraform, Java, or Node.js/TypeScript code, tests, or scripts.
---

# Internal Review Code

## Referenced skills

- `mattpocock-code-review`: imported two-axis review core (Standards + Spec) for diff-based parallel sub-agent review.
- `internal-review-high-level`: systems-level review beyond line-level defects.
- `internal-python`: Python anti-pattern depth (load the review anti-patterns reference from that skill).
- `internal-bash`: Bash anti-pattern depth (load the review anti-patterns reference from that skill).
- `internal-terraform`: Terraform anti-pattern depth (load the review anti-patterns reference from that skill).
- `internal-java`: Java anti-pattern depth (load the review anti-patterns reference from that skill).
- `internal-nodejs`: Node.js anti-pattern depth (load the review anti-patterns reference from that skill).
- `superpowers-verification-before-completion`: evidence gate before claiming no findings or merge readiness.

## When to use

- Perform a line-level code review on Python, Bash, Terraform, Java, or Node.js/TypeScript files.
- Provide structured findings with per-language anti-pattern detection.
- The diff or code change is the primary review surface.

## When not to use

- The primary target is an AI resource, workflow, policy, plan, or documentation package; use `internal-gateway-review` instead.
- The review needs systems-level architectural analysis; use `internal-review-high-level` instead.
- The user asks for a two-axis Standards + Spec parallel review; consult `mattpocock-code-review` as the imported core.

## Role

`internal-review-code` is the only repo-owned line-level review contract. It owns trigger, boundary, severity, output shape, and validation discipline. Language-specific anti-pattern depth lives in the nearest language owner, not in this wrapper.

## Standalone quick start

When this skill is used directly instead of through `internal-gateway-review`, establish these inputs first:

- the review question or requested scope
- the changed files or diff being reviewed
- the validation already run and the main evidence gaps that remain

Then produce:

- findings grouped by severity
- a file path and line reference for every finding
- a short residual-risk or unverified-area summary

## Context checklist

Establish these review inputs before grading the diff:

- What behavior, requirement, or defect is the change trying to address?
- Which files, tests, or runtime paths carry the change?
- Are there rollout, backward-compatibility, or migration constraints?
- What is the expected validation path, and what is still unverified?

## Severity levels

| Level | Meaning | Action |
| --- | --- | --- |
| `Critical` | Security flaw, data loss risk, or correctness bug | Must fix before merge |
| `Major` | High-risk maintainability issue or deviation from mandatory rules | Should fix before merge |
| `Minor` | Improvement that reduces technical debt or improves clarity | Fix recommended |
| `Nit` | Style inconsistency, naming preference, or cosmetic issue | Fix optional but encouraged |
| `Notes` | Assumptions, open questions, or follow-up suggestions | Informational only |

## Escalation rules

- Any single anti-pattern repeated three or more times in the same diff escalates one severity level.
- Any deviation from the matching language skill baseline is at minimum a `Nit`.
- Any violation of `security-baseline.md` is at minimum a `Major`.

## Cross-language checks

| Severity | Check |
| --- | --- |
| `Critical` | Hardcoded secrets, tokens, passwords, or API keys |
| `Major` | Missing input validation on external inputs |
| `Major` | Missing error handling on I/O operations |
| `Minor` | Non-English comments, logs, or error messages |
| `Minor` | TODO/FIXME/HACK without linked issue or ticket |
| `Nit` | Trailing whitespace or inconsistent EOF newlines |

## Review lenses

Always cover these dimensions:

- Functionality: correctness, edge cases, failure handling, and requirement fit
- Security: input validation, secret handling, privilege boundaries, unsafe interpolation, and dependency risk
- Performance: unnecessary loops, repeated work, hot-path regressions, or avoidable I/O
- Tests: meaningful coverage, edge-case coverage, and whether the validation actually exercises the changed behavior
- Maintainability: naming, cohesion, complexity, dead code, and local convention fit

## Simplification rubric

When the review also asks whether the change can be simplified safely, use this rubric and keep every recommendation behavior-preserving:

- Reuse: prefer an existing helper or shared abstraction over new near-duplicate logic.
- Quality: flag redundant state, parameter sprawl, copy-paste branches, and stringly-typed values when a stronger local contract already exists.
- Efficiency: flag repeated work, duplicate reads, unnecessary recomputation, and overly broad scans that add cost without benefit.
- Clarity: flag deep nesting, weak naming, dead code, redundant comments, and indirection that no longer earns its keep.

Only elevate simplification suggestions when they materially improve maintainability, correctness, or cost.

## Review workflow

1. **Identify languages and changed surfaces** in the diff.
2. **Read enough nearby context** to understand intent, requirements, and test strategy.
3. **Load applicable anti-pattern references** from the nearest language owner.
4. **Scan each changed file** against the relevant anti-pattern reference.
5. **Cross-check the review lenses** for functionality, security, performance, tests, and maintainability.
6. **Self-question each finding**: Is this really wrong, or am I misunderstanding the context?
7. **Apply escalation rules** for repeated violations.
8. **Group findings** by severity: `Critical` -> `Major` -> `Minor` -> `Nit` -> `Notes`.
9. **Include file path and line reference** for every finding.
10. **Suggest a concrete fix** for each finding.
11. **Summarize** total finding count per severity at the end.

## Delegation

Stay with `internal-review-code` when the main need is defect-first review across mixed Python, Bash, Terraform, Java, or Node.js changes.

- Add `mattpocock-code-review` when the user explicitly asks for a two-axis Standards + Spec parallel review.
- Add `internal-terraform` when the review is primarily about Terraform resource modeling, module interfaces, or drift-safe HCL changes.
- Add `antigravity-golang-pro` when the review is primarily about Go concurrency, service design, or Go performance behavior.
- Add `awesome-copilot-codeql` when the review is primarily about CodeQL workflow setup or SARIF handling.
- Add `awesome-copilot-secret-scanning` when the review is primarily about GitHub-native secret scanning or push protection.
- Add language or domain specialists only when they materially improve the finding quality.

## Validation

- Verify every finding references a real file path and line from the diff.
- Verify severity assignments match the anti-pattern reference rules.
- Verify escalation rules are applied for repeated violations.
- Verify cross-language checks are applied regardless of primary language.
- Use `superpowers-verification-before-completion` before claiming there are no findings, the review is complete, or the change is merge-ready.
