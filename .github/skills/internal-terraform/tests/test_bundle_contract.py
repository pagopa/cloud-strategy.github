from __future__ import annotations

import json
import re
import shutil
from pathlib import Path
from typing import Any

import yaml

BUNDLE_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_PATH = BUNDLE_ROOT / "tests/fixtures/routing-cases.json"
FRONTMATTER_KEYS = {"name", "description", "metadata", "license", "compatibility"}
LINK_PATTERN = re.compile(r"\]\(([^)\s#]+)(?:#[^)]*)?\)")
OWNERS = {"internal-tf", "internal-terraform"}


def _split_skill(bundle: Path) -> tuple[dict[str, Any], str]:
    text = (bundle / "SKILL.md").read_text(encoding="utf-8")
    _, frontmatter, body = text.split("---\n", 2)
    return yaml.safe_load(frontmatter), body


def _local_links(bundle: Path) -> set[str]:
    _, body = _split_skill(bundle)
    return {target for target in LINK_PATTERN.findall(body) if "://" not in target}


def _reference_files(bundle: Path) -> set[str]:
    return {
        path.relative_to(bundle).as_posix()
        for path in (bundle / "references").glob("*.md")
    }


def _scenarios() -> list[dict[str, Any]]:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))["scenarios"]


def test_frontmatter_and_metadata_are_portable() -> None:
    frontmatter, _ = _split_skill(BUNDLE_ROOT)
    metadata = yaml.safe_load((BUNDLE_ROOT / "agents/openai.yaml").read_text(encoding="utf-8"))

    assert set(frontmatter) <= FRONTMATTER_KEYS
    assert frontmatter["name"] == BUNDLE_ROOT.name
    assert {"display_name", "short_description", "default_prompt"} <= set(metadata["interface"])


def test_every_reference_is_linked_and_resolves_from_a_standalone_copy(tmp_path: Path) -> None:
    copied = tmp_path / BUNDLE_ROOT.name
    shutil.copytree(BUNDLE_ROOT, copied, ignore=shutil.ignore_patterns("__pycache__"))
    links = _local_links(copied)

    assert _reference_files(copied) <= links
    for target in links:
        resolved = (copied / target).resolve()
        assert resolved.is_relative_to(copied.resolve()), target
        assert resolved.is_file(), target


def test_routing_fixture_uses_only_wrapper_owned_references() -> None:
    scenarios = _scenarios()
    wrapper_references = _reference_files(BUNDLE_ROOT)
    used: set[str] = set()

    assert len({scenario["id"] for scenario in scenarios}) == len(scenarios)
    for scenario in scenarios:
        loaded = set(scenario["loaded_local_references"])
        forbidden = set(scenario["forbidden_local_references"])
        assert loaded | forbidden <= wrapper_references, scenario["id"]
        assert not loaded & forbidden, scenario["id"]
        assert scenario["primary_owner"] in OWNERS, scenario["id"]
        used |= loaded
    assert used == wrapper_references


def test_language_only_scenarios_load_no_wrapper_reference() -> None:
    for scenario in _scenarios():
        if scenario["primary_owner"] == "internal-tf":
            assert scenario["loaded_local_references"] == [], scenario["id"]
            assert scenario["delegated_owner"] is None, scenario["id"]
            assert scenario["execution_owner"] is None, scenario["id"]
            assert scenario["fail_closed_on_unknown"] is False, scenario["id"]


def test_operational_and_import_scenarios_keep_the_wrapper_primary() -> None:
    for scenario in _scenarios():
        if scenario["primary_owner"] == "internal-terraform":
            assert scenario["fail_closed_on_unknown"] is True, scenario["id"]
        if scenario["execution_owner"] is not None:
            assert scenario["primary_owner"] == "internal-terraform", scenario["id"]
            assert scenario["execution_owner"] == "internal-terraform-import", scenario["id"]
