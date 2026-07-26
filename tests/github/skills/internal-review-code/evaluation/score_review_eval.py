#!/usr/bin/env python3
"""Score a manually captured, sanitized code-review evaluation record."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REQUIRED_PROVENANCE_FIELDS = (
    "model",
    "target_sha256",
    "review_skill_sha256",
    "engine_sha256",
    "chat_debug_reference",
    "contract_version",
)
REQUIRED_RUN_FIELDS = (
    "loaded_skills",
    "matched_finding_ids",
    "verdict",
    "scope_violations",
)


def load_json(path: str | Path) -> dict[str, Any]:
    """Load one JSON object and turn file/schema failures into CLI errors."""

    source = Path(path)
    try:
        value = json.loads(source.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot load JSON from {source}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"JSON root must be an object: {source}")
    return value


def _validate_schema(manifest: dict[str, Any], run: dict[str, Any]) -> None:
    missing_manifest = [
        key
        for key in (
            "contract_version",
            "required_loaded_skills",
            "material_finding_ids",
            "minimum_material_recall",
            "maximum_scope_violations",
            "false_approval_allowed",
        )
        if key not in manifest
    ]
    missing_run = [
        key
        for key in (*REQUIRED_PROVENANCE_FIELDS, *REQUIRED_RUN_FIELDS)
        if key not in run
    ]
    errors = []
    if missing_manifest:
        errors.append(f"manifest missing fields: {', '.join(missing_manifest)}")
    if missing_run:
        errors.append(f"run missing fields: {', '.join(missing_run)}")
    if run.get("contract_version") != manifest.get("contract_version"):
        errors.append("manifest and run contract_version differ")
    if errors:
        raise ValueError("; ".join(errors))


def score(manifest: dict[str, Any], run: dict[str, Any]) -> dict[str, Any]:
    """Score explicit operator-recorded findings without parsing report prose."""

    _validate_schema(manifest, run)
    material = set(manifest["material_finding_ids"])
    reported = set(run["matched_finding_ids"])
    missing = sorted(material - reported)
    recall = (len(material) - len(missing)) / len(material) if material else 1.0
    loaded_exact = run["loaded_skills"] == manifest["required_loaded_skills"]
    false_approval = run["verdict"] == "approve" and bool(material)
    scope_violation_count = len(run["scope_violations"])
    accepted = (
        recall >= manifest["minimum_material_recall"]
        and loaded_exact
        and not false_approval
        and scope_violation_count <= manifest["maximum_scope_violations"]
    )
    return {
        "contract_version": manifest["contract_version"],
        "material_recall": recall,
        "missing_finding_ids": missing,
        "loaded_skills_exact": loaded_exact,
        "false_approval": false_approval,
        "scope_violation_count": scope_violation_count,
        "accepted": accepted,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--run", required=True, type=Path)
    args = parser.parse_args(argv)

    try:
        result = score(load_json(args.manifest), load_json(args.run))
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    json.dump(result, sys.stdout, sort_keys=True)
    sys.stdout.write("\n")
    return 0 if result["accepted"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
