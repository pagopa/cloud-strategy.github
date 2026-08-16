---
name: internal-github-pr
description: Use when /internal-github routes pull-request lifecycle work covering creation, body updates, readiness, reviews, merge, or terminal-state verification.
user-invocable: false
---

# Internal GitHub PR

Own pull-request lifecycle work from template resolution through verified
terminal state. Ground every statement in the actual diff, review state, and
fresh validation evidence.

## When to use

Use when the requested deliverable is pull-request content, review readiness,
merge execution, or repository-scoped terminal-state proof. A technical code
review remains owned by `/internal-review-code`; use this skill when the PR
itself is the requested lifecycle or readiness deliverable.

## PR workflow

1. Resolve one repository pull-request template and preserve its headings and
   order.
2. Extract specification outcomes and map them to the actual diff. Identify
   gaps instead of inventing completion.
3. Draft or update concise PR content with relevant scope, changes, risk,
   rollback, and validation evidence.
4. Detect the current PR state and update or create the draft as appropriate.
5. For readiness, verify checks and qualifying non-author review state from
   fresh actual PR evidence; green checks alone are insufficient under
   required review policy. Technical findings, static diff analysis, or a
   review verdict are not substitutes for current PR state, checks, review
   approvals, or terminal verification.
6. Prefer `gh pr merge --squash` unless the repository standardizes another
   allowed method. Use `--admin` only when policy permits a bypass.
7. When Actions workflows or action pins are touched, require full-SHA pins
   and consistent release references in the evidence.
8. After merge, re-fetch repository-scoped terminal state with
   `gh pr view --json state,mergedAt` and verify the final PR state.

## Template resolution

Check these paths in order and use the first existing template:

1. `.github/PULL_REQUEST_TEMPLATE.md`
2. the lowercase filename under `.github/`
3. `PULL_REQUEST_TEMPLATE.md`
4. `pull_request_template.md`

Keep headings and section order unchanged. Mark an inapplicable section `N/A`.

## Completion criteria

- Template fidelity is preserved.
- The summary and claims are grounded in the actual diff.
- Review state and required checks have fresh evidence.
- Validation evidence, risk, and rollback are explicit.
- Merge method and any admin bypass follow repository policy.
- The verified terminal state is recorded for merge or post-merge work.
