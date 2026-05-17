# Resume Protocol

Use this verify-first protocol when resuming an interrupted or compacted retained
plan execution. The goal is to recover from evidence, not memory.

## Source Pattern

- Comparative source: `tmp/external-comparison/hotl-plugin/skills/resuming/SKILL.md`.
- Adopt verify-first recovery only. Do not import HOTL state files or runtime
  commands.

## Verify-first Sequence

1. List every `done-*` file in the retained plan folder.
2. List every remaining numbered plan file and ignore `dubbi-e-domande.md` as an
   executable file.
3. Read `dubbi-e-domande.md` only for accepted decisions that affect execution.
4. Check `git status` and `git diff` for uncommitted evidence of completed work.
5. Re-run the validators declared by the plan, or name the closest available
   validator and the gap.
6. Produce a status report before editing canonical files.

## Status Report Template

```text
Resume status
Completed steps: <done-* files with evidence>
In-progress steps: <partly applied items>
Pending steps: <remaining numbered files>
Evidence gaps: <missing diff, file, or validator evidence>
Next action: <lowest-numbered safe step>
```

## Reconciliation Rules

- If a `done-*` file exists but the target diff, file, or validator evidence is
  absent, mark the item `UNVERIFIABLE` and reopen the evidence question.
- If a `done-*` file is missing but the diff shows compatible completed work,
  ask for confirmation before creating or updating the marker.
- If validators fail after resume, fix the root cause or route the blocker before
  continuing to later plan files.
- Do not create new `done-*` markers from chat memory alone.
