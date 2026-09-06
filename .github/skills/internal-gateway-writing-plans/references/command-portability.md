# Command Portability

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

The executor owns the single mechanical plan validator and normative Execution
Manifest v3 parser; its `preflight` is the sole readiness authority. The
writer bundle owns a read-only structural producer check,
`scripts/check_plan_structure.py`, that catches producer shape defects while
authoring; it imports no executor code, decides no execution semantics, and
never replaces the executor preflight. A legacy `## Execution Contract`
requires writer-side regeneration and is not a current schema exemption.

Before handoff, run the structural check
`python3 <writer-bundle>/scripts/check_plan_structure.py <plan> --format compact`
first, then resolve the executor's loaded physical bundle and run:

`bash <physical-executor-bundle>/scripts/run.sh preflight <plan> --format compact`

Confirm exit code zero and compact payload `status: passed` with zero
blocking findings for both. Run both gates against the exact final plan
bytes; a ready or handoff claim without those fresh results is invalid. The
plan uses the exact `## Execution Manifest` heading, one fenced JSON code
block in that section, and the exact canonical `handoff.requires` strings.
Only explicitly `legacy/imported` material may use reconstruction, with
refreshed Manifest v3 approval. Do not downgrade an automatable obligation to
narrative or manual evidence to make either gate pass.
