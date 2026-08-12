import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)
BUNDLE = REPO_ROOT / ".github/skills/internal-gateway-execute-plans"
SCRIPTS = BUNDLE / "scripts"
FIXTURES = BUNDLE / "fixtures"
sys.path.insert(0, str(SCRIPTS))

from plan_execution import (  # noqa: E402
    ExecutionContractError,
    Finding,
    build_compact_payload,
    canonical_json,
    compute_content_sha256,
    compute_semantic_fingerprint,
    compute_sha256,
    parse_execution_manifest,
    validate_manifest_projection,
    validate_plan,
)


def _fixture(name: str) -> Path:
    return FIXTURES / name


def _stage_valid_plan(tmp_path: Path, text: str | None = None) -> Path:
    tmp_path.mkdir(parents=True, exist_ok=True)
    (tmp_path / "AGENTS.md").write_text("# agents\n")
    (tmp_path / ".github").mkdir()
    staged = tmp_path / "tmp" / "superpowers" / "plans"
    staged.mkdir(parents=True)
    plan = staged / "valid-plan.md"
    plan.write_text(text or _fixture("valid-plan.md").read_text())
    return plan


def test_valid_plan_parses_contract_and_has_no_findings(valid_plan: Path) -> None:
    assert parse_execution_manifest(valid_plan.read_text())["schema_version"] == 1
    assert (
        parse_execution_manifest(valid_plan.read_text())["manifest_version"]
        == "execution-manifest/v1"
    )
    assert validate_plan(valid_plan, repo_root=valid_plan.parents[3]) == []


def test_plan_without_execution_manifest_is_blocking(tmp_path: Path) -> None:
    plan = _stage_valid_plan(
        tmp_path,
        "# Plan\n\n## Goal\n\nStrict plan.\n\n"
        "## Repository Preflight\n\n- Baseline Validation: run check.\n"
        "- Recovery Policy: use bounded recovery.\n"
        "- Escalation Conditions: request authority.\n"
        "- User-Facing Report: report evidence.\n\n"
        "## Global Constraints\n\n- No Git mutation.\n\n"
        "## Task 1: Validate\n\n- [ ] Run validation.\n",
    )
    findings = validate_plan(plan, repo_root=tmp_path)
    assert "missing-execution-manifest" in {item.code for item in findings}
    assert any(item.severity == "blocking" for item in findings)


def test_current_plan_requires_control_inventory(tmp_path: Path) -> None:
    text = _fixture("valid-plan.md").read_text()
    start = text.index("## Control Inventory")
    end = text.index("\n## ", start + 1)
    plan = _stage_valid_plan(tmp_path, text[:start] + text[end + 1 :])
    assert "missing-control-inventory" in {
        item.code for item in validate_plan(plan, tmp_path)
    }


def test_current_plan_requires_explicit_no_git_constraint(tmp_path: Path) -> None:
    text = _fixture("valid-plan.md").read_text().replace("- No Git mutation.\n", "", 1)
    plan = _stage_valid_plan(tmp_path, text)
    assert "missing-no-git-constraint" in {
        item.code for item in validate_plan(plan, tmp_path)
    }


def test_explicit_legacy_or_imported_plan_remains_non_actionable(
    tmp_path: Path,
) -> None:
    plan = _stage_valid_plan(tmp_path, "# Legacy plan\n\n## Goal\n\nNo manifest.\n")
    assert any(item.severity == "blocking" for item in validate_plan(plan, tmp_path))


def test_legacy_plan_is_rejected(tmp_path: Path) -> None:
    plan = _stage_valid_plan(tmp_path, "# Legacy plan\n\n## Goal\n\nNo manifest.\n")
    assert any(item.severity == "blocking" for item in validate_plan(plan, tmp_path))


def test_plan_rejects_duplicate_validation_ids(tmp_path: Path) -> None:
    text = (
        _fixture("valid-plan.md")
        .read_text()
        .replace('"id": "diff-check", "command"', '"id": "focused-tests", "command"')
    )
    plan = _stage_valid_plan(tmp_path, text)
    assert "duplicate-validation-id" in {
        item.code for item in validate_plan(plan, tmp_path)
    }


@pytest.mark.parametrize(
    ("needle", "replacement", "message"),
    (
        ('"schema_version": 1', '"schema_version": 2', "schema_version"),
        (
            '"id": "focused-tests", "command"',
            '"id": "focused-tests", "unknown": true, "command"',
            "unknown fields",
        ),
        (
            '"command": "python3 -m pytest -q tests/fixture/"',
            '"command": ""',
            "command",
        ),
        ('"phases": ["final"]', '"phases": ["other"]', "phases"),
        ('"mode": "manifest-only"', '"mode": "unsupported"', "bootstrap.mode"),
    ),
)
def test_execution_manifest_rejects_invalid_fields(
    tmp_path: Path, needle: str, replacement: str, message: str
) -> None:
    plan = _stage_valid_plan(
        tmp_path, _fixture("valid-plan.md").read_text().replace(needle, replacement, 1)
    )
    assert any(message in item.message for item in validate_plan(plan, tmp_path))


