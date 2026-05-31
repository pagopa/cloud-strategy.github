#!/usr/bin/env python3
"""Bisync skills between source .github/skills/ and home ~/.agents/skills/ using hash+mtime resolution.

Standalone operation:
  python3 bisync_skills.py plan --source-root /repo --home-root /home/user
  python3 bisync_skills.py apply --source-root /repo --home-root /home/user

Importable for CLI integration:
  from bisync_skills import build_bisync_plan, apply_bisync_plan
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

IGNORED_SYNC_PARTS: tuple[str, ...] = (".venv", "__pycache__", ".pytest_cache")
IGNORED_SYNC_SUFFIXES: tuple[str, ...] = (".pyc", ".pyo")
EXCLUDED_BUNDLE_PREFIX: str = "local-agent-sync-"


def should_ignore(path: Path) -> bool:
    return (
        any(part in IGNORED_SYNC_PARTS for part in path.parts)
        or path.suffix in IGNORED_SYNC_SUFFIXES
    )


def should_ignore_copytree(directory: str, names: list[str]) -> set[str]:
    base = Path(directory)
    ignored: set[str] = set()
    for name in names:
        candidate = base / name
        if candidate.is_dir():
            if name in IGNORED_SYNC_PARTS:
                ignored.add(name)
        elif candidate.is_file():
            if Path(name).suffix in IGNORED_SYNC_SUFFIXES:
                ignored.add(name)
    return ignored


def get_max_mtime(directory: Path) -> float:
    max_time = 0.0
    for path in directory.rglob("*"):
        if path.is_file() and not should_ignore(path):
            max_time = max(max_time, path.stat().st_mtime)
    return max_time


def hash_bundle(directory: Path) -> str:
    files: list[dict[str, str]] = []
    for path in sorted(directory.rglob("*")):
        if path.is_file() and not should_ignore(path):
            rel = path.relative_to(directory).as_posix()
            content = path.read_bytes()
            files.append({"path": rel, "hash": hashlib.sha256(content).hexdigest()[:16]})
    return hashlib.sha256(json.dumps(files, sort_keys=True).encode()).hexdigest()


def is_repo_clean(source_root: Path) -> tuple[bool, str, str]:
    result = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=all"],
        cwd=source_root,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return False, "bisync-repo-git-failed", "Unable to run git status before bisync apply."
    if result.stdout.strip():
        return (
            False,
            "bisync-repo-dirty",
            "Repository has uncommitted or untracked changes.",
        )
    return True, "", ""


def compute_next_action(
    blocked_codes: list[str],
    has_drift_items: bool,
    mode: str,
    source_root: Path,
    home_root: Path,
) -> dict:
    if mode == "plan":
        if blocked_codes:
            return {
                "action": "resolve_blockers",
                "allowed": False,
                "requires_explicit_approval": True,
                "command": "",
                "reason": "Blocked codes prevent apply. Resolve each blocker manually.",
            }
        if has_drift_items:
            return {
                "action": "apply",
                "allowed": True,
                "requires_explicit_approval": True,
                "command": f"bisync apply --source-root {source_root} --home-root {home_root}",
                "reason": "Plan shows resolvable drift. Apply copies winner to loser for each drifted skill.",
            }
        return {
            "action": "done",
            "allowed": False,
            "requires_explicit_approval": False,
            "command": "",
            "reason": "No drift detected. Source and home are in sync.",
        }
    if mode == "apply":
        if blocked_codes:
            return {
                "action": "resolve_blockers",
                "allowed": False,
                "requires_explicit_approval": True,
                "command": "",
                "reason": "Blocked codes remain after apply. Manual resolution required.",
            }
        return {
            "action": "done",
            "allowed": False,
            "requires_explicit_approval": False,
            "command": "",
            "reason": "Bisync completed. Source and home are converged.",
        }
    return {
        "action": "unknown",
        "allowed": False,
        "requires_explicit_approval": True,
        "command": "",
        "reason": f"Unknown mode: {mode}",
    }


@dataclass
class BisyncDriftEntry:
    skill_name: str
    drift_type: str
    direction: str | None = None
    repo_path: str = ""
    home_path: str = ""
    repo_hash: str = ""
    home_hash: str = ""
    repo_mtime: float = 0.0
    home_mtime: float = 0.0
    blocked_codes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        result: dict = {
            "skill": self.skill_name,
            "type": self.drift_type,
            "repo": self.repo_path,
            "home": self.home_path,
        }
        if self.direction:
            result["direction"] = self.direction
        if self.blocked_codes:
            result["blocked_codes"] = self.blocked_codes
        return result


@dataclass
class BisyncPlan:
    source_root: Path
    home_root: Path
    source_skills_root: Path
    home_skills_root: Path
    mode: str
    drifts: list[BisyncDriftEntry] = field(default_factory=list)
    blocked_codes: list[str] = field(default_factory=list)
    next_step: str = ""
    next_action: dict = field(default_factory=dict)
    verification: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "mode": self.mode,
            "source_root": self.source_root.as_posix(),
            "home_root": self.home_root.as_posix(),
            "source_skills_root": self.source_skills_root.as_posix(),
            "home_skills_root": self.home_skills_root.as_posix(),
            "drifts": [d.to_dict() for d in self.drifts],
            "blocked_codes": self.blocked_codes,
            "next_step": self.next_step,
            "next_action": self.next_action,
            "verification": self.verification,
        }


def build_bisync_plan(
    source_root: Path,
    home_root: Path,
    *,
    mode: str = "plan",
) -> BisyncPlan:
    source_skills = source_root / ".github" / "skills"
    home_skills = home_root / ".agents" / "skills"

    blocked_codes: list[str] = []
    if not source_skills.exists() or not source_skills.is_dir():
        blocked_codes.append("bisync-source-missing")

    root_check = (
        _root_check(source_skills, "bisync-source-missing")
        if source_skills.exists()
        else []
    )
    blocked_codes.extend(root_check)

    if not home_skills.exists() or not home_skills.is_dir():
        blocked_codes.append("bisync-home-missing")

    root_check_home = (
        _root_check(home_skills, "bisync-home-missing")
        if home_skills.exists()
        else []
    )
    blocked_codes.extend(root_check_home)

    drifts: list[BisyncDriftEntry] = []
    if blocked_codes:
        plan = BisyncPlan(
            source_root=source_root,
            home_root=home_root,
            source_skills_root=source_skills,
            home_skills_root=home_skills,
            mode=mode,
            blocked_codes=sorted(set(blocked_codes)),
        )
        plan.next_step = _next_step_for_bisync(plan)
        plan.next_action = compute_next_action(
            plan.blocked_codes, bool(plan.drifts), mode, source_root, home_root
        )
        return plan

    repo_names = {
        p.name
        for p in source_skills.iterdir()
        if p.is_dir() and not p.name.startswith(EXCLUDED_BUNDLE_PREFIX)
    }
    home_names = {
        p.name
        for p in home_skills.iterdir()
        if p.is_dir() and not p.name.startswith(EXCLUDED_BUNDLE_PREFIX)
    }
    all_names = sorted(repo_names | home_names)

    for skill_name in all_names:
        repo_path = source_skills / skill_name
        home_path = home_skills / skill_name
        in_repo = skill_name in repo_names
        in_home = skill_name in home_names

        if in_repo and not in_home:
            drifts.append(
                BisyncDriftEntry(
                    skill_name=skill_name,
                    drift_type="only-repo",
                    repo_path=repo_path.as_posix(),
                    home_path=home_path.as_posix(),
                    blocked_codes=["bisync-only-repo"],
                )
            )
            continue

        if in_home and not in_repo:
            drifts.append(
                BisyncDriftEntry(
                    skill_name=skill_name,
                    drift_type="only-home",
                    repo_path=repo_path.as_posix(),
                    home_path=home_path.as_posix(),
                    blocked_codes=["bisync-only-home"],
                )
            )
            continue

        repo_hash = hash_bundle(repo_path)
        home_hash = hash_bundle(home_path)

        if repo_hash == home_hash:
            continue

        repo_mtime = get_max_mtime(repo_path)
        home_mtime = get_max_mtime(home_path)

        if repo_mtime > home_mtime:
            drifts.append(
                BisyncDriftEntry(
                    skill_name=skill_name,
                    drift_type="drift",
                    direction="repo-to-home",
                    repo_path=repo_path.as_posix(),
                    home_path=home_path.as_posix(),
                    repo_hash=repo_hash,
                    home_hash=home_hash,
                    repo_mtime=repo_mtime,
                    home_mtime=home_mtime,
                )
            )
        elif home_mtime > repo_mtime:
            drifts.append(
                BisyncDriftEntry(
                    skill_name=skill_name,
                    drift_type="drift",
                    direction="home-to-repo",
                    repo_path=repo_path.as_posix(),
                    home_path=home_path.as_posix(),
                    repo_hash=repo_hash,
                    home_hash=home_hash,
                    repo_mtime=repo_mtime,
                    home_mtime=home_mtime,
                )
            )
        else:
            drifts.append(
                BisyncDriftEntry(
                    skill_name=skill_name,
                    drift_type="equal-mtime",
                    repo_path=repo_path.as_posix(),
                    home_path=home_path.as_posix(),
                    repo_hash=repo_hash,
                    home_hash=home_hash,
                    repo_mtime=repo_mtime,
                    home_mtime=home_mtime,
                    blocked_codes=["bisync-equal-mtime"],
                )
            )

    all_blocked = sorted(
        set(
            code
            for d in drifts
            for code in d.blocked_codes
        )
    )

    plan = BisyncPlan(
        source_root=source_root,
        home_root=home_root,
        source_skills_root=source_skills,
        home_skills_root=home_skills,
        mode=mode,
        drifts=drifts,
        blocked_codes=all_blocked,
    )
    plan.next_step = _next_step_for_bisync(plan)
    plan.next_action = compute_next_action(
        plan.blocked_codes, bool(plan.drifts), mode, source_root, home_root
    )
    plan.verification = {
        "status": "ok" if not all_blocked else "blocked",
        "total_drifts": len(drifts),
    }
    return plan


def apply_bisync_plan(
    source_root: Path,
    home_root: Path,
    plan: BisyncPlan,
) -> BisyncPlan:
    if plan.blocked_codes:
        return plan

    clean, blocked_code, reason = is_repo_clean(source_root)
    if not clean:
        plan.blocked_codes = [blocked_code]
        plan.mode = "apply"
        plan.next_step = "Repository is not clean. Bisync apply is blocked. Commit or stash changes."
        plan.next_action = {
            "action": "resolve_blockers",
            "allowed": False,
            "requires_explicit_approval": True,
            "command": "",
            "reason": reason,
        }
        plan.verification = {
            "status": "blocked",
            "code": blocked_code,
            "reason": reason,
        }
        return plan

    drifts_to_resolve = [d for d in plan.drifts if d.drift_type == "drift"]
    for drift in drifts_to_resolve:
        if drift.direction == "repo-to-home":
            src = Path(drift.repo_path)
            dst = Path(drift.home_path)
        elif drift.direction == "home-to-repo":
            src = Path(drift.home_path)
            dst = Path(drift.repo_path)
        else:
            continue

        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(src, dst, ignore=should_ignore_copytree)

        actual_hash = hash_bundle(dst)
        expected_hash = (
            drift.repo_hash
            if drift.direction == "repo-to-home"
            else drift.home_hash
        )
        if actual_hash != expected_hash:
            plan.blocked_codes.append("bisync-verify-failed")
            plan.blocked_codes = sorted(set(plan.blocked_codes))
            plan.verification = {
                "status": "blocked",
                "code": "bisync-verify-failed",
                "skill": drift.skill_name,
                "reason": f"Post-copy hash mismatch for {drift.skill_name}",
            }
            plan.next_step = _next_step_for_bisync(plan)
            plan.next_action = compute_next_action(
                plan.blocked_codes, bool(plan.drifts), "apply", source_root, home_root
            )
            return plan

    post_plan = build_bisync_plan(source_root, home_root, mode="verify")
    if post_plan.drifts or post_plan.blocked_codes:
        plan.blocked_codes.extend(post_plan.blocked_codes)
        if post_plan.drifts:
            plan.blocked_codes.append("bisync-residual-drift")
        plan.blocked_codes = sorted(set(plan.blocked_codes))
        plan.verification = {
            "status": "blocked",
            "code": "bisync-residual-drift" if post_plan.drifts else "bisync-post-apply-blocked",
            "reason": f"Post-apply drift still detected: {len(post_plan.drifts)} drift(s)",
            "residual_drifts": [d.to_dict() for d in post_plan.drifts],
        }
        plan.next_step = _next_step_for_bisync(plan)
        plan.next_action = compute_next_action(
            plan.blocked_codes,
            bool(post_plan.drifts),
            "apply",
            source_root,
            home_root,
        )
        return plan

    plan.blocked_codes = []
    plan.verification = {
        "status": "converged",
        "reason": "Post-apply plan shows zero drift and zero blockers.",
    }
    plan.mode = "apply"
    plan.next_step = "Bisync apply completed. 0 drift detected."
    plan.next_action = compute_next_action(
        [], False, "apply", source_root, home_root
    )
    return plan


def _next_step_for_bisync(plan: BisyncPlan) -> str:
    if plan.mode == "plan":
        if plan.blocked_codes:
            return "Resolve blocked codes before bisync apply."
        if plan.drifts:
            return "Review the drift plan and run bisync apply when ready."
        return "Source and home are already in sync."
    if plan.mode == "apply":
        if plan.blocked_codes:
            return "Bisync apply blocked. Review blocker codes."
        return "Bisync apply completed. Verify with bisync plan."
    if plan.mode == "verify":
        if plan.drifts or plan.blocked_codes:
            return "Post-apply verification shows residual drift. Manual review required."
        return "Verification passed. Source and home are converged."
    return "Review the generated output."


def _root_check(root: Path, code: str) -> list[str]:
    blocked: list[str] = []
    resolved = root.resolve()
    try:
        if not resolved.is_dir():
            blocked.append(code)
    except (OSError, PermissionError):
        blocked.append(code)
    return blocked


def run_bisync_plan(args: argparse.Namespace) -> int:
    source_root = _resolve_source_root(args)
    home_root = Path(args.home_root).expanduser().resolve()
    plan = build_bisync_plan(source_root, home_root, mode="plan")
    _emit_bisync_output(plan, args.format)
    return 1 if plan.blocked_codes else 0


def run_bisync_apply(args: argparse.Namespace) -> int:
    source_root = _resolve_source_root(args)
    home_root = Path(args.home_root).expanduser().resolve()
    plan = build_bisync_plan(source_root, home_root, mode="plan")
    if plan.blocked_codes:
        _emit_bisync_output(plan, args.format)
        return 1

    result = apply_bisync_plan(source_root, home_root, plan)
    _emit_bisync_output(result, args.format)
    return 1 if result.blocked_codes else 0


def _resolve_source_root(args: argparse.Namespace) -> Path:
    root = Path(args.source_root).resolve()
    if root.name == ".github" and (root / "skills").is_dir():
        return root.parent
    return root


def _emit_bisync_output(plan: BisyncPlan, format_name: str) -> None:
    payload = plan.to_dict()
    if format_name == "json":
        print(json.dumps(payload, indent=2, sort_keys=True))
        return

    if not plan.drifts:
        print("\u2705 No drift detected. Source and home are in sync.")
        return

    print(f"\u2139\ufe0f  Detected {len(plan.drifts)} drift(s):\n")
    for drift in plan.drifts:
        skill = drift.skill_name
        dtype = drift.drift_type
        if dtype in ("only-repo", "only-home"):
            label = "only in repo" if dtype == "only-repo" else "only in home"
            path = drift.repo_path if dtype == "only-repo" else drift.home_path
            print(f"  {skill}: {label} ({path})")
            print(f"    blocker: {', '.join(drift.blocked_codes)}")
        elif dtype == "equal-mtime":
            print(f"  {skill}: equal mtime (hashes differ)")
            print(f"    blocker: {', '.join(drift.blocked_codes)}")
        else:
            print(f"  {skill}: {drift.direction}")
            if drift.direction == "repo-to-home":
                winner, loser = "repo", "home"
            else:
                winner, loser = "home", "repo"
            print(f"    winner: {winner}")

    if plan.blocked_codes:
        print(f"\n\u26a0\ufe0f  Blocked: {', '.join(plan.blocked_codes)}")

    next_step = plan.next_step
    if next_step:
        print(f"\n\u2139\ufe0f  Next: {next_step}")

    next_action = plan.next_action
    if next_action and next_action.get("action") != "done":
        print(f"  Action: {next_action.get('reason', '')}")


def build_bisync_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Bisync skills between source repo and home directory."
    )
    subparsers = parser.add_subparsers(dest="bisync_command", required=True)
    plan_parser = subparsers.add_parser("plan", help="Detect drift without writing")
    plan_parser.add_argument("--source-root", default=".", help="Source repository root.")
    plan_parser.add_argument(
        "--home-root",
        default=str(Path.home()),
        help="Home directory root.",
    )
    plan_parser.add_argument(
        "--format", choices=["text", "json"], default="text", help="Output format."
    )
    apply_parser = subparsers.add_parser("apply", help="Apply bisync resolution")
    apply_parser.add_argument("--source-root", default=".", help="Source repository root.")
    apply_parser.add_argument(
        "--home-root",
        default=str(Path.home()),
        help="Home directory root.",
    )
    apply_parser.add_argument(
        "--format", choices=["text", "json"], default="text", help="Output format."
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_bisync_parser()
    args = parser.parse_args(argv)
    if args.bisync_command == "plan":
        raise SystemExit(run_bisync_plan(args))
    elif args.bisync_command == "apply":
        raise SystemExit(run_bisync_apply(args))


if __name__ == "__main__":
    main()
