<!-- component-readme:v1 -->
# Code Validation

## Purpose

`tools/validate_code` owns the repository static checks and the sharded Python
test run. It uses the shared `tools/validation_core` event and report
contracts for local and CI-facing output.

## Responsibilities

- Provide `validate-code.sh` at the repository root as the direct code
  entrypoint.
- Select all units by default, or one static leaf (`--leaf`) or one Python
  shard (`--group`).
- Keep Python shards complete and disjoint at the Pytest node-ID boundary.
  The canonical collection is the `testpaths` set in `pytest.ini`.
- Run shard integrity once for an all-stream or all-Python local run, and
  expose it as `python --integrity-only` for the independent CI job.
- Keep an explicit `python --group` run focused on its shard; it does not
  repeat the integrity collection.

## Speed

- Units run in parallel (`--max-parallel`, default up to 4).
- Each Python shard runs Pytest with `pytest-xdist`. The CPUs are split
  across the shards that run at the same time, so one CI shard uses every
  runner core and a local all-shard run does not oversubscribe.
- Shard integrity only collects tests, so it overlaps with the shards.
- `--compact` in terminal output prints one line per unit plus a summary, with
  the first failing test or file location as the observed headline.

## Catalog

- Static leaves: `actionlint`, `shell-static-analysis`, `python-dependencies`,
  `python-static-analysis`, `python-lint`, and `python-entrypoints`.
- Python shards: `repository`, `skills-internal`, `skills-terraform-import`,
  and `skills-local`.

Run `./validate-code.sh --list` for the resolved paths. A new test root that
no shard owns fails shard integrity until a shard claims it.

## Inputs and outputs

- Input: stream (`static` or `python`), `--leaf`, `--group`,
  `--integrity-only`, `--serial`, `--max-parallel`, `--fail-fast`,
  `--dry-run`, `--list`, `--tmp-dir`, `--no-color`, and `--compact`. Output
  controls are `--format auto|terminal|ci|json|markdown`, `--result-path`,
  and `--artifact-dir`.
- Output: a redacted `validation-run/v1` report and bounded unit logs below
  `--artifact-dir` when set. A nonzero status is returned for any failed or
  incomplete unit.
- Interpreter: `PYTHON_BIN` when set, else `.github/tools/.venv/bin/python`
  when present, else `python3`.

## Dependencies

- Python from `.python-version` with `.github/tools/requirements.txt`
  (Pytest, pytest-xdist, and Ruff).
- `actionlint` and `shellcheck` on `PATH` for the matching static leaves.
- `requirements/pip-audit.txt` pins the CI dependency audit.

## Validation

`make test` runs the Python stream and `make catalog-lint` runs the static
stream, both with `--compact`.

```bash
./validate-code.sh --dry-run
./validate-code.sh python --integrity-only --format ci
python3 -m pytest -q tools/validate_code/tests tools/validation_core/tests
```
