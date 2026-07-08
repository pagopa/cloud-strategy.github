import sys
from pathlib import Path

import pytest

REPO_ROOT = next(
    parent for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)
SCRIPT_DIR = (
    REPO_ROOT / ".github/skills/local-agent-sync-external-resources/scripts"
)
sys.path.insert(0, SCRIPT_DIR.as_posix())

from normalize_superpowers_imports import (  # noqa: E402
    load_config,
    detect_drift,
    NormalizationConfig,
    ManagedSkill,
)


def test_load_config_validates_managed_skills(tmp_path: Path) -> None:
    ref = tmp_path / "ref.yaml"
    ref.write_text("managed_skills: not-a-list\n", encoding="utf-8")
    with pytest.raises(ValueError, match="managed_skills"):
        load_config(ref)


def test_detect_drift_finds_legacy_path(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    (repo_root / ".github" / "skills" / "obra-brainstorming").mkdir(parents=True)
    (repo_root / ".github" / "skills" / "obra-brainstorming" / "SKILL.md").write_text(
        "# old\n", encoding="utf-8"
    )
    ref_dir = repo_root / ".github" / "skills" / "local-agent-sync-external-resources" / "references"
    ref_dir.mkdir(parents=True)
    ref = ref_dir / "ref.yaml"
    ref.write_text("managed_skills: []\n", encoding="utf-8")
    config = NormalizationConfig(
        reference_path=ref,
        managed_skills=(ManagedSkill(
            upstream="brainstorming",
            legacy_local="obra-brainstorming",
            local="superpowers-brainstorming",
        ),),
        managed_patches=(),
        managed_text_replacements=(),
        scan_includes=(".github/skills",),
        ignored_files=frozenset(),
    )
    changes = detect_drift(repo_root, config)
    assert any(c.kind == "legacy-path" for c in changes)
