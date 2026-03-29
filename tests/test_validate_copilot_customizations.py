from __future__ import annotations

import importlib.util
from importlib.machinery import SourceFileLoader
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = REPO_ROOT / ".github" / "scripts" / "validate-copilot-customizations.sh"


def load_validator_module():
    module_name = "validate_copilot_customizations"
    loader = SourceFileLoader(module_name, str(VALIDATOR_PATH))
    spec = importlib.util.spec_from_loader(module_name, loader)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


VALIDATOR = load_validator_module()


def test_normalize_scope_accepts_root_and_all() -> None:
    assert VALIDATOR.normalize_scope("root") == "root"
    assert VALIDATOR.normalize_scope("all") == "root"


def test_normalize_mode_supports_legacy_alias() -> None:
    assert VALIDATOR.normalize_mode("strict") == "strict"
    assert VALIDATOR.normalize_mode("legacy-compatible") == "basic"


def test_build_report_detects_current_repo_state() -> None:
    report = VALIDATOR.build_report("root", "strict")
    assert isinstance(report.valid, bool)
    assert isinstance(report.errors, list)
