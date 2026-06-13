from __future__ import annotations

from pathlib import Path


def read_text(relative_path: str) -> str:
    return Path(relative_path).read_text(encoding="utf-8")


SKILL_SOURCE_MAP = {
    ".github/skills/agent-os-discover-standards/SKILL.md": ".claude/commands/agent-os/discover-standards.md",
    ".github/skills/agent-os-index-standards/SKILL.md": ".claude/commands/agent-os/index-standards.md",
    ".github/skills/agent-os-inject-standards/SKILL.md": ".claude/commands/agent-os/inject-standards.md",
    ".github/skills/agent-os-plan-product/SKILL.md": ".claude/commands/agent-os/plan-product.md",
    ".github/skills/agent-os-shape-spec/SKILL.md": ".claude/commands/agent-os/shape-spec.md",
}


def test_agent_os_portable_skills_are_present_and_mapped() -> None:
    for skill_path, source_path in SKILL_SOURCE_MAP.items():
        text = read_text(skill_path)
        assert "## Referenced skills" in text
        assert "## Source command parity" in text
        assert source_path in text


def test_agent_os_portable_skills_keep_runtime_portability_boundary() -> None:
    for skill_path in SKILL_SOURCE_MAP:
        text = read_text(skill_path)
        assert "portable for Copilot and Codex" in text
        assert "does not rely on Claude slash commands" in text


def test_agent_os_portable_skills_preserve_declarative_storage_targets() -> None:
    discover_text = read_text(".github/skills/agent-os-discover-standards/SKILL.md")
    plan_product_text = read_text(".github/skills/agent-os-plan-product/SKILL.md")
    shape_spec_text = read_text(".github/skills/agent-os-shape-spec/SKILL.md")

    assert "agent-os/standards/" in discover_text
    assert "agent-os/product/" in plan_product_text
    assert "agent-os/specs/" in shape_spec_text
