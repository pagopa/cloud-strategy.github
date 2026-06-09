---
name: internal-graphify
description: Use when a codebase question needs the Graphify knowledge graph to inspect repository structure, paths, communities, or affected files across repositories, and the local graph is fresh enough for trust.
---

# Internal Graphify

## Referenced skills

- `graphify`: upstream skill for general graph queries. Load it only when the local graph is unavailable and the upstream contract is sufficient.

## When to use

- Use Graphify first for structure questions: community layout, ownership clusters, path relationships, affected-area analysis, or broad repository orientation.
- Use file-first search first for exact file lookup, symbol lookup, single-line verification, or final claim verification.
- Use Graphify only when the local graph is fresh enough for the current question, or when the task explicitly allows a refresh.
- Use Graphify when the question is easier to answer with `graphify query`, `graphify explain`, `graphify path`, or `graphify affected` than with one-off file reads.

## When not to use

- The task only needs a direct file lookup, symbol lookup, or a simple `rg` search.
- The graph is missing, stale, or ambiguous and the user did not ask for a refresh.
- The task would require CI, hooks, background refresh, external APIs, or versioned Graphify output.
- The current repository does not expose the configured activation gate markers. In that case, use standard search. The upstream `graphify` skill is for repositories without this wrapper or for general graph creation outside the local activation gate.

## Precedence

When the current repository exposes this skill, it is the canonical entry point for all Graphify queries against this repository. Do not bypass this wrapper by invoking the upstream `graphify` skill directly for the same repository; the upstream skill does not enforce the local freshness gate or stale-safety fallback. This wrapper owns the trust decision for the local graph.

## Graph Contract

- Canonical refresh command: `make graphify-update` (configurable local seam)
- Canonical check command: `make graphify-check` (configurable local seam)
- Canonical output path: `graphify-out/graph.json`
- Required local artifacts: `graphify-out/graph.json`, `graphify-out/GRAPH_REPORT.md`
- Optional visualization artifact: `graphify-out/graph.html`
- Treat the graph as local disposable build output. Do not commit it.
- Do not read Graphify artifacts directly with `rg` or file reads unless performing an explicit audit.

## Freshness Policy

- `graphify-out/` presence alone is never sufficient for trust.
- Trust graph-derived hints only when freshness evidence is current and valid.
- Refresh only when the graph is missing, clearly stale for the active question, or the user explicitly asks.
- Treat the canonical check command as the freshness gate. Trust graph-derived hints only when it passes, or when the current commit and governed corpus hash still match the last refresh evidence.
- After meaningful repository changes in the area under investigation, prefer a refresh before trusting older graph answers.
- If the refresh command fails, `graph.json` is missing, or the graph answer is still imprecise after refresh, fall back to `rg`, targeted reads, or symbol search and say that the graph is unavailable for the claim you are making.
- The canonical check command exits non-zero when the required local artifacts are stale, incomplete, or contain source paths outside the governed corpus.
- No repository requires local hook automation for Graphify. If automation is revisited later, keep it local and non-blocking.

## Activation Gate

This skill applies when the current working directory exposes the configured activation gate. The default gate markers are:

- `.github/skills/internal-graphify/SKILL.md`
- `.github/scripts/graphify_update.py`
- `.graphifyignore`
- `Makefile` with `graphify-update` and `graphify-check` targets

When activation gate markers are missing, this skill must not propose a refresh or assume `graphify-out/` exists. Fall back to standard search or the upstream `graphify` skill. Missing local seam always resolves to safe fallback, not silent graph trust.

## Workflow

1. Verify that the repository exposes the activation gate markers above.
2. Check whether `graphify-out/graph.json` exists and is fresh enough for the current question.
3. If refresh is needed and allowed, run the canonical refresh command.
4. Use the smallest Graphify command that answers the question.
5. Verify concrete claims against real repository files before finalizing the answer.
6. Fall back to `rg`, targeted file reads, or symbol search when Graphify output is missing, stale, ambiguous, or not precise enough.

## Command Hints

- Use `graphify query` for high-level repository structure or community questions.
- Use `graphify explain <path>` to summarize a file or folder role.
- Use `graphify path <from> <to>` to inspect relationship chains.
- Use `graphify affected <path>` to inspect likely impact around a file or area. Treat this as best-effort; always verify real callers with `rg` or targeted source reads.

## Output Expectations

- Always report graph status: `fresh`, `stale`, `missing-evidence`, `missing-config`, or `fallback-used`.
- State whether the answer came from an existing graph, a refreshed graph, or fallback search.
- Mention the freshness basis when graph-derived hints were used.
- Mention the Graphify command when it materially informed the answer.
- Separate graph-derived hints from file-verified facts.
- For ROI questions, report the smallest honest signal available: `existing graph`, `refreshed graph`, or `fallback search`, plus whether the graph was fresh enough for trust.

## Validation

- `make graphify-update`
- `make graphify-check`
- `make skill-lint`
