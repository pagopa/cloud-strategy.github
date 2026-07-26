from pathlib import Path

REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)
RETIRED_NAME = "internal-review-ai-resources"


def test_obsolete_review_entrypoints_are_removed() -> None:
    assert not (REPO_ROOT / f".github/skills/{RETIRED_NAME}").exists()
    assert not (REPO_ROOT / f".github/prompts/{RETIRED_NAME}.prompt.md").exists()


def test_catalog_contract_has_no_retired_identity() -> None:
    paths = (
        REPO_ROOT / ".github/INVENTORY.md",
        REPO_ROOT / ".github/scripts/lib/token_risks.py",
    )
    for path in paths:
        assert RETIRED_NAME not in path.read_text(encoding="utf-8")
