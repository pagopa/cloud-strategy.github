from pathlib import Path


REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)
MAKEFILE_PATH = REPO_ROOT / "Makefile"


def test_makefile_exposes_internal_gateway_idea_fast_check() -> None:
    text = MAKEFILE_PATH.read_text()

    assert "internal-gateway-idea-fast-check: scripts-bootstrap" in text
    assert ".github/skills/internal-gateway-idea/scripts/audit_workflow.py" in text
    assert "validate_internal_skills --skill internal-gateway-idea --strict" in text
    assert "tests/github/skills/internal-gateway-idea" in text
