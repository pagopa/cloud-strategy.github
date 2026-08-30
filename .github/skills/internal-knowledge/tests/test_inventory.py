"""Neutral tests for report-only inventory discovery."""

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


REQUIRED_REPORT_KEYS = (
    "mode",
    "status",
    "scope",
    "components",
    "relationships",
    "capabilities",
    "findings",
)

SUPPORTED_KINDS = {
    "terraform_root",
    "terraform_local_module",
    "github_composite_action",
    "github_workflow",
    "declaration_data",
    "script_wrapper",
    "test",
    "validator_tool",
}


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


def write_config(path: Path) -> None:
    path.write_text(
        "\n".join(
            [
                "scan_roots:",
                "  - apps",
                "  - modules",
                "  - data",
                "  - scripts",
                "  - tests",
                "  - tools",
                "  - docs",
                "  - .github/actions",
                "  - .github/workflows",
                "exclusions:",
                "  - vendor/**",
                '  - "**/.terraform/**"',
                "expected_assets: {}",
                "canonical_documents:",
                "  - docs/architecture.md",
                "coverage_rules:",
                "  terraform_root:",
                "    require: readme",
                "  terraform_local_module:",
                "    require: readme",
                "  github_composite_action:",
                "    require: readme",
                "  script_wrapper:",
                "    require: readme",
                "  validator_tool:",
                "    require: readme",
                "",
            ]
        ),
        encoding="utf-8",
    )


