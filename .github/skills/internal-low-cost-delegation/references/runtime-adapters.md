# Internal Low-Cost Runtime Adapters

These adapters describe platform prerequisites truthfully. They do not promise
that a runtime exposes the named worker or model.

## Approved differences

- Codex uses native `.codex/agents/internal-low-cost-codex.toml` with
  `gpt-5.6-luna`, `high`, and `workspace-write`.
- VS Code uses `GPT-5.6 Luna` in the profile. `high` is a model-picker and
  session prerequisite, not a portable `.agent.md` field.
- Copilot CLI must discover the runtime-reported Luna identifier, select a
  non-Auto model, and set session or settings `effortLevel: high`. Never infer
  a CLI slug from the Codex identifier.
- The Copilot route is `internal-low-cost-copilot`; the Codex route is
  `internal-low-cost-codex`.
- When the selected worker, model, effort, or invocation is unavailable,
  surface the parent fallback visibly. Do not silently substitute another
  route.

## Shared smoke tasks

Use the same bounded tasks on each runtime after its local prerequisites are
verified:

1. Research task: collect a declared set of evidence and write one research
   artifact to the packet's exact allowed path.
2. Plan task: write a plan whose decisions, section structure, destination,
   and validation are already locked by the parent packet.

The smoke task must prove the worker route, model and effort selection, packet
write confinement, artifact shape, and declared validation. Do not treat a
static profile parse as runtime acceptance.

## Required model-selection evidence

Record a timestamp, runtime, capability probe, availability result, selected
model, selected effort, suitability evidence, and fallback rationale. Include
the artifact path and a bounded diff or equivalent scope record for authorized
writes. If any required runtime field cannot be observed, keep the external
obligation unresolved and use the explicit parent fallback.
