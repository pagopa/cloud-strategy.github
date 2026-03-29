---
name: awesome-copilot-sql-optimization
description: Optimize SQL query shape, indexing strategy, joins, pagination, batching, and execution-plan outcomes across relational databases. Use when diagnosing slow SQL, rewriting queries, or reviewing relational data access for performance.
---

# SQL Optimization

Use this skill for database-agnostic SQL tuning.

## Workflow

1. Capture the query and the execution symptom.
2. Inspect predicates, joins, sort and aggregation costs.
3. Check index support and selectivity.
4. Rewrite query shape before adding compensating cache layers.
5. Validate with an execution plan or timing evidence.

## Focus Areas

- Filter and join order
- Index friendliness
- Cursor-style pagination over deep offsets
- Batch operations over row-by-row work
- Avoiding `SELECT *` in hot paths

## Guardrails

- Do not optimize without plan data when plan data is available.
- Do not add indexes blindly; account for write costs.
- Prefer explicit columns, narrow result sets, and predictable predicates.
