import copy
import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)
BUNDLE_ROOT = REPO_ROOT / ".github/skills/internal-skill-creator"
FIXTURES = BUNDLE_ROOT / "fixtures"
sys.path.insert(0, str(REPO_ROOT / ".github/skills/internal-subagent-contract/scripts"))

from subagent_contract import (  # noqa: E402
    canonical_json,
    compute_progress_signature,
    validate_brief,
    validate_result,
)
from runtime_evidence import compose_handoff  # noqa: E402


def _load(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def _materialize_creator_result(tmp_path: Path) -> tuple[dict, dict]:
    (tmp_path / "inputs").mkdir()
    (tmp_path / "inputs/source.md").write_text("source", encoding="utf-8")
    (tmp_path / "out").mkdir()
    (tmp_path / "out/worker-output.md").write_text("draft", encoding="utf-8")

    brief = _load("valid-plan-brief.json")
    brief["evidence"] = [{"ref": "inputs/source.md", "purpose": "Input source."}]
    brief["write_scope"] = ["out"]
    brief["expected_output"]["path"] = "out/worker-output.md"
    brief["result_path"] = "handoff/creator.result.json"
    template = _load("valid-plan-result.json")
    raw_worker = dict(template)
    raw_worker["artifacts"] = [{"path": "out/worker-output.md", "kind": "draft"}]
    brief_bytes = canonical_json(brief)
    materialized, _ = compose_handoff(
        raw_worker,
        brief,
        repo_root=tmp_path,
        brief_bytes=brief_bytes,
        raw_worker_bytes=canonical_json(raw_worker),
    )
    result_path = tmp_path / "handoff/materialized-result.json"
    result_path.parent.mkdir()
    result_path.write_bytes(canonical_json(materialized) + b"\n")
    return brief, json.loads(result_path.read_text(encoding="utf-8"))


@pytest.mark.parametrize(
    ("fixture", "mode", "expected_kind", "path_is_null", "scope_is_empty"),
    [
        ("valid-read-brief.json", "read", "analysis", True, True),
        ("valid-plan-brief.json", "plan", "artifact", False, False),
        ("valid-write-brief.json", "write", "artifact", False, False),
    ],
)
def test_creator_fixture_uses_explicit_mode_and_scope(
    fixture: str,
    mode: str,
    expected_kind: str,
    path_is_null: bool,
    scope_is_empty: bool,
) -> None:
    brief = _load(fixture)

    assert brief["mode"] == mode
    assert brief["expected_output"]["kind"] == expected_kind
    assert (brief["expected_output"]["path"] is None) is path_is_null
    assert bool(brief["write_scope"]) is (not scope_is_empty)
    assert validate_brief(brief, repo_root=REPO_ROOT) == []


def test_incomplete_creator_brief_fails_closed() -> None:
    errors = validate_brief(_load("invalid-incomplete-brief.json"), repo_root=REPO_ROOT)

    assert errors
    assert any("acceptance" in error or "validation" in error for error in errors)


def test_valid_creator_result_binds_artifact_acceptance_and_progress(
    tmp_path: Path,
) -> None:
    brief, result = _materialize_creator_result(tmp_path)

    assert result["progress_signature"] == compute_progress_signature(result)
    assert (
        validate_result(
            result,
            brief,
            repo_root=tmp_path,
            brief_bytes=canonical_json(brief),
        )
        == []
    )
    assert result["value_delivered"] is True
    assert any(
        evidence["acceptance_id"] == "A1" and evidence["outcome"] == "pass"
        for evidence in result["evidence"]
    )


@pytest.mark.parametrize("tamper", ["brief_hash", "artifact_hash", "artifact_path"])
def test_creator_result_rejects_tampered_binding(
    tmp_path: Path, tamper: str
) -> None:
    brief, materialized = _materialize_creator_result(tmp_path)
    result = copy.deepcopy(materialized)

    if tamper == "brief_hash":
        result["brief_sha256"] = "sha256:" + "0" * 64
    elif tamper == "artifact_hash":
        result["artifacts"][0]["sha256"] = "sha256:" + "0" * 64
    else:
        result["artifacts"][0]["path"] = (
            ".github/skills/internal-skill-creator/SKILL.md"
        )

    errors = validate_result(
        result,
        brief,
        repo_root=tmp_path,
        brief_bytes=canonical_json(brief),
    )

    assert errors
