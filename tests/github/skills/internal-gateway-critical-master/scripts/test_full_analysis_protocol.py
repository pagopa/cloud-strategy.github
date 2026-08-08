from __future__ import annotations

import importlib.util
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
MODULE_PATH = (
    REPO_ROOT
    / ".github/skills/internal-gateway-critical-master/scripts/full_analysis.py"
)
SKILL_DIR = REPO_ROOT / ".github/skills/internal-gateway-critical-master"
TARGET = "tmp/idea/sample/design.md"


def _load_module():
    assert MODULE_PATH.exists(), f"missing protocol module: {MODULE_PATH}"
    spec = importlib.util.spec_from_file_location("full_analysis", MODULE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _finding(
    *,
    finding_id: str = "C-001",
    blocking: bool = False,
    evidence: list[str] | None = None,
) -> dict[str, object]:
    return {
        "id": finding_id,
        "critique": "The proposed change weakens a current control.",
        "recommendation": "Keep the current boundary.",
        "reason": "The control has no equivalent evidence yet.",
        "blocking": blocking,
        "evidence": evidence or ["design.md#L12"],
    }


def _packet(**overrides: object) -> dict[str, object]:
    packet: dict[str, object] = {
        "schema": "internal-gateway-critical/full-analysis-v1",
        "source": "standard",
        "target_path": TARGET,
        "target_revision": 3,
        "outcome": "accepted",
        "findings": [],
        "residual_risks": [],
        "diagnostics": [],
    }
    packet.update(overrides)
    return packet


def _parse(module, packet: dict[str, object]):
    return module.parse_full_analysis_packet(
        json.dumps(packet), expected_target_path=TARGET, expected_revision=3
    )


def test_valid_packet_is_accepted() -> None:
    module = _load_module()

    result = _parse(module, _packet(outcome="revise-design", findings=[_finding()]))

    assert result.outcome == "revise-design"
    assert result.findings[0].id == "C-001"


@pytest.mark.parametrize(
    "packet_change",
    (
        {"target_path": "tmp/other/design.md"},
        {"target_revision": 4},
        {"target_revision": True},
    ),
)
def test_target_binding_is_strict(packet_change: dict[str, object]) -> None:
    module = _load_module()

    result = _parse(module, _packet(**packet_change))

    assert result.outcome == "invalid-target"
    assert result.diagnostics


def test_invalid_outcome_invariant_fails_closed() -> None:
    module = _load_module()

    result = _parse(module, _packet(outcome="accepted", findings=[_finding(blocking=True)]))

    assert result.outcome == "invalid-target"
    assert result.diagnostics


def test_markdown_card_is_not_a_full_analysis_packet() -> None:
    module = _load_module()

    result = module.parse_full_analysis_packet(
        "🎯 **Piano:** Critica\n⚠️ **Critica:** Problema\n✅ **Consiglio:** Fermarsi",
        expected_target_path=TARGET,
        expected_revision=3,
    )

    assert result.outcome == "invalid-target"
    assert result.diagnostics


def test_cli_validates_json_packet() -> None:
    packet = json.dumps(_packet(outcome="revise-design", findings=[_finding()]))

    result = subprocess.run(
        [
            sys.executable,
            str(MODULE_PATH),
            "--target-path",
            TARGET,
            "--revision",
            "3",
            "--format",
            "compact",
        ],
        input=packet,
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0
    assert '"status": "ok"' in result.stdout


def test_card_only_bundle_members_are_retired() -> None:
    retired = (
        SKILL_DIR / "references/output-contract.md",
        SKILL_DIR / "scripts/critical_master.py",
        SKILL_DIR / "scripts/validate_critical_output.py",
        SKILL_DIR / "fixtures/critical_output_valid.md",
        SKILL_DIR / "fixtures/critical_output_valid_premortem.md",
        SKILL_DIR / "fixtures/routing_cases.json",
    )

    assert all(not path.exists() for path in retired)
