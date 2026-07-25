from pathlib import Path

import yaml


REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)
SKILLS_ROOT = REPO_ROOT / ".github/skills"
SKILL_NAMES = (
    "internal-yaml",
    "internal-markdown",
    "internal-makefile",
    "internal-json",
)


def _skill_text(skill_name: str) -> str:
    return (SKILLS_ROOT / skill_name / "SKILL.md").read_text(encoding="utf-8")


def _description(skill_name: str) -> str:
    text = _skill_text(skill_name)
    return str(yaml.safe_load(text.split("---", 2)[1])["description"])


def _default_prompt(skill_name: str) -> str:
    payload = yaml.safe_load(
        (SKILLS_ROOT / skill_name / "agents/openai.yaml").read_text(
            encoding="utf-8"
        )
    )
    return str(payload["interface"]["default_prompt"])


def test_format_skill_descriptions_and_prompts_cover_review_work() -> None:
    for skill_name in SKILL_NAMES:
        assert "review" in _description(skill_name).lower()
        assert "review" in _default_prompt(skill_name).lower()


def test_markdown_skill_does_not_require_separate_readme_authorization() -> None:
    markdown = _skill_text("internal-markdown")

    assert "README files unless the user explicitly authorizes" not in markdown


def test_yaml_skill_routes_cloudformation_to_schema_aware_owner() -> None:
    yaml_skill = _skill_text("internal-yaml")

    assert "/antigravity-cloudformation-best-practices" in yaml_skill
    assert "aws cloudformation validate-template" in yaml_skill


def test_makefile_skill_routes_shell_and_treats_dry_run_as_preview() -> None:
    makefile = _skill_text("internal-makefile")

    assert "/internal-bash" in makefile
    assert "preview" in makefile.lower()
    assert "recursive" in makefile.lower()
    assert "side effect" in makefile.lower()


def test_json_skill_distinguishes_syntax_from_duplicate_key_validation() -> None:
    json_skill = _skill_text("internal-json")

    assert "syntax" in json_skill.lower()
    assert "duplicate" in json_skill.lower()
    assert "object_pairs_hook" in json_skill
