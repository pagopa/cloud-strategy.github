# Bash Operator Output Guidance

Load this reference when a Bash or POSIX shell entrypoint reports multi-step work, diagnostics, or results to an operator.

## Ownership and output flow

Keep argument parsing, selector resolution, execution and scheduling, lifecycle events, result collection, human rendering, machine-readable output, and explicitly requested artifacts as distinct responsibilities. The shell entrypoint owns its output contract. The caller may forward output or choose a supported format; it must not reinterpret the script's selectors, statuses, schemas, or result meaning.

Execution must not depend on terminal visibility, color support, or the selected human-output projection. Keep machine-readable results plain and stable. Create files only when a caller explicitly requests them. Use the script's existing shell dialect and project-specific options; this reference adds no library or universal flag.

## Lifecycle and human logs

For each selected unit in a multi-step command, write `▶️ started` when it begins and one terminal state when it ends: `✅ passed`, `❌ failed`, `⚠️ warning`, or `⏭️ skipped`. Include the unit category and selector. Add `[n/N]` when position helps the operator follow progress.

For a long-running unit, write `⏱️ heartbeat` only when it reports measured progress. Bound heartbeat frequency and output using project-specific choices. Keep a concise started event and terminal-state event for every selected unit, including failures and skips.

Human log markers pair the accepted emoji with its state word. If the active output encoding cannot represent Unicode, print the state word alone. Do not use ASCII art. `--no-color` and `NO_COLOR` disable ANSI styling only; they do not remove emoji or state words.

A portable event can use `printf`:

```sh
printf '%s\n' '▶️ started · [1/3] terraform/identity'
printf '%s\n' '❌ failed · [1/3] terraform/identity · exit=1'
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

A new, high-volume terminal interface may consider `--compact` as a terminal-only projection when measured output volume justifies it. Compact output preserves each unit's lifecycle state and does not change selectors, work units, scheduling, concurrency, exit codes, machine-readable output, CI formats, Markdown, or artifacts.

Keep `--quiet` separate: it may suppress routine narration, but it must retain lifecycle states, failure and skip records, and the final summary. Use `--verbose` or another explicit project-owned option to request additional diagnostic detail. These output choices do not select different work or alter machine-readable results.

Preserve an existing `--format compact` option, payload, and consumers as a public interface. Do not rename it to `--compact` or change its meaning. When a real CI consumer exists and the script supports a CI format, choose that format explicitly before auto-detection. A terminal-only compact projection is not a CI-format substitution.

## Continuing after failures

Independent validation units should continue after a failure unless the operator selected an explicit, safe `--fail-fast` policy. Choose fail-fast behavior for mutating or unsafe work from its actual side effects and recovery properties. Do not add a universal fail-fast default or flag. Preserve all failures and skips collected before execution stops.
