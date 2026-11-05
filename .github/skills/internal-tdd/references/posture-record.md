# Posture Record JSON

Use this shape when a posture record is stored as a file, and check it with
the script shipped in this bundle.

## Shape

The top-level fields appear exactly in this order:

- `posture`: `{value, change, reason}`. `change` is `behavior` or `refactor`
  and is required for `mandatory-test-first`.
- `boundary`: `{behavior, location}`.
- `checks`: a list of `{phase, command, result}`, one entry per phase. The
  phases are `red`, `characterization`, `focused`, and `broader`.
- `state`: one completion state from `SKILL.md`.
- `gaps`: a string naming missing evidence and the next action, or `none`.

Start each `result` with `passed`, `failed`, or `errored`. Any other value
counts as unobserved. A `failed` red result that names an import, syntax,
collection, or missing-command error counts as `errored`.

A broader check that fails outside the task scope may add
`"scope": "pre-existing"` after the failure is shown on the base state. Name
that failure in `gaps`. No other phase may set `scope`.

## Rules the checker enforces

- The state belongs to the posture; `blocked` fits any posture.
- A validated state has passing focused and broader checks, or a recorded
  pre-existing broader failure, and no unobserved check.
- `test-first-validated` for a `behavior` change has a failing red check
  before the focused check. For a `refactor` it has a passing
  characterization check instead.
- `blocked` has at least one failing or unobserved check besides red.
- `blocked`, `prototype-unverified`, and `validation-only` name their gaps.
  `validation-only` records its alternate validator as a focused check.

## Command

```bash
python3 <this-bundle>/scripts/check_posture_record.py <record.json>
```

The command prints JSON findings and exits `0` when the record is valid and
`1` otherwise.
