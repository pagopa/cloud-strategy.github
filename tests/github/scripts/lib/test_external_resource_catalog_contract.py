import sys
from pathlib import Path

import pytest
import yaml

REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)
sys.path.insert(0, str(REPO_ROOT / ".github/scripts"))

from lib.catalog_checks import (  # noqa: E402
    check_external_resource_manifest,
    check_superpowers_import_naming,
)


def _write_valid_managed_resources(root: Path) -> None:
    manifest_dir = (
        root / ".github/skills/local-agent-sync-external-resources/references"
    )
    manifest_dir.mkdir(parents=True, exist_ok=True)
    manifest = manifest_dir / "managed-resources.yaml"
    manifest.write_text(
        """\
version: 1
sources:
  obra-superpowers:
    repository: https://github.com/obra/superpowers.git
    ref: abc123
    assets:
      - upstream: skills/brainstorming
        local: .github/skills/superpowers-brainstorming
        canonical_name: superpowers-brainstorming
watchlist: []
""",
        encoding="utf-8",
    )


def _write_superpowers_skill(root: Path, name: str) -> None:
    skill_dir = root / ".github/skills/superpowers-brainstorming"
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / "SKILL.md").write_text(
        f"---\nname: {name}\n---\nContent.\n",
        encoding="utf-8",
    )


def test_catalog_check_uses_consolidated_manifest(tmp_path: Path) -> None:
    _write_valid_managed_resources(tmp_path)
    _write_superpowers_skill(tmp_path, "superpowers-brainstorming")

    findings = check_superpowers_import_naming(tmp_path)

    assert findings == []


def test_catalog_check_rejects_duplicate_managed_target(tmp_path: Path) -> None:
    manifest_dir = (
        tmp_path / ".github/skills/local-agent-sync-external-resources/references"
    )
    manifest_dir.mkdir(parents=True, exist_ok=True)
    manifest = manifest_dir / "managed-resources.yaml"
    manifest.write_text(
        """\
version: 1
sources:
  source-a:
    repository: https://example.com/a.git
    ref: abc
    assets:
      - upstream: skills/one
        local: .github/skills/same
        canonical_name: same
  source-b:
    repository: https://example.com/b.git
    ref: def
    assets:
      - upstream: skills/two
        local: .github/skills/same
        canonical_name: same-two
watchlist: []
""",
        encoding="utf-8",
    )

    findings = check_external_resource_manifest(tmp_path)

    assert any(
        finding.code == "external-resource-manifest-duplicate-target"
        for finding in findings
    )


def test_catalog_check_rejects_residual_managed_upstream_name(
    tmp_path: Path,
) -> None:
    _write_valid_managed_resources(tmp_path)
    _write_superpowers_skill(tmp_path, "brainstorming")

    findings = check_superpowers_import_naming(tmp_path)

    assert any(
        finding.code == "superpowers-import-skill-name-mismatch" for finding in findings
    )
