# Plan Run Protocol

This reference owns the marked shell commands used by the native plan executor.
Each block uses only the environment variables named in its task interface.

- [Checkout classification](#checkout-classification)
- [Commands](#commands)
- [Records](#records)

## Checkout classification

Apply this classification at preflight, before each task, on resume, and before
completion. Whole-repository checkpoints are observations, not ownership proof.

- Writable scope is the full union of task `Files`, including future files and
  allowed globs. An individual task may write only its own `Files`.
- Relevant paths include writable scope and protected inputs: the plan, spec,
  declared dependency plans and explicitly declared input/output paths. A
  dependency output is read-only unless this plan explicitly lists it in
  `Files`; the plan and spec remain read-only. Record input content identities
  at approval in a `Ruling` and compare them at subsequent gates, including
  sources under scratch paths excluded from checkpoints. A changed protected
  input requires reevaluation; dirty consent cannot authorize it.
- Inspect other retained plan ledgers under `tmp/superpowers/plans/` in this
  checkout, excluding this run. Compare declared writable scopes against each
  other's writable scopes and protected inputs, not just current dirty paths.
  Read/read overlap is harmless. `RUNNING`, `PARTIAL`, or `BLOCKED` with pending
  overlapping writes is a conflict. A malformed relevant ledger requires
  reconciliation, not an assumption that it is inactive. Disjoint runs do not
  block. Use `CHECKOUT_CHANGED/foreign-edit` for a relevant conflict and name
  the plan, overlap and pending work. Dirty consent never overrides it.
- An old timestamp does not release a conflict. Reconciliation by the run's
  owner or an explicit user decision must establish that it is inactive and
  resolve its pending writes and current content before a fresh check. Record
  the evidence in a `Ruling`; never delete or rewrite another run's ledger.
  These checks detect observed conflicts, not atomic concurrent exclusion.
- Audit the full `cmd:changed-paths` output before filtering, checking both
  rename endpoints and protected paths first. A proven executor write outside
  the active task is `OUT_OF_PERIMETER/file`, or `/protected` where applicable.
  A required out-of-scope write also stops; never hide either as Foreign.
- Changes outside relevant paths with no evidence of an executor violation
  are Foreign: preserve them, record paths and evidence in a `Ruling`, disclose
  them in chat and reviewer context, and exclude them from run-output diffs.
  When origin is unknown, label the anomaly as unattributed rather than
  inventing ownership. Such an unrelated anomaly alone does not block.
- A relevant uncertain-origin delta needs targeted consent. Show its paths and
  delta and bind the offered `execute with dirty files` command to the current
  per-file content, type, mode and deletion state. Hash file bytes with read-only
  `git hash-object`; for symlinks identify the link target, not its referent.
  Recheck before consuming consent. Changed evidence invalidates that offer.
  Record inclusion in `APPROVAL` at first start and in a `Ruling` on later
  inclusion, preserving the old record and identifying the compared checkpoints
  or saved delta. Quote unusual filenames unambiguously. Consent includes
  content; it grants neither overwrite permission nor a wider task perimeter.
- Auto-include an upstream delta only when a declared producer has `END: DONE`,
  readable checkpoints, fresh passing dependency checks and evidence attributing
  that exact delta to its completed work. Current content, type and mode must
  match and no conflicting run may remain. Record producer, checkpoint and
  content identities as Preexisting. Mere presence in a whole-tree checkpoint,
  timestamps or matching paths does not establish authorship; otherwise use
  targeted consent. Never infer a missing producer or silently adopt changed
  output. Reevaluate read-only dependency outputs rather than including them.

Existing approved or attributable run output is not new dirty work just because
it remains uncommitted. On resume, compare against its latest evidenced state,
not the initial approval blob after legitimate task writes. Automatic partial
resume needs write evidence matching the current delta in the started task;
path containment, same-session identity and a post-test snapshot alone are
insufficient. For accepted edits to completed work, reconcile affected validation
and downstream assumptions before resuming; consent alone does not keep earlier
test results valid.

Use `cmd:task-diff` with exact selected output paths after this audit. Final
review also receives all Foreign and unattributed `Ruling` entries and inclusion
evidence. A selected file can contain included preexisting work; do not claim
sole authorship. Required checks run on the observed checkout: Foreign-caused
failures still fail, and passing checks do not prove isolated-patch reproducibility.

## Commands

### Object store

Checkpoint and probe objects live in `$RUN_DIR/objects`. Repository objects
are read through Git alternates, so no block writes `.git`. The same run works
where `.git` is writable, such as Copilot in VS Code, and where it is read-only,
such as the Codex `workspace-write` sandbox.

Every block that writes or reads a checkpoint starts with the same store
prelude:

- The block body is one subshell, so `set -eu`, `cd`, and the Git redirect
  never leak into the persistent shell. Never export `GIT_OBJECT_DIRECTORY` or
  `GIT_ALTERNATE_OBJECT_DIRECTORIES` in the caller shell.
- The block moves to the repository top level. A relative `RUN_DIR` is resolved
  from there.
- A checkpoint object exists only through this redirect. Read checkpoints only
  through a marked block; plain `git cat-file`, `git diff`, or `git ls-tree` on
  a `CPn` reports a missing object.

Set block inputs as shell variables immediately before the block in the same
command, for example `RUN_DIR=<run dir> CP=<tree>` followed by the block.

During preflight, before publishing a ledger, the executor runs this block to create the run-directory object store and prove that Git can write and read a new object there.

<!-- cmd:object-probe -->
```sh
(
  set -eu
  unset GIT_OBJECT_DIRECTORY GIT_ALTERNATE_OBJECT_DIRECTORIES
  top=$(git rev-parse --show-toplevel)
  cd "$top"
  common=$(cd "$(git rev-parse --git-common-dir)" && pwd)
  mkdir -p "$RUN_DIR/objects"
  RUN_DIR=$(cd "$RUN_DIR" && pwd)
  GIT_OBJECT_DIRECTORY="$RUN_DIR/objects"
  GIT_ALTERNATE_OBJECT_DIRECTORIES="$common/objects"
  export GIT_OBJECT_DIRECTORY GIT_ALTERNATE_OBJECT_DIRECTORIES
  oid=$(printf 'probe %s %s\n' "$(date -u +%Y%m%dT%H%M%SZ)" "$$" | git hash-object -w --stdin)
  git cat-file -e "$oid"
)
```

At first-start setup and after every task or fix round, the executor runs this block to capture a checkpoint of the whole repository without touching the real index. Scratch paths that ignore rules do not cover are excluded before hashing; tracked scratch entries are removed afterward.

<!-- cmd:checkpoint -->
```sh
(
  set -eu
  unset GIT_OBJECT_DIRECTORY GIT_ALTERNATE_OBJECT_DIRECTORIES
  top=$(git rev-parse --show-toplevel)
  cd "$top"
  common=$(cd "$(git rev-parse --git-common-dir)" && pwd)
  mkdir -p "$RUN_DIR/objects"
  RUN_DIR=$(cd "$RUN_DIR" && pwd)
  GIT_OBJECT_DIRECTORY="$RUN_DIR/objects"
  GIT_ALTERNATE_OBJECT_DIRECTORIES="$common/objects"
  export GIT_OBJECT_DIRECTORY GIT_ALTERNATE_OBJECT_DIRECTORIES
  idx="$RUN_DIR/cp.idx"
  set -- ':/'
  for scratch in .superpowers tmp; do
    git check-ignore -q --no-index "$scratch/" || set -- "$@" ":(exclude,top)$scratch"
  done
  GIT_INDEX_FILE="$idx" git read-tree HEAD
  GIT_INDEX_FILE="$idx" git add -A -- "$@"
  GIT_INDEX_FILE="$idx" git rm -r -q --cached --ignore-unmatch -f -- ':/.superpowers' ':/tmp'
  GIT_INDEX_FILE="$idx" git write-tree
)
```

During resume and HEAD-adoption checks, the executor runs this block to compare HEAD with the latest checkpoint while excluding scratch paths.

<!-- cmd:head-tree -->
```sh
(
  set -eu
  unset GIT_OBJECT_DIRECTORY GIT_ALTERNATE_OBJECT_DIRECTORIES
  top=$(git rev-parse --show-toplevel)
  cd "$top"
  common=$(cd "$(git rev-parse --git-common-dir)" && pwd)
  mkdir -p "$RUN_DIR/objects"
  RUN_DIR=$(cd "$RUN_DIR" && pwd)
  GIT_OBJECT_DIRECTORY="$RUN_DIR/objects"
  GIT_ALTERNATE_OBJECT_DIRECTORIES="$common/objects"
  export GIT_OBJECT_DIRECTORY GIT_ALTERNATE_OBJECT_DIRECTORIES
  idx="$RUN_DIR/head.idx"
  GIT_INDEX_FILE="$idx" git read-tree HEAD
  GIT_INDEX_FILE="$idx" git rm -r -q --cached --ignore-unmatch -f -- ':/.superpowers' ':/tmp'
  GIT_INDEX_FILE="$idx" git write-tree
)
```

At CP0 publication, on resume, and on every status query, the executor runs this block to verify that checkpoint `CP` exists; it prints `tree` for a readable checkpoint.

<!-- cmd:checkpoint-type -->
```sh
(
  set -eu
  unset GIT_OBJECT_DIRECTORY GIT_ALTERNATE_OBJECT_DIRECTORIES
  top=$(git rev-parse --show-toplevel)
  cd "$top"
  common=$(cd "$(git rev-parse --git-common-dir)" && pwd)
  mkdir -p "$RUN_DIR/objects"
  RUN_DIR=$(cd "$RUN_DIR" && pwd)
  GIT_OBJECT_DIRECTORY="$RUN_DIR/objects"
  GIT_ALTERNATE_OBJECT_DIRECTORIES="$common/objects"
  export GIT_OBJECT_DIRECTORY GIT_ALTERNATE_OBJECT_DIRECTORIES
  git cat-file -t "$CP"
)
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

For moved HEAD, set `HEAD_BASE` to the last adopted commit or START. After
checking branch identity, inspect every new commit, including merge parents;
a net range diff can hide a relevant edit followed by a revert. Nonzero exit
means ancestry or inspection failed and adoption is withheld. Successful output
is unfiltered NUL-delimited name/status records for scope classification.
Recheck HEAD before recording adoption; retry inspection if it changed.

<!-- cmd:head-changes -->
```sh
(
  set -eu
  unset GIT_OBJECT_DIRECTORY GIT_ALTERNATE_OBJECT_DIRECTORIES
  cd "$(git rev-parse --show-toplevel)"
  git merge-base --is-ancestor "$HEAD_BASE" HEAD
  commits=$(git rev-list "$HEAD_BASE..HEAD")
  for commit in $commits; do
    git diff-tree --no-commit-id --root -m -r --name-status -z --find-renames "$commit"
  done
)
```

After each task checkpoint, the executor runs this block for the perimeter check without losing rename endpoints or unusual filename bytes.

<!-- cmd:changed-paths -->
```sh
(
  set -eu
  unset GIT_OBJECT_DIRECTORY GIT_ALTERNATE_OBJECT_DIRECTORIES
  top=$(git rev-parse --show-toplevel)
  cd "$top"
  common=$(cd "$(git rev-parse --git-common-dir)" && pwd)
  mkdir -p "$RUN_DIR/objects"
  RUN_DIR=$(cd "$RUN_DIR" && pwd)
  GIT_OBJECT_DIRECTORY="$RUN_DIR/objects"
  GIT_ALTERNATE_OBJECT_DIRECTORIES="$common/objects"
  export GIT_OBJECT_DIRECTORY GIT_ALTERNATE_OBJECT_DIRECTORIES
  git diff --name-status -z --find-renames "$CP_A" "$CP_B"
)
```

During the per-task review-package step and the final review, the executor runs
this block to save binary-safe evidence for a checkpoint range. `CP_A` may also
be the START commit. Pass the selected repository-relative file paths as
quoted positional parameters (`set -- 'src/file' 'tests/file'` before the
block). Select exact changed files only after the full changed-path audit,
including both rename endpoints. Never pass directories or unexpanded globs.
An absent selection fails closed; when the audited selection is empty, create
an empty review file explicitly and record that no run output changed.
Renames render as deletion/addition so path filtering cannot pull in Foreign
content through rename detection. Literal path handling preserves unusual names.

<!-- cmd:task-diff -->
```sh
(
  set -eu
  unset GIT_OBJECT_DIRECTORY GIT_ALTERNATE_OBJECT_DIRECTORIES
  top=$(git rev-parse --show-toplevel)
  cd "$top"
  common=$(cd "$(git rev-parse --git-common-dir)" && pwd)
  mkdir -p "$RUN_DIR/objects"
  RUN_DIR=$(cd "$RUN_DIR" && pwd)
  GIT_OBJECT_DIRECTORY="$RUN_DIR/objects"
  GIT_ALTERNATE_OBJECT_DIRECTORIES="$common/objects"
  export GIT_OBJECT_DIRECTORY GIT_ALTERNATE_OBJECT_DIRECTORIES
  [ "$#" -gt 0 ] || exit 2
  git --literal-pathspecs diff --binary --no-renames "$CP_A" "$CP_B" -- "$@" > "$RUN_DIR/$DIFF_NAME"
)
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
<YYYY-MM-DDTHH:MM:SSZ> Final review: started (reviewer=fresh <model>)
<YYYY-MM-DDTHH:MM:SSZ> Final review: started (reviewer=self)
<YYYY-MM-DDTHH:MM:SSZ> Focus: <item> -> <test>
<YYYY-MM-DDTHH:MM:SSZ> Focus: <item> -> uncovered - <disposition>
<YYYY-MM-DDTHH:MM:SSZ> Regrade: <finding> <old>-><new> - <reason>
<YYYY-MM-DDTHH:MM:SSZ> Final: fixed <summary> (CP<n>, red->green: <test>, suite: <command> -> exit 0, evidence: <log>)
<YYYY-MM-DDTHH:MM:SSZ> Final review: done (CP<n>)
<YYYY-MM-DDTHH:MM:SSZ> STOP: code=<CODE> cause=<cause> evidence=<text> next=<action>
<YYYY-MM-DDTHH:MM:SSZ> END: DONE
<YYYY-MM-DDTHH:MM:SSZ> END: PARTIAL
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
CHECKOUT_CHANGED/foreign-commit -> reconcile the relevant commits, branch or ancestry and reevaluate before resume
CHECKOUT_CHANGED/foreign-edit -> reconcile the named conflicting run or relevant delta before resume
CHECKOUT_CHANGED/ledger-mismatch -> reconcile
CHECKOUT_CHANGED/approval-stale -> reconcile, then approve again
OUT_OF_PERIMETER/file -> rewrite plan or undo the change
OUT_OF_PERIMETER/protected -> authorize <path> explicitly or choose another approach
TEST_FAILED/exhausted -> read <log> and say whether the test or the code is wrong
CHECKPOINT_MISSING/<CPn> -> reconcile
STORAGE_DENIED/run-dir -> grant write access to the run directory, then resume
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

<!-- example:final-ledger -->
```text
# Run ledger - plan: tmp/superpowers/plans/one-task-example.md
2026-09-27T13:00:00Z START: abcdef branch=feature
2026-09-27T13:00:01Z APPROVAL: plan=abc123 branch=feature default=main consent=none dirty=none choice=none
2026-09-27T13:00:02Z CP0: c0ffee
2026-09-27T13:00:03Z Task 1: started
2026-09-27T13:00:04Z Task 1: complete (CP1, tests: pytest -q -> exit 0)
2026-09-27T13:00:05Z CP1: c1ffee
2026-09-27T13:00:06Z Final review: started (reviewer=fresh gpt-5)
2026-09-27T13:00:07Z Focus: empty title -> test_empty_title_rejected
2026-09-27T13:00:08Z Focus: unicode title -> uncovered - low harm: every current caller sends ASCII titles; deferred as a minor
2026-09-27T13:00:09Z Regrade: blank title saved Minor->Important - a user silently loses the record title
2026-09-27T13:00:10Z Final: fixed blank title saved (CP2, red->green: test_blank_title_rejected, suite: pytest -q -> exit 0, evidence: tmp/superpowers/plans/one-task-example/final-fix-tests.log)
2026-09-27T13:00:11Z CP2: c2ffee
2026-09-27T13:00:12Z Final review: done (CP2)
2026-09-27T13:00:13Z END: DONE
```
