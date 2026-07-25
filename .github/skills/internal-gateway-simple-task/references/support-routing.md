# Simple Task Support Methods

Use this reference when the next move is still noisy after lane selection. Keep the guidance generic and evidence-first.

## Core Rule

Choose the first real blocker, evidence gap, or validation need. Do not preload methods because they might become useful later.

## Evidence Order

Prefer signals in this order:

1. Explicit user direction.
2. File type, path family, runtime, framework, command, or schema surface.
3. Reproduced failure loop or validation output.
4. Domain or platform evidence in the prompt or files.
5. Existing nearby patterns.

If no strong signal exists, stay local or stop with reason.

## Method Buckets

| Signal | Method posture | Boundary |
| --- | --- | --- |
| Missing intent, target path, input data, local context, or one blocker prevents starting | Ask one compact clarification block. | Stop if the answer would change scope, validation, cost, or risk. |
| Bug, failing test, failing build, drift, or unexpected output | Reproduce first, then debug by falsifiable hypothesis. | Do not patch from correlation alone. |
| Executable behavior change | Load `internal-tdd` to classify `mandatory`, `recommended`, or `not suitable` routing when a meaningful executable or evaluable seam exists. | Do not force it onto pure prose or governance wording with no executable seam. |
| Existing diff needs findings or merge-readiness | Stop with reason because the work is no longer simple execution. | Do not turn simple validation into review. |
| Orientation or unfamiliar code mapping | Stay descriptive and bounded. | Do not turn orientation into findings without concrete evidence. |
| Architecture, workflow, cross-cutting impact, or blind spots dominate | Stop with reason. | Do not keep editing while the boundary is unsettled. |
| Performance is the measured concern | Compare baseline and after evidence from the same measurement class. | Do not optimize from intuition alone. |
| Strong completion or passing claim | Run the final evidence gate with fresh validation evidence. | Do not rely on stale output or intent. |

## Claim Discipline

Use these evidence gates before strong claims:

| Claim | Evidence gate |
| --- | --- |
| `fixed` | Mark `validation` done by re-running the original failing loop, or state the blocker. |
| `covered` | Mark `execution` and `validation` done against the failing-then-passing behavior seam, or state why it could not be run. |
| `performance-improved` | Compare baseline and after evidence from the same measurement class. |
| `validator-passes` | Mark `validation` done by re-running the validator and reading fresh output before claiming success. |
| `completion`, `readiness`, `no-gap` | Mark `final-evidence` done only after all in-scope work is closed and the final evidence gate has fresh support. |

If the evidence gate would require broader staged work, stop with reason instead of over-claiming.

## Advisory Helpers

Run `scripts/resolve_simple_task.py gate` for compact operator text. Add `--format json` only when a tool or diagnostic flow needs the complete internal readiness record and Gate Evidence.

Run `scripts/resolve_simple_task.py claim` before strong status claims when the evidence requirements are the noisy part.

Run `scripts/suggest_support_skills.py` only when path or symptom signals exist and the next method still needs a deterministic hint.

`suggest_support_skills.py` emits machine-readable method labels (e.g. `governance-check`, `automation-check`, `config-check`) as shorthand for the row postures above; labels resolve to the nearest row by topic, not by exact wording.
