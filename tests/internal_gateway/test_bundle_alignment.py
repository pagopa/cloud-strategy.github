"""Cross-bundle alignment guard for the writer checker and executor parser.

The skeleton pin proves the canonical reference skeleton enumerates exactly the
field sets both parsers accept. The differential harness stages schema-derived
structural mutations under a repo-neutral retained directory so the writer
checker and the executor parser grade identical bytes, then asserts the parity
invariant: an executor blocking outcome implies a writer-check blocking
outcome. Writer-stricter outcomes (the writer blocks while the executor passes)
are permitted and are not failures. Non-structural executor blocks, such as
runtime status sibling binding, are out of corpus by rule because they do not
describe Manifest structure.
"""
from __future__ import annotations

import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
WRITER_BUNDLE = REPO_ROOT / ".github" / "skills" / "internal-gateway-writing-plans"
EXECUTOR_BUNDLE = REPO_ROOT / ".github" / "skills" / "internal-gateway-execute-plans"
WRITER_REFERENCE = WRITER_BUNDLE / "references/manifest-v3.md"
EXECUTOR_REFERENCE = EXECUTOR_BUNDLE / "references/manifest-v3.md"
WRITER_CHECKER = WRITER_BUNDLE / "scripts/check_plan_structure.py"
EXECUTOR_PARSER = EXECUTOR_BUNDLE / "scripts/plan_execution.py"
SKELETON_HEADING = "## Canonical Complete Skeleton"
FIELD_FINDING_CODES = frozenset({"missing-manifest-field", "unknown-manifest-field"})
MINIMUM_EXECUTOR_BLOCKING_CASES = 17

MINIMAL_PLAN_TEMPLATE = """# Example Plan

## Goal

Exercise the canonical skeleton.

## Global Constraints

- No Git mutation.

## Target Census

| Census ID | Target | Search | Hits | Disposition |
| --- | --- | --- | --- | --- |
| TC-01 | TGT-01 | `rg -n "target" path/to/target.py` | path/to/target.py:1 | Modify scope for T1. |

## Execution Authorization

- Mode: execution-ready
- Authorization: "Authorize execution-ready authoring of the canonical skeleton plan."

## Completeness Audit

| Census ID | Command | Evidence | Result |
| --- | --- | --- | --- |
| TC-01 | `rg -n "target" path/to/target.py` | path/to/target.py:1 | Covered by T1. |

## Repository Preflight

- **Baseline Validation:** run `python3 -m pytest -q tests/example` before edits and record the result.
- **Recovery Policy:** use one bounded, distinct, task-local repair.
- **Escalation Conditions:** stop for authority, scope, safety, or unresolved task-local barriers.
- **User-Facing Report:** report the outcome, evidence, and next action.

## Control Inventory

| ID | Requirement | Class | Owner | Command or trigger | Pass/fail | Evidence | Fallback/boundary |
| --- | --- | --- | --- | --- | --- | --- | --- |
| CI-01 | Example control | automatable-local | focused suite | `python3 -m pytest -q tests/example` | pytest exit code 0 | Suite output | None |

## Execution Manifest

```json
{manifest}
```

## Task 1: Apply the approved change

- [ ] Apply the approved change.
"""


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _writer():
    return _load_module("alignment_writer_checker", WRITER_CHECKER)


def _executor():
    return _load_module("alignment_executor_parser", EXECUTOR_PARSER)


def _extract_skeleton(reference: Path) -> dict[str, object]:
    text = reference.read_text(encoding="utf-8")
    section = text[text.index(SKELETON_HEADING) :]
    match = re.search(r"```json\n(.*?)\n```", section, re.DOTALL)
    assert match, f"{reference} has no skeleton JSON fence after {SKELETON_HEADING}"
    skeleton = json.loads(match.group(1))
    assert isinstance(skeleton, dict)
    return skeleton


def _render_plan(manifest: dict[str, object]) -> str:
    return MINIMAL_PLAN_TEMPLATE.format(manifest=json.dumps(manifest, indent=2))


def _mutated_plan(mutate) -> str:
    manifest = json.loads(json.dumps(_extract_skeleton(WRITER_REFERENCE)))
    mutate(manifest)
    return _render_plan(manifest)


def _rewrite_manifest(text: str, mutate) -> str:
    match = re.search(r"```json\n(.*?)\n```", text, re.DOTALL)
    assert match
    manifest = json.loads(match.group(1))
    mutate(manifest)
    return text[: match.start(1)] + json.dumps(manifest, indent=2) + text[match.end(1) :]


