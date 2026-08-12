import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)
BUNDLE = REPO_ROOT / ".github/skills/internal-gateway-writing-plans"
WRITER_FIXTURE = BUNDLE / "fixtures/2026-07-25-1829-valid-plan.md"
EXECUTOR_SCRIPT = (
    REPO_ROOT
    / ".github/skills/internal-gateway-execute-plans/scripts/plan_execution.py"
)


def _executor_module():
    spec = importlib.util.spec_from_file_location("plan_execution", EXECUTOR_SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_writer_plan_is_actionable_for_executor(tmp_path: Path) -> None:
    retained = tmp_path / "tmp" / "superpowers" / "plans"
    retained.mkdir(parents=True)
    (tmp_path / "AGENTS.md").write_text("# Test repository\n")
    (tmp_path / ".github").mkdir()
    plan = retained / WRITER_FIXTURE.name
    shutil.copy(WRITER_FIXTURE, plan)

    writer_text = WRITER_FIXTURE.read_text()
    assert "## Control Inventory" in writer_text
    assert "- No Git mutation." in writer_text

    findings = _executor_module().validate_plan(plan, repo_root=tmp_path)

    assert findings == []


def test_writer_plan_remains_actionable_through_preflight_cli(tmp_path: Path) -> None:
    retained = tmp_path / "tmp" / "superpowers" / "plans"
    retained.mkdir(parents=True)
    (tmp_path / "AGENTS.md").write_text("# Test repository\n")
    (tmp_path / ".github").mkdir()
    plan = retained / WRITER_FIXTURE.name
    shutil.copy(WRITER_FIXTURE, plan)

    result = subprocess.run(
        [
            sys.executable,
            str(EXECUTOR_SCRIPT),
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
    assert json.loads(result.stdout)["status"] == "passed"


def _stage_valid_plan(tmp_path: Path) -> Path:
    retained = tmp_path / "tmp" / "superpowers" / "plans"
    retained.mkdir(parents=True)
    (tmp_path / "AGENTS.md").write_text("# Test repository\n")
    (tmp_path / ".github").mkdir()
    plan = retained / WRITER_FIXTURE.name
    shutil.copy(WRITER_FIXTURE, plan)
    return plan


def _write_predecessor_state(module, plan: Path, status: str) -> Path:
    manifest = module.parse_execution_manifest(plan.read_text())
    task_ids = [
        task["id"] for task in sorted(manifest["tasks"], key=lambda item: item["order"])
    ]
    completed = task_ids if status == "DONE" else []
    state = plan.with_suffix(".status.json")
    payload = module.build_resume_state(
        plan,
        status,
        completed,
        [task_id for task_id in task_ids if task_id not in completed],
        "final: pytest=79; workflow-counts=counts=discovery:1,approvals:1,reopenings:1,critic:1,recovery:1",
        "No further execution is required.",
        repo_root=plan.parents[3],
    )
    module.write_resume_state(state, payload)
    return state


@pytest.mark.parametrize("failure", ("missing", "partial", "hash-drift"))
def test_serial_predecessor_gate_rejects_unverified_igi01_state(
    tmp_path: Path, failure: str
) -> None:
    module = _executor_module()
    plan = _stage_valid_plan(tmp_path)
    state = _write_predecessor_state(module, plan, "PARTIAL" if failure == "partial" else "DONE")

    if failure == "missing":
        state.unlink()
    elif failure == "hash-drift":
        plan.write_text(plan.read_text() + "\nEditorial drift.\n")

    findings = module.validate_serial_predecessor(plan, state, repo_root=tmp_path)
    codes = {finding.code for finding in findings}

    assert codes
    if failure == "missing":
        assert "state-not-found" in codes
    elif failure == "partial":
        assert "predecessor-not-done" in codes
    else:
        assert "content-hash-drift" in codes


def test_serial_predecessor_gate_accepts_done_state_with_final_count_evidence(
    tmp_path: Path,
) -> None:
    module = _executor_module()
    plan = _stage_valid_plan(tmp_path)
    state = _write_predecessor_state(module, plan, "DONE")

    assert module.validate_serial_predecessor(plan, state, repo_root=tmp_path) == []


def test_serial_predecessor_gate_accepts_explicit_observed_count_evidence(
    tmp_path: Path,
) -> None:
    module = _executor_module()
    plan = _stage_valid_plan(tmp_path)
    state = _write_predecessor_state(module, plan, "DONE")
    payload = json.loads(state.read_text())
    payload["last_validation"] = "final: native validations passed"
    state.write_text(json.dumps(payload))

    assert module.validate_serial_predecessor(
        plan,
        state,
        repo_root=tmp_path,
        workflow_count_evidence=(
            "counts=discovery:1,approvals:1,reopenings:1,critic:1,recovery:1"
        ),
    ) == []
