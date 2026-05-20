# Audit Dispatch

Use this reference when a systems review needs a heavy audit that can be isolated
from the main assistant context. Dispatch is optional and traceable, not the
default path.

Keep audit dispatch user-visible. State why the independent audit is worth the extra cost, latency, or context isolation before using it.

## Source Patterns

- Comparative source: `tmp/external-comparison/gstack/ship/SKILL.md`.
- Comparative source: `tmp/external-comparison/gstack/subagent/`.
- Use the sources as inspiration only. Do not import gstack runtime behavior.

## Trigger Thresholds

Consider a subagent audit when any condition is true:

- More than 6 numbered plan files or more than 6 independent executable plan
  items need completion audit.
- More than 400 changed diff lines must be mapped to plan scope.
- More than 8 changed files cross more than one repository-owned asset family.
- The reviewer explicitly asks for an independent plan-vs-diff or scope-drift
  audit.

An explicit user override may request inline review instead.

If dispatch is used, tell the user which scope is being isolated and keep the result as a report, not a hidden decision engine.

## Payload To Subagent

Pass paths, not large copied content, whenever possible:

- Plan folder path and numbered plan file list.
- `done-*` file list, if any.
- Diff command or changed-file list.
- Relevant owner references, such as `plan-completion-audit.md`,
  `scope-drift.md`, and `review-lenses.md`.
- Anti-scope: no edits, no promotion decisions, no new owners.

## Output Contract

The subagent returns only a report:

- Typed findings using the severity and confidence vocabulary from
  `review-lenses.md`.
- `UNVERIFIABLE` gaps with the missing evidence named.
- Scope classification from `scope-drift.md`.
- Suggested route for each actionable item: `delivery`, `planning`, `critical`,
  or `defer`.
- A short list of files inspected.

## Stop Conditions

- The subagent must not edit canonical files.
- The subagent must not create or promote repository owners.
- The subagent must not decide that `internal-security-review` exists.
- The main assistant must spot-check at least one high or critical finding before
  using the report.
- If all subagent output is speculative, treat it as evidence gaps rather than
  findings.
