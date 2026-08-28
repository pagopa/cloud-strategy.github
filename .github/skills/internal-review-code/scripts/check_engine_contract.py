#!/usr/bin/env python3
"""Engine-contract drift check for internal-review-code.

Canonical source: `.github/skills/internal-review-code/` in the repository.
The copy under `~/.agents/skills/internal-review-code/` is a synchronized
projection; this check fails on drift between the two.

The check also verifies that the projection-label mapping table in SKILL.md
still covers exactly the finding categories of the declared review engine,
`addyosmani-code-review-and-quality`. Run it after any engine refresh.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

BUNDLE = Path(__file__).resolve().parent.parent
WRAPPER = BUNDLE / "SKILL.md"
ENGINE_CANDIDATES = [
    BUNDLE.parent / "addyosmani-code-review-and-quality" / "SKILL.md",
    Path.home() / ".agents" / "skills" / "addyosmani-code-review-and-quality" / "SKILL.md",
]
HOME_PROJECTION = Path.home() / ".agents" / "skills" / "internal-review-code"
SPECIAL_ENGINE_NAMES = {"(no prefix)": "required change"}


def normalize(name: str) -> str:
    cleaned = name.strip().replace("*", "").replace(":", "").strip()
    cleaned = SPECIAL_ENGINE_NAMES.get(cleaned, cleaned)
    return re.sub(r"\s*/\s*", "/", cleaned).lower()


def table_first_column(text: str, header_hint: str) -> set[str]:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if header_hint in line.lower() and line.lstrip().startswith("|"):
            categories: set[str] = set()
            for row in lines[index + 2 :]:
                if not row.lstrip().startswith("|"):
                    break
                cell = row.strip().strip("|").split("|")[0]
                categories.add(normalize(cell))
            return categories
    raise ValueError(f"table with header {header_hint!r} not found")


def bundle_files(root: Path) -> dict[str, bytes]:
    return {
        str(path.relative_to(root)): path.read_bytes()
        for path in sorted(root.rglob("*"))
        if path.is_file() and "__pycache__" not in path.parts
    }


def main() -> int:
    failures: list[str] = []

    engine = next((path for path in ENGINE_CANDIDATES if path.is_file()), None)
    if engine is None:
        print("FAIL: engine SKILL.md not found in any known location")
        return 1

    wrapper_text = WRAPPER.read_text(encoding="utf-8")
    engine_categories = table_first_column(
        engine.read_text(encoding="utf-8"), "prefix"
    )
    wrapper_categories = table_first_column(wrapper_text, "engine category")

    if engine_categories != wrapper_categories:
        missing = engine_categories - wrapper_categories
        extra = wrapper_categories - engine_categories
        if missing:
            failures.append(f"engine categories missing from wrapper table: {sorted(missing)}")
        if extra:
            failures.append(f"wrapper categories absent from engine table: {sorted(extra)}")

    if HOME_PROJECTION.is_dir():
        canonical = bundle_files(BUNDLE)
        projection = bundle_files(HOME_PROJECTION)
        for name in sorted(set(canonical) - set(projection)):
            failures.append(f"projection is missing file: {name}")
        for name in sorted(set(projection) - set(canonical)):
            failures.append(f"projection has extra file: {name}")
        for name in sorted(set(canonical) & set(projection)):
            if canonical[name] != projection[name]:
                failures.append(f"projection file drifted: {name}")
    else:
        failures.append(f"home projection not found: {HOME_PROJECTION}")

    if failures:
        print(f"FAIL: {len(failures)} engine-contract drift finding(s)")
        for failure in failures:
            print(f"  - {failure}")
        return 1

    print(
        f"PASS: engine categories match the wrapper mapping "
        f"({len(engine_categories)} categories); "
        f"home projection is identical to the canonical bundle"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
