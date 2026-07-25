import sys
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)
MODULE_PATH = (
    REPO_ROOT
    / ".github/skills/internal-gateway-critical-master/scripts/critical_master.py"
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


def test_parse_critical_card_uses_emoji_as_language_neutral_keys() -> None:
    card = critical_master.parse_critical_card(
        "🎯 **Piano:** Spostare i controlli sui computer locali.\n"
        "⚠️ **Critica:** Perderemmo la prova centrale perché i controlli locali "
        "non producono un registro condiviso.\n"
        "✅ **Consiglio:** Mantenere la CI fino a un sostituto centrale.\n"
    )

    assert tuple(card.by_marker) == ("🎯", "⚠️", "✅")
    assert card.by_marker["⚠️"].content.startswith("Perderemmo")


def test_parse_critical_card_tracks_optional_risk_and_question() -> None:
    card = critical_master.parse_critical_card(
        "🎯 **Plan:** Move validation to developer machines.\n"
        "⚠️ **Critique:** Central proof disappears because local checks are private.\n"
        "💥 **Risk:** Some repositories may silently skip validation.\n"
        "✅ **Advice:** Keep CI until an equivalent central control exists.\n"
        "❓ **Open point:** What officially replaces the CI logs?\n"
    )

    assert tuple(card.by_marker) == ("🎯", "⚠️", "💥", "✅", "❓")
