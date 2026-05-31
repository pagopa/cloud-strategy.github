# Wrapper Alignment

Use this reference when updating Copilot agent wrappers, README projection, or
contract tests after operational-flow changes.

## Wrapper Roles

The active Copilot UX uses one thin wrapper per gateway skill.

| Wrapper | Core skill | Route |
| --- | --- | --- |
| `internal-gateway-operational-flow` | `internal-gateway-operational-flow` | `define`, `full-cycle`, `plan-only`, `apply-plan`, `review`, and explicit `define`, `plan`, `execute`, or `review` phases. |
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
| `grill-me` | Gate 0 support for every non-`execute` operational-flow entrypoint inside `define` | The operational-flow skill has enough evidence to classify request, target path, owner, anti-scope, and nearest validation, and the selected entrypoint is not direct `execute`. `apply-plan` and `review` use the same visible define pre-start gate. | Follow `gate-0-protocol.md` for status, closure, blocking, and realignment; wrapper docs must not restate the full Gate 0 protocol. |
| `superpowers-brainstorming` | Conditional `define` support | Creative, product, UX, architecture, or design-ambiguous work needs option exploration and design approval before planning. | Keep `grill-me` as the Gate 0 pillar; use brainstorming only after the minimum evidence pass shows options can change the plan; skip it for deterministic repository-owned maintenance of prompt, skill, agent, instruction, or Markdown assets when target state and validation are concrete. |
| `mattpocock-caveman` | Support only | A long sync, review, or governance report needs compression after blockers, risks, and validation evidence are explicit. | Never use it as primary reasoning, planning, review, or evidence gathering. |

Internal replacements:

- Failure diagnosis belongs to `internal-debugging`.
- Test-first delivery belongs to `internal-tdd`.
- Performance work belongs to `internal-performance-optimization`.
- Architecture, locality, leverage, cross-boundary review, cross-cutting impact, higher-level code
  orientation, module maps, caller maps, blind spots, and domain-vocabulary explanations
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

Support selection belongs in the gateway skills, not in wrapper skill-list sections.

- Gate 0 closure, blocking, non-waiver, phase-transition, and realignment rules live exclusively in `gate-0-protocol.md`. Wrappers, READMEs, and tests reference that file instead of restating the protocol.
- In wrapper projection terms, the loop closes only after a user closure signal.
- Restart Gate 0 before continuing if request, context, target path, environment, tool output, dependency state, validation, or dirty worktree ownership changes.
- `superpowers-brainstorming` is optional support inside `define` only when option exploration is the real work.
- Retained-plan execution belongs to `internal-executing-plans` after `apply-plan` is selected.
- Retained-plan authoring belongs to `internal-writing-plans`.
- Compression support stays support-only after blockers, risks, and validation evidence are explicit.
- The `Mini Decision Brief` introduced by `SKILL.md` remains a chat projection. It does not replace a retained plan and is not a canonical artifact.

## Handoff Rules

- Keep every Copilot wrapper handoff `send: false`.
- Keep handoff labels user-facing with `Next step:` or `Next action:`.
- Keep text next-step packages in responses because non-Copilot runtimes may ignore wrapper frontmatter.
- For non-terminal `execute`, `apply-plan`, or `review` stops, pair the text
  next-step package with explicit `State` and `Continuation`; add `User action
  required` when the workflow is waiting on the user or an external
  prerequisite.
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
