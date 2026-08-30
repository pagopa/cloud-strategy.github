"""Neutral tests for fail-closed deterministic check."""

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


def write_base_config(path: Path, extra_documents: list[str] | None = None) -> None:
    documents = ["docs/architecture.md", *(extra_documents or [])]
    document_lines = [f"  - {item}" for item in documents]
    path.write_text(
        "\n".join(
            [
                "scan_roots:",
                "  - apps",
                "  - docs",
                "exclusions:",
                "  - vendor/**",
                "expected_assets: {}",
                "canonical_documents:",
                *document_lines,
                "coverage_rules:",
                "  terraform_root:",
                "    require: readme",
                "",
            ]
        ),
        encoding="utf-8",
    )


def write_registers(
    repo_root: Path,
    mapped: list[str],
    knowledge_components: list[str],
    readme_components: list[str] | None = None,
) -> None:
    docs = repo_root / "docs"
    docs.mkdir(parents=True, exist_ok=True)
    map_lines = [
        "schema_version: 1",
        "kind: knowledge-map",
        "components:",
    ]
    for path in mapped:
        map_lines.append(f'  - path: "{path}"')
    (docs / "knowledge-map.yaml").write_text("\n".join(map_lines) + "\n", encoding="utf-8")
    (docs / "knowledge-components.txt").write_text(
        "\n".join(knowledge_components) + "\n",
        encoding="utf-8",
    )
    (docs / "readme-components.txt").write_text(
        "\n".join(readme_components or []) + "\n",
        encoding="utf-8",
    )


def write_conforming_fixture(repo_root: Path) -> Path:
    initialize_repo(repo_root)
    (repo_root / "apps" / "platform").mkdir(parents=True)
    (repo_root / "apps" / "platform" / "main.tf").write_text(
        'terraform {\n  backend "s3" {}\n}\nresource "aws_iam_role" "example" {}\n',
        encoding="utf-8",
    )
    (repo_root / "apps" / "platform" / "README.md").write_text("# platform\n", encoding="utf-8")
    (repo_root / "docs").mkdir()
    (repo_root / "docs" / "architecture.md").write_text("# Architecture\n", encoding="utf-8")
    config_path = repo_root / "docs" / "knowledge-config.yaml"
    write_base_config(config_path)
    write_registers(
        repo_root,
        mapped=["docs/architecture.md", "apps/platform"],
        knowledge_components=["docs"],
        readme_components=["apps/platform"],
    )
    subprocess.run(["git", "add", "."], cwd=repo_root, check=True, capture_output=True)
    return config_path


def test_check_without_config_returns_exit_2(tmp_path: Path) -> None:
    repo_root = tmp_path / "consumer"
    initialize_repo(repo_root)

    result = run_cli(repo_root, "check")

    report = json.loads(result.stdout)
    assert result.returncode == 2
    assert report["mode"] == "check"
    assert report["status"] == "blocked"
    assert report["findings"]


def test_check_invalid_config_returns_exit_2(tmp_path: Path) -> None:
    repo_root = tmp_path / "consumer"
    initialize_repo(repo_root)
    config_path = repo_root / "docs" / "knowledge-config.yaml"
    config_path.parent.mkdir()
    config_path.write_text("scan_roots: []\nunknown_field: true\n", encoding="utf-8")

    result = run_cli(repo_root, "check", "--config", str(config_path))

    report = json.loads(result.stdout)
    assert result.returncode == 2
    assert report["mode"] == "check"
    assert report["status"] == "blocked"


def test_check_passes_when_coverage_and_registers_agree(tmp_path: Path) -> None:
    repo_root = tmp_path / "consumer"
    config_path = write_conforming_fixture(repo_root)
    before = config_path.read_bytes()
    existing = {
        path.relative_to(repo_root).as_posix()
        for path in repo_root.rglob("*")
        if path.is_file() and ".git" not in path.parts
    }

    result = run_cli(repo_root, "check", "--config", str(config_path))

    report = json.loads(result.stdout)
    after = {
        path.relative_to(repo_root).as_posix()
        for path in repo_root.rglob("*")
        if path.is_file() and ".git" not in path.parts
    }
    assert result.returncode == 0
    assert report["mode"] == "check"
    assert report["status"] == "passed"
    assert report["findings"] == []
    assert after == existing
    assert config_path.read_bytes() == before


