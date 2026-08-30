"""Neutral tests for the host knowledge-config contract."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

BUNDLE_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_ROOT = BUNDLE_ROOT / "scripts"
KNOWLEDGE_CLI = SCRIPTS_ROOT / "knowledge.py"
if str(SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_ROOT))


CONFIG_FIELDS = (
    "scan_roots",
    "exclusions",
    "expected_assets",
    "canonical_documents",
    "coverage_rules",
)


def run_cli(repo_root: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(KNOWLEDGE_CLI),
            *arguments,
            "--repo-root",
            str(repo_root),
            "--format",
            "json",
        ],
        capture_output=True,
        text=True,
        check=False,
    )


def initialize_repo(repo_root: Path) -> None:
    repo_root.mkdir()
    subprocess.run(["git", "init"], cwd=repo_root, check=True, capture_output=True)


def write_valid_config(path: Path) -> None:
    path.write_text(
        "\n".join(
            [
                "scan_roots:",
                "  - apps",
                "  - docs",
                "exclusions:",
                "  - vendor/**",
                "expected_assets:",
                "  action: .github/actions/docs-check/action.yml",
                "  workflow: .github/workflows/docs.yml",
                "canonical_documents:",
                "  - docs/architecture.md",
                "coverage_rules:",
                "  terraform_root:",
                "    require: readme",
                "",
            ]
        ),
        encoding="utf-8",
    )


def test_missing_optional_config_returns_portable_defaults() -> None:
    from knowledge_core import load_knowledge_config

    config = load_knowledge_config(BUNDLE_ROOT, None)

    assert set(CONFIG_FIELDS) <= set(config)
    assert config["scan_roots"] == []
    assert config["exclusions"] == []
    assert config["expected_assets"] == {}
    assert config["canonical_documents"] == []
    assert config["coverage_rules"] == {}
    serialized = json.dumps(config)
    assert "eng-aws-" + "authorization-v2" not in serialized
    assert "knowledge-check" not in serialized


def test_valid_config_contains_only_discovery_policy_fields(tmp_path: Path) -> None:
    from knowledge_core import load_knowledge_config

    config_path = tmp_path / "knowledge-config.yaml"
    write_valid_config(config_path)

    config = load_knowledge_config(tmp_path, config_path)

    assert set(config) == set(CONFIG_FIELDS)
    assert "components" not in config
    assert config["scan_roots"] == ["apps", "docs"]
    assert config["exclusions"] == ["vendor/**"]
    assert config["expected_assets"]["action"] == ".github/actions/docs-check/action.yml"
    assert config["canonical_documents"] == ["docs/architecture.md"]
    assert config["coverage_rules"]["terraform_root"]["require"] == "readme"


def write_config_with_rule(path: Path, rule_body: str) -> None:
    path.write_text(
        "\n".join(
            [
                "scan_roots:",
                "  - apps",
                "exclusions: []",
                "expected_assets: {}",
                "canonical_documents: []",
                "coverage_rules:",
                "  terraform_root:",
                rule_body,
                "",
            ]
        ),
        encoding="utf-8",
    )


def test_unknown_coverage_rule_requirement_is_rejected(tmp_path: Path) -> None:
    from knowledge_core import KnowledgeConfigError, load_knowledge_config

    config_path = tmp_path / "knowledge-config.yaml"
    write_config_with_rule(config_path, "    require: inventory")

    try:
        load_knowledge_config(tmp_path, config_path)
    except KnowledgeConfigError as error:
        assert "require" in str(error)
        return
    raise AssertionError("an unknown require value must not be accepted")


def test_coverage_rule_without_require_is_rejected(tmp_path: Path) -> None:
    from knowledge_core import KnowledgeConfigError, load_knowledge_config

    config_path = tmp_path / "knowledge-config.yaml"
    write_config_with_rule(config_path, "    expect: readme")

    try:
        load_knowledge_config(tmp_path, config_path)
    except KnowledgeConfigError as error:
        assert "require" in str(error)
        return
    raise AssertionError("a coverage rule without require must not be accepted")


def test_coverage_rule_with_extra_key_is_rejected(tmp_path: Path) -> None:
    from knowledge_core import KnowledgeConfigError, load_knowledge_config

    config_path = tmp_path / "knowledge-config.yaml"
    write_config_with_rule(config_path, "    require: readme\n    severity: warn")

    try:
        load_knowledge_config(tmp_path, config_path)
    except KnowledgeConfigError as error:
        assert "require" in str(error)
        return
    raise AssertionError("a coverage rule with an extra key must not be accepted")


def test_invalid_explicit_config_returns_exit_2(tmp_path: Path) -> None:
    repo_root = tmp_path / "consumer"
    initialize_repo(repo_root)
    config_path = repo_root / "docs" / "knowledge-config.yaml"
    config_path.parent.mkdir()
    config_path.write_text("scan_roots: []\nunknown_field: true\n", encoding="utf-8")

    result = run_cli(repo_root, "audit", "--config", str(config_path))

    assert result.returncode == 2
    report = json.loads(result.stdout)
    assert report["mode"] == "audit"
    assert report["status"] == "blocked"
    assert report["findings"]


def test_audit_reads_expected_assets_from_config_and_writes_nothing(tmp_path: Path) -> None:
    repo_root = tmp_path / "consumer"
    initialize_repo(repo_root)
    config_path = repo_root / "docs" / "knowledge-config.yaml"
    config_path.parent.mkdir()
    write_valid_config(config_path)
    before = config_path.read_bytes()

    result = run_cli(repo_root, "audit", "--config", str(config_path))

    report = json.loads(result.stdout)
    assert result.returncode == 0
    assert report["mode"] == "audit"
    assert report["findings"]
    assert report["ci_assets"]["action"]["path"] == ".github/actions/docs-check/action.yml"
    assert report["ci_assets"]["workflow"]["path"] == ".github/workflows/docs.yml"
    assert report["ci_assets"]["action"]["present"] is False
    assert config_path.read_bytes() == before
    assert not (repo_root / "docs" / "knowledge-map.yaml").exists()


def test_audit_without_config_has_no_hardcoded_ci_assets(tmp_path: Path) -> None:
    repo_root = tmp_path / "consumer"
    initialize_repo(repo_root)

    result = run_cli(repo_root, "audit")

    report = json.loads(result.stdout)
    assert result.returncode == 0
    assert report["ci_assets"] == {}
    assert "knowledge-check" not in result.stdout
    assert "_knowledge-docs-analysis.yml" not in result.stdout


def test_audit_skips_adr_index_readme(tmp_path: Path) -> None:
    repo_root = tmp_path / "consumer"
    initialize_repo(repo_root)
    adr_dir = repo_root / "docs" / "adr"
    adr_dir.mkdir(parents=True)
    (adr_dir / "README.md").write_text("# ADR index\n", encoding="utf-8")
    (repo_root / "docs" / "knowledge-map.yaml").write_text(
        "schema_version: 1\nkind: knowledge-map\ncomponents: []\n",
        encoding="utf-8",
    )
    subprocess.run(["git", "add", "."], cwd=repo_root, check=True, capture_output=True)

    result = run_cli(repo_root, "audit")

    report = json.loads(result.stdout)
    assert result.returncode == 0
    assert "ADR identity mismatch: docs/adr/README.md" not in report["findings"]


def test_bootstrap_and_update_leave_host_config_byte_identical(tmp_path: Path) -> None:
    repo_root = tmp_path / "consumer"
    initialize_repo(repo_root)
    (repo_root / "README.md").write_text("# Consumer\n", encoding="utf-8")
    config_path = repo_root / "docs" / "knowledge-config.yaml"
    config_path.parent.mkdir()
    write_valid_config(config_path)
    original = config_path.read_bytes()
    subprocess.run(["git", "add", "."], cwd=repo_root, check=True, capture_output=True)

    bootstrap = run_cli(repo_root, "bootstrap")
    update = run_cli(repo_root, "update", "--target", "README.md")

    assert bootstrap.returncode == 0
    assert update.returncode == 0
    assert config_path.read_bytes() == original


def test_generic_core_does_not_hardcode_ci_assets() -> None:
    core_text = (SCRIPTS_ROOT / "knowledge_core.py").read_text(encoding="utf-8")
    skill_text = (BUNDLE_ROOT / "SKILL.md").read_text(encoding="utf-8")
    ci_reference = (BUNDLE_ROOT / "references" / "ci-assets.md").read_text(encoding="utf-8")
    audit_reference = (BUNDLE_ROOT / "references" / "modes-audit-impact.md").read_text(
        encoding="utf-8"
    )

    assert "CI_ASSETS" not in core_text
    assert "knowledge-check/action.yml" not in core_text
    assert "_knowledge-docs-analysis.yml" not in core_text
    assert "host-configured" in ci_reference or "expected_assets" in ci_reference
    assert "knowledge-check/action.yml" not in ci_reference
    assert "_knowledge-docs-analysis.yml" not in ci_reference
    assert "--config" in audit_reference
    assert "docs/adr/README.md" in audit_reference
    assert "optional" in audit_reference.lower()
    assert "--config" in skill_text


def test_bundle_declares_hash_locked_yaml_dependency() -> None:
    requirements_in = (BUNDLE_ROOT / "requirements.in").read_text(encoding="utf-8")
    requirements = (BUNDLE_ROOT / "requirements.txt").read_text(encoding="utf-8")

    assert "PyYAML" in requirements_in
    assert "PyYAML" in requirements or "pyyaml" in requirements.lower()
    assert "--hash=sha256:" in requirements
    assert "--require-hashes" in (BUNDLE_ROOT / "SKILL.md").read_text(encoding="utf-8")


def test_config_reference_documents_schema_and_exit_codes() -> None:
    reference = (
        BUNDLE_ROOT / "references" / "inventory-and-check.md"
    ).read_text(encoding="utf-8")

    for field in CONFIG_FIELDS:
        assert field in reference
    assert "exit code" in reference.lower()
    assert "never write" in reference.lower() or "must never write" in reference.lower()
