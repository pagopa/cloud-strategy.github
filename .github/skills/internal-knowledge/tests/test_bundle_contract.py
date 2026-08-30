"""Structural contract tests for the installed knowledge skill bundle."""

from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml


BUNDLE_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_ROOT = BUNDLE_ROOT / "scripts"
if str(SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_ROOT))


def test_bundle_contains_required_assets() -> None:
    required_paths = (
        "SKILL.md",
        "references/adr-maintenance.md",
        "references/architecture-maintenance.md",
        "references/madr-minimal.md",
        "references/documentation-setup.md",
        "references/ci-assets.md",
        "references/inventory-and-check.md",
        "references/modes-audit-impact.md",
        "references/modes-update.md",
        "references/readme-maintenance.md",
        "requirements.in",
        "requirements.txt",
        "scripts/bootstrap.py",
        "scripts/knowledge.py",
        "tests/test_bootstrap.py",
        "tests/test_check.py",
        "tests/test_config.py",
        "tests/test_inventory.py",
        "tests/test_modes.py",
        "evals/evaluation_scenarios.md",
    )

    missing = [path for path in required_paths if not (BUNDLE_ROOT / path).is_file()]
    assert not missing, f"missing required bundle assets: {missing}"


def detect_forbidden_capabilities(bundle_root: Path) -> list[str]:
    findings: list[str] = []
    relative_dirs = {
        path.relative_to(bundle_root).as_posix()
        for path in bundle_root.rglob("*")
        if path.is_dir()
    }
    if any(path == "templates" or path.startswith("templates/") for path in relative_dirs):
        findings.append("template-framework")
    for bundle_file in bundle_root.rglob("*"):
        if not bundle_file.is_file() or "__pycache__" in bundle_file.parts:
            continue
        relative_parts = bundle_file.relative_to(bundle_root).parts
        if relative_parts and relative_parts[0] in {"tests", "evals"}:
            continue
        suffix = bundle_file.suffix.lower()
        name = bundle_file.name.lower()
        if suffix in {".tmpl", ".j2"} or name.endswith(".template.md"):
            findings.append("template-framework")
        text = bundle_file.read_text(encoding="utf-8")
        if re.search(r"(?i)readme template framework|architecture template framework", text):
            findings.append("template-framework")
        if re.search(r"(?i)\b(selfcheck|self-check)\b", text):
            findings.append("self-check-mode")
        if re.search(r"(?i)duplicate setup contract", text):
            findings.append("duplicate-setup-contract")
    return sorted(set(findings))


def test_bundle_rejects_forbidden_authoring_capabilities() -> None:
    findings = detect_forbidden_capabilities(BUNDLE_ROOT)
    assert findings == [], f"forbidden capabilities remain: {findings}"


def test_capability_detector_rejects_renamed_template_framework(tmp_path: Path) -> None:
    bundle = tmp_path / "renamed-bundle"
    templates = bundle / "guide-kits"
    templates.mkdir(parents=True)
    (templates / "component.template.md").write_text(
        "# README template framework\nFill this scaffold.\n",
        encoding="utf-8",
    )

    assert "template-framework" in detect_forbidden_capabilities(bundle)


def test_capability_detector_rejects_renamed_self_check_mode(tmp_path: Path) -> None:
    bundle = tmp_path / "renamed-bundle"
    scripts = bundle / "scripts"
    scripts.mkdir(parents=True)
    (scripts / "health.py").write_text(
        "def run_bundle_health():\n    print('self-check complete')\n",
        encoding="utf-8",
    )

    assert "self-check-mode" in detect_forbidden_capabilities(bundle)


def test_skill_is_the_only_readme_and_architecture_authoring_source() -> None:
    repository_root = BUNDLE_ROOT.parents[2]
    retired_prompts = (
        repository_root / ".github" / "prompts" / "README-file-creator.prompt.md",
        repository_root / ".github" / "prompts" / "internal-architecture-md-creator.prompt.md",
    )

    assert not [path for path in retired_prompts if path.exists()]

    skill_text = (BUNDLE_ROOT / "SKILL.md").read_text(encoding="utf-8")
    assert "/mattpocock-domain-modeling" in skill_text


def test_skill_metadata_and_references_are_coherent() -> None:
    skill_text = (BUNDLE_ROOT / "SKILL.md").read_text(encoding="utf-8")
    frontmatter_text = skill_text.split("---", 2)[1]
    frontmatter = yaml.safe_load(frontmatter_text)

    assert frontmatter["name"] == "internal-knowledge"
    assert "eng-aws-" + "authorization-v2" not in skill_text
    assert "/" + "Users" + "/" not in skill_text
    assert "docs/adr/README.md" in skill_text

    linked_references = re.findall(r"\[[^]]+\]\((references/[^)]+)\)", skill_text)
    assert linked_references
    for reference in linked_references:
        assert (BUNDLE_ROOT / reference).is_file(), reference


