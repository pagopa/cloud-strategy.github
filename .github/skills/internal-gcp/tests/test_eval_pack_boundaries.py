from __future__ import annotations

import json
from pathlib import Path

import pytest

BUNDLE = Path(__file__).resolve().parents[1]
SKILLS_ROOT = BUNDLE.parent
PACK = BUNDLE / "tests" / "evaluation" / "evals.json"
SKILL = BUNDLE.name
RETIRED_LANES = tuple(
    f"{SKILL}-{suffix}"
    for suffix in ("governance", "operations", "organization-structure", "strategic")
)
MIRRORED_OWNERS = ("internal-cloud-policy", "internal-terraform")


def _queries(pack_path: Path) -> list[dict]:
    return json.loads(pack_path.read_text(encoding="utf-8"))["triggers"]["queries"]


def _negative_owners(pack_path: Path) -> set[str]:
    return {
        query["competing_owner"]
        for query in _queries(pack_path)
        if not query["should_trigger"] and "competing_owner" in query
    }


def _host_catalog() -> bool:
    return len(list(SKILLS_ROOT.glob("*/SKILL.md"))) > 1


def test_competing_owners_name_existing_skills() -> None:
    if not _host_catalog():
        pytest.skip("bundle is not installed inside a skill catalog")
    missing = sorted(
        owner
        for owner in _negative_owners(PACK)
        if not (SKILLS_ROOT / owner / "SKILL.md").is_file()
    )
    assert not missing, f"competing_owner values without a live skill: {missing}"


@pytest.mark.parametrize("owner", MIRRORED_OWNERS)
def test_boundary_pairs_are_mirrored(owner: str) -> None:
    sibling_pack = SKILLS_ROOT / owner / "tests" / "evaluation" / "evals.json"
    if not sibling_pack.is_file():
        pytest.skip(f"{owner} pack is not installed")
    assert owner in _negative_owners(PACK), f"{SKILL} pack lacks a near-miss owned by {owner}"
    assert SKILL in _negative_owners(sibling_pack), f"{owner} pack lacks a near-miss owned by {SKILL}"


def test_bundle_does_not_name_retired_lanes() -> None:
    offenders = sorted(
        path.relative_to(BUNDLE).as_posix()
        for path in BUNDLE.rglob("*")
        if path.is_file()
        and path.suffix in {".md", ".json", ".yaml"}
        and any(lane in path.read_text(encoding="utf-8") for lane in RETIRED_LANES)
    )
    assert not offenders, f"files naming retired lanes: {offenders}"


def test_retired_lane_bundles_are_removed() -> None:
    if not _host_catalog():
        pytest.skip("bundle is not installed inside a skill catalog")
    present = sorted(lane for lane in RETIRED_LANES if (SKILLS_ROOT / lane).exists())
    assert not present, f"retired lane bundles still present: {present}"
