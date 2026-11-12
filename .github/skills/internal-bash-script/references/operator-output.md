# Bash Operator Output Guidance

Load this reference when a Bash or POSIX shell entrypoint reports multi-step work, diagnostics, or results to an operator.

## Ownership and output flow

Keep argument parsing, selector resolution, execution and scheduling, lifecycle events, result collection, human rendering, machine-readable output, and explicitly requested artifacts as distinct responsibilities. The shell entrypoint owns its output contract. The caller may forward output or choose a supported format; it must not reinterpret the script's selectors, statuses, schemas, or result meaning.

Execution must not depend on terminal visibility, color support, or the selected human-output projection. Keep machine-readable results plain and stable. Create files only when a caller explicitly requests them. Use the script's existing shell dialect and project-specific options; this reference adds no library or universal flag.

## Mutating operator workflow

Use this order for operator-visible mutations:

1. Show target context: account or environment, scope, and selected targets.
2. Present a non-mutating plan of intended changes and material risks.
3. When the chosen flow is interactive, request proportionate confirmation
	immediately after the plan, before execution or unrelated narration.
4. Execute only the authorized plan, recording command results per target.
5. Check final state against the intended effects with non-mutating reads.
6. Render a separate outcome report from the command and verification evidence.

For fixed bounded targets, a simple yes/no prompt with default no is appropriate;
decline or EOF must leave state unchanged. Choose stronger confirmation only
when risk warrants it. Preserve an established non-interactive authorization
contract; do not impose interactive defaults or typed phrases on every script.
If the target or plan materially changes, renew authorization before mutation.

Request acceptance is not proof of effect, and an error is not proof of no
effect. Record command acceptance/errors separately from verified effects,
newly created or partial state, and unverified state. Bound verification waits;
when state cannot be established, report it as unverified, not successful.
The final report must retain those distinctions and any evidence-based next step.

Keep selector loops and confirmation/control input separate from child stdin.
When a child may read stdin but needs no input, redirect it from `/dev/null`;
when it needs data, supply a separate explicit stream or descriptor. Do not let
children consume remaining selectors or prompt responses. Exercise this boundary
with a local stdin-consuming stub, not a live provider.

## Lifecycle and human logs

For each selected unit in a multi-step command, record `started` when it begins
and one terminal state when it ends: `passed`, `failed`, `warning`, or `skipped`.
Include the unit category and selector. Add `[n/N]` when position helps.
Use deliberately sparse emojis as phase/status cues paired with words, such as
`▶️ execution`, `✅ passed`, or `⚠️ unverified`. Prefer a cue at a phase boundary
or a material outcome; do not decorate every target line or repeat markers as
clutter. Plain state words keep dense per-unit logs readable.

For a long-running unit, write `heartbeat` only when it reports measured progress. Bound heartbeat frequency and output using project-specific choices. Keep a concise started event and terminal-state event for every selected unit, including failures and skips.

Human log markers pair any chosen emoji with its phase/status word. If the active output encoding cannot represent Unicode, print the word alone. Do not use ASCII art. `--no-color` and `NO_COLOR` disable ANSI styling only; they do not remove emoji or state words. Keep emoji out of machine-readable payloads and preserve existing stdout/stderr routing and quiet contracts.

A portable event can use `printf`:

```sh
printf '%s\n' '▶️ execution'
printf '%s\n' 'started · [1/3] cache/dev'
printf '%s\n' 'failed · [1/3] cache/dev · exit=1'
```

## Diagnostics and summaries

Choose diagnostic-count and raw-output-size limits for the project and apply them per unit. Bound diagnostic excerpts and captured raw output; show an omitted count or byte count when a limit is reached. Preserve every unit's status and every failure and skip in human and structured results even when diagnostic detail is bounded.

Omit unavailable fields rather than inventing values. Do not infer a cause that the command did not establish. Keep secrets out of logs and redact sensitive values before rendering. Provide an explicit project-owned option or result path for full detail; write a diagnostic artifact only when requested.

Finish with counts by state, failures grouped by category or selector, and a next action only when evidence supports a concrete, verifiable step. For example:

```text
summary: passed=2 failed=1 warning=0 skipped=1
failures: terraform/identity=2
next: rerun the failed selector with the owning tool's documented command
```

## Compact, quiet, and verbose output

Default human output should be compact without requiring a new flag. Show
shared context once, then use readable, unambiguous target names. Avoid repeated
UUIDs and full resource IDs; include them when needed to resolve ambiguity, in
relevant diagnostics, or on explicit verbose output. Compactness must not hide
material failures, partial effects, or unverified state.

A new, high-volume terminal interface may consider `--compact` as a terminal-only projection when measured output volume justifies it. Compact output preserves each unit's lifecycle state and does not change selectors, work units, scheduling, concurrency, exit codes, machine-readable output, CI formats, Markdown, or artifacts.

Keep `--quiet` separate: it may suppress routine narration, but it must retain lifecycle states, failure and skip records, and the final summary. Use `--verbose` or another explicit project-owned option to request additional diagnostic detail. These output choices do not select different work or alter machine-readable results.

Preserve an existing `--format compact` option, payload, and consumers as a public interface. Do not rename it to `--compact` or change its meaning. When a real CI consumer exists and the script supports a CI format, choose that format explicitly before auto-detection. A terminal-only compact projection is not a CI-format substitution.

## Continuing after failures

Independent validation units should continue after a failure unless the operator selected an explicit, safe `--fail-fast` policy. Choose fail-fast behavior for mutating or unsafe work from its actual side effects and recovery properties. Do not add a universal fail-fast default or flag. Preserve all failures and skips collected before execution stops.
