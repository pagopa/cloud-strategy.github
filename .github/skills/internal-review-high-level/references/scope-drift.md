# Scope Drift

Use this reference to compare declared intent with observed delivery before a
review, merge-readiness answer, or retained-plan completion report.

## Source Pattern

- Comparative source: `tmp/external-comparison/gstack/ship/SKILL.md` Step 8.2.
- Use the source as comparative evidence only. Do not import its runtime model.

## Inputs

- Declared intent from the user request, retained plan, or Decision Brief.
- Anti-scope and stop conditions from the plan or handoff.
- Observed deliverable from changed files, `git diff`, generated artifacts, and
  validator output.
- Explicit non-actions and blockers from the completion report.

## Classification

| Status | Criteria | Required action |
| --- | --- | --- |
| `ON_SCOPE` | The observed deliverable matches the target state and anti-scope. | Continue with normal validation. |
| `EXPANDED` | The diff adds extra behavior, files, owners, or policy beyond the approved scope. | Explain why it was required or route to planning. |
| `REDUCED` | The diff omits requested requirements, validators, or target files. | Route the missing part to delivery or record a blocker. |
| `DRIFTED` | The work changed direction enough that the delivered result no longer matches the approved plan. | Stop and route to planning or critical challenge. |

## Procedure

1. Write one sentence for the declared intent.
2. List the promised deliverables and explicit anti-scope.
3. List the observed deliverables from the diff and validation evidence.
4. Identify out-of-scope changes and missing requirements.
5. Assign one classification and cite the strongest evidence.
6. Route any `EXPANDED`, `REDUCED`, or `DRIFTED` result before declaring the work
   complete.

## Output Template

| Field | Evidence |
| --- | --- |
| Declared intent | `<source>` |
| Observed deliverable | `<diff or file evidence>` |
| Out-of-scope changes | `<none or list>` |
| Missing requirements | `<none or list>` |
| Classification | `ON_SCOPE` / `EXPANDED` / `REDUCED` / `DRIFTED` |
| Route | `<delivery, planning, critical, defer, or none>` |

## Guardrails

- Do not treat useful cleanup as in scope unless it is required by the plan or a
  validator failure.
- Do not hide reduced scope inside a success summary. Name the dropped item and
  why it was dropped.
- Security-specific drift must be routed through the closest existing owner
  until a specialized security owner is promoted.
