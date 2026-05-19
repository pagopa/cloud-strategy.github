# Wrapper Alignment

Use this reference when updating the Copilot agent wrappers, README projection, or contract tests after operational-flow changes.

## Wrapper Roles

| Wrapper | Mode | Mandatory engines |
| --- | --- | --- |
| `internal-planning-leader` | `plan` phase and `plan-only` projection | `internal-gateway-operational-flow`, `internal-agent-support-lane-change-engine`, `internal-agent-support-next-step` |
| `internal-delivery-operator` | `execute` phase and clear `apply-plan` work | `internal-gateway-operational-flow`, `internal-agent-support-lane-change-engine`, `internal-agent-support-next-step` |
| `internal-review-guard` | `review` | `internal-gateway-operational-flow`, `internal-agent-support-lane-change-engine`, `internal-agent-support-next-step`, `internal-code-review` |
| `internal-critical-master` | critical challenge | `internal-gateway-critical-master`, `internal-agent-support-lane-change-engine`, `internal-agent-support-next-step` |

The wrappers keep route wording, tools, `disable-model-invocation: true`, `agents: []`, handoff buttons, boundary summary, and output shape. They should not repeat long mode tables or workflow maps from this skill bundle.

`internal-review-guard` keeps `internal-code-review` mandatory for defect-first review. It lists `internal-systems-review` as optional support when the review surface is architecture, workflow, cross-cutting impact, operational fit, or blind spots.

Imported support stays optional and never becomes a mandatory engine. Gateway
wrappers should list only the approved imported support that improves route UX:
`grill-me` in planning. Delivery and review wrappers use `internal-debugging`,
`internal-tdd`, `internal-performance-optimization`, `internal-code-review`, and
`internal-systems-review` for local diagnosis, test-first, performance, code
defect, and architecture evidence. Keep compression support in sync or
reporting owners after blockers, risks, and validation evidence are already
explicit.

## Imported Support

Keep imported support conditional, never a mandatory engine. Use imported
support as a lens, compression aid, or conversation discipline, not as a new
gateway lane. Internal owners win when they already cover the local contract.

| Support | Gateway phase | Use when | Guardrail |
| --- | --- | --- | --- |
| `grill-me` | `plan`, `full-cycle` | The user asks for grilling, real ambiguity remains, or a non-trivial retained plan needs question pressure before approval. | Inspect repository evidence first and use the local bulk-question override before one-at-a-time follow-up. |
| `mattpocock-caveman` | Support only | A long sync, review, or governance report needs compression after blockers, risks, and validation evidence are explicit. | Never use it as primary reasoning, planning, review, or evidence gathering. |

Internal replacements:

- Failure diagnosis belongs to `internal-debugging`.
- Test-first delivery belongs to `internal-tdd`.
- Performance work belongs to `internal-performance-optimization`.
- Architecture, locality, leverage, cross-boundary review, higher-level code
  orientation, module maps, caller maps, and domain-vocabulary explanations
  belong to `internal-systems-review`.
- Code defect review belongs to `internal-code-review`.
- Imported docs and setup conventions stay outside default gateway routing
  unless a future sync-governance decision deliberately changes the managed
  catalog.

## Future Security Lens

`internal-security-review` is unavailable until a promoted skill with that name
exists and the review wrapper optional-support map is updated in the same
change. Until then, do not list it as an active owner or wrapper support skill.
State security-specific gaps and route them through the closest existing owner.

## Optional Support Map

Keep this map aligned with each wrapper's `## Optional Support Skills` section.

| Wrapper | Optional support skills |
| --- | --- |
| `internal-planning-leader` | `internal-writing-plans`, `internal-executing-plans`, `internal-agent-creator`, `internal-copilot-audit`, `internal-copilot-docs-research`, `internal-systems-review`, `grill-me` |
| `internal-delivery-operator` | `superpowers-verification-before-completion`, `superpowers-using-git-worktrees`, `internal-executing-plans`, `internal-debugging`, `internal-tdd`, `internal-performance-optimization`, `internal-lesson-codification`, `internal-agent-creator` |
| `internal-review-guard` | `superpowers-verification-before-completion`, `internal-systems-review`, `internal-debugging`, `internal-performance-optimization`, `internal-agent-creator`, `awesome-copilot-codeql`, `awesome-copilot-secret-scanning` |
| `internal-critical-master` | `superpowers-brainstorming`, `internal-agent-creator` |

## Handoff Rules

- Keep every Copilot wrapper handoff `send: false`.
- Keep handoff labels user-facing with `Next step:` or `Next action:`.
- Keep text next-step packages in responses because non-Copilot runtimes may ignore wrapper frontmatter.
- Do not use wrapper handoffs as hidden dispatch.
- Critical wrappers may expose more than reformulation as manual handoff options when the outcome is delivery or evidence review.
- Skill-only outcomes such as `de-escalate-to-simple` should be named in the text next-step package because there is no simple wrapper agent.

## Sync Boundary

The repo-only sync agents remain outside the compressed operational model. They keep their local sync engines and may continue using `internal-agent-support-lane-change-engine` when the sync lane no longer fits.

## README Projection

`.github/agents/README.md` may document wrapper usage and ASCII flows, but the semantic owner for plan/execute/review behavior is `internal-gateway-operational-flow`. Keep README examples aligned with this bundle instead of adding a second operational contract.
