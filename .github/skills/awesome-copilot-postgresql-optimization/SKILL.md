---
name: awesome-copilot-postgresql-optimization
description: Optimize PostgreSQL queries and schema design using JSONB, arrays, full-text search, partial indexes, extensions, and `EXPLAIN ANALYZE`. Use when the task is specifically PostgreSQL and benefits from database-specific capabilities or tuning.
---

# PostgreSQL Optimization

Use this skill when generic SQL guidance is not enough and PostgreSQL-specific features matter.

## Focus Areas

- `EXPLAIN ANALYZE` and `pg_stat_statements`
- JSONB and GIN indexing
- Partial and expression indexes
- Full-text search
- Range, array, and extension-based patterns

## Workflow

1. Confirm the workload and bottleneck.
2. Inspect the current plan and index usage.
3. Prefer PostgreSQL-native features when they simplify the workload.
4. Validate improvements with execution evidence.

## Guardrails

- Do not use JSON as a dumping ground when relational modeling is better.
- Keep extension choices explicit and justified.
- Watch unused indexes and index bloat as carefully as missing indexes.
