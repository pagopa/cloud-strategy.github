# Internal Low-Cost Task Packet

The parent owns the packet. The worker must receive every required top-level
field before reading beyond the declared inputs or writing any artifact.

## Required fields

- `objective`: one bounded outcome, such as `Write the approved implementation plan.`
- `inputs`: exact files or resources to read, such as
  `tmp/.handoff/2026-08-07-skill-to-custom-subagent-codex-copilot.md`.
- `locked_decisions`: the native worker name and all decisions the worker must not
  revisit, including the required plan sections.
- `output_contract`: format, structure, and one exact destination.
- `write_scope`: allowed paths and forbidden paths.
- `validation`: exact commands and acceptance conditions.
- `limits`: output size and scope boundary.
- `escalate_on`: conditions that require the parent to decide or authorize.

## Complete packet example

```yaml
objective: Write the approved implementation plan.
inputs:
  - tmp/.handoff/2026-08-07-skill-to-custom-subagent-codex-copilot.md
locked_decisions:
  worker: internal-low-cost-copilot
  plan_sections: [Goal, Repository Preflight, Global Constraints, Tasks, Validation]
output_contract:
  format: markdown
  structure: [header, control inventory, execution contract, ordered tasks]
  destination: tmp/superpowers/plans/example.md
write_scope:
  allowed_paths: [tmp/superpowers/plans/example.md]
  forbidden_paths: [.github/skills, .github/agents, AGENTS.md]
validation:
  commands: [git diff --check]
  acceptance: [one retained plan exists, no other path changed]
limits:
  output_size: 12000 tokens
  scope: no implementation
escalate_on: [ambiguous requirement, conflicting evidence, new architecture decision, out-of-scope write]
```

## Worker result

The worker returns one structured result with these fields:

```yaml
status: completed | needs-parent | blocked
artifacts:
  - path: tmp/superpowers/plans/example.md
    description: The approved implementation plan.
validation:
  - command: git diff --check
    result: pass | fail
    evidence: concise reproducible result
unresolved:
  - item requiring parent action
scope:
  unexpected_changes: []
```

`needs-parent` is required before any write when a packet field is incomplete,
contradictory, or asks for a material decision. `blocked` is required for an
unsafe, denied, or unavailable authorized operation, or for a failure that the
packet does not permit the worker to repair. `completed` requires every
authorized artifact and declared validation to be complete; it does not turn
pending parent acceptance into worker evidence.
