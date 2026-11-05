from __future__ import annotations

import re
import shutil
from pathlib import Path
from typing import Any

import yaml

BUNDLE_ROOT = Path(__file__).resolve().parents[1]
FRONTMATTER_KEYS = {"name", "description", "metadata", "license", "compatibility"}
LINK_PATTERN = re.compile(r"\]\(([^)\s#]+)(?:#[^)]*)?\)")


def _split_skill(bundle: Path) -> tuple[dict[str, Any], str]:
    text = (bundle / "SKILL.md").read_text(encoding="utf-8")
    _, frontmatter, body = text.split("---\n", 2)
    return yaml.safe_load(frontmatter), body


def _local_links(markdown: str) -> set[str]:
    return {target for target in LINK_PATTERN.findall(markdown) if "://" not in target}


def test_frontmatter_and_metadata_are_portable() -> None:
    frontmatter, _ = _split_skill(BUNDLE_ROOT)
    metadata = yaml.safe_load((BUNDLE_ROOT / "agents/openai.yaml").read_text(encoding="utf-8"))

    assert set(frontmatter) <= FRONTMATTER_KEYS
    assert frontmatter["name"] == BUNDLE_ROOT.name
    assert {"display_name", "short_description", "default_prompt"} <= set(metadata["interface"])


def test_every_reference_is_linked_and_resolves_from_a_standalone_copy(tmp_path: Path) -> None:
    copied = tmp_path / BUNDLE_ROOT.name
    shutil.copytree(BUNDLE_ROOT, copied, ignore=shutil.ignore_patterns("__pycache__"))
    _, body = _split_skill(copied)
    links = _local_links(body)
    references = {
        path.relative_to(copied).as_posix() for path in (copied / "references").glob("*.md")
    }

    assert references <= links
    for target in links:
        resolved = (copied / target).resolve()
        assert resolved.is_relative_to(copied.resolve()), target
        assert resolved.is_file(), target


def test_reference_links_stay_inside_the_bundle() -> None:
    for reference in (BUNDLE_ROOT / "references").glob("*.md"):
        for target in _local_links(reference.read_text(encoding="utf-8")):
            resolved = (reference.parent / target).resolve()
            assert resolved.is_relative_to(BUNDLE_ROOT), f"{reference.name}: {target}"
