from __future__ import annotations

import json
import re
import shutil
from pathlib import Path
from typing import Any

REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").is_file() and (parent / ".github").is_dir()
)
FIXTURE_PATH = Path(__file__).parent / "fixtures/routing-cases.json"
REFERENCE_PATTERN = re.compile(
    r"(?:\.github/skills/[^`\s)]+/)?references/[A-Za-z0-9_.-]+\.md"
)


def _load_fixture() -> dict[str, Any]:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def _reference_targets(skill_text: str) -> set[str]:
    return set(REFERENCE_PATTERN.findall(skill_text))


def test_wrapper_references_resolve_from_a_standalone_materialized_bundle(
    tmp_path: Path,
) -> None:
    source_bundle = REPO_ROOT / ".github/skills/internal-terraform"
    copied_bundle = tmp_path / "standalone" / "internal-terraform"
    shutil.copytree(source_bundle, copied_bundle)

    skill_text = (copied_bundle / "SKILL.md").read_text(encoding="utf-8")
    references = _reference_targets(skill_text)
    required_references = {
        "references/existing-infrastructure-adoption.md",
        "references/operational-validation.md",
    }

    assert required_references <= references
    for reference in references:
        assert reference.startswith("references/"), (
            "local references must be bundle-relative, not source-repository paths: "
            f"{reference}"
        )
        assert (copied_bundle / reference).is_file(), reference


def test_fixture_references_are_present_in_the_owning_bundle() -> None:
    fixture = _load_fixture()
    source_bundle = REPO_ROOT / ".github/skills/internal-terraform"
    expected_references = {
        reference
        for scenario in fixture["scenarios"]
        for reference in scenario["loaded_local_references"]
        if reference.startswith("references/")
    }

    for reference in expected_references:
        if reference in {
            "references/existing-infrastructure-adoption.md",
            "references/operational-validation.md",
        }:
            assert (source_bundle / reference).is_file(), reference
