import json
import re
from dataclasses import is_dataclass
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


def test_logging_example_adapters_honor_the_reporter_protocol(tmp_path: Path) -> None:
    namespace: dict[str, object] = {"__name__": "logging_example"}
    exec("\n\n".join(python_blocks(REFERENCES / "logging-and-reporting.md")), namespace)

    summary = namespace["import_records"](tmp_path / "in.csv", tmp_path / "out.csv")
    assert is_dataclass(summary)

    calls: list[dict[str, object]] = []

    class RecordingReporter:
        def summary(self, *, status, counts, produced_files) -> None:
            calls.append({"status": status, "counts": counts, "produced_files": produced_files})

    namespace["render_human_summary"](summary, RecordingReporter())
    assert calls and calls[0]["produced_files"] == [summary.output_path]

    payload = namespace["summary_to_json"](summary)
    assert json.loads(json.dumps(payload)) == payload
