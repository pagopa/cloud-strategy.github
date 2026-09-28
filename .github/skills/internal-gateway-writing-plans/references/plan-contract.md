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
- The Status path is tmp/superpowers/plans/<plan name>/status.md, using the plan filename without its .md suffix.
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
- Dirty Files paths: git status --porcelain -- <all plan Files paths>; show every matching path or none.

Withhold execution approval when the current branch is detached or the default branch is unresolved. Require branch consent on the configured default branch and on main or master. On a ready named branch, offer execute when no consent is needed or execute on <branch> when branch consent is needed. If Files paths are dirty, also offer execute with dirty files. Offer only commands needed for the observed results. When more than one consent is needed, the user must provide each offered command.

A user-supplied Subagent-driven or Inline preference receives one short note that execution uses the native gateway. Do not ask for an execution-method choice. Route each valid approval to /internal-gateway-execute-plans; do not start execution or create a runtime record here.
