from __future__ import annotations

import importlib.util
import json
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
EXECUTOR_BUNDLE = (
    REPO_ROOT / ".github" / "skills" / "internal-gateway-execute-plans"
)
WRITER_BUNDLE = REPO_ROOT / ".github" / "skills" / "internal-gateway-writing-plans"
RUNNER = EXECUTOR_BUNDLE / "scripts/run.sh"
FIXTURE = EXECUTOR_BUNDLE / "fixtures/valid-plan.md"
TASK_IDS = ("T1",)
VERDICT_CATEGORIES = (
    "structure",
    "semantic_review",
    "artifact_provenance",
    "source_baseline",
    "execution_readiness",
)


def _fixture_manifest() -> tuple[str, dict[str, object]]:
    text = FIXTURE.read_text(encoding="utf-8")
    start = text.index("```json\n") + len("```json\n")
    end = text.index("\n```", start)
    return text, json.loads(text[start:end])


def _v2_text(*, include_hashing: bool = False) -> str:
    text, manifest = _fixture_manifest()
    manifest["schema_version"] = 2
    manifest["manifest_version"] = "execution-manifest/v2"
    manifest["approval"].pop("binds", None)
    manifest["handoff"]["requires"] = [
        "human approval",
        "exact Manifest v2 review",
        "zero blocking preflight findings",
    ]
    if include_hashing:
        manifest["hashing"] = {
            "content_sha256": {
                "algorithm": "SHA-256",
                "input": "retired",
                "binding": "external",
            },
            "semantic_fingerprint": {
                "algorithm": "SHA-256",
                "input": "retired",
                "version": "retired",
                "binding": "external",
            },
            "self_reference": False,
        }
    if not include_hashing:
        manifest.pop("hashing", None)
    start = text.index("```json\n") + len("```json\n")
    end = text.index("\n```", start)
    return text[:start] + json.dumps(manifest, indent=2) + text[end:]


def _stage_plan(tmp_path: Path, text: str | None = None) -> tuple[Path, Path]:
    (tmp_path / "AGENTS.md").write_text("# test repository\n", encoding="utf-8")
    (tmp_path / ".github").mkdir()
    plan_dir = tmp_path / "tmp/superpowers/plans"
    plan_dir.mkdir(parents=True)
    plan = plan_dir / "v2-plan.md"
    plan.write_text(text or _v2_text(), encoding="utf-8")
    return tmp_path, plan


def _run_preflight(root: Path, plan: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            "bash",
            str(RUNNER),
            "preflight",
            str(plan),
            "--repo-root",
            str(root),
            "--format",
            "compact",
        ],
        capture_output=True,
        text=True,
        check=False,
    )


def _verdicts(*, failed: str | None = None) -> list[dict[str, str]]:
    return [
        {
            "category": category,
            "outcome": "failed" if category == failed else "passed",
            "coverage": "observed v2 contract",
            "limit": "technical failure" if category == failed else "none",
        }
        for category in VERDICT_CATEGORIES
    ]


def _status_payload(
    root: Path,
    plan: Path,
    *,
    status: str = "DONE",
    failed_verdict: str | None = None,
    warnings: list[dict[str, str]] | None = None,
    deviations: list[dict[str, str]] | None = None,
) -> tuple[Path, dict[str, object]]:
    complete = status in {"DONE", "DONE_WITH_WARNINGS"}
    payload: dict[str, object] = {
        "schema_version": 2,
        "status": status,
        "plan": "tmp/superpowers/plans/v2-plan.md",
        "approval_evidence": {
            "source": "current-conversation",
            "statement": "explicit execution approval",
        },
        "delivery_verdicts": _verdicts(failed=failed_verdict),
        "completed_task_ids": list(TASK_IDS if complete else ()),
        "remaining_task_ids": list(() if complete else TASK_IDS),
        "last_validation": "focused v2 contract validation",
        "next_action": "none" if complete else "Continue the approved task loop.",
        "warnings": warnings or [],
        "deviations": deviations or [],
    }
    state = plan.with_name(f"{plan.stem}.{status}.yaml")
    state.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return state, payload


def _run_state_check(
    root: Path, plan: Path, state: Path
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            "bash",
            str(RUNNER),
            "state-check",
            str(plan),
            str(state),
            "--repo-root",
            str(root),
            "--format",
            "compact",
        ],
        capture_output=True,
        text=True,
        check=False,
    )


def _finding_codes(result: subprocess.CompletedProcess[str]) -> set[str]:
    return {
        item["code"]
        for item in json.loads(result.stdout).get("finding_sample", [])
    }


