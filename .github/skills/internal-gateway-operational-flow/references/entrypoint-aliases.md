# Entrypoint Aliases

Use this reference when a user prompt uses wording that matches an entrypoint but does not name it exactly.

## Alias index

| Entrypoint | Aliases |
| --- | --- |
| `full-cycle` | `end-to-end`, `e2e`, `start-to-finish`, `complete-workflow`, `from-scratch` |
| `define-first` | `idea-first`, `refine-first`, `shape-idea`, `ideation`, `concept-first`, `requirements-first`, `discovery-first` |
| `plan-only` | `plan-first`, `write-plan`, `create-plan`, `decision-brief`, `retained-plan-only` |
| `apply-plan` | `run-plan`, `execute-plan`, `implement-plan`, `run-approved-plan` |
| `review` | `check-this`, `audit`, `code-review`, `validate`, `defect-review`, `merge-readiness`, `review-changes` |
| `mode-explicit` | `direct-mode`, `explicit-phase`, `go-to-plan`, `switch-to-execute`, `run-define`, `run-plan`, `run-execute`, `run-review` |

## Notes

- Prompt-specific intent wins. If the user says `fix this` or `implement this` and the target state is already concrete, treat it as `mode-explicit` with phase `execute` rather than forcing a heavier entrypoint.
- If the user says `critique this plan` or `challenge this decision`, treat it as `mode-explicit` with phase `critical` and hand off to `internal-gateway-critical-master`.
- These aliases are English-only. Do not add Italian or other language variants.
- Legacy spellings such as `clarify-first` are not included and should not be used.
