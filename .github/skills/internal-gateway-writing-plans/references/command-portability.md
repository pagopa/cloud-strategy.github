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
Manifest v3 parser. Do not add a writer-local validator, second lifecycle, or
duplicate parser. A legacy `## Execution Contract` requires writer-side
regeneration and is not a current schema exemption.

Before handoff, resolve the executor's loaded physical bundle and run:

`bash <physical-executor-bundle>/scripts/run.sh preflight <plan> --format compact`

Confirm zero blocking findings. Only explicitly `legacy/imported` material may
use reconstruction, with refreshed Manifest v3 approval. Do not downgrade an
automatable obligation to narrative or manual evidence to make preflight pass.
