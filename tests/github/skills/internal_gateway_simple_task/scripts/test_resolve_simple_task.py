from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

SCRIPT_PATH = Path(
    ".github/skills/internal-gateway-simple-task/scripts/resolve_simple_task.py"
)


def load_script_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("resolve_simple_task", SCRIPT_PATH)

    assert spec is not None
    assert spec.loader is not None

    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_detect_depth_keywords_from_prompt() -> None:
    module = load_script_module()

    assert module.detect_depth_keywords("vai in modalita full", []) == ["full"]


def test_gate_returns_trivial_skip_for_bounded_local_edit() -> None:
    module = load_script_module()
    decision = module.build_gate_decision(
        task="tighten one line in a markdown file",
        lane="edit",
        trivial_kind="tiny-edit",
        validation_path="markdownlint .github/skills/internal-gateway-simple-task/SKILL.md",
    )

    assert decision["gate_outcome"] == "trivial-skip"
    assert decision["next_owner"] == "internal-gateway-simple-task"
    assert decision["lane"] == "edit"
    assert "trivial-kind:tiny-edit" in decision["reason_codes"]


def test_gate_depth_keyword_forbids_trivial_skip() -> None:
    module = load_script_module()
    decision = module.build_gate_decision(
        task="tighten one line in a markdown file",
        lane="edit",
        trivial_kind="tiny-edit",
        prompt="vai in modalita full",
        validation_path="markdownlint .github/skills/internal-gateway-simple-task/SKILL.md",
    )

    assert decision["gate_outcome"] == "full-gate"
    assert "depth-keyword:full" in decision["reason_codes"]


def test_gate_escalates_to_brainstorming_when_plan_or_ownership_is_unsettled() -> (
    None
):
    module = load_script_module()
    decision = module.build_gate_decision(
        task="redesign the simple-task bundle",
        needs_plan=True,
        owner_ambiguous=True,
        validation_gap="validation path depends on which bundle surfaces change",
    )

    assert decision["gate_outcome"] == "escalate"
    assert decision["next_owner"] == "internal-gateway-idea-brainstorming"
    assert "needs-plan" in decision["reason_codes"]
    assert "owner-ambiguous" in decision["reason_codes"]


def test_gate_escalates_to_review_when_review_is_the_real_job() -> None:
    module = load_script_module()
    decision = module.build_gate_decision(
        task="decide whether this diff is merge-ready",
        needs_review=True,
        validation_gap="review evidence is not collected yet",
    )

    assert decision["gate_outcome"] == "escalate"
    assert decision["next_owner"] == "internal-gateway-review"


def test_claim_resolution_for_fixed_requires_debugging_and_verification() -> None:
    module = load_script_module()
    requirements = module.resolve_claim_requirements(["fixed"])

    assert requirements == [
        {
            "owner": "internal-debugging",
            "evidence_gate": "Re-run the original loop, or state the blocker.",
        },
        {
            "owner": "superpowers-verification-before-completion",
            "evidence_gate": "Fresh validation evidence, not intent or stale output.",
        },
    ]


def test_claim_resolution_deduplicates_verification_owner() -> None:
    module = load_script_module()
    requirements = module.resolve_claim_requirements(["pr-ready", "completion"])

    assert requirements == [
        {
            "owner": "internal-github-pr",
            "evidence_gate": "Check PR lifecycle evidence before the claim.",
        },
        {
            "owner": "superpowers-verification-before-completion",
            "evidence_gate": "Fresh validation evidence, not intent or stale output.",
        },
    ]
