# Python CLI Reporting Guidance

Load this reference when a directly executed Python tool needs human lifecycle output, bounded diagnostics, redaction, or final operator summaries.

## Responsibility boundary

Keep CLI parsing, selector resolution, execution and scheduling, lifecycle events, result collection, human rendering, machine-readable serialization, and explicitly requested artifacts as distinct responsibilities. The entrypoint owns argument parsing and output selection. Reusable helpers return data and stay free of terminal styling.

Execution must not depend on whether a terminal is attached or which output projection is selected. Human and machine output should describe the same collected results. Create a file only when the caller explicitly requests that artifact.

Use `rich` only when polished terminal output is part of the accepted contract. Keep the dependency decision beside the owning dependency lock.

## Lifecycle output

For each selected unit in a multi-step tool:

- Emit `▶️ started` as the unit begins, then exactly one terminal state: `✅ passed`, `❌ failed`, `⚠️ warning`, or `⏭️ skipped`.
- Include the unit's category and the selector used to choose it. Add `[n/N]` when position helps the operator follow progress.
- For long units, emit heartbeats only when measured progress is useful. Bound their frequency and amount of output using project-specific choices.
- Keep a human-readable record for every failure and skip. When the output stream cannot encode Unicode, print the state word without its emoji. Never substitute ASCII art.
- Treat `--no-color` and `NO_COLOR` as requests to disable ANSI styling only. They do not remove emoji or state words.

End with counts by state and failures grouped by category or selector. Give a next action only when the evidence supports a concrete, verifiable step.

## Diagnostics, raw output, and artifacts

Choose diagnostic-count and raw-output-size limits for each project and apply them per unit. Keep a record for every unit and every failure or skip in structured output, including totals and any omitted-detail counts. Bound human-facing diagnostic and raw-output excerpts; indicate how much detail was omitted and where an operator can explicitly request the full result.

Omit unavailable fields instead of inventing values. Do not infer causes from incomplete diagnostics. Sanitize free-text diagnostics and raw output before rendering; escaping terminal markup does not redact secrets. Keep machine-readable output plain and preserve its schema. Generate full-detail files only when a caller explicitly requests them.

## Format and compatibility

A new, high-volume terminal interface may consider a terminal-only `--compact` projection when measured output volume justifies it. That projection must not change selectors, work units, scheduling, concurrency, exit codes, JSON, CI output, Markdown, or artifacts. A compact view still reports each unit's state, including failures and skips. Keep `--quiet` for routine chatter only; preserve lifecycle states and the final summary. Use `--verbose` for an explicit request for additional detail.

Preserve an existing `--format compact` name, payload, and consumers as a public interface. Do not reinterpret it as `--compact`. When a real CI consumer exists and the CLI supports a CI format, select that format explicitly before auto-detection. Machine output and artifacts remain free of terminal styling.

## Minimal Rich reporter

This example chooses two diagnostics and 4 KiB of raw output per unit. Those values belong to this example tool; they are not shared defaults.

```python
from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path

from rich.console import Console
from rich.markup import escape
from rich.table import Table


# Example project choices. Set these from the tool's actual output needs.
MAX_DIAGNOSTICS_PER_UNIT = 2
MAX_RAW_OUTPUT_BYTES_PER_UNIT = 4096
SENSITIVE_OPTION_MARKERS = (
    "authorization",
    "credential",
    "password",
    "secret",
    "token",
)
STATE_MARKERS = {
    "started": "▶️",
    "passed": "✅",
    "failed": "❌",
    "warning": "⚠️",
    "skipped": "⏭️",
    "heartbeat": "⏱️",
}


def _render_option(key: str, value: object) -> str:
    normalized_key = key.casefold().replace("-", "_")
    if any(marker in normalized_key for marker in SENSITIVE_OPTION_MARKERS):
        return "[REDACTED]"
    return escape(str(value))


class ExecutionReporter:
    def __init__(
        self,
        *,
        console: Console | None = None,
        verbose: bool = False,
        unicode_output: bool = True,
        no_color: bool = False,
    ) -> None:
        self.console = console or Console(no_color=no_color)
        self.verbose = verbose
        self.unicode_output = unicode_output

    def banner(self, title: str, *, options: Mapping[str, object]) -> None:
        self.console.print(escape(title))
        if options:
            rendered = ", ".join(
                f"{escape(str(key))}={_render_option(str(key), value)}"
                for key, value in options.items()
            )
            self.console.print(rendered)

    def state(
        self,
        state: str,
        *,
        category: str,
        selector: str,
        index: int | None = None,
        total: int | None = None,
    ) -> None:
        marker = STATE_MARKERS[state] if self.unicode_output else ""
        position = f"[{index}/{total}] " if index is not None and total is not None else ""
        prefix = f"{marker} " if marker else ""
        self.console.print(
            f"{prefix}{state} {position}· {escape(category)}/{escape(selector)}"
        )

    def detail(self, message: str) -> None:
        if self.verbose:
            self.console.print(escape(message))

    def diagnostics(
        self,
        unit: str,
        items: Sequence[str],
        *,
        raw_output: bytes = b"",
        full_detail_path: Path | None = None,
    ) -> None:
        visible = items[:MAX_DIAGNOSTICS_PER_UNIT]
        for item in visible:
            self.console.print(f"• {escape(item)}")

        omitted = len(items) - len(visible)
        if omitted:
            self.console.print(
                f"{omitted} more diagnostics omitted for {escape(unit)}; "
                "full detail requires an explicit project-owned option or result path."
            )

        raw_preview = raw_output[:MAX_RAW_OUTPUT_BYTES_PER_UNIT]
        if raw_preview:
            self.console.print(escape(raw_preview.decode("utf-8", errors="replace")))
        omitted_bytes = len(raw_output) - len(raw_preview)
        if omitted_bytes:
            self.console.print(
                f"{omitted_bytes} raw-output bytes omitted for {escape(unit)}; "
                "full detail is available only through an explicit project-owned route."
            )
        if (omitted or omitted_bytes) and full_detail_path is not None:
            self.console.print(f"Full detail: {escape(full_detail_path.as_posix())}")

    def table(
        self,
        title: str,
        columns: Sequence[str],
        rows: Iterable[Sequence[object]],
    ) -> None:
        table = Table(title=escape(title))
        for column in columns:
            table.add_column(escape(column))
        for row in rows:
            table.add_row(*(escape(str(value)) for value in row))
        self.console.print(table)

    def summary(
        self,
        *,
        status: str,
        counts: Mapping[str, int],
        failures_by_scope: Mapping[str, Sequence[str]],
        produced_files: Sequence[Path],
        next_action: str | None,
    ) -> None:
        self.console.print(f"Status: {escape(status)}")
        self.console.print(f"Counts: {escape(str(dict(counts)))}")
        for scope, diagnostics in failures_by_scope.items():
            self.console.print(f"Failures for {escape(scope)}:")
            self.diagnostics(scope, diagnostics)
        if next_action:
            self.console.print(f"Next: {escape(next_action)}")
        if produced_files:
            self.console.print("Requested files:")
            for path in produced_files:
                self.console.print(f"• {escape(path.as_posix())}")
```

Callers must sanitize diagnostic text and raw output before passing them to the reporter. The example's `--verbose` option controls additional narration; another tool may use a project-specific option or explicitly requested result path for full diagnostic detail. A verbose request does not alter unit selection, scheduling, exit codes, machine output, or the per-unit excerpt limits.
