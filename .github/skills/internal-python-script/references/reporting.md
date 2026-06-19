# Python Script Reporting

Use this reference when a Python script or operator-facing toolkit needs polished human-facing console reporting, `rich` rendering, status tables, redaction behavior, or a final summary.

## Boundary

- Keep reporting at the human-facing CLI or operator adapter boundary.
- Keep application logic, reusable helpers, project modules, and machine-readable output paths free of `rich`, panels, tables, color, and emoji formatting.
- Let application logic call semantic reporter methods such as `step()`, `success()`, or `summary()`; do not build styled strings inside business logic.
- Reserve plain `print()` for machine-readable output boundaries such as `--format json`; human output should go through the reporter.

## Dependency Decision

Use `rich` when the human-facing terminal experience is part of the script contract. Keep the dependency decision close to the owning `requirements.txt`.

```text
Dependency decision note
- Candidates: stdlib print/logging, rich
- Final choice: rich
- Why: the tool has operator-facing sections, status tables, warnings, and summaries where consistent terminal rendering reduces mistakes.
```

After adding or updating dependencies, regenerate exact pins and hashes with `pip-compile --generate-hashes` or the repository-approved equivalent, then validate with `pip install --require-hashes -r requirements.txt`.

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
            rendered = ", ".join(f"{escape(str(key))}={escape(str(value))}" for key, value in options.items())
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
```

## Summary Expectations

End operator-facing runs with a compact summary that includes final status, produced files, relevant counts, diagnostics, and remaining gaps. Use tables for repeated file or diagnostic rows, and keep secrets redacted even in debug mode.
