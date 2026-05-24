# Wrapper Alignment

Use this reference when updating Copilot agent wrappers, README projection, or
contract tests after operational-flow changes.

## Wrapper Roles

The active Copilot UX uses one thin wrapper per gateway skill.

| Wrapper | Core skill | Route |
| --- | --- | --- |
| `internal-gateway-operational-flow` | `internal-gateway-operational-flow` | `full-cycle`, `plan-only`, `apply-plan`, `review`, and explicit `plan`, `execute`, or `review` phases. |
| `internal-gateway-critical-master` | `internal-gateway-critical-master` | Critical challenge, pre-mortem, hidden-assumption tests, failure modes, and reframing before action. |
| `internal-gateway-simple-task` | `internal-gateway-simple-task` | Concrete low-to-medium-risk answer, edit, diagnose, validate, or escalate tasks that do not need staged workflow. |

Each active wrapper keeps route wording, tool scope, `disable-model-invocation:
true`, `agents: []`, manual handoff buttons, boundary summary, and output shape.
Each active wrapper has exactly one `## Core Skill` and must not re-list support
catalogs or long workflow tables from skill files.

The deprecated compatibility wrappers `internal-planning-leader`,
`internal-delivery-operator`, `internal-review-guard`, and
`internal-critical-master` remain only for the deprecation window. They are not
canonical routing owners and should stay non-invocable.

## Imported Support

Keep imported support conditional, never a mandatory engine. Use imported
support as a lens, compression aid, or conversation discipline, not as a new
gateway lane. Internal owners win when they already cover the local contract.

| Support | Gateway phase | Use when | Guardrail |
| --- | --- | --- | --- |
| `grill-me` | Gate 0 support for `plan`, `full-cycle`, and governance-sensitive pre-start delivery | The user asks for grilling, signals they are done providing context before action, governance-sensitive planning or delivery still has unresolved user-only decisions, real ambiguity remains, or a non-trivial retained plan needs question pressure before approval. | Inspect repository evidence first, run Gate 0 after the minimum evidence pass, keep Gate 0 status and phase blocking owned by `internal-gateway-operational-flow`, use `plan-only (clarify-first)` for planning decisions that can change scope, owner, or validation, block `execute` or `apply-plan` while `grill-me required` remains active, and rerun Gate 0 on request-changing realignment before one-at-a-time follow-up. |
| `mattpocock-caveman` | Support only | A long sync, review, or governance report needs compression after blockers, risks, and validation evidence are explicit. | Never use it as primary reasoning, planning, review, or evidence gathering. |

Internal replacements:

- Failure diagnosis belongs to `internal-debugging`.
- Test-first delivery belongs to `internal-tdd`.
- Performance work belongs to `internal-performance-optimization`.
- Architecture, locality, leverage, cross-boundary review, higher-level code
  orientation, module maps, caller maps, and domain-vocabulary explanations
  belong to `internal-high-level-review`.
- Code defect review belongs to `internal-code-review`.
- Imported docs and setup conventions stay outside default gateway routing
  unless a future sync-governance decision deliberately changes the managed
  catalog.

## Future Security Lens

`internal-security-review` is unavailable until a promoted skill with that name
exists and the review wrapper optional-support map is updated in the same
change. Until then, do not list it as an active owner or wrapper support skill.
State security-specific gaps and route them through the closest existing owner.

## Support Posture

Support selection belongs in the gateway skills, not in wrapper skill-list
sections.

- Planning and pre-start support include `grill-me` only when the
  operational-flow skill selects it through Gate 0 after the minimum evidence
  pass.
- If governance-sensitive planning still has unresolved user-only decisions,
  treat the lane as `plan-only (clarify-first)` until Gate 0 resolves those
  choices.
- `execute` and `apply-plan` stay blocked while the Gate 0 result is
  `grill-me required`, including request-changing realignment.
- Retained-plan execution belongs to `internal-executing-plans` after
  `apply-plan` is selected.
- Failure diagnosis belongs to `internal-debugging`.
- Test-first delivery belongs to `internal-tdd`.
- Performance work belongs to `internal-performance-optimization`.
- Code defect review belongs to `internal-code-review`.
- Architecture, workflow, cross-cutting impact, operational fit, and blind spots
  belong to `internal-high-level-review`.
- Compression support such as `mattpocock-caveman` stays support-only after
  blockers, risks, and validation evidence are explicit.

## Handoff Rules

- Keep every Copilot wrapper handoff `send: false`.
- Keep handoff labels user-facing with `Next step:` or `Next action:`.
- Keep text next-step packages in responses because non-Copilot runtimes may ignore wrapper frontmatter.
- Do not use wrapper handoffs as hidden dispatch.
- Gateway wrappers may expose manual handoffs to the other gateway wrappers when
  the current lane no longer fits.
- Handoff buttons are convenience UX only; the text next-step package remains
  the portable contract.

## Sync Boundary

The repo-only sync agents remain outside the compressed operational model. They
keep their local sync engines and may continue using
`internal-agent-support-lane-change-engine` when the sync lane no longer fits.

## README Projection

`.github/agents/README.md` may document wrapper usage and ASCII flows, but the
semantic owners are the three gateway skills. Keep README examples aligned with
this bundle instead of adding a second operational contract.
