import re
from pathlib import Path

import yaml

LINK_TARGET = re.compile(r"\]\(([^)#\s]+)(?:#[^)]*)?\)")

BUNDLE_ROOT = Path(__file__).resolve().parents[1]


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


def _relative_link_targets(markdown_path: Path) -> set[Path]:
    text = markdown_path.read_text(encoding="utf-8")
    return {
        (markdown_path.parent / target).resolve()
        for target in LINK_TARGET.findall(text)
        if "://" not in target
    }


def test_every_reference_is_linked_from_skill_md() -> None:
    linked = _relative_link_targets(BUNDLE_ROOT / "SKILL.md")
    references = {path.resolve() for path in (BUNDLE_ROOT / "references").glob("*.md")}

    assert sorted(p.name for p in references - linked) == []


def test_relative_markdown_links_resolve_inside_bundle() -> None:
    sources = [BUNDLE_ROOT / "SKILL.md", *(BUNDLE_ROOT / "references").glob("*.md")]
    bundle = BUNDLE_ROOT.resolve()

    for source in sources:
        for target in _relative_link_targets(source):
            assert target.is_file(), f"{source.name} -> {target}"
            assert target.is_relative_to(bundle), f"{source.name} -> {target}"
