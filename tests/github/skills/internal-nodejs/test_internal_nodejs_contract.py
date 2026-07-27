from pathlib import Path

import yaml


REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)
SKILLS_ROOT = REPO_ROOT / ".github/skills"


def _skill_text(name: str) -> str:
    return (SKILLS_ROOT / name / "SKILL.md").read_text(encoding="utf-8")


def _frontmatter(name: str) -> dict[str, object]:
    text = _skill_text(name)
    return yaml.safe_load(text.split("---", 2)[1])


def _interface(name: str) -> dict[str, str]:
    payload = yaml.safe_load(
        (SKILLS_ROOT / name / "agents/openai.yaml").read_text(encoding="utf-8")
    )
    return payload["interface"]


def test_descriptions_partition_baseline_and_project_work() -> None:
    baseline = str(_frontmatter("internal-nodejs")["description"])
    project = str(_frontmatter("internal-nodejs-project")["description"])

    assert baseline.startswith("Use when reviewing JavaScript or TypeScript")
    assert "package metadata, runtime configuration, dependencies" in baseline
    assert "/internal-nodejs-project" in baseline

    assert project.startswith(
        "Use when creating, modifying, or refactoring Node.js or TypeScript"
    )
    assert "application behavior and structure" in project
    assert "/internal-nodejs" in project


def test_each_skill_routes_its_near_miss_to_the_other_owner() -> None:
    baseline = _skill_text("internal-nodejs")
    project = _skill_text("internal-nodejs-project")

    assert "use `/internal-nodejs-project`" in baseline
    assert "use `/internal-nodejs`" in project
    assert "metadata-only" in project
    assert "application structure or behavior" in baseline


def test_runtime_metadata_names_the_same_ownership_boundary() -> None:
    baseline = _interface("internal-nodejs")
    project = _interface("internal-nodejs-project")

    assert baseline["display_name"] == "Internal Node.js"
    assert "review and metadata" in baseline["short_description"].lower()
    assert "$internal-nodejs" in baseline["default_prompt"]
    assert "review" in baseline["default_prompt"].lower()

    assert project["display_name"] == "Internal Node.js Project"
    assert "application structure" in project["short_description"].lower()
    assert "$internal-nodejs-project" in project["default_prompt"]
    assert "application behavior" in project["default_prompt"].lower()


def test_project_skill_does_not_duplicate_metadata_ownership() -> None:
    project = _skill_text("internal-nodejs-project")

    for baseline_owned_phrase in (
        "Keep `package.json` scripts, engines, and dependency intent explicit.",
        "Prefer strict `tsconfig.json` settings",
        "Use `node:test` and `node:assert/strict`",
    ):
        assert baseline_owned_phrase not in project


def _reference(name: str, filename: str) -> str:
    return (SKILLS_ROOT / name / "references" / filename).read_text(encoding="utf-8")


def test_review_catalog_is_defect_focused_instead_of_a_lint_catalog() -> None:
    review = _reference("internal-nodejs", "review-anti-patterns.md")

    for tool_owned_check in (
        "Missing trailing newline",
        "Inconsistent use of semicolons",
        "Import order not organized",
        "Unused imports or variables",
        "Missing purpose comment on exported modules",
    ):
        assert tool_owned_check not in review
    assert "Evidence threshold" in review
    assert "Missing unit tests for new exported functions" not in review


def test_project_references_contain_only_application_level_material() -> None:
    mistakes = _reference("internal-nodejs-project", "common-mistakes.md")
    examples = _reference("internal-nodejs-project", "examples.md")

    assert "Always `await` async calls" not in mistakes
    assert "Boundary service example" in examples
    assert "Boundary behavior test" in examples
    assert "package.json" not in examples
    assert "tsconfig.json" not in examples
    assert '"node": ">=22"' not in examples
