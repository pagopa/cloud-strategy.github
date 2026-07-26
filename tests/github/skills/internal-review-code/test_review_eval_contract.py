import importlib.util
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)
SCRIPT_PATH = (
    REPO_ROOT
    / "tests/github/skills/internal-review-code/evaluation/score_review_eval.py"
)
FIXTURE_DIR = (
    REPO_ROOT
    / "tests/github/skills/internal-review-code/fixtures/seeded-review-target"
)

MANIFEST = {
    "contract_version": "internal-review-code-eval-v1",
    "required_loaded_skills": [
        "internal-review-code",
        "addyosmani-code-review-and-quality",
    ],
    "material_finding_ids": [
        "CAP_101",
        "VERSION_BOUNDARY",
        "SOURCE_IDENTITY",
        "UTF8_COORDINATE",
    ],
    "minimum_material_recall": 1.0,
    "maximum_scope_violations": 0,
    "false_approval_allowed": False,
}
PROVENANCE = {
    "model": "comparison-model-2026-07-26",
    "target_sha256": "sha256:target",
    "review_skill_sha256": "sha256:internal-review-code",
    "engine_sha256": "sha256:addyosmani-code-review-and-quality",
    "chat_debug_reference": "sanitized://chat-debug/run-001",
    "contract_version": MANIFEST["contract_version"],
}
PASSING_RUN = {
    **PROVENANCE,
    "loaded_skills": MANIFEST["required_loaded_skills"],
    "matched_finding_ids": MANIFEST["material_finding_ids"],
    "verdict": "request-changes",
    "scope_violations": [],
}
FAILING_RUN = {
    **PROVENANCE,
    "loaded_skills": ["internal-review-code"],
    "matched_finding_ids": [
        "CAP_101",
        "VERSION_BOUNDARY",
        "SOURCE_IDENTITY",
    ],
    "verdict": "approve",
    "scope_violations": [],
}


def test_provenance_identifies_the_review_skill_and_engine() -> None:
    assert "review_skill_sha256" in PROVENANCE
    assert "engine_sha256" in PROVENANCE
    assert "agent_sha256" not in PROVENANCE


def _load_scorer():
    spec = importlib.util.spec_from_file_location("score_review_eval", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_passing_record_meets_the_benchmark_contract() -> None:
    scorer = _load_scorer()

    result = scorer.score(MANIFEST, PASSING_RUN)

    assert result["material_recall"] == 1.0
    assert result["loaded_skills_exact"] is True
    assert result["false_approval"] is False
    assert result["scope_violation_count"] == 0
    assert result["accepted"] is True


def test_missing_finding_or_skill_fails_acceptance() -> None:
    scorer = _load_scorer()

    result = scorer.score(MANIFEST, FAILING_RUN)

    assert result["accepted"] is False
    assert result["missing_finding_ids"]
    assert result["loaded_skills_exact"] is False


def test_cli_returns_bounded_json_and_distinct_failure_codes() -> None:
    manifest_path = FIXTURE_DIR / "benchmark.json"
    passing_path = FIXTURE_DIR / "passing-run.json"
    failing_path = FIXTURE_DIR / "failing-run.json"

    passing = subprocess.run(
        [
            sys.executable,
            str(SCRIPT_PATH),
            "--manifest",
            str(manifest_path),
            "--run",
            str(passing_path),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert passing.returncode == 0
    assert json.loads(passing.stdout)["accepted"] is True
    assert len(passing.stdout) < 2000

    failing = subprocess.run(
        [
            sys.executable,
            str(SCRIPT_PATH),
            "--manifest",
            str(manifest_path),
            "--run",
            str(failing_path),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert failing.returncode == 1
    assert json.loads(failing.stdout)["accepted"] is False

    malformed = FIXTURE_DIR / "malformed.json"
    malformed.write_text("{", encoding="utf-8")
    try:
        invalid = subprocess.run(
            [
                sys.executable,
                str(SCRIPT_PATH),
                "--manifest",
                str(manifest_path),
                "--run",
                str(malformed),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
    finally:
        malformed.unlink()

    assert invalid.returncode == 2
    assert invalid.stderr
