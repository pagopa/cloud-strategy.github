# Python Project Logging And Reporting

Load this reference when project code needs structured logging, typed results,
adapter-owned rendering, or a clear JSON/data versus human-output boundary.

## Boundary

- Project internals expose typed results, domain events, DTOs, return values,
  exceptions, or framework contracts.
- Importable modules use standard or framework-native logging. Keep events
  neutral, structured when useful, and searchable in production.
- Human-facing rendering belongs to a CLI, admin, report, or delivery adapter.
- JSON, API responses, events, and exported files stay plain data without
  `rich`, emoji, color, panels, or tables.

## Logging shape

```python
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
        extra={"source_path": source_path.as_posix()},
    )
    summary = ImportSummary(12, 1, output_path)
    logger.info(
        "records_import_completed",
        extra={
            "imported_count": summary.imported_count,
            "skipped_count": summary.skipped_count,
        },
    )
    return summary
```

## Adapter rendering

Adapters translate results into the boundary's output contract. The JSON
adapter returns plain data; the human adapter may use the script reporting
owner or `rich` when the CLI contract owns that dependency.

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

## Review checklist

- Does core code return typed results or framework responses instead of printing?
- Are logs searchable without terminal formatting?
- Are secrets and sensitive payloads omitted or redacted?
- Is machine-readable output plain data?
- If `rich` appears, is it isolated to a human-facing CLI/reporting adapter and
  covered by a dependency decision note?
