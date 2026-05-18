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

`internal-review-guard` keeps `internal-code-review` mandatory for defect-first review. It lists `internal-systems-review` as optional support when the review surface is architecture, workflow, cross-cutting impact, operational fit, or blind spots. Do not list `internal-security-review` in the wrapper until the promotion gate creates that skill.

Imported support stays optional and never becomes a mandatory engine. Gateway
wrappers should list only the approved imported support that improves route UX:
`grill-me` in planning. Delivery and review wrappers use `internal-debugging`,
`internal-tdd`, `internal-performance-optimization`, `internal-code-review`, and
`internal-systems-review` for local diagnosis, test-first, performance, code
defect, and architecture evidence. Keep compression support in sync or
reporting owners after blockers, risks, and validation evidence are already
explicit.

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
