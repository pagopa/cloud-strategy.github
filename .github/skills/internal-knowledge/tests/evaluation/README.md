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

## Holdout and live runs

Do not open FH or its gold while tuning graders, prompts or expected outputs.
Verify the hash seal as an integrity check only. Live baseline and candidate
runs are deferred to Plan B, which requires Copilot CLI authentication and an
approved runtime configuration.

The Mermaid parser grader returns `not-run` when `mmdc` is unavailable. Static
Mermaid checks still run offline; they do not substitute for parser evidence.
