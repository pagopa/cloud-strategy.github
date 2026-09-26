from __future__ import annotations

import json
import re
from pathlib import Path

import pytest
import yaml

BUNDLE = Path(__file__).resolve().parents[1]
SKILL = "SKILL.md"
LEDGER = "references/decision-ledger.md"
CANDIDATE = "references/candidate-and-persistence.md"
PERSISTENCE = "references/persistence.md"
AUTHORING = "references/artifact-authoring.md"

CANDIDATE_PATH = (SKILL, LEDGER, CANDIDATE)
SAVE_PATH = (*CANDIDATE_PATH, PERSISTENCE)
SPEC_PATH = (*SAVE_PATH, AUTHORING)

# Dedupe-only baseline (2026-09-26): 2471 / 3089 / 3645 words before, ~1820 / 2250 / 2580 after.
WORD_BUDGETS = {
    "candidate": (CANDIDATE_PATH, 1850),
    "save": (SAVE_PATH, 2300),
    "spec": (SPEC_PATH, 2650),
}

MENU_LABELS = (
    "🔄 continue",
    "🔍 critical review",
    "🧩 realign when findings exist",
    "📝 +spec",
    "🗺️ +plan",
    "💾 save",
    "⏹️ close",
)

CANDIDATE_INVARIANTS = (
    *MENU_LABELS,
    "analysis-only",
    "GRILL-ME",
    "CRITICAL REVIEW",
    "/grill-me",
    "/internal-gateway-critical-master",
    "/internal-tdd",
    "/internal-gateway-writing-plans",
    "/internal-gateway-execute-plans",
    "route_contract",
    "subject-change",
    "mode-change",
    "Implementation permission",
    "Authorized paths",
    "Authorized actions",
    "authority-or-scope",
    "accepted-risk",
    "fail closed",
    "blocking-now",
    "acceptance-required",
    "follow-up",
    "separate-design",
    "rejected-with-reason",
    "`integrate`",
    "`reject`",
    "`accept-risk`",
    "`route`",
    "analogy",
    "reverse-assumption",
    "Facts",
    "Reports",
    "Assumptions",
    "Unknowns",
    "Constraints",
    "eligible-now",
    "blocked-later",
    "resolved-from-evidence",
    "plan_authoring_ready: true",
    "critical_review: pending",
    "Specific critical focus",
    "Rejected alternatives",
    "Disconfirming signals",
    "Decision ID",
)

SAVE_INVARIANTS = (
    "unit_lock",
    "state_capsule",
    "decision_ledger",
    "authority_envelope",
    "communication_projection",
    "global_gates",
    "gate_override",
    "diagnostic word count",
    "Resume from here",
    "tmp/superpowers/specs/YYYY-MM-DD-<topic>-analysis.md",
    "does not close the review gate",
)

SPEC_INVARIANTS = (
    "delegation.mode: none",
    "worker: primary-owner",
    "result: not_applicable",
    "value gate",
    "/internal-subagent-contract",
    "internal-luna-executor",
    "DelegationBrief",
    "LifecycleRecord",
    "no-Git-mutation",
)

STALE_PATTERNS = (
    r"four-option",
    r"\boptions? [12]\b",
    r"Save the analysis",
    r"Accept as the Consolidated",
    r"\bAUTH-\d+",
)


def _read(relative: str) -> str:
    return (BUNDLE / relative).read_text(encoding="utf-8")


def _joined(paths: tuple[str, ...]) -> str:
    return "\n".join(_read(path) for path in paths)


def _bundle_text_files() -> list[Path]:
    return sorted(
        path
        for path in BUNDLE.rglob("*")
        if path.is_file()
        and path.suffix in {".md", ".yaml", ".yml"}
        and "tests" not in path.relative_to(BUNDLE).parts
    )


@pytest.mark.parametrize("path_name", sorted(WORD_BUDGETS))
def test_loaded_words_per_phase_stay_within_budget(path_name: str) -> None:
    paths, budget = WORD_BUDGETS[path_name]
    words = len(_joined(paths).split())
    assert words <= budget, f"{path_name} path loads {words} words (budget {budget})"


@pytest.mark.parametrize(
    ("paths", "invariants"),
    [
        (CANDIDATE_PATH, CANDIDATE_INVARIANTS),
        (SAVE_PATH, SAVE_INVARIANTS),
        (SPEC_PATH, SPEC_INVARIANTS),
    ],
    ids=["candidate", "save", "spec"],
)
def test_rule_inventory_survives_on_each_path(
    paths: tuple[str, ...], invariants: tuple[str, ...]
) -> None:
    text = " ".join(_joined(paths).split())
    missing = [token for token in invariants if token not in text]
    assert missing == []


def test_seven_entry_menu_is_defined_in_exactly_one_file() -> None:
    owners = [
        path.relative_to(BUNDLE).as_posix()
        for path in _bundle_text_files()
        if "🔄 continue" in path.read_text(encoding="utf-8")
    ]
    assert owners == [SKILL]


def test_no_stale_acceptance_or_undefined_id_references() -> None:
    hits = [
        f"{path.relative_to(BUNDLE).as_posix()}: {pattern}"
        for path in _bundle_text_files()
        for pattern in STALE_PATTERNS
        if re.search(pattern, path.read_text(encoding="utf-8"))
    ]
    assert hits == []


def test_public_default_prompt_is_a_short_pointer() -> None:
    metadata = yaml.safe_load(_read("agents/openai.yaml"))
    words = len(metadata["interface"]["default_prompt"].split())
    assert words <= 120, f"default_prompt has {words} words"


def _anchor(heading: str) -> str:
    slug = re.sub(r"[^\w\- ]", "", heading.strip().lower())
    return slug.replace(" ", "-")


def test_relative_links_and_anchors_resolve() -> None:
    broken = []
    for source in (SKILL, LEDGER, CANDIDATE, PERSISTENCE, AUTHORING):
        for target in re.findall(r"\]\(([^)\s]+)\)", _read(source)):
            if re.match(r"[a-z]+://", target):
                continue
            file_part, _, anchor = target.partition("#")
            resolved = (BUNDLE / source).parent / file_part if file_part else BUNDLE / source
            if not resolved.is_file():
                broken.append(f"{source} -> {target}")
                continue
            if anchor:
                headings = re.findall(r"^#+\s+(.+)$", resolved.read_text(encoding="utf-8"), re.M)
                if anchor not in {_anchor(heading) for heading in headings}:
                    broken.append(f"{source} -> {target}")
    assert broken == []


def test_eval_case_files_exist_in_bundle() -> None:
    manifest = json.loads(_read("tests/evaluation/evals.json"))
    missing = [
        f"{case['id']}: {name}"
        for case in manifest["cases"]
        for name in case.get("files", [])
        if not (BUNDLE / name).is_file()
    ]
    assert missing == []
