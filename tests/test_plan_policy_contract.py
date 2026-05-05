from __future__ import annotations

from pathlib import Path

PLAN_SKILL_PATHS = {
    "internal-writing-plans": ".github/skills/internal-writing-plans/SKILL.md",
    "internal-executing-plans": ".github/skills/internal-executing-plans/SKILL.md",
}

PLAN_TASK_PATH = "tmp/superpowers/<clear-action-or-task-name>/"


def read_text(relative_path: str) -> str:
    return Path(relative_path).read_text(encoding="utf-8")


def assert_plan_policy_anchors(text: str) -> None:
    assert PLAN_TASK_PATH in text
    assert "01-...md" in text
    assert "01-contesto-e-vincoli.md" in text
    assert "dubbi-e-domande.md" in text
    assert "done-*" in text


def test_root_policy_files_define_repository_plan_defaults() -> None:
    agents_text = read_text("AGENTS.md")
    copilot_text = read_text(".github/copilot-instructions.md")

    assert (
        "The default authoring language for repository artifacts is English"
        in agents_text
    )
    assert_plan_policy_anchors(agents_text)
    assert "Italian" in agents_text
    assert "clear, local, quick, or banal tasks" not in agents_text
    assert "non-banal" in agents_text
    assert "macro-categories" in agents_text
    assert "continue through the remaining numbered plan files" in agents_text
    assert "`Obiettivo`" not in agents_text
    assert "5-7 bullets when practical" not in agents_text

    assert (
        "The default authoring language for repository artifacts is English"
        in copilot_text
    )
    assert_plan_policy_anchors(copilot_text)
    assert "Italian" in copilot_text
    assert "clear, local, quick, or banal tasks" in copilot_text
    assert "retained planning is justified" in copilot_text
    assert "`internal-writing-plans`" in copilot_text
    assert "continue through the remaining numbered plan files" in copilot_text
    assert "`Obiettivo`" not in copilot_text
    assert "5-7 bullets when practical" not in copilot_text


def test_internal_planning_leader_prefers_repository_plan_wrappers() -> None:
    planning_leader_text = read_text(".github/agents/internal-planning-leader.agent.md")

    assert "- `internal-writing-plans`" in planning_leader_text
    assert "- `internal-executing-plans`" in planning_leader_text
    assert "prefer `internal-writing-plans`" in planning_leader_text
    assert "prefer `internal-executing-plans`" in planning_leader_text
    assert "clear, local, quick, or banal tasks" in planning_leader_text
    assert "retained execution plan" in planning_leader_text


def test_plan_wrapper_skills_are_listed_in_ownership_map_and_inventory() -> None:
    ownership_map_text = read_text(
        ".github/skills/internal-agent-operational-flow/references/mode-contracts.md"
    )
    inventory_text = read_text(".github/INVENTORY.md")

    assert (
        "| `internal-writing-plans` | `plan` mode |"
        in ownership_map_text
    )
    assert (
        "| `internal-executing-plans` | `plan` mode oversight |"
        in ownership_map_text
    )
    assert PLAN_TASK_PATH in ownership_map_text

    for skill_path in PLAN_SKILL_PATHS.values():
        assert f"- `{skill_path}`" in inventory_text

    assert "- `.github/skills/internal-agent-operational-flow/SKILL.md`" in inventory_text
    assert "- `.github/skills/internal-agent-critical-master/SKILL.md`" in inventory_text


def test_plan_wrapper_skills_define_local_plan_contracts() -> None:
    writing_skill_text = read_text(PLAN_SKILL_PATHS["internal-writing-plans"])
    executing_skill_text = read_text(PLAN_SKILL_PATHS["internal-executing-plans"])

    assert "## When to use" in writing_skill_text
    assert PLAN_TASK_PATH in writing_skill_text
    assert "crosses turns" in writing_skill_text
    assert "handoff, tracking, or provenance" in writing_skill_text
    assert "01-contesto-e-vincoli.md" in writing_skill_text
    assert "macro-category" in writing_skill_text
    assert "monolithic" in writing_skill_text
    assert "dubbi-e-domande.md" in writing_skill_text
    assert "Italian" in writing_skill_text
    assert "## Local retained-plan contract" in writing_skill_text
    assert "## Numbered-file shape" in writing_skill_text
    assert "scanability and decision review" in writing_skill_text
    assert "`Obiettivo`" in writing_skill_text
    assert "`Logica scelta`" in writing_skill_text
    assert "`Assunzioni chiave`" in writing_skill_text
    assert "`Passi eseguibili`" in writing_skill_text
    assert "`Validazione`" in writing_skill_text
    assert "5-7 bullets when practical" in writing_skill_text
    assert "1-2 lines when practical" in writing_skill_text
    assert "outside the plan-and-apply loop" in writing_skill_text

    assert "## When to use" in executing_skill_text
    assert "retained numbered plans" in executing_skill_text
    assert "done-<source-file-name>.md" in executing_skill_text
    assert "dubbi-e-domande.md" in executing_skill_text
    assert "move it into the matching `done-*` file" in executing_skill_text
    assert "remove it from the active plan file" in executing_skill_text
    assert "Delete an active plan file" in executing_skill_text
    assert "Continue automatically" in executing_skill_text
    assert "Stop only for real blockers" in executing_skill_text


def test_plan_wrapper_skills_ship_openai_metadata() -> None:
    writing_metadata_text = read_text(
        ".github/skills/internal-writing-plans/agents/openai.yaml"
    )
    executing_metadata_text = read_text(
        ".github/skills/internal-executing-plans/agents/openai.yaml"
    )

    for metadata_text in (writing_metadata_text, executing_metadata_text):
        assert "interface:" in metadata_text
        assert "display_name:" in metadata_text
        assert "short_description:" in metadata_text

    assert "$internal-writing-plans" in writing_metadata_text
    assert "single or multi-file shape as needed" in writing_metadata_text
    assert "$internal-executing-plans" in executing_metadata_text
