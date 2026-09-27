"""Cross-bundle routing consistency for the GitHub skill family.

The family has no router, so the three eval packs must agree on ownership.
"""

import json
import re
from pathlib import Path

REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)
SKILLS_ROOT = REPO_ROOT / ".github" / "skills"
FAMILY = ("internal-github-actions", "internal-github-pr", "internal-github-platform")
RETIRED = re.compile(r"internal-github(?:-governance|-operations|-strategic)?(?![-\w])")
ACTIVE_ROOT_FILES = (
    "AGENTS.md",
    "AGENTS.local.md",
    "INTERNAL_CONTRACT.md",
    "README.md",
    "CONTRIBUTING.md",
)
EXCLUDED_PARTS = {"runs", "__pycache__", ".git", "graphify-out", "tmp"}
TEXT_SUFFIXES = {".md", ".json", ".yaml", ".yml", ".py", ".txt", ".sh"}


def _pack(skill: str) -> dict:
    return json.loads(
        (SKILLS_ROOT / skill / "tests" / "evaluation" / "evals.json").read_text(
            encoding="utf-8"
        )
    )


def _queries(skill: str) -> list[dict]:
    return _pack(skill)["triggers"]["queries"]


def test_family_bundles_exist_with_packs() -> None:
    for skill in FAMILY:
        assert (SKILLS_ROOT / skill / "SKILL.md").is_file(), skill
        assert _pack(skill)["skill"] == skill


def test_sibling_near_misses_are_positive_in_the_sibling_pack() -> None:
    positives = {
        skill: {q["query"] for q in _queries(skill) if q["should_trigger"]}
        for skill in FAMILY
    }
    missing = [
        f"{skill}:{q['id']} -> {q['competing_owner']}"
        for skill in FAMILY
        for q in _queries(skill)
        if not q["should_trigger"]
        and q.get("competing_owner") in FAMILY
        and q["query"] not in positives[q["competing_owner"]]
    ]
    assert not missing, "sibling near-miss without identical positive: " + ", ".join(
        missing
    )


def test_no_prompt_is_positive_in_two_siblings() -> None:
    seen: dict[str, str] = {}
    duplicates = []
    for skill in FAMILY:
        for q in _queries(skill):
            if q["should_trigger"]:
                if q["query"] in seen:
                    duplicates.append(f"{seen[q['query']]} and {skill}: {q['query']}")
                seen[q["query"]] = skill
    assert not duplicates, "; ".join(duplicates)


def test_competing_owners_resolve_to_skill_directories() -> None:
    unresolved = sorted(
        {
            q["competing_owner"]
            for skill in FAMILY
            for q in _queries(skill)
            if q.get("competing_owner")
            and not (SKILLS_ROOT / q["competing_owner"]).is_dir()
        }
        - {
            "summarize-github-issue-pr-notification"
        }  # provided by the VS Code GitHub extension
    )
    assert not unresolved, ", ".join(unresolved)


def _active_files():
    for name in ACTIVE_ROOT_FILES:
        path = REPO_ROOT / name
        if path.is_file():
            yield path
    for base in (REPO_ROOT / ".github", REPO_ROOT / "docs"):
        for path in base.rglob("*"):
            rel = path.relative_to(REPO_ROOT)
            if (
                path.is_file()
                and path.suffix in TEXT_SUFFIXES
                and not EXCLUDED_PARTS.intersection(rel.parts)
                and path.name != "CHANGELOG.md"
            ):
                yield path


def test_active_surfaces_do_not_name_retired_skills() -> None:
    hits = []
    for path in _active_files():
        for number, line in enumerate(
            path.read_text(encoding="utf-8", errors="ignore").splitlines(), 1
        ):
            if RETIRED.search(line):
                hits.append(f"{path.relative_to(REPO_ROOT)}:{number}")
    assert not hits, "retired GitHub skill names remain: " + ", ".join(hits[:40])
