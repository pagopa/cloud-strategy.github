from __future__ import annotations

import json
from pathlib import Path

import pytest

BUNDLE = Path(__file__).resolve().parents[1]
SKILLS_ROOT = BUNDLE.parent
PACK = BUNDLE / "tests" / "evaluation" / "evals.json"
SKILL = BUNDLE.name
SIBLING = f"{SKILL}-lambda"
RETIRED_LANES = tuple(
    f"{SKILL}-{suffix}"
    for suffix in (
        "governance",
        "mcp-research",
        "operations",
        "organization-structure",
        "strategic",
    )
)


def _queries(pack_path: Path) -> list[dict]:
    return json.loads(pack_path.read_text(encoding="utf-8"))["triggers"]["queries"]


def _host_catalog() -> bool:
    return len(list(SKILLS_ROOT.glob("*/SKILL.md"))) > 1


def _sibling_pack() -> Path:
    pack = SKILLS_ROOT / SIBLING / "tests" / "evaluation" / "evals.json"
    if not pack.is_file():
        pytest.skip(f"{SIBLING} pack is not installed")
    return pack


def test_competing_owners_name_existing_skills() -> None:
    if not _host_catalog():
        pytest.skip("bundle is not installed inside a skill catalog")
    packs = [PACK, _sibling_pack()]
    missing = sorted(
        {
            query["competing_owner"]
            for pack in packs
            for query in _queries(pack)
            if "competing_owner" in query
            and not (SKILLS_ROOT / query["competing_owner"] / "SKILL.md").is_file()
        }
    )
    assert not missing, f"competing_owner values without a live skill: {missing}"


@pytest.mark.parametrize("direction", ["platform-to-lambda", "lambda-to-platform"])
def test_sibling_near_misses_are_reciprocal(direction: str) -> None:
    sibling = _sibling_pack()
    source, target, owner = (
        (PACK, sibling, SIBLING)
        if direction == "platform-to-lambda"
        else (sibling, PACK, SKILL)
    )
    target_positive = {q["query"] for q in _queries(target) if q["should_trigger"]}
    near_misses = [
        q["query"]
        for q in _queries(source)
        if not q["should_trigger"] and q.get("competing_owner") == owner
    ]
    assert near_misses, f"{source.parent.parent.parent.name} pack lacks a near-miss owned by {owner}"
    unmatched = sorted(set(near_misses) - target_positive)
    assert not unmatched, f"near-misses without a positive query in {owner}: {unmatched}"


def test_no_prompt_is_positive_in_both_packs() -> None:
    sibling = _sibling_pack()
    platform = {q["query"] for q in _queries(PACK) if q["should_trigger"]}
    lambda_ = {q["query"] for q in _queries(sibling) if q["should_trigger"]}
    assert not platform & lambda_, f"dual-positive prompts: {sorted(platform & lambda_)}"


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
