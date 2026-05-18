# Imported Support Routing

Use this reference only after the gateway phase is selected. Internal owners win
when they already cover the local contract.

## Principles

- Keep imported support conditional, never a mandatory engine.
- Use imported support as a lens, compression aid, or conversation discipline,
  not as a new gateway lane.
- Do not adopt `CONTEXT.md`, ADR, glossary, or setup conventions as repository
  policy through an imported support skill.
- Do not edit imported upstream assets in place for repository behavior unless
  the sync override workflow explicitly approves and registers the fork.

## Approved Support

| Support | Gateway phase | Use when | Guardrail |
| --- | --- | --- | --- |
| `grill-me` | `plan`, `full-cycle` | The user asks for grilling, real ambiguity remains, or a non-trivial retained plan needs question pressure before approval. | Inspect repository evidence first and use the local bulk-question override before one-at-a-time follow-up. |
| `mattpocock-zoom-out` | `plan`, `review` | The work crosses wrappers, skills, projections, scripts, sync boundaries, or generated catalog artifacts and needs a higher-level map. | Use repository evidence and local docs; keep review findings owned by `internal-systems-review`. |
| `mattpocock-caveman` | Support only | A long sync, review, or governance report needs compression after blockers, risks, and validation evidence are explicit. | Never use it as primary reasoning, planning, review, or evidence gathering. |

## Internal Replacements

- Failure diagnosis now belongs to `internal-debugging`.
- Test-first delivery now belongs to `internal-tdd`.
- Performance work now belongs to `internal-performance-optimization`.
- Architecture, locality, leverage, and cross-boundary review now belong to
  `internal-systems-review`.
- Imported docs and setup conventions stay outside default gateway routing unless
  a future sync-governance decision deliberately changes the managed catalog.

## Validation

- The selected gateway phase is explicit before imported support is loaded.
- Internal owners remain the route for debugging, TDD, performance, and systems
  review.
- Imported support remains conditional and does not reintroduce catalog decision
  matrices into the gateway.