def _stage_plan(tmp_path: Path, text: str) -> Path:
    (tmp_path / "AGENTS.md").write_text("# Alignment test repository\n", encoding="utf-8")
    (tmp_path / ".github").mkdir(exist_ok=True)
    retained = tmp_path / "tmp" / "superpowers" / "plans"
    retained.mkdir(parents=True, exist_ok=True)
    plan = retained / "2026-01-01-example-plan.md"
    plan.write_text(text, encoding="utf-8")
    return plan


def _blocking(results: object) -> bool:
    return any(item.severity == "blocking" for item in results)


def test_reference_skeleton_top_level_matches_both_parsers() -> None:
    skeleton = _extract_skeleton(WRITER_REFERENCE)
    executor_skeleton = _extract_skeleton(EXECUTOR_REFERENCE)
    writer_parser = _writer()
    executor_parser = _executor()

    assert skeleton == executor_skeleton
    assert set(skeleton) == set(writer_parser.MANIFEST_FIELDS)
    assert set(skeleton) == set(executor_parser.MANIFEST_FIELDS)
    assert len(skeleton) == 16


def test_reference_skeleton_nested_keys_match_writer_declarations() -> None:
    skeleton = _extract_skeleton(WRITER_REFERENCE)
    writer_parser = _writer()

    assert set(skeleton["authority_boundaries"]) == set(writer_parser.AUTHORITY_FIELDS)
    assert set(skeleton["delegation"]) == set(writer_parser.DELEGATION_FIELDS)
    assert set(skeleton["tasks"][0]) == set(writer_parser.TASK_FIELDS)
    assert set(skeleton["bootstrap"]["projection_binding"]) == set(
        writer_parser.PROJECTION_BINDING
    )


def test_reference_skeleton_wraps_into_a_clean_minimal_plan(tmp_path: Path) -> None:
    skeleton = _extract_skeleton(WRITER_REFERENCE)
    plan = _stage_plan(tmp_path, _render_plan(skeleton))

    writer_findings = _writer().check_plan_structure(
        plan.read_text(encoding="utf-8"), plan
    )
    executor_findings = _executor().validate_plan(plan, tmp_path)

    assert not [
        item for item in writer_findings if item.code in FIELD_FINDING_CODES
    ], writer_findings
    assert not [
        item for item in executor_findings if item.code in FIELD_FINDING_CODES
    ], executor_findings
    assert not _blocking(writer_findings), writer_findings
    assert not _blocking(executor_findings), executor_findings


def _without_authorization_section(text: str) -> str:
    start = text.index("## Execution Authorization")
    end = text.index("## Completeness Audit", start)
    return text[:start] + text[end:]


def _authoring_only(text: str) -> str:
    return re.sub(
        r"(?m)^- Authorization:.*\n",
        "",
        text.replace("- Mode: execution-ready", "- Mode: authoring-only", 1),
        count=1,
    )


def _structural_corpus() -> tuple[tuple[str, object], ...]:
    return (
        (
            "missing-top-level-field",
            lambda text: _rewrite_manifest(text, lambda m: m.pop("tasks")),
        ),
        (
            "unknown-top-level-field",
            lambda text: _rewrite_manifest(text, lambda m: m.update({"hashing": {}})),
        ),
        (
            "missing-nested-field",
            lambda text: _rewrite_manifest(
                text, lambda m: m["authority_boundaries"].pop("no_git_mutation")
            ),
        ),
        (
            "unknown-nested-field",
            lambda text: _rewrite_manifest(
                text, lambda m: m["authority_boundaries"].update({"unexpected": True})
            ),
        ),
        (
            "partial-manifest-missing-fields",
            lambda text: _rewrite_manifest(
                text,
                lambda m: [
                    m.pop(key) for key in ("manifest_version", "repository_root")
                ],
            ),
        ),
        (
            "controls-serialized-as-array",
            lambda text: _rewrite_manifest(
                text,
                lambda m: m.update(
                    controls=[
                        {
                            "class": "automatable-local",
                            "owner": "focused suite",
                            "binding": ["T1"],
                        }
                    ]
                ),
            ),
        ),
        (
            "missing-task-field",
            lambda text: _rewrite_manifest(
                text, lambda m: m["tasks"][0].pop("acceptance")
            ),
        ),
        (
            "git-mutating-validation-command",
            lambda text: _rewrite_manifest(
                text,
                lambda m: m["validations"][0].update(
                    {"command": "git commit -am forbidden"}
                ),
            ),
        ),
        (
            "delegation-mode-delegated",
            lambda text: _rewrite_manifest(
                text, lambda m: m["delegation"].update({"mode": "delegated"})
            ),
        ),
        (
            "manifest-heading-suffix",
            lambda text: text.replace(
                "## Execution Manifest", "## Execution Manifest v3", 1
            ),
        ),
        (
            "manifest-separator-after-fence",
            lambda text: text.replace(
                "\n```\n\n## Task 1:", "\n```\n\n---\n\n## Task 1:", 1
            ),
        ),
        (
            "manifest-section-trailing-prose",
            lambda text: text.replace(
                "## Task 1:",
                "Editorial note after the manifest fence.\n\n## Task 1:",
                1,
            ),
        ),
        (
            "duplicate-manifest-field",
            lambda text: text.replace(
                '"plan_id": "2026-01-01-example-plan",',
                '"plan_id": "2026-01-01-example-plan", "plan_id": "drift",',
                1,
            ),
        ),
        (
            "authorization-missing",
            lambda text: _without_authorization_section(text),
        ),
        (
            "authoring-only-mode",
            lambda text: _authoring_only(text),
        ),
        (
            "gating-prose",
            lambda text: text.replace(
                "- No Git mutation.",
                "- No Git mutation.\n"
                "- Analysis and planning only; do not execute implementation steps.",
                1,
            ),
        ),
        (
            "scope-limiting-conflict",
            lambda text: text.replace(
                "- No Git mutation.",
                "- No Git mutation.\n- Do not modify path/to/target.py.",
                1,
            ),
        ),
        (
            "task-self-dependency",
            lambda text: _rewrite_manifest(
                text, lambda m: m["tasks"][0].update({"depends_on": ["T1"]})
            ),
        ),
    )