def test_execution_manifest_rejects_malformed_json_and_duplicate_blocks(
    tmp_path: Path,
) -> None:
    malformed = _stage_valid_plan(
        tmp_path,
        _fixture("valid-plan.md")
        .read_text()
        .replace('"schema_version": 1', '"schema_version":', 1),
    )
    assert "malformed-execution-manifest" in {
        item.code for item in validate_plan(malformed, tmp_path)
    }
    duplicate = _stage_valid_plan(
        tmp_path / "duplicate",
        _fixture("valid-plan.md").read_text()
        + "\n## Execution Manifest\n\n```json\n{}\n```\n",
    )
    assert "duplicate-execution-manifest" in {
        item.code for item in validate_plan(duplicate, duplicate.parents[3])
    }


def test_compact_output_is_bounded() -> None:
    assert (
        build_compact_payload([Finding("missing-heading", "detail", "blocking")])[
            "status"
        ]
        == "failed"
    )


def test_preflight_cli_valid_fixture(tmp_path: Path) -> None:
    plan = _stage_valid_plan(tmp_path)
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPTS / "plan_execution.py"),
            "preflight",
            str(plan),
            "--repo-root",
            str(tmp_path),
            "--format",
            "compact",
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr


def test_manifest_only_plan_rejects_legacy_execution_contract_projection(
    tmp_path: Path,
) -> None:
    text = _fixture("valid-plan.md").read_text()
    plan = _stage_valid_plan(
        tmp_path,
        text + "\n## Execution Contract\n\n```json\n{}\n```\n",
    )
    codes = {item.code for item in validate_plan(plan, tmp_path)}
    assert "obsolete-execution-contract" in codes


def _current_bootstrap_plan() -> Path:
    return (
        REPO_ROOT / "tmp/superpowers/plans/2026-08-11-skills-orchestration-alignment.md"
    )


def _manifest_text(plan: Path) -> str:
    return plan.read_text(encoding="utf-8")


def test_execution_manifest_parses_and_binds_current_bootstrap_projection() -> None:
    plan = _current_bootstrap_plan()
    text = _manifest_text(plan)
    manifest = parse_execution_manifest(text)

    assert manifest["manifest_version"] == "execution-manifest/v1"
    assert validate_manifest_projection(text, manifest) == []


def test_execution_manifest_rejects_duplicate_fenced_blocks(tmp_path: Path) -> None:
    plan = _current_bootstrap_plan()
    text = _manifest_text(plan) + "\n## Execution Manifest\n\n```json\n{}\n```\n"

    with pytest.raises(ExecutionContractError) as exc:
        parse_execution_manifest(text)
    assert exc.value.code == "duplicate-execution-manifest"


def test_execution_manifest_rejects_unknown_fields(tmp_path: Path) -> None:
    plan = _current_bootstrap_plan()
    text = _manifest_text(plan)
    text = text.replace(
        '"manifest_version": "execution-manifest/v1"',
        '"unknown": true,\n  "manifest_version": "execution-manifest/v1"',
        1,
    )

    with pytest.raises(ExecutionContractError) as exc:
        parse_execution_manifest(text)
    assert exc.value.code == "unknown-manifest-field"


def test_content_hash_tracks_editorial_bytes_but_semantic_hash_does_not(
    tmp_path: Path,
) -> None:
    plan = _current_bootstrap_plan()
    original = _manifest_text(plan)
    editorial = original + "\nEditorial note that does not change the manifest.\n"
    original_manifest = parse_execution_manifest(original)
    editorial_manifest = parse_execution_manifest(editorial)

    (tmp_path / "original.md").write_text(original, encoding="utf-8")
    (tmp_path / "editorial.md").write_text(editorial, encoding="utf-8")
    assert compute_content_sha256(tmp_path / "original.md") != compute_content_sha256(
        tmp_path / "editorial.md"
    )
    assert compute_semantic_fingerprint(
        original_manifest
    ) == compute_semantic_fingerprint(editorial_manifest)


@pytest.mark.parametrize(
    "mutator",
    [
        lambda m: m["authority_boundaries"].update({"no_git_mutation": False}),
        lambda m: m["targets"][0].update({"path": "changed/path"}),
        lambda m: m["controls"]["SUBAGENT-VALUE"]["binding"].append("T8"),
        lambda m: m["validations"][0].update({"command": "make changed"}),
        lambda m: m["tasks"][0].update({"depends_on": ["T8"]}),
        lambda m: m["bootstrap"].update({"mode": "generic"}),
        lambda m: m["handoff"].update({"next_owner": "/other-owner"}),
    ],
)
def test_every_normative_manifest_class_changes_semantic_fingerprint(mutator) -> None:
    manifest = parse_execution_manifest(_manifest_text(_current_bootstrap_plan()))
    changed = json.loads(json.dumps(manifest))
    mutator(changed)

    assert compute_semantic_fingerprint(manifest) != compute_semantic_fingerprint(
        changed
    )


