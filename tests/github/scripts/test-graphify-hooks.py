from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
INSTALLER = REPOSITORY_ROOT / ".github/scripts/install-graphify-hooks.sh"
DELEGATE = REPOSITORY_ROOT / ".github/scripts/graphify-file-change-hook.sh"
HOOK_NAMES = ("post-commit", "post-checkout", "post-merge")


def _copy_graphify_scripts(repository: Path) -> None:
    scripts = repository / ".github/scripts"
    scripts.mkdir(parents=True)
    for source in (INSTALLER, DELEGATE):
        target = scripts / source.name
        shutil.copy2(source, target)
        target.chmod(target.stat().st_mode | 0o111)


def _run_installer(repository: Path) -> None:
    result = subprocess.run(
        [str(repository / ".github/scripts/install-graphify-hooks.sh")],
        cwd=repository,
        check=False,
        text=True,
        capture_output=True,
    )
    assert result.returncode == 0, result.stderr


def test_installer_creates_idempotent_delegating_hooks_and_preserves_foreign_hook(
    tmp_path: Path,
) -> None:
    repository = tmp_path / "repository"
    repository.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=repository, check=True)
    _copy_graphify_scripts(repository)

    hooks = repository / ".github/hooks"
    hooks.mkdir(parents=True)
    foreign_hook = hooks / "post-merge"
    foreign_hook.write_text(
        "#!/usr/bin/env bash\nprintf 'foreign\n'\n", encoding="utf-8"
    )
    foreign_hook.chmod(0o755)

    _run_installer(repository)
    first_contents = {
        name: (hooks / name).read_text(encoding="utf-8") for name in HOOK_NAMES
    }
    _run_installer(repository)

    assert (
        subprocess.run(
            ["git", "config", "--get", "core.hooksPath"],
            cwd=repository,
            check=True,
            text=True,
            capture_output=True,
        ).stdout.strip()
        == ".github/hooks"
    )

    for name in HOOK_NAMES:
        hook = hooks / name
        assert hook.is_file()
        assert os.access(hook, os.X_OK)
        contents = hook.read_text(encoding="utf-8")
        assert "graphify-hook: managed delegate" in contents
        assert "graphify-file-change-hook.sh" in contents
        assert contents.count("graphify-hook: managed delegate") == 1
        assert contents == first_contents[name]

    preserved = hooks / "post-merge.graphify-original"
    assert (
        preserved.read_text(encoding="utf-8")
        == "#!/usr/bin/env bash\nprintf 'foreign\n'\n"
    )
