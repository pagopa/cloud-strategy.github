#!/usr/bin/env python3
"""Deterministic bundle-local audit helper for internal-gateway-idea-brainstorming.

Reports file inventory, byte/token estimates, loaded vs on-demand buckets,
required sibling presence, compact contract marker checks, and cross-bundle
consumer contract verification.
The script is read-only and advisory. It does not infer whether a user answer
is correct or which route should win.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ESTIMATED_TOKEN_BYTES = 4

LOADED_FILES = {"SKILL.md"}
ON_DEMAND_DIRS = {"references", "agents", "scripts"}
IGNORE_SUFFIXES = {".pyc", ".pyo"}
IGNORE_DIRS = {"__pycache__"}

REQUIRED_MARKERS: dict[str, str] = {
    "evidence-first-discovery": "Inspect repository evidence first",
    "iterative-question-blocks": "numbered question block",
    "visible-default-acceptance": "visible recommendations as accepted",
    "decision-ledger": "decision ledger",
    "interview-ready-for-critical": "Interview checkpoint: ready-for-critical",
    "interview-reopen": "Interview checkpoint: reopen",
    "handoff-ready-for-owner-change": "Handoff checkpoint: ready-for-owner-change",
    "mandatory-critical-pass": "mandatory critical pass",
    "exactly-one-next-owner": "exactly one next owner",
    "manual-next-owner-confirmation": "Stop and ask for explicit user confirmation before any next-owner transition",
    "chat-only-simple-task-brief": "chat-only `Simple Task Brief`",
    "no-hidden-dispatch": "no hidden dispatch",
}

CROSS_BUNDLE_CHECKS: dict[str, dict[str, str]] = {
    "operational-flow-gate-0-protocol": {
        "relative_path": "internal-gateway-operational-flow/references/gate-0-protocol.md",
        "pattern": "Validated Definition Brief Intake",
        "description": "Consumer gate-0-protocol must define validated-brief intake conditions.",
    },
    "operational-flow-handoff-lock": {
        "relative_path": "internal-gateway-operational-flow/references/gate-0-protocol.md",
        "pattern": "Handoff lock cleared",
        "description": "Consumer gate-0-protocol must require cleared handoff lock for validated intake.",
    },
    "operational-flow-skill": {
        "relative_path": "internal-gateway-operational-flow/SKILL.md",
        "pattern": "validated Definition Brief from",
        "description": "Consumer operational-flow skill must accept validated-brief intake.",
    },
    "grill-me-follow-up-override": {
        "relative_path": "grill-me/SKILL.md",
        "pattern": "caller may override the follow-up pacing",
        "description": "grill-me must support caller-owned follow-up override.",
    },
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Audit idea-gateway bundle shape, contract markers, and cross-bundle consumer contracts."
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail when a required marker, sibling, cross-bundle check, or structural expectation is missing.",
    )
    parser.add_argument(
        "--dir",
        type=Path,
        default=None,
        help="Bundle directory (default: repo-relative parent of this script).",
    )
    return parser.parse_args()


def find_bundle_dir(script_path: Path) -> Path:
    return script_path.resolve().parent.parent


def estimate_tokens(byte_count: int) -> int:
    return (byte_count + ESTIMATED_TOKEN_BYTES - 1) // ESTIMATED_TOKEN_BYTES


def collect_files(bundle_dir: Path) -> list[Path]:
    result: list[Path] = []
    for entry in sorted(bundle_dir.rglob("*")):
        if entry.is_file():
            if entry.suffix in IGNORE_SUFFIXES:
                continue
            if any(part in IGNORE_DIRS for part in entry.parts):
                continue
            result.append(entry)
    return result


def classify_bucket(relative: Path) -> str:
    parts = relative.parts
    if len(parts) == 1 and parts[0] in LOADED_FILES:
        return "loaded"
    if len(parts) >= 2 and parts[0] in ON_DEMAND_DIRS:
        return "on-demand"
    return "other"


def check_markers(skill_text: str) -> dict[str, bool]:
    return {
        key: pattern.lower() in skill_text.lower()
        for key, pattern in REQUIRED_MARKERS.items()
    }


def check_siblings(bundle_dir: Path) -> dict[str, bool]:
    return {
        "agents/openai.yaml": (bundle_dir / "agents" / "openai.yaml").is_file(),
    }


def check_cross_bundle(bundle_dir: Path) -> dict[str, dict]:
    skills_dir = bundle_dir.parent
    results: dict[str, dict] = {}
    for check_id, spec in CROSS_BUNDLE_CHECKS.items():
        target = skills_dir / spec["relative_path"]
        present = target.is_file()
        found = False
        if present:
            text = target.read_text(encoding="utf-8")
            found = spec["pattern"].lower() in text.lower()
        results[check_id] = {
            "file": spec["relative_path"],
            "description": spec["description"],
            "file_present": present,
            "pattern_found": found,
            "pass": present and found,
        }
    return results


def build_report(bundle_dir: Path) -> dict:
    all_files = collect_files(bundle_dir)
    files_detail: list[dict] = []
    totals: dict[str, int] = {"loaded": 0, "on-demand": 0, "other": 0, "script_code": 0}

    for fp in all_files:
        rel = fp.relative_to(bundle_dir)
        bucket = classify_bucket(rel)
        raw_bytes = len(fp.read_bytes())
        tokens = estimate_tokens(raw_bytes)
        files_detail.append({
            "relative_path": rel.as_posix(),
            "bucket": bucket,
            "bytes": raw_bytes,
            "estimated_tokens": tokens,
        })
        totals[bucket] += tokens
        if rel.suffix == ".py":
            totals["script_code"] += tokens

    skill_md = bundle_dir / "SKILL.md"
    skill_text = skill_md.read_text(encoding="utf-8") if skill_md.exists() else ""

    markers = check_markers(skill_text)
    missing_markers = [k for k, v in markers.items() if not v]

    siblings = check_siblings(bundle_dir)
    missing_siblings = [k for k, v in siblings.items() if not v]

    cross_bundle = check_cross_bundle(bundle_dir)
    cross_bundle_failures = [
        f"{check_id}: {check['description']}"
        for check_id, check in cross_bundle.items()
        if not check["pass"]
    ]

    findings: list[str] = []
    if missing_markers:
        for m in missing_markers:
            findings.append(f"missing marker: {m} ({REQUIRED_MARKERS[m]})")
    if missing_siblings:
        for s in missing_siblings:
            findings.append(f"missing expected sibling: {s}")
    if cross_bundle_failures:
        for f in cross_bundle_failures:
            findings.append(f"cross-bundle check failed: {f}")

    return {
        "bundle_dir": bundle_dir.as_posix(),
        "files": files_detail,
        "totals": totals,
        "total_estimated_tokens": sum(totals.values()),
        "markers": markers,
        "siblings": siblings,
        "cross_bundle": cross_bundle,
        "findings": findings,
        "strict_ok": len(findings) == 0,
    }


def render_text(report: dict) -> None:
    print(f"Bundle: {report['bundle_dir']}")
    print()
    print("Files:")
    for f in report["files"]:
        print(
            f"  [{f['bucket']:9s}] {f['relative_path']:<50s} "
            f"{f['bytes']:>6d} B  ~{f['estimated_tokens']:>4d} tokens"
        )
    print()
    print("Totals:")
    for bucket, tokens in report["totals"].items():
        print(f"  {bucket:<12s} ~{tokens:>4d} tokens")
    print(f"  {'total':<12s} ~{report['total_estimated_tokens']:>4d} tokens")
    print()
    print("Contract markers:")
    for key, present in report["markers"].items():
        status = "PASS" if present else "FAIL"
        print(f"  [{status}] {key}: {REQUIRED_MARKERS[key]}")
    print()
    print("Expected siblings:")
    for path, present in report["siblings"].items():
        status = "PASS" if present else "FAIL"
        print(f"  [{status}] {path}")
    print()
    print("Cross-bundle consumer checks:")
    for check_id, check in report["cross_bundle"].items():
        status = "PASS" if check["pass"] else "FAIL"
        print(f"  [{status}] {check_id}: {check['description']}")
        if not check["file_present"]:
            print(f"          file missing: {check['file']}")
        elif not check["pattern_found"]:
            print(f"          pattern not found: {check['file']}")
    print()
    if report["findings"]:
        print("Findings:")
        for finding in report["findings"]:
            print(f"  - {finding}")
    else:
        print("Findings: none")
    print()
    print(f"strict_ok: {report['strict_ok']}")


def render_json(report: dict) -> None:
    print(json.dumps(report, indent=2))


def main() -> int:
    args = parse_args()
    script_path = Path(__file__)
    bundle_dir = args.dir or find_bundle_dir(script_path)

    if not bundle_dir.is_dir():
        print(f"ERROR: bundle directory not found: {bundle_dir}", file=sys.stderr)
        return 1

    report = build_report(bundle_dir)

    if args.format == "json":
        render_json(report)
    else:
        render_text(report)

    if args.strict and not report["strict_ok"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
