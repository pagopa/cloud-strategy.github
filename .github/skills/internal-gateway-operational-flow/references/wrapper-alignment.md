# Wrapper Alignment

Use this reference when updating Copilot agent wrappers or contract tests after operational-flow changes.

## Wrapper Roles

The active Copilot UX uses one thin wrapper per gateway skill.

| Wrapper | Core skill | Route |
| --- | --- | --- |
| `internal-gateway-idea-brainstorming` | `internal-gateway-idea-brainstorming` | Substantive idea definition, brainstorming, clarification, convergence, and validated handoff before planning. |
| `internal-gateway-operational-flow` | `internal-gateway-operational-flow` | `define`, `full-cycle`, `plan-only`, `apply-plan`, `review`, and explicit phases. |
| `internal-gateway-critical-master` | `internal-gateway-critical-master` | Critical challenge, pre-mortem, hidden-assumption tests, failure modes, and reframing. |
| `internal-gateway-simple-task` | `internal-gateway-simple-task` | Concrete low-to-medium-risk answer, edit, diagnose, validate, or escalate. |

Each wrapper keeps route wording, tool scope, `disable-model-invocation: true`, `agents: []`, manual handoff buttons, boundary summary, and output shape. Each has exactly one `## Core Skill` and must not re-list support catalogs or long workflow tables from skill files.

## Imported Support

Keep imported support conditional, never a mandatory engine. Internal owners win when they already cover the local contract.

| Support | Gateway phase | Use when | Guardrail |
| --- | --- | --- | --- |
| `grill-me` | Gate 0 support for every non-`execute` entrypoint inside `define` | The operational-flow skill has enough evidence to classify request, target path, owner, anti-scope, and nearest validation, and the selected entrypoint is not direct `execute`. | Follow `gate-0-protocol.md`; wrapper docs must not restate the full Gate 0 protocol. |
| `superpowers-brainstorming` | Conditional `define` support | Creative or design-ambiguous work needs option exploration before planning. | Keep `grill-me` as the Gate 0 pillar; skip for deterministic repository-owned maintenance. |
| `mattpocock-caveman` | Support only | A long sync, review, or governance report needs compression after blockers, risks, and validation evidence are explicit. | Never use as primary reasoning, planning, review, or evidence gathering. |

Internal replacements:

- Failure diagnosis belongs to `internal-debugging`.
- Test-first delivery belongs to `internal-tdd`.
- Performance work belongs to `internal-performance-optimization`.
- Architecture, cross-cutting impact, blind spots, and code orientation belong to `internal-high-level-review`.
- Code defect review belongs to `internal-code-review`.

## Future Security Lens

`internal-security-review` is unavailable until a promoted skill with that name exists and the review wrapper optional-support map is updated in the same change. Until then, do not list it as an active owner or wrapper support skill. State security-specific gaps and route them through the closest existing owner.

Use a promoted `internal-security-review` only after that skill exists.

## Support Posture

Support selection belongs in the gateway skills, not in wrapper skill-list sections.

- Gate 0 closure, blocking, non-waiver, phase-transition, and realignment rules live exclusively in `gate-0-protocol.md`. Wrappers, READMEs, and tests reference that file instead of restating the protocol.
- Restart Gate 0 before continuing if request, context, target path, environment, tool output, dependency state, validation, or dirty worktree ownership changes.
- In wrapper projection terms, the loop closes only after a user closure signal.
- `superpowers-brainstorming` is optional support inside `define` only when option exploration is the real work.
- Retained-plan execution belongs to `internal-executing-plans` after `apply-plan` is selected.
- Retained-plan authoring belongs to `internal-writing-plans`.
- Compression support stays support-only after blockers, risks, and validation evidence are explicit.
- The `Mini Decision Brief` introduced by `SKILL.md` remains a chat projection. It does not replace a retained plan and is not a canonical artifact.

## Handoff Rules

- Keep every Copilot wrapper handoff `send: false`.
- Keep handoff labels user-facing with `Next step:` or `Next action:`.
- Keep text next-step packages in responses because non-Copilot runtimes may ignore wrapper frontmatter.
- For non-terminal stops, pair the text next-step package with explicit `State` and `Continuation`; add `User action required` when waiting.
- Do not use wrapper handoffs as hidden dispatch.
- Gateway wrappers may expose manual handoffs to the other gateway wrappers when the current lane no longer fits.
- Handoff buttons are convenience only; the text next-step package remains the portable contract.

## Sync Boundary

The repo-only sync agents remain outside the compressed operational model. They keep their local sync engines and may continue using `internal-agent-support-lane-change-engine` when the sync lane no longer fits.

## README Projection

`.github/agents/README.md` may document wrapper usage and ASCII flows, but the semantic owners are the four gateway skills. Keep README examples aligned with this bundle instead of adding a second operational contract.
