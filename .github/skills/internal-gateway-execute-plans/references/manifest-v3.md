# Manifest v3 Reference

This executor-local reference is loaded for Execution Manifest preflight and
execution review. Its parser and `scripts/run.sh preflight` remain the sole
mechanical authority.

## Top-Level Contract

A current Manifest v3 has exactly these fields:

- `schema_version`: `3`
- `manifest_version`: `execution-manifest/v3`
- `plan_id`: non-empty string
- `repository_root`: exactly `.`
- `authority_boundaries`
- `delegation`
- `targets`
- `controls`
- `validations`
- `manual_obligations`
- `tasks`
- `retry_policy`
- `approval`
- `bootstrap`
- `rollout`
- `handoff`

Field sets are exact: unknown or missing fields are rejected, and duplicate
JSON keys are rejected. No approval digest, runtime status, delivery verdict,
task progress, or content-hash field belongs in the plan. Approval evidence is
external and contains the computed current Manifest `semantic_fingerprint`.

## Nested Rules

- `authority_boundaries` has exactly `normative_owner`, `execution_owner`,
  `worker`, `caller_owns`, `protected_paths`, and `no_git_mutation`; the last
  field is `true` and `.git/**` is protected.
- `delegation` has exactly `schema_version`, `mode`, `worker`, `result`,
  `receipt`, and `acceptance`. Current plans use `1`, `none`,
  `primary-owner`, `not_applicable`, `null`, and `null`.
- `targets` have `id`, `path`, and `state`; `condition` is the only optional
  field. `state` is required on every target and is `create`, `modify`, or
  `inspect`; paths must not point into `.git/**`.
- `controls` is a non-empty JSON object map, never an array. Keys are the
  Control Inventory IDs in uppercase ID form and must match the inventory
  table exactly. Each value has exactly `class`, `owner`, and `binding`.
  Classes are
  `automatable-local`, `observable-runtime`, `external-capability`,
  `authority-or-scope`, and `genuine-human-judgment`.
- `validations` have exactly `id`, `command`, `owner`, `pass_signal`, and
  `phases`; `equivalence` is optional. Phases are `baseline`, `focused`, and
  `final`. Commands must be directly executable and must not mutate Git. IDs
  are unique.
- `manual_obligations` items have exactly `id`, `kind`, `required`, and
  `acceptance`; kind is `human` or `external`. The list may be empty.
- `tasks` have exactly `id`, `order`, `posture`, `objective`, `depends_on`,
  `target_ids`, `validation_ids`, `manual_obligation_ids`, `acceptance`, and
  `stop_conditions`. References must resolve to existing IDs; `order` is a
  unique positive integer and matches the Markdown task-heading order.
- `retry_policy` has exactly `initial_attempts`, `max_context_refills`,
  `max_corrective_retries`, `caller_may_lower`, `repeat_progress_status`, and
  `minor_or_cosmetic_reopens`. New plans default to `1`, `1`, `3`, `true`,
  `stalled`, and `false`; corrective retries are finite per task and the
  executor accepts values from `1` through `5`.
- `approval` has exactly `editorial_content_change` and
  `normative_manifest_change`, both non-empty strings. Editorial Markdown
  drift does not change the parsed Manifest; normative Manifest drift requires
  refreshed external approval.
- `bootstrap` has exactly `mode`, `compatibility_projection`,
  `projection_binding`, `legacy_only`, and `retirement_evidence`. Current
  output is `manifest-only` with an empty compatibility projection,
  `legacy_only: reject`, and bindings to `manifest.controls`, `manifest.tasks`,
  `manifest.validations`, and `manifest.authority_boundaries`.
- `rollout` is a non-empty list of strings.
- `handoff` has exactly `next_owner`, `requires`, `status_sibling`, and
  `git_mutation`. `next_owner` is `/internal-gateway-execute-plans`;
  `requires` must contain the exact canonical strings `human approval`,
  `exact Manifest v3 review`, and `zero blocking preflight findings`;
  `status_sibling` is `none`; and `git_mutation` is `prohibited`.

## Markdown Projection

