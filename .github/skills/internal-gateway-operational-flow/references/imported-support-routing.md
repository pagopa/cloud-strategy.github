# Imported Support Routing

Use this reference when staged gateway work needs imported Matt Pocock skills as
conditional support. This file does not make imported skills mandatory engines.
Repository-owned policy, scoped instructions, and gateway phase contracts win
over imported workflow text.

## Routing Principles

- Load imported support only after the gateway phase is selected.
- Prefer internal owners when an internal skill already owns the local contract.
- Treat imported skills as lenses or workflow discipline, not as new gateway
  lanes.
- Do not run skills that assume `CONTEXT.md`, `CONTEXT-MAP.md`, `docs/adr/`, or
  `docs/agents/` unless those structures exist or the user explicitly asks to
  adopt them.
- Do not edit imported upstream assets in place for repository-specific behavior
  unless the sync override workflow explicitly approves and registers the fork.

## Active Support

| Skill | Gateway phase | Use when | Guardrail |
| --- | --- | --- | --- |
| `grill-me` | `plan`, `full-cycle` | The user asks for grilling, real ambiguity remains, or a non-trivial retained plan is being created, reformulated, or validated. | Inspect repository evidence first and use the local bulk-question override before one-at-a-time follow-up. |
| `mattpocock-zoom-out` | `plan`, `review` | A task crosses wrappers, skills, runtime projections, scripts, or sync boundaries and needs a higher-level map before deciding or reviewing. | Use repository evidence and local docs as the domain source; do not require `CONTEXT.md` or ADRs. |
| `mattpocock-diagnose` | `execute`, `review` | A failing script, validator, test, refresh, or performance signal needs a disciplined feedback-loop diagnosis. | Use it for real break/fix work. It complements `superpowers-systematic-debugging`; it does not replace validation evidence. |

## Situational Support

| Skill | Gateway phase | Use when | Guardrail |
| --- | --- | --- | --- |
| `mattpocock-improve-codebase-architecture` | `plan`, `review` | Wrapper, skill, projection, or catalog structure shows real architectural friction and needs a targeted deepening lens. | Start with `internal-systems-review` for repo-local fit. Do not create `CONTEXT.md` or ADRs as a side effect. |
| `mattpocock-tdd` | `execute` | Executable helpers, validators, or scripts need public-interface-oriented test-first work and the seam is meaningful. | Do not force it onto Markdown, prompt, agent, skill, or instruction authoring with no executable contract. |
| `mattpocock-caveman` | Support only | A long sync, review, or governance narrative needs compression after blockers, risks, and validation evidence are explicit. | Never use it as primary reasoning, planning, review, or evidence gathering. |

## Dormant Support

| Skill | Default gateway route | Use only when |
| --- | --- | --- |
| `mattpocock-grill-with-docs` | None | The user explicitly adopts glossary or ADR discipline for this repository, or the relevant `CONTEXT.md` and `docs/adr/` structures already exist and are in scope. |
| `mattpocock-setup-matt-pocock-skills` | None | A deliberate sync-governance decision chooses Matt Pocock setup conventions for a consumer repository or a future repository layer. |

## Extraction Decision

No new internal skill is needed for the current gateway integration. Existing
internal owners already capture the useful local behavior:

- `internal-gateway-operational-flow` owns staged gateway routing.
- `internal-gateway-critical-master` owns pressure testing.
- `internal-systems-review` owns systems-level review and architecture fit.
- `internal-ddd` owns justified domain-modeling depth when domain pressure is
  real.
- `superpowers-systematic-debugging` and `superpowers-test-driven-development`
  own stricter execution gates for debugging and TDD.

Keep the low-fit imported skills as dormant catalog depth unless sync
maintenance cost or trigger overlap becomes a real problem. If that happens,
route the retire or extract decision through the source-side sync owner.

## Validation

- The selected gateway phase remains explicit before any imported support is
  loaded.
- Imported support is conditional and never listed as a mandatory engine.
- Dormant docs and setup skills are not used unless their supporting structures
  or an explicit user decision exist.
- Any future removal or replacement of managed Matt Pocock assets goes through
  the catalog sync owner, not ad hoc deletion from a gateway workflow.
