# Wrapper Alignment

Use this reference when updating the Copilot agent wrappers, README projection, or contract tests after operational-flow changes.

## Wrapper Roles

| Wrapper | Mode | Mandatory engines |
| --- | --- | --- |
| `internal-planning-leader` | `plan` | `internal-agent-operational-flow`, `internal-agent-support-lane-change-engine`, `internal-agent-support-next-step` |
| `internal-delivery-operator` | `execute` | `internal-agent-operational-flow`, `internal-agent-support-lane-change-engine`, `internal-agent-support-next-step` |
| `internal-review-guard` | `review` | `internal-agent-operational-flow`, `internal-agent-support-lane-change-engine`, `internal-agent-support-next-step`, `internal-code-review` |
| `internal-critical-master` | critical challenge | `internal-agent-critical-master`, `internal-agent-support-lane-change-engine`, `internal-agent-support-next-step` |

The wrappers keep route wording, tools, `disable-model-invocation: true`, `agents: []`, handoff buttons, boundary summary, and output shape. They should not repeat long mode tables or workflow maps from this skill bundle.

## Handoff Rules

- Keep every Copilot wrapper handoff `send: false`.
- Keep handoff labels user-facing with `Next step:` or `Next action:`.
- Keep text next-step packages in responses because non-Copilot runtimes may ignore wrapper frontmatter.
- Do not use wrapper handoffs as hidden dispatch.

## Sync Boundary

The repo-only sync agents remain outside the compressed operational model. They keep their local sync engines and may continue using `internal-agent-support-lane-change-engine` when the sync lane no longer fits.

## README Projection

`.github/agents/README.md` may document wrapper usage and ASCII flows, but the semantic owner for plan/execute/review behavior is `internal-agent-operational-flow`. Keep README examples aligned with this bundle instead of adding a second operational contract.
