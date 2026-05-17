# Decision Brief

Use this template when a plan phase or next-step package needs a compact bridge
to execution, review, or critical challenge. The brief is a projection of the
decision, not a second canonical plan.

## Source Pattern

- Comparative source: `tmp/external-comparison/compound-engineering-plugin/plugins/compound-engineering/skills/ce-plan/references/plan-handoff.md`.
- Adopt the handoff shape only. Do not import the external runtime.

## Required Fields

| Field | Required content |
| --- | --- |
| Target state | The smallest complete outcome the next owner should deliver. |
| Anti-scope | Work the next owner must not add silently. |
| Suggested owner | Exact skill or agent owner already selected. |
| Evidence source | Plan path, request, diff, validator output, or reference that justifies the step. |
| Validation path | Command, review path, validator, or explicit validation gap. |
| Known risks | Residual risk, tradeoff, rollback note, or missing evidence. |
| Stop conditions | Conditions that must stop execution or trigger lane change. |

## Template

```text
Decision Brief
Target state: <outcome>
Anti-scope: <exclusions>
Suggested owner: <owner>
Evidence source: <path, diff, command, or request>
Validation path: <command, review, or gap>
Known risks: <risk or none>
Stop conditions: <stop rules>
```

## Missing Field Handling

- If a required field is missing before execution, state the gap visibly.
- If the gap is recoverable from repository files, inspect those files first.
- If the gap cannot be recovered safely, stop and ask for the missing decision.
- Do not fill missing owner, validation, or stop-condition fields from memory.
