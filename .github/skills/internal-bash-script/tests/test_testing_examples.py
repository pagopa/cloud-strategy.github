"""Execute published recipes against working and known defective shell targets."""

import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

BUNDLE = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("variant", ["valid", "defective"])
def test_recipe_detects_real_shell_defects(tmp_path: Path, variant: str) -> None:
    reference = (BUNDLE / "references/testing.md").read_text(encoding="utf-8")
    (recipe,) = re.findall(r"```python\n(.*?)```", reference, re.DOTALL)
    (tmp_path / "test_recipe.py").write_text(recipe, encoding="utf-8")
    fixture = BUNDLE / f"tests/evaluation/fixtures/cache-clean-{variant}.sh"
    target = tmp_path / "tool.sh"
    target.write_bytes(fixture.read_bytes())
    target.chmod(0o755)
    result = subprocess.run(
        [sys.executable, "-m", "unittest", "test_recipe", "-v"],
        cwd=tmp_path,
        env={"PATH": os.defpath, "HOME": str(tmp_path), "LC_ALL": "C"},
        capture_output=True, text=True, check=False, timeout=20,
    )
    if variant == "valid":
        assert result.returncode == 0, result.stderr
    else:
        assert result.returncode == 1, result.stderr
        assert "FAIL:" in result.stderr, result.stderr
