# Optional Tool Fallbacks

Optional accelerators improve feedback speed but never replace the retained
plan's native command or its evidence contract. The native command is the
authoritative command and must remain the evidence label in baseline, focused,
and final validation.

## Recovery Protocol

1. Preserve the native plan command as the authoritative command and evidence
   label.
2. Probe an accelerator before use. Missing, unhealthy, stale, or incompatible
   RTK routes immediately to the native command.
3. If RTK fails after invocation, establish whether the target command started.
   When non-start is proven, run the native command. When start state is
   unknown or execution may have occurred, inspect observable state and run the
   nearest validation; retry only through an idempotent path that cannot
   duplicate effects.
4. A warning records recovery context but never completes recovery. Recovery
   completes only after the fallback runs and its required result is validated.
5. Graphify failure routes to the bounded search ladder below and may not
   become the blocker.
6. Classify and stop only on the final native operation or repository-evidence
   failure, never on optional-tool availability alone.

Never use `rtk <command> || <command>` for a possibly mutating command. It can
retry a command that already started and duplicate its effects.

## Graphify Fallback Ladder

When graphify is absent, stale, or its query fails, use these steps in order:

1. State one bounded evidence question and the expected owner, path, or symbol
   shape.
2. Inspect aggregate facts first: candidate paths, filenames, counts, sizes,
   headings, and anomalies. Never dump a large file or broad search result.
3. Use filename or glob search when the likely path or extension is known.
4. Use one `rg` query with combined exact terms or regex alternatives, a narrow
   include glob, line numbers, and a bounded match count. Prefer `rg --files`
   plus a path filter for discovery; do not run repository-wide content search
   when path discovery can answer the question.
5. Use semantic search only when vocabulary is uncertain; use symbol-reference
   tooling for known code symbols and relationship questions.
6. Read only the smallest relevant ranges around matches. Expand one local hop
   at a time to the owning abstraction, neighboring test, or call site.
7. Stop when the evidence answers the bounded question. Widen paths, terms,
   result count, or read range one dimension at a time only when a named
   evidence gap remains.

## Routing Cases

| Condition | Required route | Completion evidence |
| --- | --- | --- |
| RTK missing | Run the native authoritative command. | Native result is validated. |
| RTK unhealthy before command start | Skip RTK and run the native command. | Native result is validated. |
| RTK fails with proven non-start | Run the native command once. | Native result is validated. |
| RTK fails with unknown start state | Inspect observable state, validate the target, and use only an idempotent recovery path. | State and validation show no unsafe duplicate, then the required result is validated. |
| Graphify absent | Start the graphify fallback ladder at the bounded question. | Bounded search result and stop condition are recorded. |
| Graphify stale | Treat graph output as unavailable and start the ladder. | Fresh bounded search result and stop condition are recorded. |
| Graphify query failure | Record the failed query context and start the ladder. | Bounded search result and stop condition are recorded. |
| Fallback search success | Continue with the evidence obtained; do not widen without a named gap. | The bounded question is answered. |
| Native or fallback operation failure | Classify the underlying operation and stop only when no safe native or evidence path remains. | Failure is attributed to the final operation or evidence path, not the optional tool. |

Warnings, missing accelerators, and stale graph data are recovery context. They
are not successful validation and are not final blockers while a safe fallback
exists.
