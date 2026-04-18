from __future__ import annotations

import importlib.util
from pathlib import Path


def load_module():
    script_path = Path(
        ".github/skills/internal-agent-sync-control-center/scripts/apply_imported_asset_overrides.py"
    )
    spec = importlib.util.spec_from_file_location("apply_imported_asset_overrides", script_path)
    module = importlib.util.module_from_spec(spec)
    assert spec is not None
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_detect_patch_status_uses_registered_3way_fallback(monkeypatch) -> None:
    module = load_module()

    commands: list[tuple[str, ...]] = []

    def fake_run_git(command, repo_root, quiet=False):  # noqa: ARG001
        commands.append(tuple(command))
        if command[:3] == ["git", "apply", "--check"]:
            return 1
        if command[:4] == ["git", "apply", "--reverse", "--check"]:
            return 1
        if command[:4] == ["git", "apply", "--3way", "--check"]:
            return 0
        return 1

    monkeypatch.setattr(module, "run_git", fake_run_git)

    status = module.detect_patch_status(
        Path("."),
        Path("override.patch"),
        apply_strategy="git-apply-3way",
    )

    assert status == "applicable-with-3way"
    assert ("git", "apply", "--3way", "--check", "override.patch") in commands


def test_build_apply_command_uses_3way_only_when_needed() -> None:
    module = load_module()

    patch_path = Path("override.patch")

    assert module.build_apply_command(patch_path, "applicable") == [
        "git",
        "apply",
        "override.patch",
    ]
    assert module.build_apply_command(patch_path, "applicable-with-3way") == [
        "git",
        "apply",
        "--3way",
        "override.patch",
    ]
