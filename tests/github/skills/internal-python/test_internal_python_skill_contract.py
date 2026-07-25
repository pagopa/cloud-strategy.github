from pathlib import Path

import yaml


REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)
SKILLS_ROOT = REPO_ROOT / ".github/skills"
PYTHON = SKILLS_ROOT / "internal-python"
PROJECT = SKILLS_ROOT / "internal-python-project"
SCRIPT = SKILLS_ROOT / "internal-python-script"


def _frontmatter_description(bundle: Path) -> str:
    text = (bundle / "SKILL.md").read_text(encoding="utf-8")
    return str(yaml.safe_load(text.split("---", 2)[1])["description"])


def _runtime(bundle: Path) -> dict[str, str]:
    payload = yaml.safe_load(
        (bundle / "agents/openai.yaml").read_text(encoding="utf-8")
    )
    return payload["interface"]


def test_python_descriptions_express_distinct_primary_contracts() -> None:
    generic = _frontmatter_description(PYTHON).lower()
    project = _frontmatter_description(PROJECT).lower()
    script = _frontmatter_description(SCRIPT).lower()

    assert "primary contract is still unclear" in generic
    assert "importable" in project
    assert "directly executed" in script
    assert len({generic, project, script}) == 3


def test_python_skills_route_near_miss_cases_to_the_right_owner() -> None:
    generic = (PYTHON / "SKILL.md").read_text(encoding="utf-8")
    project = (PROJECT / "SKILL.md").read_text(encoding="utf-8")
    script = (SCRIPT / "SKILL.md").read_text(encoding="utf-8")

    assert "operator-facing" in generic and "internal-python-script" in generic
    assert "importable" in generic and "internal-python-project" in generic
    assert "operator-facing" in project and "internal-python-script" in project
    assert "imported behavior" in script and "internal-python-project" in script


def test_python_runtime_metadata_names_real_owners() -> None:
    expected = {
        PYTHON: ("Python baseline and ownership routing", "$internal-python"),
        PROJECT: (
            "Importable Python application guidance",
            "$internal-python-project",
        ),
        SCRIPT: ("Direct-execution Python tooling", "$internal-python-script"),
    }

    for bundle, (short_description, invocation) in expected.items():
        runtime = _runtime(bundle)
        assert runtime["short_description"] == short_description
        assert invocation in runtime["default_prompt"]
        assert "Help with Internal" not in runtime["short_description"]


def test_python_script_uses_one_toolkit_helper_convention() -> None:
    skill = (SCRIPT / "SKILL.md").read_text(encoding="utf-8")
    layout = (SCRIPT / "references/layout-and-templates.md").read_text(
        encoding="utf-8"
    )

    assert "`lib/`" in skill
    assert "`utils/`" not in skill
    assert "│   └── lib/" in layout
    assert skill.count("references/reporting.md") == 1


def test_dependency_example_matches_its_decision() -> None:
    layout = (SCRIPT / "references/layout-and-templates.md").read_text(
        encoding="utf-8"
    )

    assert "Final choice: PyYAML" in layout
    assert "PyYAML==" in layout
    assert "requests==" not in layout


def test_reporter_skeleton_implements_the_advertised_summary_method() -> None:
    reporting = (SCRIPT / "references/reporting.md").read_text(encoding="utf-8")

    assert "- `summary(status, counts, produced_files, diagnostics)`" in reporting
    assert "def summary(" in reporting
    assert "Produced files" in reporting
    assert "Diagnostics" in reporting


def test_python_review_catalog_defers_formatter_owned_nits() -> None:
    review = (PYTHON / "references/review-anti-patterns.md").read_text(
        encoding="utf-8"
    )

    assert "## Nit" not in review
    assert "configured formatter and linter" in review