Control Inventory IDs must equal `manifest.controls` keys, bijective in both
directions; the inventory table contains only the header row, the separator
row, and one row per control ID. Ordered Task headings must equal
`manifest.tasks` IDs in manifest order, and task references must resolve to
manifest targets, validations, manual obligations, and tasks. A current
manifest-only plan has no `## Execution Contract`.

## Plan Markdown Binding

- Required headings are exactly `## Goal`, `## Global Constraints`,
  `## Repository Preflight`, and `## Control Inventory`, each at exact level
  two. Heading text must match exactly after the marker with no suffix or
  trailing punctuation.
- `## Global Constraints` contains an explicit no-Git bullet such as
  `- No Git mutation.`
- `## Repository Preflight` is the canonical heading for new plans and
  contains the four bold bullets `- **Baseline Validation:**`,
  `- **Recovery Policy:**`, `- **Escalation Conditions:**`, and
  `- **User-Facing Report:**`, each with a concrete value.
- The `## Execution Manifest` heading text is exact with no version suffix;
  its section body is exactly one fenced JSON code block opened with the
  `json` language tag and contains no surrounding prose.
- Each manifest task has one `## Task N: <title>` heading at any level from
  two to six, numbered consecutively in manifest order; manifest task ids are
  exactly `T1` through `T<N>` and match the heading numbers. Task headings
  exist only for manifest tasks; no other `Task N:` heading may appear.
- Control Inventory first-column IDs use uppercase `[A-Z][A-Z0-9-]+` form.

## Canonical Authoring Blocks

- `delegation`:

  ```json
  {"schema_version": 1, "mode": "none", "worker": "primary-owner", "result": "not_applicable", "receipt": null, "acceptance": null}
  ```

- `retry_policy`:

  ```json
  {"initial_attempts": 1, "max_context_refills": 1, "max_corrective_retries": 3, "caller_may_lower": true, "repeat_progress_status": "stalled", "minor_or_cosmetic_reopens": false}
  ```

- `bootstrap`: mode `manifest-only`, an empty `compatibility_projection`,
  `projection_binding` exactly `controls: manifest.controls`,
  `tasks: manifest.tasks`, `validations: manifest.validations`, and
  `authority: manifest.authority_boundaries`, `legacy_only: reject`, and a
  concrete non-empty `retirement_evidence`.
- `handoff`: `next_owner` `/internal-gateway-execute-plans`; `requires`
  exactly `["human approval", "exact Manifest v3 review", "zero blocking preflight findings"]`;
  `status_sibling` `none`; `git_mutation` `prohibited`.
- `rollout` such as `["baseline", "focused", "final"]`.

## Runtime Separation

The plan remains separate from the schema-2 YAML status sibling. Status has
exactly `schema_version`, `status`, `plan`, `approval_evidence`,
`delivery_verdicts`, `completed_task_ids`, `remaining_task_ids`,
`last_validation`, `next_action`, `warnings`, and `deviations`. The status
approval evidence contains `source`, the exact statement `explicit execution
approval`, and the external computed `semantic_fingerprint`.

Bootstrap records contain only `check`, `status`, and `next_action`; status is
`PASS` or `BLOCKED`. Delivery records retain the five categories:
`structure`, `semantic_review`, `artifact_provenance`, `source_baseline`, and
`execution_readiness`. Both successful terminal statuses require every category
to pass.

## Projection Checklist

Before handoff, confirm target and authority boundaries, task order and
references, exact field sets, no Git mutation, approval separation, status
separation, and zero blocking findings on both producer gates. Run the writer
structural check
`python3 <writer-bundle>/scripts/check_plan_structure.py <plan> --format compact`
first, then resolve the loaded executor bundle and run
`bash <physical-executor-bundle>/scripts/run.sh preflight <plan> --format compact`
against the exact final plan bytes; a completion or handoff claim requires
fresh zero-blocking evidence from both, and a prose assertion never
substitutes for either. The binding rules above prevent the five observed
producer failures: a manifest heading with a version suffix, `controls`
serialized as an array, missing `manifest_version`, `repository_root`, or
`targets[].state` fields, a missing Baseline Validation preflight bullet, and
non-canonical `handoff.requires` strings. Do not create a status sibling while
writing the plan. The parser wins if prose and parser disagree; do not add a
second parser or a shared cross-bundle dependency.
