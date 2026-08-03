---
name: mattpocock-handoff
description: Compact the current conversation into a handoff document for another agent to pick up.
argument-hint: "What will the next session be used for?"
---

Write a handoff document summarising the current conversation so a fresh agent can continue the work. Save it under `tmp/.handoff/` in the current workspace, creating that directory if needed.

Include a "suggested skills" section in the document, which suggests skills that the agent should invoke.

Do not duplicate content already captured in other artifacts (PRDs, plans, ADRs, issues, commits, diffs). Reference them by path or URL instead.

Redact any sensitive information, such as API keys, passwords, or personally identifiable information.

If the user passed arguments, treat them as a description of what the next session will focus on and tailor the doc accordingly.

<!-- local-sync:handoff-workspace:start -->
## Local handoff-workspace contract

This repository-owned contract overrides earlier workspace and output-path
instructions.

- Save handoff documents under `tmp/.handoff/`.
- Do not duplicate content already captured in other artifacts (PRDs, plans, ADRs, issues, commits, diffs). Reference them by path or URL instead.
<!-- local-sync:handoff-workspace:end -->

<!-- local-sync:mattpocock-git-autonomy:start -->
## Local Git-autonomy contract

- Keep completed changes in the working tree for user review.
- You may stage only changes owned by the current task when staging helps inspect the exact diff.
- Leave changes uncommitted and unpushed unless the current user explicitly requests the specific commit or push action.
- Keep pre-existing or unrelated user changes out of the index.
<!-- local-sync:mattpocock-git-autonomy:end -->
