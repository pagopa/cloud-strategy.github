import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

BUNDLE = Path(__file__).resolve().parents[1]
REFERENCES = BUNDLE / "references"
PYTHON_BLOCK = re.compile(r"```python\n(.*?)```", re.DOTALL)


def python_blocks(path: Path) -> list[str]:
    return PYTHON_BLOCK.findall(path.read_text(encoding="utf-8"))


REFERENCES_WITH_PYTHON = sorted(
    path for path in REFERENCES.glob("*.md") if python_blocks(path)
)


def test_some_reference_contains_python_examples() -> None:
    assert REFERENCES_WITH_PYTHON


@pytest.mark.parametrize("path", REFERENCES_WITH_PYTHON, ids=lambda p: p.name)
def test_reference_python_examples_compile(path: Path) -> None:
    for index, block in enumerate(python_blocks(path)):
        compile(block, f"{path.name}[{index}]", "exec")


def test_entrypoint_template_returns_exit_codes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    (template,) = python_blocks(REFERENCES / "layout-and-templates.md")
    namespace: dict[str, object] = {"__name__": "entrypoint_template"}
    exec(template, namespace)

    monkeypatch.setattr(sys, "argv", ["tool", "--target", "demo"])
    assert namespace["main"]() == 0

    monkeypatch.setattr(sys, "argv", ["tool"])
    with pytest.raises(SystemExit) as missing_argument:
        namespace["main"]()
    assert missing_argument.value.code == 2


def test_entrypoint_accepts_explicit_arguments_without_changing_process_argv() -> None:
    (template,) = python_blocks(REFERENCES / "layout-and-templates.md")
    namespace: dict[str, object] = {"__name__": "entrypoint_template"}
    exec(template, namespace)
    original_argv = sys.argv.copy()

    assert namespace["main"](["--target", "demo"]) == 0
    assert sys.argv == original_argv
    with pytest.raises(SystemExit) as missing_argument:
        namespace["main"]([])
    assert missing_argument.value.code == 2


@pytest.mark.parametrize("defective", [False, True])
def test_published_cli_recipe_detects_exit_defects(tmp_path: Path, defective: bool) -> None:
    (contract,) = python_blocks(REFERENCES / "layout-and-templates.md")
    (recipe,) = python_blocks(REFERENCES / "testing.md")
    if defective:
        contract += "\nmain = lambda argv=None: 0\n"
    (tmp_path / "cli.py").write_text(contract, encoding="utf-8")
    (tmp_path / "test_cli.py").write_text(recipe, encoding="utf-8")
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "test_cli.py"],
        cwd=tmp_path,
        env={"PATH": os.defpath, "HOME": str(tmp_path), "LC_ALL": "C",
             "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1"},
        capture_output=True, text=True, check=False, timeout=20,
    )
    assert result.returncode == (1 if defective else 0), result.stdout + result.stderr
    if defective:
        assert "FAILED" in result.stdout, result.stdout
