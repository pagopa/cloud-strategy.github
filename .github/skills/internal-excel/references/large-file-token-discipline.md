# Large-File Token Discipline

Use this reference when CSV, TSV, `.xlsx`, or exported worksheet work could create large prompts, repeated tool output, expensive profiling, or memory-heavy local processing.

## Gate

- Start with metadata and bounded evidence: file size, format, worksheet names, dimensions when cheap, delimiter or encoding clues, headers, row counts, and column counts.
- Decide whether the next action is discovery, transformation, or proof. Do not use discovery samples as completion evidence.
- Name the cost checkpoint before expanding to all rows, all sheets, all columns, broad profiling, or repeated wide joins.

## Output posture

- Avoid full content reads, full profiler output, raw workbook XML, and unbounded terminal output in chat.
- Save detailed reports as local artifacts and summarize only counts, schema changes, anomalies, transformation rules, artifact paths, and validation gaps.
- Keep samples small, representative, and redacted. Use hashed, truncated, or representative-key examples when raw identifiers are sensitive.

## Large-file handling

- Project only needed columns and target only needed sheets before sampling, profiling, joining, or converting.
- Prefer streaming reads, chunked scans, DuckDB, Polars, or PyArrow when a full in-memory load is unnecessary or risky.
- For `.xlsx`, inspect workbook metadata first and avoid full workbook traversal unless workbook scope proves it is needed.

## Proof

- Use deterministic full-file aggregate checks for proof: row counts, schema diffs, duplicate-key scans, unmatched-key counts, coercion failures, null increases, and reconciliation totals.
- For multi-file joins, report join cardinality, unmatched-key counts, duplicate-key counts, and only the smallest safe examples needed to diagnose anomalies.
- If the user asks for full output, state the context impact and provide the smallest bounded next slice or a local artifact path.
