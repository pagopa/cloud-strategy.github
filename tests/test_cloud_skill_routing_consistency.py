"""Cross-bundle routing consistency for the cloud platform skills.

Sibling eval packs must agree on who owns each boundary prompt.
"""

import json
from pathlib import Path

import pytest

REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)
SKILLS_ROOT = REPO_ROOT / ".github" / "skills"
OWNER_CHECKED_PACKS = ("internal-aws", "internal-aws-lambda", "internal-gcp")
RECIPROCAL_PAIRS = (("internal-aws", "internal-aws-lambda"),)
MIRRORED_PAIRS = (
    ("internal-gcp", "internal-cloud-policy"),
    ("internal-gcp", "internal-terraform"),
)


def _queries(skill: str) -> list[dict]:
    pack = SKILLS_ROOT / skill / "tests" / "evaluation" / "evals.json"
    return json.loads(pack.read_text(encoding="utf-8"))["triggers"]["queries"]


def _positives(skill: str) -> set[str]:
    return {q["query"] for q in _queries(skill) if q["should_trigger"]}


def _near_misses_owned_by(skill: str, owner: str) -> list[str]:
    return [
        q["query"]
        for q in _queries(skill)
        if not q["should_trigger"] and q.get("competing_owner") == owner
    ]


@pytest.mark.parametrize("skill", OWNER_CHECKED_PACKS)
def test_competing_owners_name_existing_skills(skill: str) -> None:
    missing = sorted(
        {
            q["competing_owner"]
            for q in _queries(skill)
            if "competing_owner" in q
            and not (SKILLS_ROOT / q["competing_owner"] / "SKILL.md").is_file()
        }
    )
    assert not missing, (
        f"{skill} competing_owner values without a live skill: {missing}"
    )


@pytest.mark.parametrize(
    ("source", "target"),
    [pair for a, b in RECIPROCAL_PAIRS for pair in ((a, b), (b, a))],
)
def test_sibling_near_misses_are_reciprocal(source: str, target: str) -> None:
    near_misses = _near_misses_owned_by(source, target)

    assert near_misses, f"{source} pack lacks a near-miss owned by {target}"
    unmatched = sorted(set(near_misses) - _positives(target))
    assert not unmatched, (
        f"near-misses without a positive query in {target}: {unmatched}"
    )


@pytest.mark.parametrize(("first", "second"), RECIPROCAL_PAIRS)
def test_no_prompt_is_positive_in_both_packs(first: str, second: str) -> None:
    shared = _positives(first) & _positives(second)

    assert not shared, f"dual-positive prompts: {sorted(shared)}"


@pytest.mark.parametrize(("skill", "owner"), MIRRORED_PAIRS)
def test_boundary_pairs_are_mirrored(skill: str, owner: str) -> None:
    assert _near_misses_owned_by(skill, owner), (
        f"{skill} lacks a near-miss owned by {owner}"
    )
    assert _near_misses_owned_by(owner, skill), (
        f"{owner} lacks a near-miss owned by {skill}"
    )
