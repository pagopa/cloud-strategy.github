import json
import subprocess
import sys
from pathlib import Path

import yaml

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
    "External Research Checkpoint",
    "Assumption Challenge Gate",
    "Alternative discovery",
    "Critical Challenge Gate",
    "Critical resolution loop",
    "Automatic plan handoff",
    "Stop before implementation execution",
]


def _assert_in_order(text: str, markers: list[str]) -> None:
    positions = [text.index(marker) for marker in markers]
    assert positions == sorted(positions)


def test_skill_and_workflow_keep_the_same_gate_order() -> None:
    _assert_in_order(SKILL_PATH.read_text(), MANDATORY_SEQUENCE)
    _assert_in_order(WORKFLOW_PATH.read_text(), MANDATORY_SEQUENCE)


def test_runtime_prompt_keeps_the_full_mandatory_gate_sequence() -> None:
    _assert_in_order(AGENT_PATH.read_text(), MANDATORY_SEQUENCE)


def test_idea_runtime_surfaces_delegate_to_the_expected_owners() -> None:
    surfaces = (
        SKILL_PATH.read_text(encoding="utf-8"),
        WORKFLOW_PATH.read_text(encoding="utf-8"),
        yaml.safe_load(AGENT_PATH.read_text(encoding="utf-8"))["interface"][
            "default_prompt"
        ],
        SCRIPT_PATH.read_text(encoding="utf-8"),
    )
    for text in surfaces:
        assert "/superpowers-brainstorming" in text
        assert "/internal-gateway-writing-plans" in text


def test_idea_skill_allows_model_invocation() -> None:
    skill_frontmatter = yaml.safe_load(SKILL_PATH.read_text().split("---", 2)[1])

    assert skill_frontmatter.get("disable-model-invocation") is not True


def test_bundle_docs_use_repository_root_validation_commands() -> None:
    root_command = (
        "python3 .github/skills/internal-gateway-idea/scripts/audit_workflow.py"
    )
    assert root_command in SKILL_PATH.read_text()
    assert root_command in WORKFLOW_PATH.read_text()


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
    assert payload["markers"]["compact_chat_projection"] is True
    assert payload["markers"]["runtime_gate_sequence"] is True
    assert payload["markers"]["runtime_research_checkpoint"] is True
    assert payload["markers"]["skill_exclusion_removed"] is True
    assert payload["markers"]["critical_routing"] is True
    assert payload["markers"]["critical_mermaid_routing"] is True
    assert payload["markers"]["handoff_card"] is True
    assert payload["markers"]["automatic_plan_handoff"] is True


def test_idea_bundle_has_compact_user_facing_projection() -> None:
    skill_text = SKILL_PATH.read_text()
    workflow_text = WORKFLOW_PATH.read_text()
    runtime_text = AGENT_PATH.read_text()

    required = [
        "compact user-facing decision card",
        "internal workflow state",
        "🎯",
        "🧭",
        "🛠️",
        "🧪",
        "⚠️",
        "✅",
        "💡",
        "✈️",
    ]
    for marker in required:
        assert marker in skill_text
        assert marker in workflow_text
        assert marker in runtime_text


def test_idea_projection_hides_non_decision_bookkeeping() -> None:
    skill_text = SKILL_PATH.read_text()

    assert "Do not announce skipped checkpoints" in skill_text
    assert "Do not print the internal gate ledger" in skill_text
    assert "four content lines" in skill_text


def test_idea_gate_preserves_bulk_questions_and_scopes_compact_cards() -> None:
    skill_text = SKILL_PATH.read_text()
    workflow_text = WORKFLOW_PATH.read_text()
    runtime_text = AGENT_PATH.read_text()

    required = [
        "numbered bulk question block",
        "Question",
        "Recommendation",
        "Why",
        "Default if accepted",
        "content-bearing output",
    ]
    for text in (skill_text, workflow_text, runtime_text):
        for marker in required:
            assert marker in text

    assert "one unresolved decision at a time" not in skill_text
    assert "one unresolved decision at a time" not in workflow_text
    assert "one unresolved decision at a time" not in runtime_text


