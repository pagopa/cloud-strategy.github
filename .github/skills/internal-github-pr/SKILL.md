---
name: internal-github-pr
description: Use when creating, updating, validating, or merging GitHub pull requests in this repository — PR template bodies, approval and required-review checks, merge method choice, terminal-state verification via `gh pr view --json state,mergedAt`, or PR lifecycle evidence. Do not use for workflow authoring touched by a PR; route that to internal-github-actions.
---

# Internal GitHub PR

## Referenced skills

This index lists every other skill that this file asks the agent to load, route to, compare against, or delegate to.
Treat the referenced skills below as on-demand supports. Do not preload them
for every PR task; load only the owner proved by the touched surface, review
need, workflow change, or lifecycle claim.

- `internal-review-code`: defect-first review after PR body or lifecycle work.
- `internal-github-actions`: workflow/action pinning and Actions security rules for PRs that touch workflows.
- `internal-review-high-level`: systems-level impact analysis that feeds PR risk.
- `openai-gh-address-comments`: review-thread remediation after PR body work exists.
- `superpowers-verification-before-completion`: evidence gate before claiming PR readiness, validity, mergeability, or completion.
- `internal-github`: route back under material routing uncertainty when the owning GitHub lane is unclear or the work is still strategic platform framing.

## When to use

- Create a new pull request description.
- Improve an incomplete pull request body.
- Summarize changes from modified files and checks.
- Map a specification, issue, or template-driven request into a PR title and body without overstating what the diff actually delivers.
- Check whether a pull request is ready to merge.
- Merge a pull request or verify its terminal state after merge.

## Mandatory rules

- Use English for all PR content.
- Keep summary concise and outcome-oriented.
- Include only relevant scope checkboxes.
- Provide a short bullet list of key changes.
- Include validation commands and results.
- Explicitly state risk level and rollback plan.
- If PR tools are available, apply updates to the PR directly.
- Do not modify any `README.md` file unless explicitly requested.
- For self-authored PRs under required-review policy, do not treat green checks as sufficient; confirm a qualifying non-author approval still exists before merge.
- Prefer `gh pr merge --squash` over the default merge-commit path unless the repository clearly standardizes on another allowed merge method.
- Use `--admin` only when policy explicitly allows a bypass.
- Treat organization-wide `gh search prs` results as eventually consistent immediately after merge; confirm terminal state with repository-scoped `gh pr view --json state,mergedAt` before treating a just-merged PR as still open.
- When the PR touches GitHub Actions workflow/action pinning, follow `internal-github-actions` for full-SHA and adjacent release-reference rules.
- Use `superpowers-verification-before-completion` before claiming a PR is ready,
  valid, mergeable, merged, or complete.

## Template resolution

Resolve and use one existing repository template:

1. `.github/PULL_REQUEST_TEMPLATE.md`
2. the lowercase filename under `.github/` if the repository exposes one
3. `PULL_REQUEST_TEMPLATE.md`
4. `pull_request_template.md`

Keep headings and section order unchanged. If a section is not applicable, write `N/A`.

## Specification-aware drafting

If the user provides a specification, issue, or acceptance outline:

- Extract the required outcomes, constraints, and acceptance points first.
- Map the actual diff to that requested scope instead of inventing completion.
- Call out anything requested by the specification that is not present in the diff as a gap, follow-up, or `N/A`.
- Keep the PR body grounded in the repository template, not in the source specification's original formatting.

## Tool-driven workflow

1. Detect whether an open PR exists for the current branch.
2. If PR exists → update title/body directly.
3. If PR does not exist → create a draft PR first.
4. Update PR title/body using template-compliant content.
5. For merge-readiness work, verify checks and required review state from PR-specific evidence.
6. For merge or post-merge work, re-fetch repository-scoped terminal state with `gh pr view --json state,mergedAt`.
7. Re-fetch PR and verify required section headings exist when editing body content.
8. Return PR URL and a concise confirmation.
9. If PR tools are unavailable → return ready-to-paste markdown plus CLI fallback commands.

## Minimal example

- Input:
  - title: "Externalize Copilot inventory"
  - changed_files: "AGENTS.md, .github/INVENTORY.md, .github/copilot-instructions.md"
  - validation: "make lint"
- Expected output: Complete PR body with all required template sections and concise change bullets.

## Common mistakes

| Mistake | Why it matters | Instead |
| --- | --- | --- |
| Generic summary ("Various improvements") | Reviewers cannot assess impact or scope | Write specific outcome: "Adds region validation to SCP deploy pipeline" |
| Missing risk level or rollback plan | Reviewers approve without understanding blast radius | Always fill Risk and Rollback sections explicitly |
| Adding sections not in the repo template | Breaks template consistency across PRs | Use only the sections from the resolved template |
| Leaving placeholder text (`TODO`, `fill in`) | Looks unfinished, blocks approval | Fill every section with real content or `N/A` |
| Listing every changed file instead of summarizing | Noisy description that obscures intent | Group changes by purpose; detail only non-obvious changes |
| Not including validation commands and output | Reviewer has no confidence that code was tested | Always include the exact commands and their results |

## Cross-references

- **internal-review-high-level**: for systems-level impact analysis that feeds the risk section.
- **internal-review-code**: for the review that follows the PR.
- **internal-github-actions**: for workflow/action pinning and Actions security rules touched by the PR.
- **openai-gh-address-comments**: for addressing review threads and PR comments after the PR body exists; keep review-thread remediation separate from PR lifecycle/body work.
- **superpowers-verification-before-completion**: for evidence before readiness,
  mergeability, merge, or completion claims.

## Validation

- Every template-defined section heading is present.
- `Changes` has concise bullets describing the real diff.
- Risk and rollback are explicit and actionable.
- Final PR body is persisted when tooling supports PR updates.
- Merge readiness is based on PR-scoped checks and qualifying review evidence.
- Recently merged PR state is confirmed with repository-scoped `gh pr view --json state,mergedAt`.
- `superpowers-verification-before-completion` was applied before claiming PR
  readiness, validity, mergeability, merge, or completion.
