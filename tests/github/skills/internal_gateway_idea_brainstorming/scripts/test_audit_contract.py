from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest


SCRIPT_PATH = Path(
    ".github/skills/internal-gateway-idea-brainstorming/scripts/audit_contract.py"
)


def run_audit(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT_PATH), *args],
        capture_output=True,
        text=True,
        check=True,
    )


def run_audit_json(*args: str) -> dict:
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "--format", "json", *args],
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(result.stdout)


def test_text_output_contains_bundle_and_totals() -> None:
    result = run_audit("--format", "text")
    assert "Bundle:" in result.stdout
    assert "Totals:" in result.stdout
    assert "Contract markers:" in result.stdout
    assert "Expected siblings:" in result.stdout
    assert "Findings:" in result.stdout
    assert "strict_ok:" in result.stdout


def test_json_output_has_deterministic_shape() -> None:
    report = run_audit_json()
    assert isinstance(report, dict)
    assert "bundle_dir" in report
    assert "files" in report
    assert "totals" in report
    assert "total_estimated_tokens" in report
    assert "markers" in report
    assert "siblings" in report
    assert "findings" in report
    assert "strict_ok" in report
    assert isinstance(report["files"], list)
    assert isinstance(report["totals"], dict)
    assert isinstance(report["markers"], dict)
    assert isinstance(report["siblings"], dict)


def test_bucket_totals_sum_to_total() -> None:
    report = run_audit_json()
    bucket_total = sum(report["totals"].values())
    assert bucket_total == report["total_estimated_tokens"]


def test_required_markers_are_checked() -> None:
    report = run_audit_json()
    expected_markers = {
        "evidence-first-discovery",
        "one-question-per-turn",
        "explicit-user-answer",
        "decision-ledger",
        "interview-ready-for-critical",
        "interview-reopen",
        "handoff-ready-for-owner-change",
        "mandatory-critical-pass",
        "exactly-one-next-owner",
        "chat-only-simple-task-brief",
        "no-hidden-dispatch",
    }
    assert set(report["markers"].keys()) == expected_markers


def test_all_current_markers_pass() -> None:
    report = run_audit_json()
    assert report["findings"] == []
    assert report["strict_ok"] is True


def test_agents_sibling_is_present() -> None:
    report = run_audit_json()
    assert report["siblings"]["agents/openai.yaml"] is True


def test_strict_mode_passes_for_current_bundle() -> None:
    result = run_audit("--format", "json", "--strict")
    assert result.returncode == 0


def test_files_have_correct_buckets() -> None:
    report = run_audit_json()
    loaded = [f for f in report["files"] if f["bucket"] == "loaded"]
    on_demand = [f for f in report["files"] if f["bucket"] == "on-demand"]
    assert len(loaded) >= 1
    all_loaded_paths = {f["relative_path"] for f in loaded}
    assert "SKILL.md" in all_loaded_paths
    on_demand_paths = {f["relative_path"] for f in on_demand}
    assert (
        all(
            any(d in p for d in ("references/", "agents/", "scripts/"))
            for p in on_demand_paths
        )
        or len(on_demand) == 0
    )


def test_strict_fails_when_marker_is_missing_in_fixture(tmp_path: Path) -> None:
    fixture = tmp_path / "fixture_bundle"
    fixture.mkdir()
    (fixture / "SKILL.md").write_text("# Empty skill\nNo markers here.\n")
    (fixture / "agents").mkdir()
    (fixture / "agents" / "openai.yaml").write_text("name: fixture\n")

    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "--format", "json", "--strict", "--dir", str(fixture)],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    report = json.loads(result.stdout)
    assert len(report["findings"]) > 0
    assert report["strict_ok"] is False


def test_strict_fails_when_sibling_is_missing(tmp_path: Path) -> None:
    fixture = tmp_path / "fixture_bundle"
    fixture.mkdir()
    (fixture / "SKILL.md").write_text(
        "# Idea skill\n"
        "Inspect repository evidence first\n"
        "one unresolved material decision question per turn\n"
        "explicit answer\n"
        "decision ledger\n"
        "Interview checkpoint: ready-for-critical\n"
        "Interview checkpoint: reopen\n"
        "Handoff checkpoint: ready-for-owner-change\n"
        "mandatory critical pass\n"
        "exactly one next owner\n"
        "chat-only `Simple Task Brief`\n"
        "no hidden dispatch\n"
    )

    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "--format", "json", "--strict", "--dir", str(fixture)],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    report = json.loads(result.stdout)
    assert any("missing expected sibling" in f for f in report["findings"])


def test_script_does_not_modify_audited_files(tmp_path: Path) -> None:
    fixture = tmp_path / "fixture_bundle"
    fixture.mkdir()
    skill_md = fixture / "SKILL.md"
    original = "evidence pass before questions\none unresolved material question\n"
    skill_md.write_text(original)
    (fixture / "agents").mkdir()
    (fixture / "agents" / "openai.yaml").write_text("name: fixture\n")

    subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "--dir", str(fixture)],
        capture_output=True,
        text=True,
        check=True,
    )

    assert skill_md.read_text() == original
