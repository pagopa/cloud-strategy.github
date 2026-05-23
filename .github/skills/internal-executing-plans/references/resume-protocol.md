# Resume Protocol

Use this verify-first protocol when resuming an interrupted or compacted retained
plan execution. The goal is to recover from evidence, not memory.

## Source Pattern

- Comparative source: `tmp/external-comparison/hotl-plugin/skills/resuming/SKILL.md`.
- Adopt verify-first recovery only. Do not import HOTL state files or runtime
  commands.

## Verify-first Sequence

1. Read `01-change-summary.md` first when present, then
   `02-source-item-ledger.md`, and recover the intended folder purpose, `Uso
   consigliato`, `Mappa file e ruolo`, `Evidence pass iniziale`, `Budget
   lettura`, and source-item coverage.
2. Run the shortest safe evidence pass before reading broadly: target existence, riskiest claim, and nearest validator or explicit gap.
3. Use `rg --no-ignore` or equivalent ignored-file-aware search for retained artifacts under `tmp/`.
4. List every `done-*` file in the retained plan folder.
5. List every remaining numbered plan file and ignore `questions.md` as an
   executable file.
6. Check whether each `done-*` file preserves the completed item and evidence,
  or points to an evidence envelope.
7. Check whether the source-item ledger exists and whether every row has a
   credible status, evidence, and route.
8. Read `questions.md` only for accepted decisions that affect execution.
9. Check `git status` and `git diff` for uncommitted evidence of completed work.
10. Re-run the validators declared by the plan, or name the closest available
   validator and the gap.
11. Produce a status report before editing canonical files.

## Status Report Template

```text
Resume status
Summary control file: <present and usable, missing, or stale>
Source-item ledger: <complete, incomplete, missing, or stale>
Evidence pass: <declared pass, fallback pass, or gap>
Completed steps: <done-* files with evidence>
In-progress steps: <partly applied items>
Pending steps: <remaining numbered files>
Evidence gaps: <missing diff, file, or validator evidence>
Next action: <lowest-numbered safe step>
```

## Reconciliation Rules

- If a `done-*` file exists but the target diff, file, or validator evidence is
  absent, mark the item `UNVERIFIABLE` and reopen the evidence question.
- If `01-change-summary.md` or `02-source-item-ledger.md` is missing or stale
  enough that file roles and source coverage cannot be inferred safely, stop and
  reopen the plan-handoff gap before execution resumes.
- If `Evidence pass iniziale`, `Budget lettura`, or source-item coverage is
  missing, reconstruct the minimum pass from reachable evidence before broad
  reading, or mark the resume state `UNVERIFIABLE`.
- If a `done-*` file lacks an item/evidence table or evidence-envelope pointer,
  reconstruct the item from reachable artifacts or mark it `UNVERIFIABLE`.
- If a source-item ledger row is `PENDING`, `PARTIAL`, `NOT_DONE`,
  `UNVERIFIABLE`, or `BLOCKED`, do not claim completion until the row is
  delivered, intentionally closed with evidence, or reported as a blocker.
- If a `done-*` file is missing but the diff shows compatible completed work,
  ask for confirmation before creating or updating the marker.
- If validators fail after resume, fix the root cause or route the blocker before
  continuing to later plan files.
- Do not create new `done-*` markers from chat memory alone.
