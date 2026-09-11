from __future__ import annotations

import sys
from pathlib import Path
from typing import Callable

import pytest

REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)
TOOLS_ROOT = REPO_ROOT / ".github/tools"
if str(TOOLS_ROOT) not in sys.path:
    sys.path.insert(0, str(TOOLS_ROOT))

from common.findings import Finding  # noqa: E402
from tokens.rules import (  # noqa: E402
    check_agents_operational_procedure_markers,
    check_copilot_review_budget,
    check_duplicate_markdown_bodies,
    check_gateway_core_budget,
    check_imported_skill_description_budget,
    check_internal_agent_skill_list_size,
    check_internal_root_policy_overlap,
    check_inventory_dumps,
    check_paired_agent_skill_overlap,
    check_review_baseline_window,
    check_root_always_on_budget,
    check_root_policy_overlap,
    check_skill_description_trigger_collisions,
)

RuleCase = Callable[[Path], list[Finding]]


def _write(root: Path, relative_path: str, content: str) -> Path:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def _root_always_on_budget(root: Path) -> list[Finding]:
    _write(root, "AGENTS.md", "x" * 16001)
    return check_root_always_on_budget(root)


def _copilot_review_budget(root: Path) -> list[Finding]:
    _write(root, ".github/copilot-instructions.md", "x" * 2401)
    return check_copilot_review_budget(root)


def _agents_operational_marker(root: Path) -> list[Finding]:
    _write(root, "AGENTS.md", "## Retained Plans\n")
    return check_agents_operational_procedure_markers(root)


def _review_baseline_window(root: Path) -> list[Finding]:
    _write(root, ".github/instructions/copilot-code-review.instructions.md", "review\n")
    return check_review_baseline_window(root)


def _shared_policy_lines() -> str:
    return "\n".join(
        [
            "Stable policy line for shared governance context.",
            "Another stable policy line for shared governance context.",
            "A third stable policy line for shared governance context.",
            "A fourth stable policy line for shared governance context.",
            "A fifth stable policy line for shared governance context.",
        ]
    )


def _root_policy_overlap(root: Path) -> list[Finding]:
    shared = _shared_policy_lines()
    _write(root, "AGENTS.md", shared)
    _write(root, ".github/copilot-instructions.md", shared)
    return check_root_policy_overlap(root)


def _inventory_dump(root: Path) -> list[Finding]:
    paths = "\n".join(f"- .github/asset-{index}" for index in range(1, 6))
    _write(root, "AGENTS.md", paths + "\n")
    return check_inventory_dumps(root)


def _duplicate_markdown_body(root: Path) -> list[Finding]:
    body = "\n".join(
        "A repeated governance sentence with enough detail." for _ in range(6)
    )
    _write(root, ".github/agents/internal-one.agent.md", body)
    _write(root, ".github/agents/internal-two.agent.md", body)
    return check_duplicate_markdown_bodies(root)


def _imported_description_budget(root: Path) -> list[Finding]:
    description = "x" * 500
    _write(
        root,
        ".github/skills/external-example/SKILL.md",
        f"---\nname: external-example\ndescription: {description}\n---\n",
    )
    return check_imported_skill_description_budget(root)


def _description_trigger_collision(root: Path) -> list[Finding]:
    description = "Use when validating the same long routing trigger for this fixture."
    content = f"---\nname: example\ndescription: {description}\n---\n"
    _write(root, ".github/skills/internal-one/SKILL.md", content)
    _write(
        root,
        ".github/skills/internal-two/SKILL.md",
        content.replace("name: example", "name: internal-two"),
    )
    return check_skill_description_trigger_collisions(root)


def _large_skill_list(root: Path) -> list[Finding]:
    bullets = "\n".join(f"- internal-support-{index}" for index in range(1, 10))
    _write(
        root,
        ".github/agents/internal-example.agent.md",
        f"## Optional Support Skills\n\n{bullets}\n",
    )
    return check_internal_agent_skill_list_size(root)


def _duplicate_skill_entry(root: Path) -> list[Finding]:
    _write(
        root,
        ".github/agents/internal-example.agent.md",
        "## Optional Support Skills\n\n- internal-support\n- internal-support\n",
    )
    return check_internal_agent_skill_list_size(root)


def _internal_root_policy_overlap(root: Path) -> list[Finding]:
    shared = _shared_policy_lines()
    _write(root, "AGENTS.md", shared)
    _write(root, ".github/copilot-instructions.md", shared)
    _write(
        root,
        ".github/agents/internal-example.agent.md",
        "AGENTS.md\n.github/copilot-instructions.md\n" + shared,
    )
    return check_internal_root_policy_overlap(root)


def _paired_agent_skill_overlap(root: Path) -> list[Finding]:
    shared = "\n".join(
        f"Shared paired boundary guidance line number {index} is intentionally repeated."
        for index in range(1, 7)
    )
    _write(
        root,
        ".github/agents/internal-example.agent.md",
        "---\nname: internal-example\n---\n"
        "## Mandatory Engine Skills\n\n- internal-example\n\n" + shared + "\n",
    )
    _write(
        root,
        ".github/skills/internal-example/SKILL.md",
        "---\nname: internal-example\ndescription: Use when testing paired overlap.\n---\n\n"
        + shared
        + "\n",
    )
    return check_paired_agent_skill_overlap(root)


def _gateway_core_budget(root: Path) -> list[Finding]:
    _write(root, ".github/skills/internal-gateway-idea/SKILL.md", "x" * 16287)
    return check_gateway_core_budget(root)


TOKEN_RULE_CASES: list[tuple[str, RuleCase]] = [
    ("root-always-on-budget", _root_always_on_budget),
    ("copilot-review-over-budget", _copilot_review_budget),
    ("agents-operational-procedure-marker", _agents_operational_marker),
    ("review-baseline-window-missing-core-rules", _review_baseline_window),
    ("root-policy-overlap", _root_policy_overlap),
    ("inventory-dump-in-root-policy", _inventory_dump),
    ("duplicate-markdown-body", _duplicate_markdown_body),
    ("imported-skill-description-budget", _imported_description_budget),
    ("skill-description-trigger-collision", _description_trigger_collision),
    ("large-skill-list", _large_skill_list),
    ("duplicate-skill-entry", _duplicate_skill_entry),
    ("internal-root-policy-overlap", _internal_root_policy_overlap),
    ("paired-agent-skill-overlap", _paired_agent_skill_overlap),
    ("gateway-core-byte-budget", _gateway_core_budget),
]


def test_token_rule_case_inventory_is_explicit() -> None:
    codes = [code for code, _ in TOKEN_RULE_CASES]
    assert len(codes) == len(set(codes))
    assert len(codes) == 14


@pytest.mark.parametrize(
    "code, build_findings", TOKEN_RULE_CASES, ids=[code for code, _ in TOKEN_RULE_CASES]
)
def test_token_rule_reports_non_absence_finding(
    tmp_path: Path, code: str, build_findings: RuleCase
) -> None:
    findings = build_findings(tmp_path)
    matching = [finding for finding in findings if finding.code == code]

    assert matching, f"{code} did not produce its expected finding"
    assert matching[0].path
    assert matching[0].message