def test_manifest_hashes_are_external_and_self_reference_is_rejected() -> None:
    manifest = parse_execution_manifest(_manifest_text(_current_bootstrap_plan()))
    content_hash = compute_content_sha256(_current_bootstrap_plan())
    semantic_hash = compute_semantic_fingerprint(manifest)
    encoded = canonical_json(manifest)

    assert content_hash.encode() not in encoded
    assert semantic_hash.encode() not in encoded

    polluted = json.loads(encoded)
    polluted["semantic_fingerprint"] = semantic_hash
    with pytest.raises(ExecutionContractError) as exc:
        compute_semantic_fingerprint(polluted)
    assert exc.value.code == "manifest-hash-self-reference"


def test_bootstrap_projection_drift_fails_closed() -> None:
    text = _manifest_text(_current_bootstrap_plan())
    manifest = parse_execution_manifest(text)
    changed = json.loads(json.dumps(manifest))
    changed["controls"].pop("SUBAGENT-VALUE")

    findings = validate_manifest_projection(text, changed)

    assert any("projection" in finding.lower() for finding in findings)


def test_legacy_only_plan_has_no_manifest_fallback() -> None:
    with pytest.raises(ExecutionContractError) as exc:
        parse_execution_manifest("# Legacy plan\n\n## Goal\n\nNo manifest.\n")
    assert exc.value.code == "missing-execution-manifest"


def _write_resume_state(plan: Path, state: Path, status: str = "DONE") -> None:
    manifest = parse_execution_manifest(plan.read_text())
    tasks = sorted(manifest["tasks"], key=lambda item: item["order"])
    task_ids = [item["id"] for item in tasks]
    completed = task_ids if status == "DONE" else []
    state.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "status": status,
                "plan": str(plan.relative_to(plan.parents[3])),
                "plan_fingerprint": compute_semantic_fingerprint(manifest),
                "content_hash": compute_content_sha256(plan),
                "completed_task_ids": completed,
                "remaining_task_ids": [
                    item for item in task_ids if item not in completed
                ],
                "last_validation": "focused-tests: passed",
                "next_action": "No further execution is required.",
            }
        )
    )


def _run_state_check(
    plan: Path, state: Path, repo_root: Path
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(SCRIPTS / "plan_execution.py"),
            "state-check",
            str(plan),
            str(state),
            "--repo-root",
            str(repo_root),
            "--format",
            "compact",
        ],
        capture_output=True,
        text=True,
    )


def test_state_check_accepts_hash_bound_done_state(tmp_path: Path) -> None:
    plan = _stage_valid_plan(tmp_path)
    state = plan.with_suffix(".status.json")
    _write_resume_state(plan, state)

    result = _run_state_check(plan, state, tmp_path)

    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["status"] == "passed"


def test_state_check_rejects_content_hash_drift(tmp_path: Path) -> None:
    plan = _stage_valid_plan(tmp_path)
    state = plan.with_suffix(".status.json")
    _write_resume_state(plan, state)
    plan.write_text(plan.read_text() + "\nEditorial drift.\n")

    result = _run_state_check(plan, state, tmp_path)

    assert result.returncode != 0
    assert "content-hash-drift" in {
        item["code"] for item in json.loads(result.stdout)["finding_sample"]
    }


@pytest.mark.parametrize("status", ("DONE", "PARTIAL", "BLOCKED"))
def test_state_check_accepts_only_new_run_statuses(tmp_path: Path, status: str) -> None:
    plan = _stage_valid_plan(tmp_path)
    state = plan.with_suffix(".status.json")
    _write_resume_state(plan, state, status)

    result = _run_state_check(plan, state, tmp_path)

    assert result.returncode == 0, result.stderr


def test_state_check_rejects_retired_needs_review_status(tmp_path: Path) -> None:
    plan = _stage_valid_plan(tmp_path)
    state = plan.with_suffix(".status.json")
    _write_resume_state(plan, state, "NEEDS_REVIEW")

    result = _run_state_check(plan, state, tmp_path)

    assert result.returncode != 0
    assert "unknown-status" in {
        item["code"] for item in json.loads(result.stdout)["finding_sample"]
    }


@pytest.mark.parametrize(
    "retired_command",
    ("status-check", "resume-check", "closeout-check", "completion-check"),
)
def test_retired_status_protocol_commands_are_not_exposed(retired_command: str) -> None:
    result = subprocess.run(
        [sys.executable, str(SCRIPTS / "plan_execution.py"), retired_command, "--help"],
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
