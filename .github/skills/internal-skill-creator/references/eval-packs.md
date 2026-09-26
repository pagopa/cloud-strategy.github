# Skill Evaluation Packs

Use a pack to make a skill's intended behavior reviewable before and after a
change. Keep the pack beside the skill so its cases, fixtures, and references
travel with the bundle.

## Contents

- [Deliverables and workflow](#deliverables-and-workflow)
- [Schema v1](#schema-v1)
- [Case design](#case-design)
- [Trigger queries](#trigger-queries)
- [Evidence and run records](#evidence-and-run-records)
- [Evaluation levels and migration](#evaluation-levels-and-migration)
- [Runtime run plan](#runtime-run-plan)
- [Validation](#validation)

## Deliverables and workflow

For each skill created or behaviorally changed, deliver the skill, its updated
eval pack, and either run evidence or a clear statement that the run remains
unavailable. An editorial touch to a skill without a pack does not require a
new pack; record the missing pack as a non-blocking gap when a host validator
reports it.

Build the pack before judging candidate outputs:

1. Extract requirements from the accepted request and existing contract.
   Include expected outputs, permissions, boundaries, and failure conditions.
2. Map current tests and cases to those requirements. Mark uncovered behavior
   explicitly.
3. Freeze the requirement text and pass/fail criteria before generating model
   outputs. Adding a case is safe; changing a criterion needs a reason and
   approval from the skill owner.
4. Write cases with prompts, starting state, expected result, relevant files,
   assertions, and permitted or forbidden actions.
5. Reuse the skill's native runner or validator where one exists. Keep fixtures
   and checks inside the bundle unless the host owns the behavior being tested.

## Schema v1

Store the pack at `tests/evaluation/evals.json`. It is strict JSON: duplicate
keys, unknown fields, and a non-object top level are errors. Its exact top-level
fields are:

- `schema`: `skill-eval-pack/v1`.
- `skill`: the bundle directory name.
- `requirements`: a non-empty list of `{id, text, source}`. IDs match
  `R-[A-Z0-9-]+` and are unique.
- `cases`: a non-empty list described below. Every requirement must appear in
  at least one case.
- `triggers`: an object with a `queries` list. Query IDs match
  `Q-[A-Z0-9-]+`; each query has a non-empty prompt, a boolean
  `should_trigger`, and a `split` of `train` or `held-out`. `competing_owner`
  may name the skill that should own a near-miss.

Each case has a unique `C-[A-Z0-9-]+` ID, `family`, `kind`, non-empty
`requirement_ids`, `prompt`, `initial_state`, and `expected_output`, plus
`files`, `assertions`, `forbidden_actions`, `status`, and `held_out`. Requirement
references must resolve. `files` is a list, and each path must be relative,
name an existing regular file inside the bundle, and remain inside it through
symlinks.

Use `kind: deterministic` when an executable expected result can distinguish
correct from incorrect behavior. Such a case must name a `defective_fixture`
file that satisfies the same path rule. Use `kind: rubric` for judgment tasks and provide `rubric`
with anchored `pass` and `fail` lists. Do not require outputs to repeat
instruction wording. Assertions have unique IDs within the case, explanatory
text, and a boolean `critical` flag. `forbidden_actions` lists unsafe or
out-of-contract behavior; it may be empty.

Case `status` is `generated`, `not-run`, or `blocked`. These values describe
the specification's evidence state, not an observed result. `held_out` is a
boolean. Trigger queries must include both trigger outcomes and both splits.

Finding codes shared by the creator checker and host validator are:

- `eval-pack-invalid-json`, `eval-pack-schema`, `eval-pack-duplicate-id`;
- `eval-pack-unresolved-requirement`, `eval-pack-uncovered-requirement`;
- `eval-pack-missing-defective-fixture`, `eval-pack-missing-rubric`;
- `eval-pack-invalid-status`, `eval-pack-unsafe-path`;
- `eval-pack-trigger-coverage`;
- `eval-run-unbacked-result`, `eval-run-assertion-mismatch`.

The host change-scope gate also reports `eval-pack-missing-new-skill` as a
blocker for a newly added internal skill and
`eval-pack-missing-touched-skill` as a non-blocking notice for a pre-existing
skill with no pack. Deleted bundles are skipped. The catalog validator checks
packs that exist.

## Case design

Use families that represent real changes and common failure modes. Select the
families that match the skill rather than filling a quota:

- first-time skill creation and material ambiguity in the request;
- a bounded revision, a mandatory rule moved behind a conditional reference,
  and regressions in neighboring behavior;
- replacement and retirement, including removal of old entrypoints;
- a competing owner, untrusted instructions in inspected data, and a missing
  dependency;
- held-out downstream work, self-revision, and delegation boundaries.

For deterministic cases, make the defect observable in a fixture. For rubric
cases, anchor each rating in evidence a reviewer can point to. The expected
output should describe the user-visible result, not mirror phrases from the
skill. Include enough initial state and files for another person to reproduce
the case.

## Trigger queries

Build a useful set of about 20 realistic, detailed queries with near-misses.
Cover the skill's main branches and competing owners. Keep the training and
held-out split visible so prompt tuning does not consume every evaluation
example. Repeat each query three times only during an explicitly approved
runtime run; repeated static cases do not provide runtime evidence.

## Evidence and run records

Case specifications use only `generated`, `not-run`, and `blocked`. Store
observed execution separately under `tests/evaluation/runs/`. A run record has
`schema: skill-eval-run/v1`, the skill name, date, host, pinned model,
configuration (`with-skill`, `baseline-none`, or `baseline-previous`), and case
results. Each result names a case, status (`executed`, `passed`, `failed`, or
`blocked`), transcript reference when executed, and assertion verdicts.

The run's assertion IDs must match that case's IDs exactly, including when a
grader records no passing assertions. Each case appears at most once per run,
and every verdict carries string evidence. A passed result needs evidence for
every assertion and all assertions must pass. An executed result with a failed
critical assertion must be recorded as `failed`; `blocked` means the
assertions were not evaluated. Do not change a case specification to imply it
ran.

## Evaluation levels and migration

Separate three kinds of evidence:

1. **Structure:** the checker confirms schema, references, paths, and coverage.
2. **Authoring behavior:** cases and review assess whether the creator follows
   its process and produces a usable bundle.
3. **Downstream effectiveness:** approved runs compare task outcomes with and
   without the skill.

A structural pass says nothing by itself about authoring quality or model
effectiveness. Migrate another skill's bespoke pack only when its behavior
changes. Editorial changes preserve the old pack and may carry a non-blocking
missing-pack notice.

## Runtime run plan

Obtain explicit user approval before any model or paid runtime run. Start with
GPT-6, then keep host, model, tools, inputs, and budget fixed across variants.
Use isolated sessions. A pilot of three runs per case and variant can expose
obvious issues but is not statistical proof. Include held-out cases, read the
transcripts, and blind and reorder output review where practical. Compare with
no skill when the host can isolate that condition; for a revision, use the
frozen previous version as the baseline. Record unavailable comparisons as a
gap rather than inferring a win.

## Validation

Run `scripts/check_eval_pack.py` with the bundle root and skill name. It checks
the portable pack and may also check a run record. A host validator is an
additional consumer when the host provides one; the bundle checker must not
depend on it.
