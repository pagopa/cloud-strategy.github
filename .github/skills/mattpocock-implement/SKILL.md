---
name: mattpocock-implement
description: "Implement a piece of work based on a spec or set of tickets."
---

Implement the work described by the user in the spec or tickets.

Use /mattpocock-tdd where possible, at pre-agreed seams.

Run typechecking regularly, single test files regularly, and the full test suite once at the end.

Once done, use /mattpocock-code-review to review the work.

Commit your work to the current branch.

<!-- local-sync:mattpocock-git-autonomy:start -->
## Local Git-autonomy contract

- Keep completed changes in the working tree for user review.
- You may stage only changes owned by the current task when staging helps inspect the exact diff.
- Leave changes uncommitted and unpushed unless the current user explicitly requests the specific commit or push action.
- Keep pre-existing or unrelated user changes out of the index.
<!-- local-sync:mattpocock-git-autonomy:end -->
