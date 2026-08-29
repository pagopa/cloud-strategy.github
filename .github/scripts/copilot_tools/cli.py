from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Protocol, TypeVar

from .checks.catalog import run_consistency_checks
from .checks.token_risks import detect_token_risks
from .core.output import render_json
from .core.repo_paths import find_repo_root as _find_repo_root


class FindingLike(Protocol):
    severity: str

    def to_dict(self) -> dict[str, object]: ...


FindingT = TypeVar("FindingT", bound=FindingLike)


def find_repo_root(start: Path) -> Path:
    return _find_repo_root(
        start,
        lambda candidate: (
            (candidate / ".github").is_dir() or (candidate / ".git").exists()
        ),
    )


def run_catalog_checks(
    root: Path, *, include_token_risks: bool = False
) -> list[FindingLike]:
    token_risk_detector = detect_token_risks if include_token_risks else None
    return run_consistency_checks(
        root,
        include_token_risks=include_token_risks,
        token_risk_detector=token_risk_detector,
    )


def run_finding_cli(
    *,
    detect_fn: Callable[[], list[FindingT]],
    format_name: str,
    render_text: Callable[[list[FindingT]], None],
    compact_builder: Callable[[list[FindingT]], dict[str, object]] | None = None,
) -> list[FindingT]:
    findings = detect_fn()
    if format_name == "json":
        print(render_json([finding.to_dict() for finding in findings]))
    elif format_name == "compact":
        if compact_builder is None:
            raise ValueError("compact output requires a compact_builder")
        print(render_json(compact_builder(findings)))
    else:
        render_text(findings)
    return findings


def has_severity(findings: list[FindingLike], severity: str) -> bool:
    return any(finding.severity == severity for finding in findings)


def should_fail(
    findings: list[FindingLike],
    *,
    strict: bool = False,
    blocking_severity: str | None = "blocking",
) -> bool:
    if blocking_severity is not None and has_severity(findings, blocking_severity):
        return True
    return strict and bool(findings)
