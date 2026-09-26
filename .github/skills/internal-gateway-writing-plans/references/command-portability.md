# Command Portability

## Command form

- Write every baseline, focused, and final validation command in directly
  executable native form. The recorded command is authoritative.
- Use an optional accelerator such as `graphify` only when it is the task's
  subject. Executor optimization must not change authoritative command meaning.
- Before handoff, probe every `validations[].command` executable or native path.
  Distinguish a missing command from validation failure. Exit 127 is a
  missing-tool condition: record an unambiguous native equivalent and its
  deviation, or retain the residual obligation and stop.
- Order discovery and availability checks before implementation and place
  environment-dependent verification after implementation.

## Validator ownership

The executor owns the single mechanical plan validator and normative Execution
Manifest v3 parser; its `preflight` is the sole readiness authority. The
writer bundle owns a read-only structural producer check,
`scripts/check_plan_structure.py`, that catches producer shape defects while
authoring; it imports no executor code, decides no execution semantics, and
never replaces the executor preflight. A legacy `## Execution Contract`
requires writer-side regeneration and is not a current schema exemption.

## Handoff gates

Before handoff, run both gates against the exact final plan bytes, in order:

```bash
python3 <writer-bundle>/scripts/check_plan_structure.py <plan> --format compact
bash <physical-executor-bundle>/scripts/run.sh preflight <plan> --format compact
```

Resolve the executor's loaded physical bundle before the second command.
Confirm exit code zero and compact payload `status: passed` with zero
blocking findings for both; a ready or handoff claim without those fresh
results is invalid. The plan uses the exact `## Execution Manifest` heading,
one fenced JSON code block in that section, and the exact canonical
`handoff.requires` strings.
Only explicitly `legacy/imported` material may use reconstruction, with
refreshed Manifest v3 approval. Do not downgrade an automatable obligation to
narrative or manual evidence to make either gate pass.

## Producer readiness

The writer owns producer-side readiness: it may prove the control inventory,
ordered task projection, manifest-only shape, and handoff ownership from the
plan it emits. These checks use parsed structure and do not import
`internal-gateway-execute-plans` or any executor-private module. Producer
readiness is writer-owned and structural. The executor bundle remains the only
owner of retained-plan mechanical preflight, loaded bundle resolution, state,
and execution validation.

Also run the structural check (the first command above) after every
manifest-affecting edit and before human review, and require zero blocking
findings. The check is writer-owned, structural, read-only, and
stdlib-only; it never replaces the executor preflight, and a divergence between
the two is a bundle defect to fix through the writer tests.
