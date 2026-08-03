import importlib.util
import shutil
import sys
from pathlib import Path

REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)
BUNDLE = REPO_ROOT / ".github/skills/internal-gateway-writing-plans"
WRITER_FIXTURE = BUNDLE / "fixtures/2026-07-25-1829-valid-plan.md"
EXECUTOR_SCRIPT = (
    REPO_ROOT
    / ".github/skills/internal-gateway-execute-plans/scripts/plan_execution.py"
)


def _executor_module():
    spec = importlib.util.spec_from_file_location("plan_execution", EXECUTOR_SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_writer_plan_is_actionable_for_executor(tmp_path: Path) -> None:
    retained = tmp_path / "tmp" / "superpowers" / "plans"
    retained.mkdir(parents=True)
    (tmp_path / "AGENTS.md").write_text("# Test repository\n")
    (tmp_path / ".github").mkdir()
    plan = retained / WRITER_FIXTURE.name
    shutil.copy(WRITER_FIXTURE, plan)

    writer_text = WRITER_FIXTURE.read_text()
    assert "## Control Inventory" in writer_text
    assert "- No Git mutation." in writer_text

    findings = _executor_module().validate_plan(plan, repo_root=tmp_path)

    assert findings == []
