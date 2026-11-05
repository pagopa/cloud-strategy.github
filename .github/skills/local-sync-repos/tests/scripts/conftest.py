import subprocess
import sys
from collections.abc import Callable
from pathlib import Path

import pytest

REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)
BUNDLE_ROOT = REPO_ROOT / ".github/skills/local-sync-repos"
SCRIPT_DIR = BUNDLE_ROOT / "scripts"
if SCRIPT_DIR.as_posix() not in sys.path:
    sys.path.insert(0, SCRIPT_DIR.as_posix())

MANAGED_COPY_PATHS_EXPECTED = (
    "AGENTS.md",
    ".python-version",
    ".pre-commit-config.yaml",
    ".editorconfig",
    ".vscode/settings.json",
    ".github/copilot-instructions.md",
    ".github/workflows/_pre-commit.yml",
    ".github/workflows/_pr-title.yml",
)


def _git(repo: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True)


def _git_init(repo: Path) -> None:
    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True)
    _git(repo, "config", "user.email", "test@example.com")
    _git(repo, "config", "user.name", "Test")


def _populate_source(source: Path) -> None:
    (source / "AGENTS.md").write_text("# agents\n", encoding="utf-8")
    (source / ".python-version").write_text("3.13\n", encoding="utf-8")
    (source / ".pre-commit-config.yaml").write_text("repos: []\n", encoding="utf-8")
    (source / ".editorconfig").write_text("root = true\n", encoding="utf-8")
    settings = source / ".vscode" / "settings.json"
    settings.parent.mkdir(parents=True, exist_ok=True)
    settings.write_text(
        "{\n"
        '  "chat.permissions.default": "default",\n'
        '  "chat.tools.global.autoApprove": false,\n'
        '  "chat.tools.terminal.autoReplyToPrompts": false,\n'
        '  "chat.tools.terminal.enableAutoApprove": false\n'
        "}\n",
        encoding="utf-8",
    )
    (source / ".github").mkdir(exist_ok=True)
    (source / ".github" / "copilot-instructions.md").write_text(
        "# copilot\n", encoding="utf-8"
    )
    (source / ".github" / "workflows").mkdir(parents=True, exist_ok=True)
    (source / ".github" / "workflows" / "_pre-commit.yml").write_text(
        "name: pre-commit\n", encoding="utf-8"
    )
    (source / ".github" / "workflows" / "_pr-title.yml").write_text(
        "name: pr-title\n", encoding="utf-8"
    )
    instructions = source / ".github" / "instructions"
    instructions.mkdir(parents=True, exist_ok=True)
    (instructions / "internal-python.instructions.md").write_text(
        "# python\n", encoding="utf-8"
    )


@pytest.fixture(scope="session")
def managed_copy_paths() -> tuple[str, ...]:
    return MANAGED_COPY_PATHS_EXPECTED


@pytest.fixture(scope="session")
def agents_local_template() -> Path:
    return BUNDLE_ROOT / "templates/AGENTS.local.md"


@pytest.fixture
def git_repo() -> Callable[[Path], Path]:
    """Create an initialized repository with one empty commit."""

    def _create(repo: Path) -> Path:
        repo.mkdir()
        _git_init(repo)
        _git(repo, "commit", "-m", "init", "--allow-empty")
        return repo

    return _create


@pytest.fixture
def source_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "source"
    repo.mkdir()
    _git_init(repo)
    _populate_source(repo)
    _git(repo, "add", "-A")
    _git(repo, "commit", "-m", "init", "--allow-empty")
    return repo


@pytest.fixture
def target_repo(tmp_path: Path, git_repo: Callable[[Path], Path]) -> Path:
    return git_repo(tmp_path / "target")
