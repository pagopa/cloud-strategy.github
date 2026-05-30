---
name: internal-graphify
description: Use when a codebase question needs the local Graphify knowledge graph to inspect repository structure, paths, communities, or affected files.
---

# Internal Graphify

## Referenced skills

- None.

## When to use

- A codebase question needs graph-style structure, communities, paths, or affected-file analysis rather than plain text search alone.
- The local Graphify output under `tmp/.graphify/graphify/graphify-out/` already exists, or the task explicitly allows refreshing it with `make graphify-update`.
- The question is easier to answer with `graphify query`, `graphify explain`, `graphify path`, or `graphify affected` than with one-off file reads.

## When not to use

- The task only needs a direct file lookup, symbol lookup, or a simple `rg` search.
- The graph is missing or stale and the user did not ask for a refresh.
- The task would require CI, hooks, background refresh, external APIs, or versioned Graphify output.

## Graph Contract

- Canonical refresh command: `make graphify-update`
- Canonical output path: `tmp/.graphify/graphify/graphify-out/graph.json`
- Graphify workspace path: `tmp/.graphify/`
- Working corpus path: `tmp/.graphify/graphify/`
- Treat the graph as local disposable build output. Do not commit it.

## Freshness Policy

- Refresh only when the graph is missing, clearly stale for the active question, or the user explicitly asks.
- After meaningful repository changes in the area under investigation, prefer `make graphify-update` before trusting older graph answers.
- If the refresh command fails or `graph.json` is missing, fall back to normal repository search and say that the graph is unavailable.

## Workflow

1. Check whether `tmp/.graphify/graphify/graphify-out/graph.json` exists and is fresh enough for the current question.
2. If refresh is needed and allowed, run `make graphify-update`.
3. Use the smallest Graphify command that answers the question.
4. Verify concrete claims against real repository files before finalizing the answer.
5. Fall back to `rg`, targeted file reads, or symbol search when Graphify output is missing, ambiguous, or not precise enough.

## Command Hints

- Use `graphify query` for high-level repository structure or community questions.
- Use `graphify explain <path>` to summarize a file or folder role.
- Use `graphify path <from> <to>` to inspect relationship chains.
- Use `graphify affected <path>` to inspect likely impact around a file or area.

## Output Expectations

- State whether the answer came from an existing graph, a refreshed graph, or fallback search.
- Mention the Graphify command when it materially informed the answer.
- Separate graph-derived hints from file-verified facts.

## Validation

- `make graphify-update`
- `make skill-lint`
