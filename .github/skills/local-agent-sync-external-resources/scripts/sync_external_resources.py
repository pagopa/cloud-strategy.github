"""Manifest-driven CLI for auditing, planning, and applying external resource syncs."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal, Sequence

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, SCRIPT_DIR.as_posix())

from sync_external_resources_core import (  # noqa: E402
    ManagedResources,
    OverrideResult,
    SyncCommandError,
    find_dirty_targets,
    load_managed_resources,
    load_overrides,
    materialize_candidate,
    normalize_candidate,
    replay_overrides,
    validate_external_workspace,
)

DEFAULT_MANIFEST = (
    SCRIPT_DIR.parent / "references" / "managed-resources.yaml"
).as_posix()
DEFAULT_OVERRIDES = (
    SCRIPT_DIR.parent / "references" / "imported-asset-overrides.yaml"
).as_posix()


@dataclass(frozen=True)
class SyncOutcome:
    mode: Literal["audit", "plan", "apply"]
    workspace: str | None
    managed_assets: int
    changed_paths: tuple[str, ...]
    override_results: tuple[OverrideResult, ...]
    validations: tuple[str, ...]
    blockers: tuple[str, ...]
    repository_changed: bool

    def to_dict(self) -> dict[str, object]:
        return {
            "mode": self.mode,
            "workspace": self.workspace,
            "managed_assets": self.managed_assets,
            "changed_paths": list(self.changed_paths),
            "override_results": [
                {
                    "override_id": r.override_id,
                    "status": r.status,
                    "target_path": r.target_path,
                }
                for r in self.override_results
            ],
            "validations": list(self.validations),
            "blockers": list(self.blockers),
            "repository_changed": self.repository_changed,
        }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Audit, plan, or apply declared external resource refreshes."
    )
    parser.add_argument("mode", choices=("audit", "plan", "apply"))
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--workspace")
    parser.add_argument("--manifest", default=DEFAULT_MANIFEST)
    parser.add_argument("--overrides", default=DEFAULT_OVERRIDES)
    parser.add_argument(
        "--source-root",
        help="Use prepared source checkouts instead of network fetch.",
    )
    parser.add_argument("--allow-dirty", action="store_true")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    return parser


def _run_git(repo_root: Path, args: list[str]) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        ["git", *args],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
        timeout=60,
    )
    if result.returncode != 0:
        raise SyncCommandError(["git", *args], result.returncode, result.stderr)
    return result


def _build_candidate_patch(
    repo_root: Path, candidate: Path, resources: ManagedResources
) -> str:
    diff_result = subprocess.run(
        ["git", "diff", "--no-index", "--", "."],
        cwd=candidate,
        check=False,
        capture_output=True,
        text=True,
    )
    return diff_result.stdout


def _apply_candidate_patch(repo_root: Path, patch_text: str) -> bool:
    if not patch_text.strip():
        return False
    result = subprocess.run(
        ["git", "apply", "--check", "-"],
        cwd=repo_root,
        input=patch_text,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise ValueError(f"Patch check failed: {result.stderr[:500]}")
    subprocess.run(
        ["git", "apply", "-"],
        cwd=repo_root,
        input=patch_text,
        check=True,
        capture_output=True,
        text=True,
    )
    return True


def _audit(
    repo_root: Path,
    resources: ManagedResources,
    overrides_path: Path,
) -> SyncOutcome:
    blockers: list[str] = []
    dirty = find_dirty_targets(repo_root, resources.assets)
    if dirty:
        blockers.append(f"dirty managed targets: {', '.join(dirty)}")

    overrides = load_overrides(overrides_path) if overrides_path.exists() else ()

    return SyncOutcome(
        mode="audit",
        workspace=None,
        managed_assets=len(resources.assets),
        changed_paths=(),
        override_results=(),
        validations=("manifest-parsed", "overrides-parsed"),
        blockers=tuple(blockers),
        repository_changed=False,
    )


def _plan(
    repo_root: Path,
    workspace: Path,
    resources: ManagedResources,
    overrides_path: Path,
    source_root: Path | None,
) -> SyncOutcome:
    validate_external_workspace(repo_root, workspace)

    candidate = workspace / "candidate"
    materialize_candidate(resources, workspace, candidate)
    changed = normalize_candidate(resources, candidate)

    overrides = load_overrides(overrides_path) if overrides_path.exists() else ()
    override_results = replay_overrides(candidate, overrides, overrides_path.parent.parent) if overrides else ()

    return SyncOutcome(
        mode="plan",
        workspace=str(workspace),
        managed_assets=len(resources.assets),
        changed_paths=tuple(changed),
        override_results=override_results,
        validations=("candidate-built", "normalized", "overrides-replayed"),
        blockers=(),
        repository_changed=False,
    )


def _apply(
    repo_root: Path,
    workspace: Path,
    resources: ManagedResources,
    overrides_path: Path,
    source_root: Path | None,
    allow_dirty: bool,
) -> SyncOutcome:
    validate_external_workspace(repo_root, workspace)

    dirty = find_dirty_targets(repo_root, resources.assets)
    if dirty and not allow_dirty:
        return SyncOutcome(
            mode="apply",
            workspace=str(workspace),
            managed_assets=len(resources.assets),
            changed_paths=(),
            override_results=(),
            validations=(),
            blockers=(f"dirty managed targets: {', '.join(dirty)}",),
            repository_changed=False,
        )

    candidate = workspace / "candidate"
    materialize_candidate(resources, workspace, candidate)
    changed = normalize_candidate(resources, candidate)

    overrides = load_overrides(overrides_path) if overrides_path.exists() else ()
    override_results = replay_overrides(candidate, overrides, overrides_path.parent.parent) if overrides else ()

    patch_text = _build_candidate_patch(repo_root, candidate, resources)
    repository_changed = _apply_candidate_patch(repo_root, patch_text)

    return SyncOutcome(
        mode="apply",
        workspace=str(workspace),
        managed_assets=len(resources.assets),
        changed_paths=tuple(changed),
        override_results=override_results,
        validations=("candidate-built", "normalized", "overrides-replayed", "patch-applied"),
        blockers=(),
        repository_changed=repository_changed,
    )


def _format_text(outcome: SyncOutcome) -> str:
    lines = [
        f"Mode: {outcome.mode}",
        f"Workspace: {outcome.workspace or 'n/a'}",
        f"Managed assets: {outcome.managed_assets}",
        f"Changed paths: {len(outcome.changed_paths)}",
        f"Override results: {len(outcome.override_results)}",
        f"Validations: {', '.join(outcome.validations) or 'none'}",
        f"Repository changed: {outcome.repository_changed}",
    ]
    if outcome.blockers:
        lines.append(f"Blockers: {'; '.join(outcome.blockers)}")
    return "\n".join(lines)


def run(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    repo_root = Path(args.repo_root).resolve()
    manifest_path = Path(args.manifest)
    if not manifest_path.is_absolute():
        manifest_path = repo_root / manifest_path
    overrides_path = Path(args.overrides)
    if not overrides_path.is_absolute():
        overrides_path = repo_root / overrides_path

    resources = load_managed_resources(manifest_path)

    if args.mode == "audit":
        outcome = _audit(repo_root, resources, overrides_path)
    elif args.mode == "plan":
        if not args.workspace:
            parser.error("plan mode requires --workspace")
        outcome = _plan(
            repo_root,
            Path(args.workspace).resolve(),
            resources,
            overrides_path,
            Path(args.source_root).resolve() if args.source_root else None,
        )
    elif args.mode == "apply":
        if not args.workspace:
            parser.error("apply mode requires --workspace")
        outcome = _apply(
            repo_root,
            Path(args.workspace).resolve(),
            resources,
            overrides_path,
            Path(args.source_root).resolve() if args.source_root else None,
            args.allow_dirty,
        )
    else:
        parser.error(f"unknown mode: {args.mode}")

    if args.format == "json":
        print(json.dumps(outcome.to_dict(), indent=2))
    else:
        print(_format_text(outcome))

    if outcome.blockers:
        return 2
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    return run(argv)


if __name__ == "__main__":
    sys.exit(main())
