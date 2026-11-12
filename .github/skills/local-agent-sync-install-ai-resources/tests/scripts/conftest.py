import sys
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path

import pytest
import yaml

REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)
SCRIPT_DIR = REPO_ROOT / ".github/skills/local-agent-sync-install-ai-resources/scripts"
REFS_RELATIVE = Path(".github/skills/local-agent-sync-install-ai-resources/references")
if SCRIPT_DIR.as_posix() not in sys.path:
    sys.path.insert(0, SCRIPT_DIR.as_posix())

from home_syncing import HomeSyncPlan  # noqa: E402
from sync_home_ai_resources import parse_args, run  # noqa: E402

DEFAULT_CATALOG_DEFAULTS: dict[str, object] = {
    "include_internal_skills": True,
    "include_local_skills": False,
    "include_unlisted_skills": True,
    "unmanaged_existing_skills_policy": "repo-wins",
    "excluded_skills": [],
    "skill_targets": ["codex"],
}
DEFAULT_MATRIX_ROW: dict[str, object] = {
    "support_level": "Documented",
    "direct_copy_possible": True,
    "translation_required": False,
    "include_in_v1": True,
    "evidence": [],
    "notes": "test",
}


@pytest.fixture(scope="session")
def repo_root() -> Path:
    return REPO_ROOT


@pytest.fixture(scope="session")
def script_dir() -> Path:
    return SCRIPT_DIR


@pytest.fixture
def write_refs() -> Callable[..., Path]:
    # `defaults`/`rows` merge over the module defaults; `catalog_text` writes raw YAML.
    def _write(
        root: Path,
        *,
        defaults: Mapping[str, object] | None = None,
        resources: Sequence[Mapping[str, object]] = (),
        rows: Sequence[Mapping[str, object]] | None = None,
        catalog_text: str | None = None,
    ) -> Path:
        refs = root / REFS_RELATIVE
        refs.mkdir(parents=True, exist_ok=True)
        if catalog_text is None:
            catalog_text = yaml.safe_dump(
                {
                    "version": 1,
                    "defaults": {**DEFAULT_CATALOG_DEFAULTS, **(defaults or {})},
                    "resources": [dict(resource) for resource in resources],
                },
                sort_keys=False,
            )
        (refs / "home-sync-catalog.yaml").write_text(catalog_text, encoding="utf-8")
        if rows is not None:
            (refs / "runtime-support-matrix.yaml").write_text(
                yaml.safe_dump(
                    {
                        "version": 1,
                        "rows": [{**DEFAULT_MATRIX_ROW, **row} for row in rows],
                    },
                    sort_keys=False,
                ),
                encoding="utf-8",
            )
        return refs

    return _write


@pytest.fixture
def make_plan(tmp_path: Path) -> Callable[..., HomeSyncPlan]:
    def _make(**overrides: object) -> HomeSyncPlan:
        fields: dict[str, object] = {
            "source_root": tmp_path,
            "home_root": tmp_path / "home",
            "state_root": tmp_path / "state",
            "mode": "apply",
            "selected_targets": ("skills",),
            "retired_targets": (),
            "source_revision": "abc",
            "source_resources_considered": 0,
            "operations": (),
            "desired_resources": (),
            "missing_dirs": (),
            "unsupported_families_by_target": {},
            "residual_drift": (),
        }
        fields.update(overrides)
        return HomeSyncPlan(**fields)

    return _make


@pytest.fixture
def run_cli() -> Callable[..., int]:
    def _run(*argv: object) -> int:
        return run(parse_args([str(arg) for arg in argv]))

    return _run


@pytest.fixture
def demo_skill(tmp_path: Path) -> Path:
    skill_dir = tmp_path / ".github/skills/demo"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text("# demo\n", encoding="utf-8")
    return skill_dir
