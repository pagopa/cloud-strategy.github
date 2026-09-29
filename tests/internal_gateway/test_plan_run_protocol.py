from __future__ import annotations

import json
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
SKILLS_ROOT = REPO_ROOT / ".github" / "skills"
IDEA_ROOT = SKILLS_ROOT / "internal-gateway-idea"
WRITER_ROOT = SKILLS_ROOT / "internal-gateway-writing-plans"
EXECUTOR_ROOT = SKILLS_ROOT / "internal-gateway-execute-plans"


def _metadata(skill_root: Path) -> dict[str, object]:
    return yaml.safe_load(
        (skill_root / "agents" / "openai.yaml").read_text(encoding="utf-8")
    )


def _eval_pack(skill_root: Path) -> dict[str, object]:
    return json.loads(
        (skill_root / "tests" / "evaluation" / "evals.json").read_text(
            encoding="utf-8"
        )
    )


def _cases(skill_root: Path) -> dict[str, dict[str, object]]:
    return {case["id"]: case for case in _eval_pack(skill_root)["cases"]}


def test_public_route_metadata_has_one_explicit_owner_per_handoff() -> None:
    assert _metadata(IDEA_ROOT)["route_contract"] == {
        "owner": "/internal-gateway-idea",
        "mode": "analysis-only",
        "spec_handoff": "/mattpocock-to-spec",
        "plan_handoff": "/internal-gateway-writing-plans",
        "execution_handoff": "/internal-gateway-execute-plans",
        "forbidden_pre_acceptance_routes": [
            "/internal-tdd",
            "/internal-gateway-writing-plans",
            "/internal-gateway-execute-plans",
        ],
    }
    writer_prompt = _metadata(WRITER_ROOT)["interface"]["default_prompt"]
    executor_prompt = _metadata(EXECUTOR_ROOT)["interface"]["default_prompt"]
    assert "/addyosmani-planning-and-task-breakdown" in writer_prompt
    assert "/internal-gateway-execute-plans" in writer_prompt
    assert "/mattpocock-implement" in executor_prompt
    assert "/internal-gateway-execute-plans" in executor_prompt


def test_f1_and_f2_cases_bind_the_new_authoring_contracts() -> None:
    idea_cases = _cases(IDEA_ROOT)
    writer_cases = _cases(WRITER_ROOT)
    executor_cases = _cases(EXECUTOR_ROOT)
    assert {"C-SPEC-DIRECT", "C-SPEC-COHERENCE", "C-SPEC-CONTENT-COMPARISON", "C-SPEC-NEW-TEST-DECISION", "C-PLAN-ROUTE"} <= idea_cases.keys()
    assert {"C-F1-CONTENT-COMPARISON", "C-F2-MULTI-TARGET", "C-F2-UNRESOLVED", "C-F2-SOURCE-DRIFT"} <= writer_cases.keys()
    assert {"C-F2-MULTI-TARGET", "C-F2-UNRESOLVED", "C-F2-STALE-APPROVAL", "C-HISTORICAL-RUN", "C-CURRENT-RESUME"} <= executor_cases.keys()
    for cases in (idea_cases, writer_cases, executor_cases):
        for case in cases.values():
            assert case["kind"] == "rubric"
            assert case["status"] == "not-run"
            assert case["assertions"]
            assert any(assertion["critical"] for assertion in case["assertions"])


def test_retired_gateway_protocol_files_and_routes_are_absent() -> None:
    retired_paths = (
        WRITER_ROOT / "references" / "plan-contract.md",
        EXECUTOR_ROOT / "references" / "run-protocol.md",
        EXECUTOR_ROOT / "references" / "chat-templates.md",
        EXECUTOR_ROOT / "tests" / "test_run_commands.py",
    )
    assert all(not path.exists() for path in retired_paths)
