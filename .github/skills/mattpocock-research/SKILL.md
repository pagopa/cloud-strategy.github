---
name: mattpocock-research
description: Investigate a question against high-trust primary sources and capture the findings as a Markdown file in the repo. Use when the user wants a topic researched, docs or API facts gathered, or reading legwork delegated to a background agent.
---

Spin up a **background agent** to do the research, so you keep working while it reads.

Its job:

1. Investigate the question against **primary sources** — official docs, source code, specs, first-party APIs — not a secondary write-up of them. Follow every claim back to the source that owns it.
2. Write the findings to a single Markdown file, citing each claim's source.
3. Save it where the repo already keeps such notes; match the existing convention, and if there is none, put it somewhere sensible and say where.

<!-- local-sync:research-workspace:start -->
## Local research-workspace contract

This repository-owned contract overrides earlier workspace and output-path
instructions.

- Save the default one-file research output to `tmp/.research/YYYY-MM-DD-<slug>.md`.
- An explicit caller-owned output path may override this default.
<!-- local-sync:research-workspace:end -->

<!-- local-sync:research-delegation:start -->
## Local research-delegation contract

The caller owns a value gate before delegating research. Delegate only when a
bounded worker is likely to improve evidence quality, reduce material context
cost, or preserve useful parallel progress compared with direct research.

- When the value gate passes, load `/internal-subagent-contract` and issue one
    bounded brief with the question, context, primary-source and citation
    requirements, output path, and validation expectations.
- The caller retains routing, authority, acceptance, and final validation.
- When delegation adds no clear value or no suitable worker is available,
    research directly instead of manufacturing a delegation requirement.
- In either path, verify that the report exists, is non-empty, and includes
    source citations.
<!-- local-sync:research-delegation:end -->
