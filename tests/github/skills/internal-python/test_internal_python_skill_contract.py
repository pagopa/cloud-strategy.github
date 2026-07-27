import re
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

    assert "ownership is unclear" in generic
    assert "cross-cutting" in generic
    assert "importable" in project
    assert "directly executed" in script
    assert len({generic, project, script}) == 3


def test_python_skills_do_not_call_or_reference_other_skills() -> None:
    all_skill_names = {
        path.name
        for path in SKILLS_ROOT.iterdir()
        if path.is_dir() and (path / "SKILL.md").exists()
    }

    for bundle in (PYTHON, PROJECT, SCRIPT):
        skill = (bundle / "SKILL.md").read_text(encoding="utf-8")
        prompt = _runtime(bundle)["default_prompt"]

        assert "## Referenced skills" not in skill
        for other_name in all_skill_names - {bundle.name}:
            invocation = re.compile(
                rf"(?<![\w-])(?:/|\$|`){re.escape(other_name)}(?![\w-])"
            )
            assert invocation.search(skill) is None
            assert invocation.search(prompt) is None


def test_python_skills_define_balanced_positive_and_negative_boundaries() -> None:
    generic = (PYTHON / "SKILL.md").read_text(encoding="utf-8").lower()
    project = (PROJECT / "SKILL.md").read_text(encoding="utf-8").lower()
    script = (SCRIPT / "SKILL.md").read_text(encoding="utf-8").lower()

    assert "cross-cutting" in generic and "ownership is unclear" in generic
    assert "do not use" in generic
    assert "reusable imported code" in generic
    assert "direct-execution tool" in generic

    assert "reusable imported behavior" in project
    assert "do not use" in project
    assert "primary contract is direct execution" in project

    assert "primary contract is direct execution" in script
    assert "do not use" in script
    assert "primary contract is reusable imported behavior" in script


def test_python_baseline_stays_cross_cutting_and_template_free() -> None:
    skill = (PYTHON / "SKILL.md").read_text(encoding="utf-8").lower()

    for marker in (
        "declared runtime",
        "declared dependency manager",
        "focused `pytest`",
        "machine-readable",
    ):
        assert marker in skill

    assert "minimal entry point" not in skill
    assert "executivereporter" not in skill
    assert "domain/service/adapter" not in skill


def test_project_skill_follows_repository_conventions_before_optional_patterns() -> (
    None
):
    skill = (PROJECT / "SKILL.md").read_text(encoding="utf-8").lower()

    assert "existing" in skill and "test naming" in skill
    assert "existing framework" in skill
    assert "when separation improves" in skill
    assert "bdd-like names:" not in skill
    assert (
        "god classes with 10+ methods"
        not in (PROJECT / "references/common-mistakes.md")
        .read_text(encoding="utf-8")
        .lower()
    )


def test_project_reporting_keeps_human_rendering_at_the_cli_boundary() -> None:
    skill = (PROJECT / "SKILL.md").read_text(encoding="utf-8").lower()

    assert "human-facing" in skill and "cli adapter" in skill
    assert "plain data" in skill


def test_script_optional_complexity_is_contract_driven() -> None:
    skill = (SCRIPT / "SKILL.md").read_text(encoding="utf-8").lower()

    assert "follow the repository's existing layout" in skill
    assert "only when" in skill and "`rich`" in skill
    assert "only when" in skill and "`run.sh`" in skill
    assert "configuration section near the end" not in skill
    assert "rich` as the preferred" not in skill


def test_script_references_do_not_silently_provision_on_every_run() -> None:
    layout = (SCRIPT / "references/layout-and-templates.md").read_text(encoding="utf-8")

    assert '"$VENV_DIR/bin/pip" install' not in layout
    assert "repository-declared environment" in layout


OWNER_MARKERS = {
    PYTHON: ("cross-cutting", "ownership"),
    PROJECT: ("import", "package"),
    SCRIPT: ("direct", "script"),
}


def test_frontmatter_body_and_runtime_share_the_owner_vocabulary() -> None:
    for bundle, markers in OWNER_MARKERS.items():
        description = _frontmatter_description(bundle).lower()
        body = (bundle / "SKILL.md").read_text(encoding="utf-8").lower()
        prompt = _runtime(bundle)["default_prompt"].lower()

        for marker in markers:
            assert marker in description
            assert marker in body
            assert marker in prompt


