from pathlib import Path

import yaml

REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)
BUNDLE_ROOT = REPO_ROOT / ".github/skills/internal-skill-creator"


def test_skill_metadata_is_structurally_valid() -> None:
    skill_text = (BUNDLE_ROOT / "SKILL.md").read_text(encoding="utf-8")
    metadata = yaml.safe_load(skill_text.split("---", 2)[1])

    assert metadata["name"] == "internal-skill-creator"
    assert isinstance(metadata["description"], str)
    assert metadata["description"]


def test_bundle_metadata_has_typed_interface_fields() -> None:
    metadata = yaml.safe_load(
        (BUNDLE_ROOT / "agents/openai.yaml").read_text(encoding="utf-8")
    )
    interface = metadata["interface"]

    assert isinstance(interface["display_name"], str)
    assert isinstance(interface["short_description"], str)
    assert isinstance(interface["default_prompt"], str)


def test_bundle_contains_declared_local_siblings() -> None:
    assert (BUNDLE_ROOT / "SKILL.md").is_file()
    assert (BUNDLE_ROOT / "agents/openai.yaml").is_file()
    assert (BUNDLE_ROOT / "references/authoring-and-evaluation.md").is_file()
