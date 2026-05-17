from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def load_module():
    script_path = Path(
        ".github/skills/local-agent-sync-external-resources/scripts/normalize_superpowers_imports.py"
    )
    spec = importlib.util.spec_from_file_location("normalize_superpowers_imports", script_path)
    module = importlib.util.module_from_spec(spec)
    assert spec is not None
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_reference(root: Path) -> Path:
    reference_path = (
        root
        / ".github/skills/local-agent-sync-external-resources/references/superpowers-normalization.yaml"
    )
    write_file(
        reference_path,
        "version: 1\n"
        "source_family: obra/superpowers\n"
        "managed_skills:\n"
        "  - upstream: demo\n"
        "    legacy_local: obra-demo\n"
        "    local: superpowers-demo\n"
        "managed_patches:\n"
        "  - legacy_path: patches/obra-demo.patch\n"
        "    path: patches/superpowers-demo.patch\n"
        "live_scan:\n"
        "  include:\n"
        "    - .github/agents\n"
        "    - .github/skills\n"
        "  ignored_files:\n"
        "    - superpowers-normalization.yaml\n",
    )
    return reference_path


def test_normalizer_detects_and_applies_legacy_skill_drift(tmp_path: Path) -> None:
    module = load_module()
    reference_path = write_reference(tmp_path)
    write_file(
        tmp_path / ".github/skills/obra-demo/SKILL.md",
        "---\nname: obra-demo\ndescription: Demo.\n---\n\nUse superpowers:demo.\n",
    )
    write_file(
        tmp_path / ".github/agents/local-demo.agent.md",
        "---\nname: local-demo\ntools: [read]\n---\n\n- `obra-demo`\n",
    )
    write_file(
        tmp_path / ".github/skills/local-agent-sync-external-resources/patches/obra-demo.patch",
        "diff --git a/.github/skills/obra-demo/SKILL.md b/.github/skills/obra-demo/SKILL.md\n",
    )

    config = module.load_config(reference_path)
    drift = module.detect_drift(tmp_path, config)

    assert {change.kind for change in drift} == {"legacy-path", "legacy-reference"}

    changes = module.apply_normalization(tmp_path, config)

    assert changes
    assert not (tmp_path / ".github/skills/obra-demo").exists()
    assert (tmp_path / ".github/skills/superpowers-demo/SKILL.md").is_file()
    assert (
        "name: superpowers-demo"
        in (tmp_path / ".github/skills/superpowers-demo/SKILL.md").read_text(encoding="utf-8")
    )
    assert (
        "superpowers-demo"
        in (tmp_path / ".github/agents/local-demo.agent.md").read_text(encoding="utf-8")
    )
    assert not (
        tmp_path / ".github/skills/local-agent-sync-external-resources/patches/obra-demo.patch"
    ).exists()
    assert (
        tmp_path / ".github/skills/local-agent-sync-external-resources/patches/superpowers-demo.patch"
    ).is_file()
    assert module.detect_drift(tmp_path, config) == []