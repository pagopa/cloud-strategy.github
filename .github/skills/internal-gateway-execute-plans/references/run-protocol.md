# Plan Run Protocol

This reference owns the marked shell commands used by the native plan executor.
Each block uses only the environment variables named in its task interface.

## Commands

During preflight, before publishing a ledger, the executor runs this block to prove that Git can write and read a new object.

<!-- cmd:object-probe -->
```sh
set -eu
oid=$(printf 'probe %s %s\n' "$(date -u +%Y%m%dT%H%M%SZ)" "$$" | git hash-object -w --stdin)
git cat-file -e "$oid"
```

At first-start setup and after every task or fix round, the executor runs this block to capture a checkpoint without touching the real index.

<!-- cmd:checkpoint -->
```sh
set -eu
idx="$RUN_DIR/cp.idx"
GIT_INDEX_FILE="$idx" git read-tree HEAD
GIT_INDEX_FILE="$idx" git add -A -- .
GIT_INDEX_FILE="$idx" git rm -r -q --cached --ignore-unmatch -f -- .superpowers tmp
GIT_INDEX_FILE="$idx" git write-tree
```

During resume and HEAD-adoption checks, the executor runs this block to compare HEAD with the latest checkpoint while excluding scratch paths.

<!-- cmd:head-tree -->
```sh
set -eu
idx="$RUN_DIR/head.idx"
GIT_INDEX_FILE="$idx" git read-tree HEAD
GIT_INDEX_FILE="$idx" git rm -r -q --cached --ignore-unmatch -f -- .superpowers tmp
GIT_INDEX_FILE="$idx" git write-tree
```

During preflight, the executor runs this block to resolve the configured default branch, reporting unresolved when no origin HEAD is available.

<!-- cmd:default-branch -->
```sh
ref=$(git symbolic-ref --quiet --short refs/remotes/origin/HEAD 2>/dev/null) && printf '%s\n' "${ref#origin/}" || printf 'unresolved\n'
```

During preflight, the executor runs this block to identify the current branch, reporting detached when HEAD is detached.

<!-- cmd:current-branch -->
```sh
git symbolic-ref --quiet --short HEAD 2>/dev/null || printf 'detached\n'
```

After each task checkpoint, the executor runs this block for the perimeter check without losing rename endpoints or unusual filename bytes.

<!-- cmd:changed-paths -->
```sh
git diff --name-status -z --find-renames "$CP_A" "$CP_B"
```

During the per-task review-package step, the executor runs this block to save binary-safe evidence for the checkpoint range.

<!-- cmd:task-diff -->
```sh
git diff --binary "$CP_A" "$CP_B" > "$RUN_DIR/$DIFF_NAME"
```

## Records

<!-- protocol:status -->
```text
Plan: <plan path>
State: RUNNING|PARTIAL|BLOCKED|DONE
Executor: native
Tasks: <complete>/<total>
Current: Task <N> <title>|none
Checkpoint: CP<n> <tree>|none
Blocker: <CODE>/<cause>: <evidence>|none
Next: <action>|none
Updated: <YYYY-MM-DDTHH:MM:SSZ>
```

<!-- protocol:ledger -->
```text
# Run ledger - plan: <plan path>
<YYYY-MM-DDTHH:MM:SSZ> START: <head> branch=<branch>
<YYYY-MM-DDTHH:MM:SSZ> APPROVAL: plan=<blob> branch=<branch> default=<branch|unresolved> consent=<default-branch|none> dirty=<path:blob;...|none> choice=<include|none>
<YYYY-MM-DDTHH:MM:SSZ> CP<n>: <tree>
<YYYY-MM-DDTHH:MM:SSZ> Task <N>: started
<YYYY-MM-DDTHH:MM:SSZ> Task <N>: resumed on partial state
<YYYY-MM-DDTHH:MM:SSZ> Task <N>: repair <k>/2 - <cause>
<YYYY-MM-DDTHH:MM:SSZ> Task <N>: complete (CP<n>, tests: <command> -> exit 0)
<YYYY-MM-DDTHH:MM:SSZ> HEAD adopted: <old> -> <new>
<YYYY-MM-DDTHH:MM:SSZ> Ruling: <text>
<YYYY-MM-DDTHH:MM:SSZ> RESUME: from CP<n>
<YYYY-MM-DDTHH:MM:SSZ> Final review: started
<YYYY-MM-DDTHH:MM:SSZ> Final: fixed <summary> (CP<n>)
<YYYY-MM-DDTHH:MM:SSZ> Final review: done (CP<n>)
<YYYY-MM-DDTHH:MM:SSZ> STOP: code=<CODE> cause=<cause> evidence=<text> next=<action>
<YYYY-MM-DDTHH:MM:SSZ> END: DONE|PARTIAL
```

