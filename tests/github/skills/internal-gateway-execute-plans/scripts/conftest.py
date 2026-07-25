import shutil
from pathlib import Path

import pytest

BUNDLE = (
    Path(__file__).resolve().parents[5]
    / ".github/skills/internal-gateway-execute-plans"
)
FIXTURES = BUNDLE / "fixtures"


@pytest.fixture()
def valid_plan(tmp_path: Path) -> Path:
    (tmp_path / "AGENTS.md").write_text("# agents\n")
    (tmp_path / ".github").mkdir()
    staged = tmp_path / "tmp" / "superpowers" / "plans"
    staged.mkdir(parents=True)
    target = staged / "valid-plan.md"
    shutil.copy(FIXTURES / "valid-plan.md", target)
    return target


@pytest.fixture()
def valid_partial_status(tmp_path: Path) -> Path:
    target = tmp_path / "valid-plan.PARTIAL.md"
    shutil.copy(FIXTURES / "valid-plan.PARTIAL.md", target)
    return target


@pytest.fixture()
def invalid_status() -> Path:
    return FIXTURES / "invalid-status.md"
