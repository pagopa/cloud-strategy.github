import sys
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)
MODULE_PATH = (
    REPO_ROOT / ".github/skills/internal-gateway-critical-master/scripts/critical_master.py"
)
SPEC = spec_from_file_location("critical_master", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
critical_master = module_from_spec(SPEC)
sys.modules[SPEC.name] = critical_master
SPEC.loader.exec_module(critical_master)


def test_validate_outcome_value_accepts_allowed_value() -> None:
    assert critical_master.validate_outcome_value("accept-with-risk")


def test_count_words_ignores_fenced_code_blocks() -> None:
    assert critical_master.count_words("alpha ```python\nbeta\n``` gamma") == 2


def test_parse_findings_detects_optional_root_question() -> None:
    findings = critical_master.parse_findings(
        "### 1. Audit trail weakens\n\n"
        "- **Impact:** Central logs become incomplete.\n"
        "- **Evidence:** `inference` - no replacement is described.\n"
        "- **Mitigation:** Add a signed attestation.\n"
        "- **Question:** Which audit record replaces CI?\n"
    )

    assert len(findings) == 1
    assert findings[0].has_question
