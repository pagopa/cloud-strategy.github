"""Execute published recipes against working and known defective shell targets."""

import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

BUNDLE = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("variant", ["valid", "defective"])
@pytest.mark.parametrize(
    ("test_directory", "script_path"),
    [("tools/tests", "tools/tool.sh"), ("tests/operators", "scripts/tool.sh")],
)
def test_recipe_detects_real_shell_defects(
    tmp_path: Path, variant: str, test_directory: str, script_path: str,
) -> None:
    reference = (BUNDLE / "references/testing.md").read_text(encoding="utf-8")
    (recipe,) = re.findall(r"```python\n(.*?)```", reference, re.DOTALL)
    test_root = tmp_path / test_directory
    test_root.mkdir(parents=True)
    (test_root / "test_recipe.py").write_text(recipe, encoding="utf-8")
    fixture = BUNDLE / f"tests/evaluation/fixtures/cache-clean-{variant}.sh"
    target = tmp_path / script_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(fixture.read_bytes())
    target.chmod(0o755)
    result = subprocess.run(
        [sys.executable, "-m", "unittest", "test_recipe", "-v"],
        cwd=test_root,
        env={"PATH": os.defpath, "HOME": str(tmp_path), "LC_ALL": "C",
             "TOOL_UNDER_TEST": str(target)},
        capture_output=True, text=True, check=False, timeout=20,
    )
    if variant == "valid":
        assert result.returncode == 0, result.stderr
    else:
        assert result.returncode == 1, result.stderr
        assert "FAIL:" in result.stderr, result.stderr