def test_manifest_v2_rejects_hash_fields(tmp_path: Path) -> None:
    root, plan = _stage_plan(tmp_path, _v2_text(include_hashing=True))

    result = _run_preflight(root, plan)

    assert result.returncode != 0
    assert "unknown-manifest-field" in _finding_codes(result)


def test_manifest_v2_accepts_hash_free_approval(tmp_path: Path) -> None:
    root, plan = _stage_plan(tmp_path)

    result = _run_preflight(root, plan)

    assert result.returncode == 0, result.stderr or result.stdout


def test_done_with_warnings_requires_passed_verdicts(tmp_path: Path) -> None:
    root, plan = _stage_plan(tmp_path)
    warning = {
        "kind": "human-follow-up",
        "evidence": "The required offline review remains open.",
        "next_action": "Complete the offline review before closeout.",
    }
    state, _ = _status_payload(
        root, plan, status="DONE_WITH_WARNINGS", warnings=[warning]
    )

    result = _run_state_check(root, plan, state)

    assert result.returncode == 0, result.stderr or result.stdout
    failed_state, _ = _status_payload(
        root,
        plan,
        status="DONE_WITH_WARNINGS",
        failed_verdict="execution_readiness",
        warnings=[warning],
    )
    failed_result = _run_state_check(root, plan, failed_state)
    assert failed_result.returncode != 0
    assert "done-with-unpassed-delivery-verdicts" in _finding_codes(failed_result)

    missing_tool_warning = {
        "kind": "missing-tool-equivalent",
        "evidence": "The declared tool exited 127.",
        "next_action": "Retain the accepted native equivalent in the deviation record.",
    }
    missing_tool_state, _ = _status_payload(
        root,
        plan,
        status="DONE_WITH_WARNINGS",
        warnings=[missing_tool_warning],
    )
    missing_tool_result = _run_state_check(root, plan, missing_tool_state)
    assert missing_tool_result.returncode != 0
    assert "missing-tool-equivalent-deviation" in _finding_codes(
        missing_tool_result
    )


def test_blocked_technical_failure_cannot_become_warning(tmp_path: Path) -> None:
    root, plan = _stage_plan(tmp_path)
    warning = {
        "kind": "external-unavailable",
        "evidence": "The external evidence endpoint was unavailable.",
        "next_action": "Collect the external evidence and resume validation.",
    }
    state, _ = _status_payload(
        root,
        plan,
        status="DONE_WITH_WARNINGS",
        failed_verdict="source_baseline",
        warnings=[warning],
    )

    result = _run_state_check(root, plan, state)

    assert result.returncode != 0
    assert "done-with-unpassed-delivery-verdicts" in _finding_codes(result)


def test_deviation_records_are_strict(tmp_path: Path) -> None:
    root, plan = _stage_plan(tmp_path)
    valid_deviation = {
        "task": "T1",
        "mismatch": "target already has the declared state",
        "resolution": "Kept the target unchanged and recorded the observation.",
    }
    state, _ = _status_payload(
        root, plan, status="PARTIAL", deviations=[valid_deviation]
    )
    result = _run_state_check(root, plan, state)
    assert result.returncode == 0, result.stderr or result.stdout

    invalid_deviation = {
        "task": "T1",
        "mismatch": "ambiguous semantic scope",
        "resolution": "Selected one of several plausible interpretations.",
    }
    invalid_state, _ = _status_payload(
        root, plan, status="PARTIAL", deviations=[invalid_deviation]
    )
    invalid_result = _run_state_check(root, plan, invalid_state)
    assert invalid_result.returncode != 0
    assert "invalid-deviation" in _finding_codes(invalid_result)


def test_writer_requires_command_probe() -> None:
    text = (WRITER_BUNDLE / "fixtures/2026-07-25-1829-valid-plan.md").read_text(
        encoding="utf-8"
    )
    start = text.index("```json\n") + len("```json\n")
    end = text.index("\n```", start)
    manifest = json.loads(text[start:end])

    for validation in manifest["validations"]:
        executable = shlex.split(validation["command"])[0]
        assert shutil.which(executable), validation["id"]


def test_non_done_report_contains_causes_and_actions() -> None:
    source = EXECUTOR_BUNDLE / "scripts/plan_execution.py"
    spec = importlib.util.spec_from_file_location("v2_report_parser", source)
    assert spec is not None and spec.loader is not None
    executor = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = executor
    spec.loader.exec_module(executor)

    report = executor.build_non_done_report(
        ["The focused validation failed."],
        ["Inspect the failure evidence.", "Apply one task-local repair."],
    )

    assert report == (
        "Perché mi sono fermato",
        "- The focused validation failed.",
        "Cosa fare",
        "- Inspect the failure evidence.",
        "- Apply one task-local repair.",
    )