def test_python_runtime_metadata_names_real_owners() -> None:
    expected = {
        PYTHON: ("Cross-cutting Python baseline", "$internal-python"),
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
    layout = (SCRIPT / "references/layout-and-templates.md").read_text(encoding="utf-8")

    assert "`lib/`" in skill
    assert "`utils/`" not in skill
    assert "│   └── lib/" in layout
    assert skill.count("references/reporting.md") == 1


def test_dependency_policy_preserves_the_declared_toolchain() -> None:
    instruction = (
        REPO_ROOT / ".github/instructions/internal-python.instructions.md"
    ).read_text(encoding="utf-8")
    generic = (PYTHON / "SKILL.md").read_text(encoding="utf-8")
    project = (PROJECT / "SKILL.md").read_text(encoding="utf-8")
    script = (SCRIPT / "SKILL.md").read_text(encoding="utf-8")

    for text in (instruction, generic, project, script):
        assert "declared dependency manager" in text
        assert "exact pins and hashes" in text


def test_dependency_template_does_not_publish_partial_real_hashes() -> None:
    layout = (SCRIPT / "references/layout-and-templates.md").read_text(encoding="utf-8")

    assert "00c4bdeba853cc34e7dd471f16b4114f" not in layout
    assert "0150219816b6a1fa26fb4699fb7daa9c" not in layout
    assert "requirements.in" in layout
    assert "pip-compile --generate-hashes" in layout
    assert "illustrative input" in layout.lower()


def test_script_dependency_policy_has_one_authoritative_section() -> None:
    skill = (SCRIPT / "SKILL.md").read_text(encoding="utf-8")

    assert skill.count("## Dependency policy") == 1
    assert skill.count("pip-compile --generate-hashes") == 1


def test_reporter_skeleton_implements_the_advertised_summary_method() -> None:
    reporting = (SCRIPT / "references/reporting.md").read_text(encoding="utf-8")

    assert "- `summary(status, counts, produced_files, diagnostics)`" in reporting
    assert "def summary(" in reporting
    assert "Produced files" in reporting
    assert "Diagnostics" in reporting


def test_reporter_skeleton_redacts_sensitive_options() -> None:
    reporting = (SCRIPT / "references/reporting.md").read_text(encoding="utf-8")

    assert "SENSITIVE_OPTION_MARKERS" in reporting
    assert "def _render_option(" in reporting
    assert 'return "[REDACTED]"' in reporting
    assert "_render_option(str(key), value)" in reporting
    assert (
        "escape(str(value))"
        not in reporting.split("if options:", 1)[1].split("self.console.print", 1)[0]
    )


def test_python_review_catalog_defers_formatter_owned_nits() -> None:
    review = (PYTHON / "references/review-anti-patterns.md").read_text(encoding="utf-8")

    assert "## Nit" not in review
    assert "configured formatter and linter" in review


def test_exception_guidance_respects_python_exception_hierarchy() -> None:
    project_mistakes = (PROJECT / "references/common-mistakes.md").read_text(
        encoding="utf-8"
    )
    script_mistakes = (SCRIPT / "references/common-mistakes.md").read_text(
        encoding="utf-8"
    )

    for text in (project_mistakes, script_mistakes):
        assert "`except Exception` catches `KeyboardInterrupt`" not in text
        assert "`except Exception` catches `SystemExit`" not in text
        assert "bare `except:`" in text
        assert "`except Exception`" in text


def test_review_catalog_requires_evidence_for_python_findings() -> None:
    review = (PYTHON / "references/review-anti-patterns.md").read_text(encoding="utf-8")

    unsupported_rules = (
        "Function body longer than 40 lines",
        "Cyclomatic complexity > 10",
        "Missing docstring on public functions/classes",
        "Mixed `str.format()` and f-strings",
        "Missing `__all__` in modules with public API",
        "Nested functions deeper than 2 levels",
    )
    assert all(rule not in review for rule in unsupported_rules)
    assert "Missing focused tests for new or changed behavior" in review


def test_project_test_example_imports_its_subject() -> None:
    examples = (PROJECT / "references/examples.md").read_text(encoding="utf-8")

    assert "account_status.py" in examples
    assert "from account_status import AccountId" in examples
