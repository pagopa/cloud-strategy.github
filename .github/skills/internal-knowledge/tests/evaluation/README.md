# Internal Knowledge Evaluation Pack

Offline evaluation data for the `internal-knowledge` skill. It records the
expected behavior, fixtures, grader inputs and compatibility mapping before
any live model run.

## Layout

- [evals.json](evals.json): requirements, cases and trigger queries.
- [bindings.json](bindings.json): case-to-fixture, profile and grader links.
- [fixtures](fixtures/F1.tree.json): repository snapshots stored as JSON trees.
- [gold](gold/F1.gold.json): expected facts and relationships, separate from runtime input.
- [grader-fixtures](grader-fixtures/adr_format.json): good and mutant grader examples.
- [compatibility.json](compatibility.json): mapping from prior scenarios to
  cases.
- [holdout.sha256](holdout.sha256): integrity seal for the FH holdout inputs.

## Evidence states

Every case remains `not-run`. A pack-check or offline grader result is
structural evidence only. It does not show that the skill followed the workflow
or improved a user outcome. Verdicts use `pass`, `fail`, `blocked` and
`not-run`; only `pass` is green.

## Offline checks

Run from the repository root:

```sh
python3 .github/skills/internal-skill-creator/scripts/check_eval_pack.py .github/skills/internal-knowledge/tests/evaluation/evals.json --bundle-root .github/skills/internal-knowledge --skill-name internal-knowledge --format compact
.github/tools/.venv/bin/python -m pytest -q .github/skills/internal-knowledge/tests
.github/tools/.venv/bin/ruff check .github/skills/internal-knowledge
```

The runtime view copies only `SKILL.md`, `references/`, `agents/` and the
fixture tree into a temporary workspace. It excludes `evals/`, `tests/`,
gold answers and grader mutants, then checks for byte-identical planted data.

## Revision coverage

The glossary, progressive-maintenance and migration cases use anchored rubrics
and remain `not-run`. They cover lazy creation, legacy ownership, multi-round
resolution, authority, owner maturity, bounded detection, activation, transfer
and interruption. The report consumer has offline executable v1/v2 checks in
`tests/test_report_migration.py`; path checks do not establish semantic transfer
or complete migration. Existing v1 fixtures remain compatibility checks. The R-REPORT criterion now
selects v2 for new authoring under the accepted contract evolution; its truth
requirement is unchanged. Baseline snapshots used for comparisons stay in disposable session storage.

## Complete setup coverage

The accepted complete-installation request narrows R-OPTIONAL-ARTIFACTS:
evidence-free claims remain forbidden, but an explicitly marked scaffold is
valid preparation in complete setup. Narrow vocabulary updates and ordinary
knowledge maintenance retain the lazy glossary behavior.

FS0-FS2 and C-SETUP-AUDIT, C-SETUP-EMPTY, C-SETUP-REAL, and C-SETUP-REPEAT cover the glossary
placeholder, operational templates in one setup, zero-real-domain mock gate,
technical-folder exclusion, a real project evidenced without a README,
customized-template preservation, retained historical mock, and zero-write
repeat. The audit case covers complete setup as an inspection subject without
permitting installation; existing align cases retain the read-only boundary.
The added rubric cases remain `not-run`; native checks validate the pack,
not observed model idempotence or successful installation.

### Area/Topic setup and migration checks

- FS3 / C-SETUP-AREA-TOPIC: document-only Area and work README scaffolds,
  Topic glossary and root map, four managed guides, and a placement block
  capped at 15 lines. Exact allowlists reject deliverables in either tree.
- FS2 / C-SETUP-MANAGED-REPEAT: current managed setup, custom CRLF outside
  managed blocks, protected tracker templates, and no repeat write attempts.
  The original FS2 file tree is retained byte-for-byte as FS2L and bound to
  C-SETUP-LEGACY-REPEAT; its legacy template protection is unchanged.
- FS4 / C-MIGRATION-OPERATIONAL-DRIFT: propose each exact operational move
  from legacy `docs/domains/` to `work/`, requiring approval and zero writes.
  C-MIGRATION-VERIFIED-MOVE authorizes only the offer transfer. The source
  leaves fixed-path protection only in that binding, replaced by an exact
  old/new sha256 manifest checked before, during, and after the move. Other
  inputs remain protected at their original paths.
- FS5 / C-SETUP-OBSIDIAN: permit managed config only when opted in and
  allowlisted. Check key ownership, existing exclusions, protected private
  config, Markdown links, bounded frontmatter, and approved Base YAML.
  The JSON schemas and Base rendering are not runtime-verified by these tests.

The new graders have good and mutant offline fixtures. Native tests exercise
their composed bindings, including negative cases. All model cases remain
`not-run`; passing a grader self-test does not establish model compliance.

`eval-pack-stale-source` checks source heading anchors, not content hashes.
This checkout has no Makefile regeneration target or generated source-hash
file. Update the authored requirement anchor and run `make skill-lint` plus
the pack checker above; do not invent a hash refresh step.

## Holdout and live runs

Do not open FH or its gold while tuning graders, prompts or expected outputs.
Verify the hash seal as an integrity check only. Live baseline and candidate
runs are deferred to Plan B, which requires Copilot CLI authentication and an
approved runtime configuration.

The Mermaid parser grader returns `not-run` when `mmdc` is unavailable. Static
Mermaid checks still run offline; they do not substitute for parser evidence.

## Contract realignment coverage

Router cases now require zero writes even when a policy path is attested.
Legacy router-block grader fixtures remain offline compatibility examples, not
permission for new skill invocations. Component README cases admit durable
knowledge updates and hand off operational authoring. New anchored rubrics
cover that boundary, semantic standard classification after automation, and
stable principle and standard IDs with file-level strategic links. All revised
and new runtime cases remain `not-run`.
