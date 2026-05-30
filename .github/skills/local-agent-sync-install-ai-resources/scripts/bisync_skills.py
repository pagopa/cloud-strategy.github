#!/usr/bin/env python3
"""Bisync skills between .github/skills/ and ~/.agents/skills/ using mtime resolution."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from datetime import datetime
from pathlib import Path

IGNORED_SYNC_PARTS: tuple[str, ...] = (".venv", "__pycache__", ".pytest_cache")
IGNORED_SYNC_SUFFIXES: tuple[str, ...] = (".pyc", ".pyo")
REPO_SKILLS = Path(".github/skills")
HOME_SKILLS = Path.home() / ".agents" / "skills"


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


def detect_drift() -> list[dict]:
    drifts: list[dict] = []
    repo_skills = {p.name for p in REPO_SKILLS.iterdir() if p.is_dir()}
    home_skills = {p.name for p in HOME_SKILLS.iterdir() if p.is_dir()}
    all_skills = repo_skills | home_skills

    for skill_name in sorted(all_skills):
        repo_path = REPO_SKILLS / skill_name
        home_path = HOME_SKILLS / skill_name

        if not home_path.exists():
            drifts.append({"skill": skill_name, "type": "only-repo", "repo": repo_path, "home": home_path})
            continue
        if not repo_path.exists():
            drifts.append({"skill": skill_name, "type": "only-home", "repo": repo_path, "home": home_path})
            continue

        repo_hash = hash_bundle(repo_path)
        home_hash = hash_bundle(home_path)

        if repo_hash == home_hash:
            continue

        repo_mtime = get_max_mtime(repo_path)
        home_mtime = get_max_mtime(home_path)

        if repo_mtime > home_mtime:
            direction = "repo-to-home"
            winner = "repo"
            winner_time = datetime.fromtimestamp(repo_mtime)
            loser_time = datetime.fromtimestamp(home_mtime)
        else:
            direction = "home-to-repo"
            winner = "home"
            winner_time = datetime.fromtimestamp(home_mtime)
            loser_time = datetime.fromtimestamp(repo_mtime)

        drifts.append({
            "skill": skill_name,
            "type": "drift",
            "direction": direction,
            "winner": winner,
            "winner_time": winner_time,
            "loser_time": loser_time,
            "repo": repo_path,
            "home": home_path,
        })

    return drifts


def plan() -> None:
    drifts = detect_drift()

    if not drifts:
        print("\u2705 No drift detected. Repo and home are in sync.")
        return

    print(f"\u2139\ufe0f  Detected {len(drifts)} drift(s):\n")

    for drift in drifts:
        skill = drift["skill"]
        dtype = drift["type"]

        if dtype == "only-repo":
            print(f"  {skill}: only in repo ({drift['repo']})")
        elif dtype == "only-home":
            print(f"  {skill}: only in home ({drift['home']})")
        else:
            direction = drift["direction"]
            winner = drift["winner"]
            winner_time = drift["winner_time"].strftime("%Y-%m-%d %H:%M:%S")
            loser_time = drift["loser_time"].strftime("%Y-%m-%d %H:%M:%S")
            print(f"  {skill}: {direction}")
            print(f"    winner: {winner} ({winner_time})")
            print(f"    loser:  {loser_time}")

    print(f"\n\u2139\ufe0f  Run with 'apply' to resolve drifts.")


def apply() -> None:
    drifts = detect_drift()

    if not drifts:
        print("\u2705 No drift detected. Nothing to apply.")
        return

    applied = 0
    for drift in drifts:
        skill = drift["skill"]
        dtype = drift["type"]

        if dtype in {"only-repo", "only-home"}:
            print(f"\u26a0\ufe0f  {skill}: {dtype}, skipping (manual action required)")
            continue

        direction = drift["direction"]
        if direction == "repo-to-home":
            src = Path(drift["repo"])
            dst = Path(drift["home"])
        else:
            src = Path(drift["home"])
            dst = Path(drift["repo"])

        if dst.exists():
            shutil.rmtree(dst)

        shutil.copytree(src, dst, ignore=should_ignore_copytree)
        print(f"\u2705 {skill}: {direction}")
        applied += 1

    print(f"\n\u2139\ufe0f  Applied {applied} bisync operation(s).")


def main() -> None:
    parser = argparse.ArgumentParser(description="Bisync skills between repo and home.")
    parser.add_argument("command", choices=["plan", "apply"], help="Command to execute")
    args = parser.parse_args()

    if args.command == "plan":
        plan()
    elif args.command == "apply":
        apply()


if __name__ == "__main__":
    main()
