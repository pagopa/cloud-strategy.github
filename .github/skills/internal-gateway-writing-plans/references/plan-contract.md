# Plan Contract

This reference defines the plan header, task perimeter, lint checklist, and handoff gate for the writer.

<!-- protocol:plan-header -->
```text
**Spec:** <source path>|direct requirements
**Status:** tmp/superpowers/plans/<plan name>/status.md
**Depends on:** <repository root>:<retained plan path>|unresolved — <required output>; check: <command>|none (<pass|fail|not-run> <YYYY-MM-DD>)
```

<!-- protocol:files-globs -->
```text
glob-prefix: A `Files:` glob is allowed only when the entry starts with `tests/`, `**/tests/`, or `**/fixtures/`, or its literal prefix before the first wildcard ends in a `tests/` or `fixtures/` segment.
segment: `*` matches within one path segment.
any-depth: `**` matches zero or more path segments.
production: Paths outside the allowed test and fixture prefixes must be exact paths, including production files and directories.
precedence: Check protected and read-only paths before glob matching; no glob matches them.
changes: Paths are repository-relative; read changes with `git diff --name-status -z --find-renames`.
renames: Both endpoints of a rename must match the active task's `Files:`.
```

## Plan lint

Before handoff, check every item:

- The plan header lines match the shared plan-header block above.
- The Status path is `tmp/superpowers/plans/<plan name>/status.md`, using the plan filename without its .md suffix.
- Every task has a Files block, exactly one Posture line, and a native validation command.
- Each validation tool exists in the repository environment; use command -v or the repository's tool-resolution check before writing a command.
- Every Files glob follows the files-globs rules above. Production paths are exact.
- Check protected and read-only paths before evaluating a glob. No protected or read-only path is allowed.
- Every upstream plan dependency has a Depends on header line with its repository root and retained path, required output, read-only check, result, and date.
- No dependency appears only in prose. A missing producer path is marked unresolved; never guess a path.
- No task contains a commit step or Git mutation.
- Every executable or evaluable task has its required /internal-tdd posture and matching step order.
- The imported /superpowers-writing-plans self-review Step scan and Proportion items have run. A plan several times longer than its spec or dominated by code blocks is revised before handoff, and test assertions stay as code.
- A failing lint item is fixed inline and lint runs again. If a user decision is needed, keep the plan unfinished and withhold handoff.

## Handoff

Run one read-only gate after plan lint passes and every Depends on check passes. Show the results together in one message:

- Current branch: git symbolic-ref --quiet --short HEAD; report detached when it has no symbolic branch.
- Default branch: git symbolic-ref --quiet --short refs/remotes/origin/HEAD; report unresolved when it has no symbolic target.
- Dependencies: report each Depends on check and its pass, fail, or not-run result.
- Dirty Files paths: read git status --porcelain -z and match the shared Files rules, retaining both rename endpoints. Show matching paths and their current content identities or none.
- Foreign: show unrelated changed paths separately; they do not withhold handoff.
- Conflicting runs: inspect retained plan ledgers in this checkout and report relevant overlaps or none, using the rules below.

Relevant paths are all task Files, including future paths and allowed globs,
plus the plan, spec, declared dependency plans and explicitly declared inputs
and outputs. The plan and spec stay read-only; dependency outputs are read-only
unless explicitly assigned to Files. Compare sources against the approved
content. Changed protected inputs require reevaluation, not dirty inclusion.
Record current input identities in the handoff evidence for the executor.

Inspect other ledgers under tmp/superpowers/plans/ in the same checkout. A
RUNNING, PARTIAL or BLOCKED run with pending write/write or write/input overlap
with this plan blocks handoff; read/read overlap and disjoint runs do not.
Compare full declared scopes, not only paths already written. Name the other
plan, overlap and pending work. An old or malformed relevant ledger requires
reconciliation: the owner or an explicit user decision must establish inactivity
and resolve pending writes and current content. Never delete or rewrite its
ledger, expire it by age, or treat dirty consent as conflict resolution. These
read-only checks do not promise atomic concurrent exclusion.

For each dirty writable file, show the delta and bind any inclusion offer to
its current bytes, type, mode and deletion state. Use read-only git hash-object
for file bytes and identify symlink targets without following them. Preserve
unusual filenames unambiguously. Recheck identities before forwarding approval;
changed content needs renewed consent, not silent reuse of a path-only answer.
Inclusion preserves user work and never authorizes overwriting it.

Verified output of a declared completed upstream run may be included without
redundant dirty consent only when END: DONE, readable checkpoints, fresh passing
dependency checks and attribution evidence identify the exact current delta,
type and mode, and no conflict remains. Show the producer, checkpoint and
content identities as Preexisting evidence. Whole-tree checkpoint presence or
matching paths alone is not authorship. Missing attribution or changed output
falls back to targeted consent for writable files, never automatic inclusion.

Withhold execution approval for an unresolved relevant conflict or changed
protected input, a detached branch, or an unresolved default branch. Require
branch consent on the configured default branch and on main or master. On a
ready named branch, offer `execute` when no consent is needed or
`execute on <branch>` when branch consent is needed. Offer execute with dirty files only
for the displayed relevant content needing consent, not Foreign or verified
upstream output. When more than one consent is needed, require each offered
command. Pass the evidence to the executor for fresh verification; do not
create runtime records here.

A user-supplied Subagent-driven or Inline preference receives one short note that execution uses the native gateway. Do not ask for an execution-method choice. Route each valid approval to /internal-gateway-execute-plans; do not start execution or create a runtime record here.
