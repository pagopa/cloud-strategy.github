import re
import sys
from pathlib import Path

import pytest

BUNDLE = Path(__file__).resolve().parents[1]
REFERENCES = BUNDLE / "references"
PYTHON_BLOCK = re.compile(r"```python\n(.*?)```", re.DOTALL)


def python_blocks(path: Path) -> list[str]:
    return PYTHON_BLOCK.findall(path.read_text(encoding="utf-8"))


@pytest.mark.parametrize("path", sorted(REFERENCES.glob("*.md")), ids=lambda p: p.name)
def test_reference_python_examples_compile(path: Path) -> None:
    for index, block in enumerate(python_blocks(path)):
        compile(block, f"{path.name}[{index}]", "exec")


def test_entrypoint_template_returns_exit_codes(monkeypatch: pytest.MonkeyPatch) -> None:
    (template,) = python_blocks(REFERENCES / "layout-and-templates.md")
    namespace: dict[str, object] = {"__name__": "entrypoint_template"}
    exec(template, namespace)

    monkeypatch.setattr(sys, "argv", ["tool", "--target", "demo"])
    assert namespace["main"]() == 0

    monkeypatch.setattr(sys, "argv", ["tool"])
    with pytest.raises(SystemExit) as missing_argument:
        namespace["main"]()
    assert missing_argument.value.code == 2