def test_bundle_has_no_host_specific_paths() -> None:
    forbidden = (
        "eng-aws-" + "authorization-v2",
        "/" + "Users" + "/",
        "src/00-global-" + "cross-payer",
    )
    findings: list[str] = []

    for bundle_file in BUNDLE_ROOT.rglob("*"):
        if not bundle_file.is_file() or "__pycache__" in bundle_file.parts:
            continue
        text = bundle_file.read_text(encoding="utf-8")
        for value in forbidden:
            if value in text:
                findings.append(f"{bundle_file.relative_to(BUNDLE_ROOT)}: {value}")

    assert not findings, "host-specific bundle content: " + ", ".join(findings)


def test_evaluations_cover_trigger_and_near_miss_cases() -> None:
    scenarios = (BUNDLE_ROOT / "evals" / "evaluation_scenarios.md").read_text(
        encoding="utf-8"
    )

    assert "Should trigger" in scenarios
    assert "Should not trigger" in scenarios
    assert "Baseline" in scenarios
    assert "CI routing" in scenarios
    assert "Do not author GitHub Actions YAML" in scenarios


def test_ci_reference_is_routing_only() -> None:
    ci_reference = (BUNDLE_ROOT / "references" / "ci-assets.md").read_text(encoding="utf-8")
    skill_text = (BUNDLE_ROOT / "SKILL.md").read_text(encoding="utf-8")

    assert "expected_assets" in ci_reference
    assert "host-configured" in ci_reference
    assert "manifest" in ci_reference
    assert "repo-root" in ci_reference
    assert "exit code" in ci_reference.lower()
    assert "/internal-github-actions" in ci_reference
    assert "/internal-python-script" in ci_reference
    assert "```yaml" not in ci_reference
    assert "references/ci-assets.md" in skill_text
    assert ".github/actions/knowledge-check/action.yml" not in ci_reference
    assert ".github/workflows/_knowledge-docs-analysis.yml" not in ci_reference


def test_setup_suggestion_is_user_invoked_and_out_of_boundary() -> None:
    skill_text = (BUNDLE_ROOT / "SKILL.md").read_text(encoding="utf-8")

    assert "/mattpocock-writing-for-agents" in skill_text
    assert "user-invoked" in skill_text
    assert "non-blocking" in skill_text
    assert "AGENTS.md" in skill_text
    assert "outside this skill" in skill_text


def test_audit_ci_signal_binds_to_reference_routing() -> None:
    from knowledge_core import audit_repository, load_knowledge_config

    skill_text = (BUNDLE_ROOT / "SKILL.md").read_text(encoding="utf-8")
    ci_reference = (BUNDLE_ROOT / "references" / "ci-assets.md").read_text(encoding="utf-8")
    report = audit_repository(BUNDLE_ROOT.parents[2])
    configured = load_knowledge_config(BUNDLE_ROOT, None)

    assert "ci_assets" in report
    assert report["ci_assets"] == {}
    assert configured["expected_assets"] == {}
    assert "references/ci-assets.md" in skill_text
    assert "expected_assets" in ci_reference
    assert "host-configured" in ci_reference


def test_readme_reference_restores_output_changing_parity_rules() -> None:
    readme = (BUNDLE_ROOT / "references" / "readme-maintenance.md").read_text(
        encoding="utf-8"
    )

    assert "nature precedence" in readme
    assert "mixed" in readme
    assert "independently evidenced" in readme
    assert "composition precedence" in readme
    assert "atomic writes" in readme or "atomic-write" in readme
    assert "rollback" in readme
    assert "validator" in readme.lower()
    assert "universal" in readme
    assert "semantic" in readme.lower() and "heading" in readme.lower()
    assert "omitted-with-reason" in readme
    assert "preflight table" in readme
    assert "Mermaid" in readme
    assert "flowchart" in readme
    assert "sequenceDiagram" in readme
    assert "accTitle" in readme
    assert "accDescr" in readme
    assert "click" in readme
    assert "table of contents" in readme.lower() or "TOC" in readme


def test_architecture_reference_restores_minor_authoring_rules() -> None:
    architecture = (
        BUNDLE_ROOT / "references" / "architecture-maintenance.md"
    ).read_text(encoding="utf-8")

    assert "| --- | --- |" in architecture
    assert "|---|---|" in architecture
    assert "on-disk" in architecture
    assert "monorepo" in architecture.lower()
    assert "numbered prefixes" in architecture or "`00-`" in architecture
    assert "Section 12" in architecture or "section 12" in architecture
    assert "per-repository" in architecture or "one repository" in architecture
    assert "Do not guess" in architecture or "do not guess" in architecture or "Stop before analysis" in architecture
