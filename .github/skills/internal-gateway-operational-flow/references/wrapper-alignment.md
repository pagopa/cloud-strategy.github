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
| `grill-me` | Gate 0 support for every non-`execute` operational-flow entrypoint | The operational-flow skill has enough evidence to classify request, target path, owner, anti-scope, and nearest validation, and the selected entrypoint is not direct `execute`. | Inspect repository evidence first, run Gate 0 after the minimum evidence pass, keep Gate 0 status and phase blocking owned by `internal-gateway-operational-flow`, use `plan-only (clarify-first)` before planning output, block `apply-plan`, `review`, and planning output while `grill-me required` remains active, require a user answer or accepted defaults plus a closure/proceed signal before `grill-me satisfied`, and rerun Gate 0 on request, context, or environment change. |
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

- Planning, review, and retained-plan application always start `grill-me`
  through Gate 0 after the minimum evidence pass. Direct `execute` is the
  automatic Gate 0 exception unless the user asks for `grill-me` or the lane
  changes away from `execute`.
- Treat planning as `plan-only (clarify-first)` until the user closes the active
  `grill-me` loop.
- Rich prompts, concrete tasks, mechanical tasks, retained-plan approval, fully
  recoverable repository evidence, and pre-start signals do not waive Gate 0
  when Gate 0 applies. For mechanical work covered by Gate 0, ask a minimal,
  clear, and concise question set instead of skipping `grill-me`.
- The agent may recommend ending a `grill-me` loop when the answers are
  coherent, but the loop closes only after a user closure signal such as "ok",
  "chiudi", "va bene", "vai", "procedi", accepted defaults, or an equivalent
  proceed instruction.
- `apply-plan`, `review`, and planning output stay blocked while the Gate 0
  result is `grill-me required`, including request-changing realignment.
- Restart Gate 0 before continuing if request, context, target path,
  environment, tool output, dependency state, validation, or dirty worktree
  ownership changes.
- Retained-plan execution belongs to `internal-executing-plans` after
  `apply-plan` is selected.
- Non-trivial or governance-sensitive retained-plan authoring belongs to
  `internal-writing-plans`, including the detailed critical-before-plan
  requirement that uses `internal-gateway-critical-master`.
- Failure diagnosis belongs to `internal-debugging`.
- Test-first delivery belongs to `internal-tdd`.
- Performance work belongs to `internal-performance-optimization`.
- Code defect review belongs to `internal-code-review`.
- Architecture, workflow, cross-cutting impact, operational fit, and blind spots
  belong to `internal-high-level-review`.
- Compression support such as `mattpocock-caveman` stays support-only after
  blockers, risks, and validation evidence are explicit.
- The `Mini Decision Brief` introduced by `SKILL.md` remains a chat projection.
  It does not replace a retained plan, is not catalog material, and Copilot
  wrappers must not expose it as a canonical artifact.

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