def test_external_research_checkpoint_is_lazy_and_skill_owned() -> None:
    skill_text = SKILL_PATH.read_text()
    workflow_text = WORKFLOW_PATH.read_text()

    required = [
        "mattpocock-research",
        "External Research Checkpoint",
        "tmp/research/",
        "on-demand",
        "local evidence is insufficient",
        "feasibility, approach, constraints, or risk",
    ]
    for marker in required:
        assert marker in skill_text
        assert marker in workflow_text

    assert "does not preload" in skill_text
    assert "owns when research is warranted" in skill_text
    assert "owns how the research is performed" in skill_text


def test_external_research_checkpoint_sits_between_idea_and_challenge() -> None:
    skill_text = SKILL_PATH.read_text()
    workflow_text = WORKFLOW_PATH.read_text()

    skill_sequence = [
        "3. `Idea Gate 0`",
        "4. `External Research Checkpoint`",
        "5. `Assumption Challenge Gate`",
    ]
    workflow_sequence = [
        "D[Idea Gate 0]",
        "F{External Research Checkpoint}",
        "H[Assumption Challenge Gate]",
    ]
    _assert_in_order(skill_text, skill_sequence)
    _assert_in_order(workflow_text, workflow_sequence)


def test_external_research_checkpoint_has_bounded_outcomes() -> None:
    skill_text = SKILL_PATH.read_text(encoding="utf-8")
    workflow_text = WORKFLOW_PATH.read_text(encoding="utf-8")

    outcomes = [
        "skip",
        "load `/mattpocock-research`",
        "one bounded research question",
        "one Markdown report",
        "decision-relevant conclusions",
        "do not start a second research pass automatically",
    ]
    for marker in outcomes:
        assert marker in skill_text
        assert marker in workflow_text


def test_skill_has_no_when_not_to_use_exclusion_block() -> None:
    skill_text = SKILL_PATH.read_text(encoding="utf-8")

    assert "## When not to use" not in skill_text


def test_critical_routing_contract_exposes_only_approved_outcomes() -> None:
    surfaces = (
        SKILL_PATH.read_text(encoding="utf-8"),
        WORKFLOW_PATH.read_text(encoding="utf-8"),
        yaml.safe_load(AGENT_PATH.read_text(encoding="utf-8"))["interface"][
            "default_prompt"
        ],
    )
    outcomes = [
        "accepted",
        "revise-design",
        "reopen-analysis",
        "needs-clarification",
    ]
    for text in surfaces:
        for marker in outcomes:
            assert marker in text
        assert "every material objection raised during the current critical pass is closed or explicitly routed" in text
        assert "accepted" in text and "Automatic plan handoff" in text
        assert "revise-design" in text and "design presentation" in text and "design approval" in text
        assert "reopen-analysis" in text and "Idea Gate 0" in text
        assert "needs-clarification" in text and "/grill-me" in text
        assert "material change" in text and "Critical Challenge Gate" in text
        assert "Spec vs plan decision" not in text
        assert "Decision: spec first" not in text
        assert "Approval request" not in text


def test_critical_routing_uses_the_exact_plan_handoff_card() -> None:
    surfaces = (
        SKILL_PATH.read_text(encoding="utf-8"),
        WORKFLOW_PATH.read_text(encoding="utf-8"),
        yaml.safe_load(AGENT_PATH.read_text(encoding="utf-8"))["interface"][
            "default_prompt"
        ],
    )
    card = """🚀 **Scrittura del piano avviata**
✅ La critica si è conclusa senza obiezioni materiali aperte.
🛠️ `/internal-gateway-writing-plans` sta preparando il piano di implementazione."""
    for text in surfaces:
        assert card in text


def test_writing_gateway_is_only_an_implementation_plan_owner() -> None:
    surfaces = (
        SKILL_PATH.read_text(encoding="utf-8"),
        WORKFLOW_PATH.read_text(encoding="utf-8"),
        AGENT_PATH.read_text(encoding="utf-8"),
    )
    for text in surfaces:
        assert "internal-gateway-writing-plans" in text
        assert "retained spec or implementation-plan writing" not in text
    assert "implementation-plan writing" in surfaces[0]
