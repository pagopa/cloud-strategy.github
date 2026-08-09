from __future__ import annotations

from pathlib import Path


REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)
SKILL_DIR = REPO_ROOT / ".github/skills/internal-gateway-critical-master"
SKILL_PATH = SKILL_DIR / "SKILL.md"


def test_critical_bundle_does_not_retain_the_consumer_protocol() -> None:
    assert not (SKILL_DIR / "references/full-analysis-contract.md").exists()
    assert not (SKILL_DIR / "scripts/full_analysis.py").exists()
