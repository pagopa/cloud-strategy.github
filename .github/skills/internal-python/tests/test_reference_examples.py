import re
from pathlib import Path

import pytest

BUNDLE = Path(__file__).resolve().parents[1]
REFERENCES = BUNDLE / "references"
PYTHON_BLOCK = re.compile(r"```python\n(.*?)```", re.DOTALL)


@pytest.mark.parametrize("path", sorted(REFERENCES.glob("*.md")), ids=lambda p: p.name)
def test_reference_python_examples_compile(path: Path) -> None:
    for index, block in enumerate(PYTHON_BLOCK.findall(path.read_text(encoding="utf-8"))):
        compile(block, f"{path.name}[{index}]", "exec")
