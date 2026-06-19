# Python Project Logging And Reporting

Use this reference when Python project code needs professional logging, reporting layout, structured log context, result DTOs, adapter-owned rendering, or a clear boundary between JSON/data output and human-facing CLI reporting.

## Boundary

- Project internals should expose behavior through typed results, domain events, DTOs, return values, exceptions, or framework contracts.
- Domain, service, persistence, and framework modules should use standard `logging` or the repository framework's native logging.
- Logs from importable modules should be neutral, structured when useful, and parsable in production.
- Human-facing rendering belongs to adapters: CLI, admin command, report command, or delivery script.
- Machine-readable outputs such as JSON, API responses, event payloads, or exported files must stay plain data. Do not decorate them with `rich`, emoji, color, panels, or tables.
- A CLI adapter may use the script `ExecutionReporter` pattern or `rich`, but the project core should not import or know about that reporter.

## Professional Layout

Prefer this ownership split when the project needs both reusable behavior and operator-facing reporting:

```text
src/{package}/
├── domain/          # entities, value objects, domain rules; no logging UI
├── services/        # use cases; structured logging and typed results
├── adapters/
│   ├── cli.py       # optional human-facing rendering boundary
│   ├── http.py      # framework/API response boundary
│   └── persistence.py
└── observability.py # logger setup helpers only when the project owns setup
```

Use existing repository structure first. Do not create these folders just to satisfy the shape when the current project has a clearer convention.

## Logging Shape

Use stable event names and explicit context. Prefer values that help production search, alerting, and diagnosis.

```python
from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ImportSummary:
    imported_count: int
    skipped_count: int
    output_path: Path


def import_records(source_path: Path, output_path: Path) -> ImportSummary:
    logger.info(
        "records_import_started",
        extra={"source_path": source_path.as_posix(), "output_path": output_path.as_posix()},
    )

    summary = ImportSummary(imported_count=12, skipped_count=1, output_path=output_path)

    logger.info(
        "records_import_completed",
        extra={
            "imported_count": summary.imported_count,
            "skipped_count": summary.skipped_count,
            "output_path": summary.output_path.as_posix(),
        },
    )
    return summary
```

## Adapter Rendering

Adapters translate project results into the output contract for that boundary.

```python
def summary_to_json(summary: ImportSummary) -> dict[str, object]:
    return {
        "imported_count": summary.imported_count,
        "skipped_count": summary.skipped_count,
        "output_path": summary.output_path.as_posix(),
    }


def render_human_summary(summary: ImportSummary, reporter: object) -> None:
    reporter.summary(
        status="completed",
        counts={"imported": summary.imported_count, "skipped": summary.skipped_count},
        produced_files=[summary.output_path],
        diagnostics=[],
    )
```

The JSON adapter returns plain data. The human adapter may use `ExecutionReporter` or `rich` if the CLI/reporting boundary owns that dependency.

## Review Checklist

- Does the core return typed results or framework-native responses instead of printing?
- Are logs searchable and useful without terminal formatting?
- Are secrets, tokens, bearer values, passwords, credentials, and sensitive payloads omitted or redacted?
- Is JSON or other machine-readable output plain data?
- If `rich` appears, is it isolated to a human-facing CLI/reporting adapter with a dependency decision note?
