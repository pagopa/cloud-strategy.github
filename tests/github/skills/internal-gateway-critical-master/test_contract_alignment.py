import re
import sys
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)

BUNDLE = REPO_ROOT / ".github/skills/internal-gateway-critical-master"

MODULE_PATH = BUNDLE / "scripts/critical_master.py"
MODULE_SPEC = spec_from_file_location("critical_master_cm", MODULE_PATH)
assert MODULE_SPEC is not None and MODULE_SPEC.loader is not None
critical_master = module_from_spec(MODULE_SPEC)
sys.modules[MODULE_SPEC.name] = critical_master
MODULE_SPEC.loader.exec_module(critical_master)


def _load_text(relative_path: str) -> str:
    return (BUNDLE / relative_path).read_text(encoding="utf-8")


SKILL_TEXT = _load_text("SKILL.md")
CONTRACT_TEXT = _load_text("references/output-contract.md")
AGENT_YAML = _load_text("agents/openai.yaml")
FIXTURE_TEXT = _load_text("fixtures/critical_output_valid.md")

EXPECTED_OUTCOMES = {
    "reformulate-plan",
    "de-escalate-to-simple",
    "route-to-execution-owner",
    "review-evidence",
    "continue-critical-with-new-evidence",
    "accept-with-risk",
}


def test_skill_requires_exactly_three_lenses() -> None:
    assert "Select exactly **three lenses**" in SKILL_TEXT


def test_skill_requires_lateral_third_lens() -> None:
    assert "lens three must be lateral" in SKILL_TEXT.lower()


def test_contract_contains_challenge_context_section() -> None:
    assert "## Challenge Context" in CONTRACT_TEXT


def test_contract_contains_premortem_status_field() -> None:
    assert "**Pre-mortem:** `not-triggered`" in CONTRACT_TEXT


def test_contract_contains_defense_field() -> None:
    assert "**Defense:** `none`" in CONTRACT_TEXT


def test_agent_yaml_does_not_duplicate_lens_count() -> None:
    assert "2-3 lenses" not in AGENT_YAML


def test_allowed_outcomes_match_expected_set() -> None:
    assert critical_master.ALLOWED_OUTCOMES == frozenset(EXPECTED_OUTCOMES)


def test_skill_contains_route_to_execution_owner() -> None:
    assert "`route-to-execution-owner`" in SKILL_TEXT


def test_skill_contains_continue_critical_with_new_evidence() -> None:
    assert "`continue-critical-with-new-evidence`" in SKILL_TEXT


def test_skill_outcome_table_matches_allowed_outcomes() -> None:
    table_rows = re.findall(
        r"^\|\s*`([^`]+)`\s*\|", SKILL_TEXT, re.MULTILINE
    )
    outcome_values = {
        row.strip() for row in table_rows if row.strip() in {
            "reformulate-plan",
            "de-escalate-to-simple",
            "route-to-execution-owner",
            "review-evidence",
            "continue-critical-with-new-evidence",
            "accept-with-risk",
            "execute-clear-next-step",
            "continue-critical",
        }
    }
    assert outcome_values == EXPECTED_OUTCOMES


def test_fixture_contains_challenge_context() -> None:
    assert "## Challenge Context" in FIXTURE_TEXT


def test_fixture_contains_evidence_quality() -> None:
    assert "quality=" in FIXTURE_TEXT


def test_fixture_contains_defense_metadata() -> None:
    assert "**Defense:**" in FIXTURE_TEXT


def test_fixture_does_not_contain_old_outcomes() -> None:
    assert "execute-clear-next-step" not in FIXTURE_TEXT
    assert "continue-critical`" not in FIXTURE_TEXT


def _load_routing_cases() -> list[dict]:
    import json
    path = BUNDLE / "fixtures/routing_cases.json"
    return json.loads(path.read_text(encoding="utf-8"))


def test_routing_case_ids_are_unique() -> None:
    cases = _load_routing_cases()
    ids = [c["id"] for c in cases]
    assert len(ids) == len(set(ids))


def test_routing_cases_have_non_empty_prompts() -> None:
    cases = _load_routing_cases()
    for case in cases:
        assert case["prompt"].strip()


def test_routing_cases_cover_expected_owners() -> None:
    cases = _load_routing_cases()
    owners = {c["expected_owner"] for c in cases}
    assert "internal-gateway-critical-master" in owners
    assert "internal-gateway-idea" in owners
    assert "internal-gateway-simple-task" in owners


def test_critical_master_description_leads_with_challenge() -> None:
    import re
    frontmatter_match = re.search(r"^description:\s*(.+)$", SKILL_TEXT, re.MULTILINE)
    assert frontmatter_match is not None
    description = frontmatter_match.group(1).strip().lower()
    assert "critical challenge" in description
    assert "before action" in description
