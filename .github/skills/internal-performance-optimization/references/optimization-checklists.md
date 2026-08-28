# Optimization Checklists

## Frontend

- Re-render frequency
- Bundle size and lazy loading
- DOM churn and expensive layout work
- Image, font, and asset weight
- Request waterfalls and client caching

## Backend

- N+1 patterns
- Avoidable I/O round-trips
- Unbounded concurrency
- Slow serialization or parsing
- Inefficient algorithms or data structures

## Database

- Execution plan shape and row-estimate mismatches
- Missing or badly ordered indexes
- Functions on indexed columns in predicates
- Over-fetching
- Offset pagination on large tables
- Repeated aggregations that should be consolidated

## PostgreSQL-Specific

- `EXPLAIN ANALYZE` and `pg_stat_statements`
- JSONB with GIN indexes only when the workload truly benefits
- Partial and expression indexes for selective predicates
- Full-text search when text filtering outgrows `LIKE`
- Extension choices only when they are explicit, justified, and operationally supportable

## Memory and CPU

- High allocation churn
- Duplicate object creation
- Work that should be streamed or batched
- Work happening on the critical path that can move off it
