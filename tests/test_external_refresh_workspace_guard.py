from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def load_module():
    script_path = Path(
        ".github/skills/local-agent-sync-external-resources/scripts/check_external_refresh_workspace.py"
    )
    spec = importlib.util.spec_from_file_location(
        "check_external_refresh_workspace", script_path
    )
    module = importlib.util.module_from_spec(spec)
    assert spec is not None
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_missing_graphifyignore_patterns_are_reported(tmp_path: Path) -> None:
    module = load_module()
    write_file(tmp_path / ".graphifyignore", "/graphify-out/\n")

    missing = module.missing_graphifyignore_patterns(tmp_path)

    assert "tmp/" in missing
    assert "/tmp/" in missing
    assert "tmp/external-refresh/" in missing
    assert "**/.git/" in missing


def test_repo_local_workspace_is_rejected(tmp_path: Path) -> None:
    module = load_module()
    workspace = tmp_path / "tmp/external-refresh"
    workspace.mkdir(parents=True)

    findings = module.validate_workspace(tmp_path, workspace)

    assert findings == [
        "External refresh workspace must be outside the repository: tmp/external-refresh"
    ]


def test_external_workspace_is_accepted(tmp_path: Path) -> None:
    module = load_module()
    workspace = tmp_path.parent / "cloud-strategy-github-external-refresh"
    workspace.mkdir(exist_ok=True)

    findings = module.validate_workspace(tmp_path, workspace)

    assert findings == []


def test_repo_local_refresh_leftovers_are_reported(tmp_path: Path) -> None:
    module = load_module()
    (tmp_path / "tmp/external-refresh/awesome-copilot").mkdir(parents=True)

    findings = module.find_repo_local_refresh_dirs(tmp_path)

    assert findings == ["tmp/external-refresh"]