def write_inventory_fixture(repo_root: Path) -> Path:
    initialize_repo(repo_root)
    (repo_root / "apps" / "platform").mkdir(parents=True)
    (repo_root / "apps" / "platform" / "main.tf").write_text(
        "\n".join(
            [
                "terraform {",
                '  backend "s3" {}',
                "}",
                'resource "aws_iam_role" "example" {}',
                'data "aws_caller_identity" "current" {}',
                'module "shared" {',
                '  source = "../../modules/shared"',
                "}",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (repo_root / "apps" / "platform" / "README.md").write_text("# platform\n", encoding="utf-8")
    (repo_root / "apps" / "notes.txt").write_text("unclassified note\n", encoding="utf-8")

    (repo_root / "modules" / "shared").mkdir(parents=True)
    (repo_root / "modules" / "shared" / "main.tf").write_text(
        'resource "aws_iam_policy" "shared" {}\n',
        encoding="utf-8",
    )
    (repo_root / "modules" / "shared" / "README.md").write_text("# shared\n", encoding="utf-8")

    action = repo_root / ".github" / "actions" / "docs-check"
    action.mkdir(parents=True)
    (action / "action.yml").write_text(
        "name: docs-check\nruns:\n  using: composite\n  steps: []\n",
        encoding="utf-8",
    )
    (action / "README.md").write_text("# docs-check\n", encoding="utf-8")

    workflows = repo_root / ".github" / "workflows"
    workflows.mkdir(parents=True)
    (workflows / "docs.yml").write_text(
        "\n".join(
            [
                "name: docs",
                "on: push",
                "jobs:",
                "  check:",
                "    runs-on: ubuntu-latest",
                "    steps:",
                "      - uses: ./.github/actions/docs-check",
                "      - run: ./scripts/run.sh",
                "",
            ]
        ),
        encoding="utf-8",
    )

    (repo_root / "data").mkdir()
    (repo_root / "data" / "accounts.yaml").write_text("accounts: []\n", encoding="utf-8")

    (repo_root / "scripts").mkdir()
    (repo_root / "scripts" / "run.sh").write_text("#!/bin/sh\necho run\n", encoding="utf-8")
    (repo_root / "scripts" / "README.md").write_text("# scripts\n", encoding="utf-8")

    (repo_root / "tests").mkdir()
    (repo_root / "tests" / "test_example.py").write_text(
        "def test_ok():\n    assert True\n",
        encoding="utf-8",
    )

    tool = repo_root / "tools" / "docs_lint"
    tool.mkdir(parents=True)
    (tool / "lint.py").write_text("print('lint')\n", encoding="utf-8")
    (tool / "README.md").write_text("# docs_lint\n", encoding="utf-8")

    docs = repo_root / "docs"
    docs.mkdir()
    (docs / "architecture.md").write_text(
        "See apps/platform and scripts/run.sh\n",
        encoding="utf-8",
    )
    write_config(docs / "knowledge-config.yaml")

    vendor = repo_root / "vendor" / "secret"
    vendor.mkdir(parents=True)
    (vendor / "main.tf").write_text('resource "aws_s3_bucket" "hidden" {}\n', encoding="utf-8")
    generated = repo_root / "apps" / "platform" / ".terraform"
    generated.mkdir()
    (generated / "ignored.tf").write_text(
        'resource "aws_s3_bucket" "generated" {}\n',
        encoding="utf-8",
    )

    tracked = [
        "apps/platform/main.tf",
        "apps/platform/README.md",
        "apps/notes.txt",
        "modules/shared/main.tf",
        "modules/shared/README.md",
        ".github/actions/docs-check/action.yml",
        ".github/actions/docs-check/README.md",
        ".github/workflows/docs.yml",
        "data/accounts.yaml",
        "scripts/run.sh",
        "scripts/README.md",
        "tests/test_example.py",
        "tools/docs_lint/lint.py",
        "tools/docs_lint/README.md",
        "docs/architecture.md",
        "docs/knowledge-config.yaml",
    ]
    subprocess.run(["git", "add", *tracked], cwd=repo_root, check=True, capture_output=True)
    return docs / "knowledge-config.yaml"


def component_paths(report: dict[str, object], kind: str) -> set[str]:
    components = report["components"]
    assert isinstance(components, list)
    return {
        str(item["path"])
        for item in components
        if isinstance(item, dict) and item.get("kind") == kind
    }


def serialized_report(report: dict[str, object]) -> str:
    return json.dumps(report, sort_keys=True)


def test_inventory_emits_stable_report_without_writing(tmp_path: Path) -> None:
    repo_root = tmp_path / "consumer"
    config_path = write_inventory_fixture(repo_root)
    before = config_path.read_bytes()
    existing = {
        path.relative_to(repo_root).as_posix()
        for path in repo_root.rglob("*")
        if path.is_file() and ".git" not in path.parts
    }

    result = run_cli(repo_root, "inventory", "--config", str(config_path))

    report = json.loads(result.stdout)
    after = {
        path.relative_to(repo_root).as_posix()
        for path in repo_root.rglob("*")
        if path.is_file() and ".git" not in path.parts
    }
    assert result.returncode == 0
    assert report["mode"] == "inventory"
    assert report["status"] == "reported"
    assert set(REQUIRED_REPORT_KEYS) <= set(report)
    assert report["scope"]["scan_roots"]
    assert report["scope"]["exclusions"]
    assert after == existing
    assert config_path.read_bytes() == before
    assert "eng-aws-" + "authorization-v2" not in serialized_report(report)


def test_inventory_discovers_supported_component_kinds(tmp_path: Path) -> None:
    repo_root = tmp_path / "consumer"
    config_path = write_inventory_fixture(repo_root)

    result = run_cli(repo_root, "inventory", "--config", str(config_path))

    report = json.loads(result.stdout)
    kinds = {item["kind"] for item in report["components"] if isinstance(item, dict)}
    assert SUPPORTED_KINDS <= kinds
    assert "apps/platform" in component_paths(report, "terraform_root")
    assert "modules/shared" in component_paths(report, "terraform_local_module")
    assert ".github/actions/docs-check" in component_paths(report, "github_composite_action")
    assert ".github/workflows/docs.yml" in component_paths(report, "github_workflow")
    assert "data/accounts.yaml" in component_paths(report, "declaration_data")
    assert "scripts/run.sh" in component_paths(report, "script_wrapper")
    assert "tests/test_example.py" in component_paths(report, "test")
    assert "tools/docs_lint" in component_paths(report, "validator_tool")
    for item in report["components"]:
        assert item.get("evidence")
        assert ".terraform" not in str(item["path"])
        assert not str(item["path"]).startswith("vendor/")


def test_inventory_omits_excluded_and_untracked_paths(tmp_path: Path) -> None:
    repo_root = tmp_path / "consumer"
    config_path = write_inventory_fixture(repo_root)

    result = run_cli(repo_root, "inventory", "--config", str(config_path))
    report = json.loads(result.stdout)
    discovered = json.dumps(
        {
            "components": report["components"],
            "relationships": report["relationships"],
            "capabilities": report["capabilities"],
            "findings": report["findings"],
        }
    )

    assert result.returncode == 0
    assert report["mode"] == "inventory"
    assert "vendor/secret" not in discovered
    assert "aws_s3_bucket" not in discovered
    assert "generated" not in discovered
    assert all(".terraform" not in str(item.get("path", "")) for item in report["components"])


def test_inventory_reports_capabilities_and_relationships(tmp_path: Path) -> None:
    repo_root = tmp_path / "consumer"
    config_path = write_inventory_fixture(repo_root)

    report = json.loads(run_cli(repo_root, "inventory", "--config", str(config_path)).stdout)

    capability_owners = {
        item["owner"] for item in report["capabilities"] if isinstance(item, dict)
    }
    assert "apps/platform" in capability_owners
    platform = next(item for item in report["capabilities"] if item["owner"] == "apps/platform")
    assert "aws_iam_role" in platform["resource_types"]
    assert "aws_caller_identity" in platform["data_source_types"]
    assert platform["static_counts"]["resource"] == 1
    assert platform["static_counts"]["data"] == 1
    assert "aws_iam_role.example" not in serialized_report(report)

    relation_pairs = {
        (item["type"], item["from"], item["to"])
        for item in report["relationships"]
        if isinstance(item, dict)
    }
    assert ("local_module", "apps/platform", "modules/shared") in relation_pairs
    assert (
        "local_action",
        ".github/workflows/docs.yml",
        ".github/actions/docs-check",
    ) in relation_pairs
    assert ("wrapper_caller", ".github/workflows/docs.yml", "scripts/run.sh") in relation_pairs
    assert ("documentation", "docs/architecture.md", "apps/platform") in relation_pairs
    for item in report["relationships"]:
        assert item.get("evidence")


def test_inventory_records_ambiguous_classification_as_finding(tmp_path: Path) -> None:
    repo_root = tmp_path / "consumer"
    config_path = write_inventory_fixture(repo_root)

    report = json.loads(run_cli(repo_root, "inventory", "--config", str(config_path)).stdout)

    assert report["status"] == "reported"
    assert any("apps/notes.txt" in str(finding) for finding in report["findings"])
    assert all(
        isinstance(item, dict) and item.get("kind") in SUPPORTED_KINDS
        for item in report["components"]
    )
