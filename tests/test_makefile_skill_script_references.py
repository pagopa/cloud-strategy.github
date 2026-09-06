import re
from pathlib import Path

REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)


def test_makefile_does_not_reference_skill_runtime_scripts() -> None:
    makefile = (REPO_ROOT / "Makefile").read_text()

    forbidden = (
        "critical-validate",
        "internal-gateway-idea-fast-check",
        "retained-plan-check",
        "audit_internal_gateway_idea",
        "plan_authoring",
        "plan_execution",
    )
    assert not any(marker in makefile for marker in forbidden)
    assert not re.search(r"\.github/skills/[^\s]+/scripts", makefile)


def test_github_catalog_validation_uses_the_repository_script_runner() -> None:
    makefile = (REPO_ROOT / "Makefile").read_text(encoding="utf-8")

    assert "$(TOOLS_RUNNER) validate-github-catalog" in makefile
    assert "./validate-github-catalog.sh" not in makefile
