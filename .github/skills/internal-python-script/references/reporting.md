# Python Script Reporting

Load this reference when a script needs human-facing output, `rich` rendering,
redaction, diagnostics, or a final operator summary.

## Boundary and dependency decision

Keep reporting at the human-facing CLI or operator adapter boundary. Reusable
helpers and machine-readable output stay free of terminal styling. Use `rich`
only when the terminal experience is part of the accepted contract, and keep
the decision beside the declared dependency lock.

## Reporter contract

Prefer semantic methods such as `banner`, `section`, `step`, `detail`,
`success`, `warning`, `error`, `table`, and

- `summary(status, counts, produced_files, diagnostics)`. Keep technical details
behind a verbose flag and never log tokens, passwords, credentials, or
sensitive payloads.

## Minimal rich reporter

```python
from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path

from rich.console import Console
from rich.markup import escape
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

    def banner(self, title: str, *, options: Mapping[str, object]) -> None:
        self.console.print(escape(title))
        if options:
            rendered = ", ".join(
                f"{escape(str(key))}={_render_option(str(key), value)}"
                for key, value in options.items()
            )
            self.console.print(rendered)

    def section(self, title: str, description: str | None = None) -> None:
        self.console.rule(escape(title))
        if description:
            self.console.print(escape(description))

    def step(self, message: str) -> None:
        self.console.print(f"• {escape(message)}")

    def detail(self, message: str) -> None:
        if self.verbose:
            self.console.print(escape(message))

    def success(self, message: str) -> None:
        self.console.print(f"✅ {escape(message)}")

    def warning(self, message: str) -> None:
        self.console.print(f"⚠️ {escape(message)}")

    def error(self, message: str) -> None:
        self.console.print(f"❌ {escape(message)}")

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
        self.console.print(f"Status: {escape(status)}")
        self.console.print("Produced files:")
        for path in produced_files:
            self.console.print(f"• {escape(path.as_posix())}")
        self.console.print("Diagnostics:")
        for diagnostic in diagnostics:
            self.console.print(f"• {escape(diagnostic)}")
```

Callers must sanitize free-text diagnostics before passing them to a reporter.
Summaries should state final status, produced files, relevant counts, and
remaining gaps without exposing secrets.
