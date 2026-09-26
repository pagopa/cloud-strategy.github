import re
from pathlib import Path

import yaml

LINK_TARGET = re.compile(r"\]\(([^)#\s]+)(?:#[^)]*)?\)")

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


def _relative_link_targets(markdown_path: Path) -> set[Path]:
    text = markdown_path.read_text(encoding="utf-8")
    return {
        (markdown_path.parent / target).resolve()
        for target in LINK_TARGET.findall(text)
        if "://" not in target
    }


def test_every_reference_is_linked_from_skill_md() -> None:
    linked = _relative_link_targets(BUNDLE_ROOT / "SKILL.md")
    references = {
        path.resolve() for path in (BUNDLE_ROOT / "references").glob("*.md")
    }

    assert sorted(p.name for p in references - linked) == []


def test_relative_markdown_links_resolve_inside_bundle() -> None:
    sources = [BUNDLE_ROOT / "SKILL.md", *(BUNDLE_ROOT / "references").glob("*.md")]
    bundle = BUNDLE_ROOT.resolve()

    for source in sources:
        for target in _relative_link_targets(source):
            assert target.is_file(), f"{source.name} -> {target}"
            assert target.is_relative_to(bundle), f"{source.name} -> {target}"


def test_bundle_contains_declared_local_siblings() -> None:
    assert (BUNDLE_ROOT / "SKILL.md").is_file()
    assert (BUNDLE_ROOT / "agents/openai.yaml").is_file()
    assert (BUNDLE_ROOT / "references/authoring-and-evaluation.md").is_file()
    assert (BUNDLE_ROOT / "references/cache-and-token-efficiency.md").is_file()
    assert (BUNDLE_ROOT / "references/eval-packs.md").is_file()
    assert (BUNDLE_ROOT / "references/grading-and-analysis.md").is_file()
    assert (BUNDLE_ROOT / "scripts/check_eval_pack.py").is_file()
    assert (BUNDLE_ROOT / "fixtures/eval-packs/valid-pack.json").is_file()
    assert (BUNDLE_ROOT / "fixtures/eval-packs/defective-packs.json").is_file()
    assert (BUNDLE_ROOT / "fixtures/eval-packs/valid-run-record.json").is_file()
    assert (BUNDLE_ROOT / "fixtures/eval-packs/pack-mutations.json").is_file()
    assert (BUNDLE_ROOT / "tests/evaluation/evals.json").is_file()
    assert (BUNDLE_ROOT / "tests/evaluation/fixtures/generated-pack-output.json").is_file()
    assert (BUNDLE_ROOT / "tests/evaluation/fixtures/generated-pack-defective.json").is_file()
