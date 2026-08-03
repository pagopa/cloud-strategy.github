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

<!-- local-sync:mattpocock-git-autonomy:start -->
## Local Git-autonomy contract

- Keep completed changes in the working tree for user review.
- You may stage only changes owned by the current task when staging helps inspect the exact diff.
- Leave changes uncommitted and unpushed unless the current user explicitly requests the specific commit or push action.
- Keep pre-existing or unrelated user changes out of the index.
<!-- local-sync:mattpocock-git-autonomy:end -->
