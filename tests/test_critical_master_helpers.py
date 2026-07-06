import sys
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

MODULE_PATH = Path(
    ".github/skills/internal-gateway-critical-master/scripts/critical_master.py"
).resolve()
SPEC = spec_from_file_location("critical_master", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
critical_master = module_from_spec(SPEC)
sys.modules[SPEC.name] = critical_master
SPEC.loader.exec_module(critical_master)


def test_validate_outcome_value_accepts_allowed_value() -> None:
    assert critical_master.validate_outcome_value("accept-with-risk")


def test_count_words_ignores_fenced_code_blocks() -> None:
    assert critical_master.count_words("alpha ```python\nbeta\n``` gamma") == 2