def test_check_fails_when_readme_coverage_is_missing(tmp_path: Path) -> None:
    repo_root = tmp_path / "consumer"
    config_path = write_conforming_fixture(repo_root)
    (repo_root / "apps" / "platform" / "README.md").unlink()
    subprocess.run(["git", "add", "-u"], cwd=repo_root, check=True, capture_output=True)

    result = run_cli(repo_root, "check", "--config", str(config_path))

    report = json.loads(result.stdout)
    assert result.returncode == 1
    assert report["status"] == "failed"
    assert any("apps/platform" in str(finding) for finding in report["findings"])


def test_check_fails_when_canonical_document_is_unmapped(tmp_path: Path) -> None:
    repo_root = tmp_path / "consumer"
    initialize_repo(repo_root)
    (repo_root / "docs").mkdir()
    (repo_root / "docs" / "architecture.md").write_text("# Architecture\n", encoding="utf-8")
    config_path = repo_root / "docs" / "knowledge-config.yaml"
    write_base_config(config_path)
    write_registers(repo_root, mapped=[], knowledge_components=["docs"])
    subprocess.run(["git", "add", "."], cwd=repo_root, check=True, capture_output=True)

    result = run_cli(repo_root, "check", "--config", str(config_path))

    report = json.loads(result.stdout)
    assert result.returncode == 1
    assert any("docs/architecture.md" in str(finding) for finding in report["findings"])


def test_check_fails_when_canonical_document_lacks_knowledge_component_coverage(
    tmp_path: Path,
) -> None:
    repo_root = tmp_path / "consumer"
    initialize_repo(repo_root)
    (repo_root / "docs").mkdir()
    (repo_root / "docs" / "architecture.md").write_text("# Architecture\n", encoding="utf-8")
    config_path = repo_root / "docs" / "knowledge-config.yaml"
    write_base_config(config_path)
    write_registers(
        repo_root,
        mapped=["docs/architecture.md"],
        knowledge_components=["README.md"],
    )
    subprocess.run(["git", "add", "."], cwd=repo_root, check=True, capture_output=True)

    result = run_cli(repo_root, "check", "--config", str(config_path))

    report = json.loads(result.stdout)
    assert result.returncode == 1
    assert any("docs/architecture.md" in str(finding) for finding in report["findings"])


def test_check_reports_unclassified_top_level_canonical_guide(tmp_path: Path) -> None:
    repo_root = tmp_path / "consumer"
    config_path = write_conforming_fixture(repo_root)
    (repo_root / "docs" / "operations.md").write_text("# Operations\n", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=repo_root, check=True, capture_output=True)

    result = run_cli(repo_root, "check", "--config", str(config_path))

    report = json.loads(result.stdout)
    assert result.returncode == 1
    assert any("docs/operations.md" in str(finding) for finding in report["findings"])


def test_check_treats_readme_registration_as_distinct_from_canonical_docs(
    tmp_path: Path,
) -> None:
    repo_root = tmp_path / "consumer"
    config_path = write_conforming_fixture(repo_root)
    (repo_root / "docs" / "readme-components.txt").write_text("\n", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=repo_root, check=True, capture_output=True)

    result = run_cli(repo_root, "check", "--config", str(config_path))

    report = json.loads(result.stdout)
    serialized = json.dumps(report)
    assert result.returncode == 1
    assert "apps/platform" in serialized
    assert "docs/architecture.md" not in serialized or report["status"] == "failed"
    assert any("readme" in str(finding).lower() for finding in report["findings"])


def test_check_reuses_inventory_model(tmp_path: Path) -> None:
    from knowledge_core import check_repository, inventory_repository, load_knowledge_config

    repo_root = tmp_path / "consumer"
    config_path = write_conforming_fixture(repo_root)
    config = load_knowledge_config(repo_root, config_path)

    inventory = inventory_repository(repo_root, config)
    check = check_repository(repo_root, config, inventory=inventory)

    inventory_paths = {item["path"] for item in inventory["components"]}
    check_paths = {item["path"] for item in check["inventory"]["components"]}
    assert inventory_paths == check_paths
    assert check["mode"] == "check"
    assert "scan" not in json.dumps(check).lower() or check["inventory"]["mode"] == "inventory"