def test_differential_structural_parity(tmp_path: Path) -> None:
    base_text = _render_plan(_extract_skeleton(WRITER_REFERENCE))
    base_executor = _executor()
    base_writer = _writer()

    base_plan = _stage_plan(tmp_path, base_text)
    assert not _blocking(
        base_writer.check_plan_structure(base_plan.read_text(encoding="utf-8"), base_plan)
    )
    assert not _blocking(base_executor.validate_plan(base_plan, tmp_path))

    executor_blocking_cases: list[str] = []
    writer_blocking_cases: list[str] = []
    for name, mutate in _structural_corpus():
        case_dir = tmp_path / name
        case_dir.mkdir()
        plan = _stage_plan(case_dir, mutate(base_text))

        writer_blocking = _blocking(
            base_writer.check_plan_structure(plan.read_text(encoding="utf-8"), plan)
        )
        executor_blocking = _blocking(base_executor.validate_plan(plan, case_dir))

        if writer_blocking:
            writer_blocking_cases.append(name)
        if executor_blocking:
            executor_blocking_cases.append(name)
        assert not executor_blocking or writer_blocking, name

    assert {
        "authorization-missing",
        "authoring-only-mode",
        "gating-prose",
    } <= set(executor_blocking_cases)
    # scope-limiting-conflict stays writer-stricter by design: the writer gate
    # rejects scope-limiting prose that contradicts a declared modify target
    # while the executor parser leaves scope judgment to the writer gate.
    assert "scope-limiting-conflict" in writer_blocking_cases
    assert len(executor_blocking_cases) == MINIMUM_EXECUTOR_BLOCKING_CASES, (
        executor_blocking_cases
    )


def _run_cli_preflight(
    repo_root: Path, plan: Path
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            "bash",
            str(EXECUTOR_BUNDLE / "scripts/run.sh"),
            "preflight",
            str(plan),
            "--repo-root",
            str(repo_root),
            "--format",
            "compact",
        ],
        capture_output=True,
        text=True,
        check=False,
    )


def test_run_sh_cli_matches_in_process_parser(tmp_path: Path) -> None:
    """CLI residual guard: the run.sh wrapper must not alter parser findings."""

    base_text = _render_plan(_extract_skeleton(WRITER_REFERENCE))

    clean_dir = tmp_path / "clean"
    clean_dir.mkdir()
    clean_plan = _stage_plan(clean_dir, base_text)
    clean_result = _run_cli_preflight(clean_dir, clean_plan)
    assert clean_result.returncode == 0, clean_result.stderr
    assert json.loads(clean_result.stdout)["status"] == "passed"

    blocking_text = _rewrite_manifest(
        base_text, lambda m: m["tasks"][0].update({"depends_on": ["T1"]})
    )
    blocking_dir = tmp_path / "blocking"
    blocking_dir.mkdir()
    blocking_plan = _stage_plan(blocking_dir, blocking_text)
    blocking_result = _run_cli_preflight(blocking_dir, blocking_plan)
    assert blocking_result.returncode != 0, blocking_result.stdout

    in_process_codes = {
        item.code
        for item in _executor().validate_plan(blocking_plan, blocking_dir)
        if item.severity == "blocking"
    }
    cli_codes = {
        item["code"]
        for item in json.loads(blocking_result.stdout)["finding_sample"]
        if item["severity"] == "blocking"
    }
    assert "invalid-task-dependency" in in_process_codes
    assert cli_codes == in_process_codes
