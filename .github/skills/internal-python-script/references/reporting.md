# Python Script Reporting

Use this reference when a Python script or operator-facing toolkit needs polished human-facing console reporting, `rich` rendering, status tables, redaction behavior, or a final summary.

## Boundary

- Keep reporting at the human-facing CLI or operator adapter boundary.
- Keep application logic, reusable helpers, project modules, and machine-readable output paths free of `rich`, panels, tables, color, and emoji formatting.
- Let application logic call semantic reporter methods such as `step()`, `success()`, or `summary()`; do not build styled strings inside business logic.
- Reserve plain `print()` for machine-readable output boundaries such as `--format json`; human output should go through the reporter.

## Dependency Decision

Use `rich` when the human-facing terminal experience is part of the script contract. Preserve the declared dependency manager and keep the decision close to its canonical lock artifact.

```text
Dependency decision note
- Candidates: stdlib print/logging, rich
- Final choice: rich
- Why: the tool has operator-facing sections, status tables, warnings, and summaries where consistent terminal rendering reduces mistakes.
```

After adding or updating dependencies, follow the `internal-python-script` Dependency policy for the declared manager's lock generation and validation.

## Reporter Shape

Preferred methods:

- `banner(title, *, run_id, mode, scope, output_path, options)`
- `section(title, description=None)`
- `step(message)`
- `detail(message)`
- `success(message)`
- `warning(message)`
- `error(message)`
- `table(title, columns, rows)`
- `summary(status, counts, produced_files, diagnostics)`

Use concise, deduplicated retry messages. Put technical details behind `--verbose` or `--debug`. Never log tokens, bearer values, passwords, secrets, credentials, or sensitive payloads.

## Rich Skeleton

```python
from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path

from rich.console import Console
from rich.markup import escape
from rich.panel import Panel
from rich.table import Table


SENSITIVE_OPTION_MARKERS = (
    "authorization",
    "credential",
    "password",
    "secret",
    "token",
)


def _render_option(key: str, value: object) -> str:
    normalized_key = key.casefold().replace("-", "_")
    if any(marker in normalized_key for marker in SENSITIVE_OPTION_MARKERS):
        return "[REDACTED]"
    return escape(str(value))


class ExecutionReporter:
    def __init__(self, *, console: Console | None = None, verbose: bool = False) -> None:
        self.console = console or Console()
        self.verbose = verbose

    def banner(
        self,
        title: str,
        *,
        run_id: str,
        mode: str,
        scope: str,
        output_path: Path | None,
        options: Mapping[str, object],
    ) -> None:
        lines = [
            f"Run: {escape(run_id)}",
            f"Mode: {escape(mode)}",
            f"Scope: {escape(scope)}",
        ]
        if output_path is not None:
            lines.append(f"Output: {escape(output_path.as_posix())}")
        if options:
            rendered = ", ".join(
                f"{escape(str(key))}={_render_option(str(key), value)}"
                for key, value in options.items()
            )
            lines.append(f"Options: {rendered}")
        self.console.print(Panel("\n".join(lines), title=escape(title), border_style="blue"))

    def section(self, title: str, description: str | None = None) -> None:
        self.console.rule(f"ℹ️  {escape(title)}")
        if description:
            self.console.print(escape(description))

    def step(self, message: str) -> None:
        self.console.print(f"• {escape(message)}")

    def detail(self, message: str) -> None:
        if self.verbose:
            self.console.print(f"ℹ️  {escape(message)}", style="dim")

    def success(self, message: str) -> None:
        self.console.print(f"✅ {escape(message)}", style="green")

    def warning(self, message: str) -> None:
        self.console.print(f"⚠️  {escape(message)}", style="yellow")

    def error(self, message: str) -> None:
        self.console.print(f"❌ {escape(message)}", style="red")

    def table(self, title: str, columns: Sequence[str], rows: Iterable[Sequence[object]]) -> None:
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
        produced_files: Sequence[Path],
        diagnostics: Sequence[str],
    ) -> None:
        rows = [(name, value) for name, value in counts.items()]
        if rows:
            self.table("Counts", ("Metric", "Value"), rows)
        self.console.print(f"Status: {escape(status)}")
        self.console.print("Produced files:")
        for path in produced_files:
            self.console.print(f"• {escape(path.as_posix())}")
        self.console.print("Diagnostics:")
        for diagnostic in diagnostics:
            self.console.print(f"• {escape(diagnostic)}")
```

Callers must pass only sanitized diagnostics because arbitrary free-text diagnostics cannot be reliably redacted by key inspection.

## Summary Expectations

End operator-facing runs with a compact summary that includes final status, produced files, relevant counts, diagnostics, and remaining gaps. Use tables for repeated file or diagnostic rows, and keep secrets redacted even in debug mode.
