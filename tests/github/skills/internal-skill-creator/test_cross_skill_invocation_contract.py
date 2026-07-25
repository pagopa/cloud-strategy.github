import re
from pathlib import Path

import yaml

REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)
SKILLS_ROOT = REPO_ROOT / ".github" / "skills"
CREATOR_ROOT = SKILLS_ROOT / "internal-skill-creator"

CALLED_SKILLS = {
    "internal-skill-creator": {
        "mattpocock-writing-great-skills",
    },
    "internal-gateway-codebase-improvement": {
        "addyosmani-code-simplification",
        "internal-tdd",
        "mattpocock-improve-codebase-architecture",
        "superpowers-verification-before-completion",
    },
    "internal-gateway-idea": {
        "internal-gateway-writing-plans",
        "mattpocock-research",
        "superpowers-brainstorming",
    },
    "internal-gateway-simple-task": {
        "addyosmani-code-simplification",
        "grill-me",
        "internal-gateway-critical-master",
        "internal-tdd",
        "superpowers-verification-before-completion",
    },
    "internal-gateway-writing-plans": {
        "internal-gateway-execute-plans",
        "superpowers-writing-plans",
    },
    "internal-gateway-execute-plans": {
        "addyosmani-code-simplification",
        "internal-tdd",
        "superpowers-executing-plans",
        "superpowers-verification-before-completion",
    },
}


def _instruction_text(skill_name: str) -> str:
    root = SKILLS_ROOT / skill_name
    paths = [root / "SKILL.md", root / "agents" / "openai.yaml"]
    paths.extend(sorted((root / "references").glob("*.md")))
    return "\n".join(
        path.read_text(encoding="utf-8") for path in paths if path.exists()
    )


def _frontmatter(skill_name: str) -> dict[str, object]:
    text = (SKILLS_ROOT / skill_name / "SKILL.md").read_text(encoding="utf-8")
    return yaml.safe_load(text.split("---", 2)[1])


def test_skill_creator_defines_slash_prefixed_cross_skill_invocation() -> None:
    text = (CREATOR_ROOT / "SKILL.md").read_text(encoding="utf-8")
    assert "Prefix every cross-skill invocation with `/`" in text


def test_creator_and_gateway_calls_are_slash_prefixed() -> None:
    for caller, callees in CALLED_SKILLS.items():
        text = _instruction_text(caller)
        for callee in callees:
            unprefixed = re.compile(
                rf"(?<![/a-z0-9-]){re.escape(callee)}(?![a-z0-9-])"
            )
            assert not unprefixed.search(text), (
                f"{caller} references {callee} without the required slash prefix"
            )
            assert f"/{callee}" in text


def test_called_skills_allow_model_invocation() -> None:
    for callee in set().union(*CALLED_SKILLS.values()):
        frontmatter = _frontmatter(callee)
        assert frontmatter.get("disable-model-invocation") is not True, (
            f"{callee} is called by another skill but blocks model invocation"
        )
