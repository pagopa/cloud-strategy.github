---
name: internal-github-pr
description: Use when creating, updating, checking readiness of, merging, or verifying the final state of a GitHub pull request. Route diff review to /internal-review-code, review-comment replies to /openai-gh-address-comments, failing-check repair to /openai-gh-fix-ci, and required-review or ruleset policy to /internal-github-platform.
---

# Internal GitHub PR

Own the pull-request lifecycle from template resolution to verified terminal
state. Ground every statement in the actual diff, review state, and fresh
`gh` output.

## When to use

- Open or update a pull request and its body from the repository template.
- Check whether a pull request is ready to merge, or why it is blocked.
- Merge a pull request within repository policy and confirm the final state.

## Boundaries

| Request | Owner |
|---|---|
| Technical review of the diff | `/internal-review-code` |
| Replies to review comments | `/openai-gh-address-comments` |
| Repair of failing checks | `/openai-gh-fix-ci` |
| Required-review, ruleset, or bypass policy | `/internal-github-platform` |

Technical findings or a review verdict never establish readiness.

## Workflow

1. **Template.** Use the first existing file:
   1. `.github/PULL_REQUEST_TEMPLATE.md`
   2. `.github/pull_request_template.md`
   3. `PULL_REQUEST_TEMPLATE.md`
   4. `pull_request_template.md`

   Keep headings and order. Mark an inapplicable section `N/A`.
2. **Content.** Map the specification outcomes to the actual diff. State
   scope, changes, risk, rollback, and validation evidence. Name gaps; never
   claim a change or test the diff does not contain.
3. **Create or update.** Detect whether the PR exists and update it, or open a
   draft.
4. **Readiness.** Fetch fresh evidence for both review state and checks:

   ```bash
   gh pr view <n> --json reviewDecision,statusCheckRollup,mergeStateStatus,reviews,author
   gh pr checks <n>
   ```

   Under required reviews, ready means `reviewDecision` is `APPROVED` by a
   non-author and required checks pass. Green checks alone, or the author's own
   approval, are not ready. Report `mergeStateStatus` when it blocks the merge.
5. **Merge.** Use `gh pr merge <n> --squash` unless the repository
   standardizes another allowed method. Use `--admin` only when repository
   policy explicitly permits the bypass, and cite that policy.
6. **Terminal state.** Confirm with repository-scoped
   `gh pr view <n> --json state,mergedAt`. Organization-wide `gh search prs`
   results can lag right after a merge; do not treat them as authoritative.

## Completion criteria

- Template fidelity is preserved.
- Every claim in the PR body maps to the diff; gaps are named.
- Readiness cites fresh `reviewDecision` and check evidence.
- Merge method and any `--admin` use follow repository policy.
- The terminal state is verified from the repository-scoped view.
- Out-of-scope requests are handed to the owner in the boundaries table.
