from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path
from types import ModuleType

SCRIPT_PATH = Path(
    ".github/skills/internal-gateway-simple-task/scripts/resolve_simple_task.py"
)
SKILL_PATH = Path(".github/skills/internal-gateway-simple-task/SKILL.md")
LANES_REFERENCE_PATH = Path(
    ".github/skills/internal-gateway-simple-task/references/simple-lanes.md"
)
INTERNAL_ONLY_LANES = ("unspecified",)
OUTCOME_ONLY_LANES = ("escalate",)


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


def test_gate_escalates_to_brainstorming_when_plan_or_ownership_is_unsettled() -> None:
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


def lanes_from_simple_lanes_reference(reference_text: str) -> set[str]:
    table_start = reference_text.index("## Lane Selection")
    table_end = reference_text.index("\n## ", table_start + 1)
    table_body = reference_text[table_start:table_end]
    return {
        match.group(1)
        for match in re.finditer(r"^\| `([a-z-]+)` \|", table_body, flags=re.MULTILINE)
    }


def lanes_from_skill_when_to_use(skill_text: str) -> set[str]:
    section_start = skill_text.index("## When to use")
    section_end = skill_text.index("\n## ", section_start + 1)
    section_body = skill_text[section_start:section_end]
    for line in section_body.splitlines():
        if "quick lane can finish" not in line:
            continue
        return set(re.findall(r"`([a-z-]+)`", line))
    return set()


def test_helper_lanes_match_canonical_simple_lanes_reference() -> None:
    module = load_script_module()
    documented_lanes = lanes_from_simple_lanes_reference(
        LANES_REFERENCE_PATH.read_text(encoding="utf-8")
    )
    user_choosable_lanes = set(module.LANES) - set(INTERNAL_ONLY_LANES)
    documented_choosable_lanes = documented_lanes - set(OUTCOME_ONLY_LANES)

    assert user_choosable_lanes == documented_choosable_lanes


def test_skill_when_to_use_lane_list_matches_helper_lanes() -> None:
    module = load_script_module()
    skill_text = SKILL_PATH.read_text(encoding="utf-8")
    listed_lanes = lanes_from_skill_when_to_use(skill_text)
    user_choosable_lanes = set(module.LANES) - set(INTERNAL_ONLY_LANES)

    assert listed_lanes == user_choosable_lanes


def test_execute_lane_is_not_exposed_by_helper_or_skill_summary() -> None:
    module = load_script_module()
    skill_text = SKILL_PATH.read_text(encoding="utf-8")

    assert "execute" not in module.LANES
    assert "execute" not in lanes_from_skill_when_to_use(skill_text)
