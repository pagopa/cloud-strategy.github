# Issue tracker: GitHub

Issues and PRDs for this repo live as GitHub issues. Use the `gh` CLI for all operations.

## Conventions

- **Create an issue**: `gh issue create --title "..." --body "..."`. Use a heredoc for multi-line bodies.
- **Read an issue**: `gh issue view <number> --comments`, filtering comments by `jq` and also fetching labels.
- **List issues**: `gh issue list --state open --json number,title,body,labels,comments --jq '[.[] | {number, title, body, labels: [.labels[].name], comments: [.comments[].body]}]'` with appropriate `--label` and `--state` filters.
- **Comment on an issue**: `gh issue comment <number> --body "..."`
- **Apply / remove labels**: `gh issue edit <number> --add-label "..."` / `--remove-label "..."`
- **Close**: `gh issue close <number> --comment "..."`

Infer the repo from `git remote -v` — `gh` does this automatically when run inside a clone.

## Pull requests as a triage surface

**PRs as a request surface: no.**

When set to `yes`, PRs run through the same labels and states as issues, using the `gh pr` equivalents.

## When a skill says "publish to the issue tracker"

Create a GitHub issue.

## When a skill says "fetch the relevant ticket"

Run `gh issue view <number> --comments`.

## Wayfinding operations

Used by `/mattpocock-wayfinder`. The map is a single issue with child issues as tickets.

- **Map**: a single issue labelled `wayfinder:map`, holding the Notes, Decisions-so-far, and Fog body.
- **Child ticket**: an issue linked to the map as a GitHub sub-issue. Where sub-issues are unavailable, use a task list and add `Part of #<map>` to the child.
- **Blocking**: use GitHub’s native issue dependencies. Where unavailable, add a `Blocked by: #<n>` line.
- **Frontier query**: list the map’s open, unassigned, unblocked children; first in map order wins.
- **Claim**: `gh issue edit <n> --add-assignee @me`.
- **Resolve**: comment on and close the issue, then update the map’s Decisions-so-far.
