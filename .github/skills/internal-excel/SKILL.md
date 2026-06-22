---
name: internal-excel
description: Use when tasks involve CSV, TSV, or Excel tabular data profiling, schema validation, cleanup, joins, conversions, optimization, or large-file integrity.
---

# Internal Excel

## Referenced skills

- `openai-spreadsheet`: on-demand support owner when formulas, workbook layout, charts, rendering, or formatting preservation matter.

## When to use

- CSV, TSV, or `.xlsx` tasks centered on tabular data quality, profiling, schema choices, normalization, joins, dedupe, reconciliation, conversion, or large-file processing.
- Requests where the main decision is tool selection for scale, memory use, or integrity tradeoffs across local data files.
- Workbook extraction or value-level updates where presentation fidelity is not the primary requirement.

## When not to use

- Spreadsheet layout, formulas, charts, styling, rendered review, or preserving workbook presentation as a first-class requirement; use `openai-spreadsheet`.
- Single-language implementation work after the tabular-data approach is already chosen; use the narrower file or runtime owner for that code.
- Database or warehouse design work that is not primarily about local CSV, TSV, or Excel artifacts.

## Boundary

- This skill owns data integrity first: headers, types, nulls, duplicates, joins, reconciliation, stable IDs, delimiter detection, encoding, and row-count preservation.
- Keep evidence compact for large files: report headers, counts, targeted anomalies, transformation rules, and exact validation gaps.
- Treat `.xlsx` as a workbook container. Stay here when the job is tabular extraction or safe value-level transformation. Route to `openai-spreadsheet` when workbook behavior matters.
- Read `references/tool-selection.md` when choosing between Python `csv`, `pandas`, `openpyxl`, PyArrow, Polars, or DuckDB.

## Workflow

1. Confirm the artifact type, row scale, and whether workbook fidelity matters.
2. Pick the narrowest tool that preserves the needed integrity and performance.
3. Inspect headers, sample rows, counts, null patterns, and key columns before broad transforms.
4. Apply deterministic transformations and keep a reconciliation path for row counts, keys, duplicates, and dropped records.
5. Re-run focused integrity checks after each material transform.
6. Hand workbook UX, formulas, formatting, charts, or rendering follow-up to `openai-spreadsheet`.

## Validation

- Run the smallest deterministic check that proves the transform: row counts, schema diff, duplicate-key scan, delimiter or encoding confirmation, join cardinality, or a reconciliation sample.
- Run `python3 ./.github/scripts/validate_internal_skills.py --skill internal-excel --strict` after editing this skill bundle.
- Run the closest inventory consistency check when registering or renaming the skill.
