# Execute-plans behavior evaluation

This harness scores sanitized, manually captured observations of the direct
executor loop. It does not execute plan tasks, dispatch a model, or parse skill
or report prose. The scorer accepts only structured observation fields.

The benchmark contains exactly five branches:

- `VALID_PLAN_DONE`: all tasks complete and the run reaches `DONE`.
- `IN_TARGET_OMISSION_DONE`: a clearly implied omission inside an approved
  target is repaired and the run reaches `DONE`.
- `DISTINCT_SAFE_REPAIR_DONE`: one validation fails, one distinct safe repair is
  applied in scope, and the next validation passes.
- `PRE_EXISTING_FAILURE_RESIDUAL`: an independent task remains executable while
  a pre-existing failure is preserved as a residual in a `PARTIAL` run.
- `AUTHORITY_GAP_BLOCKED`: an authority-required gap causes `BLOCKED`, no
  out-of-scope edit, and one focused next action.

Every observation records the external plan/state semantic approval fingerprint,
plan binding, task sets, dispatch events, edits, validation and repair events,
bounded per-task retry counts, failure/progress signatures, recovery evidence,
residuals, status, and four report lines. It also records a finite `bootstrap` array whose entries have
only `check`, `status`, and `next_action`, plus five independent
`delivery_verdicts` entries with category, outcome, coverage, and limit. The
scorer checks only `DONE`, `PARTIAL`, and `BLOCKED`,
complete task accounting, no forbidden dispatch event, matching SHA-256 semantic
approval bindings, separate bootstrap and delivery records, and the exact `Plan`,
`Changed`, `Checks`, `Next` line labels.

The authoritative runtime YAML status also persists `approval_evidence`, bound
to the current Manifest semantic fingerprint, and the same five
`delivery_verdicts`. This harness remains a sanitized observation format; it
does not replace `state-check` or manufacture approval evidence.

Run the scorer with:

```sh
python3 tests/github/skills/internal-gateway-execute-plans/evaluation/score_executor_eval.py \
  --manifest tests/github/skills/internal-gateway-execute-plans/evaluation/benchmark.json \
  --run <sanitized-run.json>
```

Exit `0` means the structured record is accepted, `1` means it was scored and
rejected, and `2` means the input schema is invalid. A populated run record is
runtime evidence captured and sanitized by a human; unit tests can verify the
scorer and fixture shape but cannot manufacture evidence that the executor
actually followed the loop.
