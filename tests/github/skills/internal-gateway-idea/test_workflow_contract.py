import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)
SKILL_PATH = REPO_ROOT / ".github/skills/internal-gateway-idea/SKILL.md"
WORKFLOW_PATH = (
    REPO_ROOT / ".github/skills/internal-gateway-idea/references/workflow.md"
)
AGENT_PATH = REPO_ROOT / ".github/skills/internal-gateway-idea/agents/openai.yaml"
SCRIPT_PATH = (
    REPO_ROOT / ".github/skills/internal-gateway-idea/scripts/audit_workflow.py"
)

MANDATORY_SEQUENCE = [
    "Specialization Checkpoint: gated",
    "Idea Gate 0",
    "Assumption Challenge Gate",
    "Alternative discovery",
    "Critical Challenge Gate",
    "Spec vs plan decision",
    "Stop before implementation execution",
]


def _assert_in_order(text: str, markers: list[str]) -> None:
    positions = [text.index(marker) for marker in markers]
    assert positions == sorted(positions)


def test_skill_and_workflow_keep_the_same_gate_order() -> None:
    _assert_in_order(SKILL_PATH.read_text(), MANDATORY_SEQUENCE)
    _assert_in_order(WORKFLOW_PATH.read_text(), MANDATORY_SEQUENCE)


def test_bundle_docs_reference_the_scoped_fast_lane() -> None:
    assert "make internal-gateway-idea-fast-check" in SKILL_PATH.read_text()
    assert "make internal-gateway-idea-fast-check" in WORKFLOW_PATH.read_text()


def test_audit_workflow_reports_extended_contract_status() -> None:
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH)],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)

    assert payload["strict_ok"] is True
    assert payload["markers"]["skill_gate_sequence"] is True
    assert payload["markers"]["workflow_gate_sequence"] is True
    assert payload["markers"]["runtime_core_markers"] is True
    assert payload["markers"]["local_fast_lane_documented"] is True