<!-- protocol:derivation -->
```text
State: last of START|RESUME|STOP|END; END: DONE -> DONE; END: PARTIAL -> PARTIAL; STOP -> BLOCKED; START|RESUME -> RUNNING
Tasks: distinct Task <N>: complete / count of ### Task headings in the plan
Current: last Task <N>: started without a later Task <N>: complete, else none
Checkpoint: last CP<n>, else none
Blocker: <code>/<cause>: <evidence> of the last STOP when State is BLOCKED, else none
Next: next of the last STOP when BLOCKED; resume when PARTIAL; else none
Updated: timestamp of the last event line
```

<!-- protocol:stop-codes -->
```text
PLAN_INVALID/legacy -> rewrite plan
PLAN_INVALID/prose-dep -> rewrite plan
PLAN_INVALID/plan-wrong -> rewrite plan
DEPENDS_FAILED/<plan> -> execute <plan> first
NEEDS_CONSENT/default-branch -> execute on <branch>
NEEDS_CONSENT/dirty -> execute with dirty files
NEEDS_CONSENT/safety -> type the exact confirmation offered in the message
CHECKOUT_CHANGED/foreign-commit -> undo or confirm the commit, then resume
CHECKOUT_CHANGED/foreign-edit -> stop the other session, then resume
CHECKOUT_CHANGED/ledger-mismatch -> reconcile
CHECKOUT_CHANGED/approval-stale -> reconcile, then approve again
OUT_OF_PERIMETER/file -> rewrite plan or undo the change
OUT_OF_PERIMETER/protected -> authorize <path> explicitly or choose another approach
TEST_FAILED/exhausted -> read <log> and say whether the test or the code is wrong
CHECKPOINT_MISSING/<CPn> -> reconcile
STORAGE_DENIED/git-objects -> grant write access, then resume
STORAGE_DENIED/run-dir -> grant write access, then resume
```

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

<!-- example:ledger -->
```text
# Run ledger - plan: tmp/superpowers/plans/three-task-example.md
2026-09-27T12:00:00Z START: abcdef branch=feature
2026-09-27T12:00:01Z APPROVAL: plan=abc123 branch=feature default=main consent=none dirty=none choice=none
2026-09-27T12:00:02Z CP0: c0ffee
2026-09-27T12:00:03Z Task 1: started
2026-09-27T12:00:04Z Task 1: complete (CP1, tests: pytest -q -> exit 0)
2026-09-27T12:00:05Z CP1: c1ffee
2026-09-27T12:00:06Z Task 2: started
2026-09-27T12:00:07Z Task 2: repair 1/2 - flaky test
2026-09-27T12:00:08Z STOP: code=TEST_FAILED cause=exhausted evidence=tmp/logs/task-2.log next=read tmp/logs/task-2.log and say whether the test or the code is wrong
```

<!-- example:status -->
```text
Plan: tmp/superpowers/plans/three-task-example.md
State: BLOCKED
Executor: native
Tasks: 1/3
Current: Task 2 <title>
Checkpoint: CP1 c1ffee
Blocker: TEST_FAILED/exhausted: tmp/logs/task-2.log
Next: read tmp/logs/task-2.log and say whether the test or the code is wrong
Updated: 2026-09-27T12:00:08Z
```
