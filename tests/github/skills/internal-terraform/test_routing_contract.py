from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import pytest
import yaml

REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").is_file() and (parent / ".github").is_dir()
)
FIXTURE_PATH = Path(__file__).parent / "fixtures/routing-cases.json"
SKILL_PATHS = {
    "internal-terraform": REPO_ROOT / ".github/skills/internal-terraform",
    "internal-tf": REPO_ROOT / ".github/skills/internal-tf",
}


def _load_fixture() -> dict[str, Any]:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def _load_skill_contract(skill_name: str) -> tuple[dict[str, Any], dict[str, Any], str]:
    skill_path = SKILL_PATHS[skill_name]
    skill_text = (skill_path / "SKILL.md").read_text(encoding="utf-8")
    frontmatter_match = re.match(r"\A---\n(.*?)\n---\n", skill_text, re.DOTALL)
    assert frontmatter_match, f"{skill_name} must have YAML frontmatter"
    frontmatter = yaml.safe_load(frontmatter_match.group(1))
    metadata = yaml.safe_load((skill_path / "agents/openai.yaml").read_text(encoding="utf-8"))
    return frontmatter, metadata["interface"], skill_text


def test_routing_fixture_covers_the_required_scenario_matrix() -> None:
    fixture = _load_fixture()
    scenarios = fixture["scenarios"]
    expected_ids = {
        "hcl-only",
        "tfvars-json-only",
        "mixed-adoption",
        "native-test",
        "state-or-drift",
        "module-architecture",
        "ci-or-provider-operation",
        "ambiguous-adoption-identity",
    }

    assert {scenario["id"] for scenario in scenarios} == expected_ids
    assert {scenario["primary_owner"] for scenario in scenarios} == {
        "internal-tf",
        "internal-terraform",
    }
    assert all("fail_closed_on_unknown" in scenario for scenario in scenarios)

    for scenario in scenarios:
        assert scenario["primary_owner"] == (
            "internal-tf"
            if scenario["id"] in {"hcl-only", "tfvars-json-only"}
            else "internal-terraform"
        )
        if scenario["id"] == "mixed-adoption":
            assert scenario["delegated_owner"] == "internal-tf"
        else:
            assert scenario["delegated_owner"] is None


def test_public_metadata_preserves_the_two_owner_boundary() -> None:
    fixture = _load_fixture()
    language_frontmatter, language_interface, _ = _load_skill_contract("internal-tf")
    wrapper_frontmatter, wrapper_interface, _ = _load_skill_contract("internal-terraform")

    language_public_text = " ".join(
        [
            language_frontmatter["description"],
            language_interface["short_description"],
            language_interface["default_prompt"],
        ]
    ).casefold()
    wrapper_public_text = " ".join(
        [
            wrapper_frontmatter["description"],
            wrapper_interface["short_description"],
            wrapper_interface["default_prompt"],
        ]
    ).casefold()

    for term in fixture["metadata_contract"]["internal-tf"]["required_terms"]:
        assert term.casefold() in language_public_text
    for marker in fixture["metadata_contract"]["internal-tf"]["forbidden_primary_markers"]:
        assert marker.casefold() not in language_interface["default_prompt"].casefold()

    for term in fixture["metadata_contract"]["internal-terraform"]["required_terms"]:
        assert term.casefold() in wrapper_public_text
    assert wrapper_frontmatter["name"] == "internal-terraform"
    assert language_frontmatter["name"] == "internal-tf"


def test_mixed_and_ambiguous_scenarios_keep_one_fail_safe_primary_owner() -> None:
    fixture = _load_fixture()
    scenarios = {
        scenario["id"]: scenario for scenario in fixture["scenarios"]
    }

    for scenario_id in (
        "mixed-adoption",
        "native-test",
        "state-or-drift",
        "module-architecture",
        "ci-or-provider-operation",
        "ambiguous-adoption-identity",
    ):
        scenario = scenarios[scenario_id]
        assert scenario["primary_owner"] == "internal-terraform"
        assert scenario["fail_closed_on_unknown"] is True

    assert scenarios["mixed-adoption"]["delegated_owner"] == "internal-tf"
    assert scenarios["ambiguous-adoption-identity"]["delegated_owner"] is None


def test_language_structure_reference_excludes_operational_ownership() -> None:
    fixture = _load_fixture()
    reference_path = REPO_ROOT / ".github/skills/internal-tf" / fixture[
        "language_boundary"
    ]["reference"]
    reference_text = reference_path.read_text(encoding="utf-8").casefold()

    for forbidden_term in fixture["language_boundary"]["forbidden_terms"]:
        assert forbidden_term.casefold() not in reference_text


@pytest.mark.parametrize(
    "scenario_id",
    ["hcl-only", "tfvars-json-only"],
)
def test_language_only_scenarios_have_no_delegated_owner(
    scenario_id: str,
) -> None:
    scenarios = {
        scenario["id"]: scenario for scenario in _load_fixture()["scenarios"]
    }

    assert scenarios[scenario_id]["primary_owner"] == "internal-tf"
    assert scenarios[scenario_id]["delegated_owner"] is None
    assert scenarios[scenario_id]["fail_closed_on_unknown"] is False
