# Manifest v3 Reference

This bundle-local reference is loaded only for Execution Manifest authoring or
review. The executor parser and `scripts/run.sh preflight` remain the sole
mechanical authority.

## Top-Level Contract

A current Manifest v3 has exactly these fields:

- `schema_version`: `3`
- `manifest_version`: `execution-manifest/v3`
- `plan_id`: non-empty string
- `repository_root`: `.`
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

No approval digest, runtime status, delivery verdict, task progress, or
content-hash field belongs in the plan. Approval evidence is external and
contains the computed current Manifest `semantic_fingerprint`.

## Nested Rules

- `authority_boundaries` has exactly `normative_owner`, `execution_owner`,
  `worker`, `caller_owns`, `protected_paths`, and `no_git_mutation`; the last
  field is `true` and `.git/**` is protected.
- `delegation` has exactly `schema_version`, `mode`, `worker`, `result`,
  `receipt`, and `acceptance`. Current plans use `1`, `none`,
  `primary-owner`, `not_applicable`, `null`, and `null`.
- `targets` have `id`, `path`, and `state`; `condition` is the only optional
  field. State is `create`, `modify`, or `inspect`.
- `controls` is a non-empty map. Each value has exactly `class`, `owner`, and
  `binding`. Classes are `automatable-local`, `observable-runtime`,
  `external-capability`, `authority-or-scope`, and `genuine-human-judgment`.
- `validations` have exactly `id`, `command`, `owner`, `pass_signal`, and
  `phases`; `equivalence` is optional. Phases are `baseline`, `focused`, and
  `final`. Commands must be directly executable and must not mutate Git.
- `manual_obligations` items have exactly `id`, `kind`, `required`, and
  `acceptance`; kind is `human` or `external`.
- `tasks` have exactly `id`, `order`, `posture`, `objective`, `depends_on`,
  `target_ids`, `validation_ids`, `manual_obligation_ids`, `acceptance`, and
  `stop_conditions`. References must resolve to existing IDs.
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
  `git_mutation`; the owner is `/internal-gateway-execute-plans`, status is
  `none`, and Git mutation is `prohibited`.

## Markdown Projection

Control Inventory IDs must equal `manifest.controls` keys. Ordered Task
headings must equal `manifest.tasks` IDs. Task references must resolve to
manifest targets, validations, manual obligations, and tasks. A current
manifest-only plan has no `## Execution Contract`.

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
separation, and zero blocking physical preflight findings. Do not create a
status sibling while writing the plan. The parser wins if prose and parser
disagree; do not add a second parser or a shared cross-bundle dependency.
