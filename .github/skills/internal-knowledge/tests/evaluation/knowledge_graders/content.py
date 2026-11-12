"""Content, placement, README, and Markdown-link graders."""

from __future__ import annotations

import posixpath
import re

from .core import RunInput, Verdict, changed_paths, register


def _verdict(name: str, code: str | None, evidence: str) -> Verdict:
    return Verdict(name, "fail" if code else "pass", code, evidence)


@register("must_write")
def must_write(run: RunInput, gold: dict) -> Verdict:
    missing = sorted(
        path
        for path in gold.get("must_write", [])
        if path not in run.after or path not in changed_paths(run.before, run.after)
    )
    return _verdict(
        "must_write",
        "critical-omission" if missing else None,
        f"required paths absent or unchanged: {missing}" if missing else "all required paths were written",
    )


@register("must_contain_facts")
def must_contain_facts(run: RunInput, gold: dict) -> Verdict:
    missing: list[str] = []
    for fact in gold.get("facts", []):
        path, expected = fact["path"], re.sub(r"\s+", " ", fact["text"]).strip().casefold()
        actual = re.sub(r"\s+", " ", run.after.get(path, "")).strip().casefold()
        if expected not in actual:
            missing.append(path)
    return _verdict(
        "must_contain_facts",
        "critical-omission" if missing else None,
        f"facts missing from paths: {sorted(missing)}" if missing else "all required facts are present",
    )


@register("taxonomy_placement")
def taxonomy_placement(run: RunInput, gold: dict) -> Verdict:
    placements = gold.get("expected_placements", {})
    misplaced = sorted(
        destination
        for source, destination in placements.items()
        if destination not in run.after or source in run.after
    )
    return _verdict(
        "taxonomy_placement",
        "wrong-placement" if misplaced else None,
        f"missing destinations or retained sources: {misplaced}" if misplaced else "documents occupy expected destinations",
    )


@register("mode_split")
def mode_split(run: RunInput, gold: dict) -> Verdict:
    problems: list[str] = []
    for section in gold.get("sections", []):
        marker, destination = section["marker"], section["dest"]
        if marker not in run.after.get(destination, ""):
            problems.append(f"{marker} missing from {destination}")
        problems.extend(
            f"{marker} also appears in {path}"
            for path, text in run.after.items()
            if path != destination and marker in text
        )
    return _verdict(
        "mode_split",
        "mode-mixed" if problems else None,
        "; ".join(problems) if problems else "section markers are isolated in their destinations",
    )


@register("readme_opening")
def readme_opening(run: RunInput, gold: dict) -> Verdict:
    invalid: list[str] = []
    for path in gold.get("readme_paths", []):
        lines = [line.strip() for line in run.after.get(path, "").splitlines() if line.strip()]
        has_title = bool(lines and lines[0].startswith("# "))
        has_summary = has_title and any(
            not line.startswith("#") and not line.startswith("<!--")
            for line in lines[1:4]
        )
        if not has_summary:
            invalid.append(path)
    return _verdict(
        "readme_opening",
        "readme-opening" if invalid else None,
        f"README openings need a title and nearby summary: {invalid}" if invalid else "README openings are useful",
    )


def _link_targets(text: str) -> set[str]:
    return {
        target.strip()
        for target in re.findall(r"\[[^]]+\]\(([^)]+)\)", text)
    }


def _resolve_link(source: str, target: str) -> str | None:
    if not target or target.startswith(("#", "//")) or "://" in target or target.startswith("mailto:"):
        return None
    path = target.split("#", 1)[0].split("?", 1)[0]
    if not path:
        return None
    return posixpath.normpath(posixpath.join(posixpath.dirname(source), path))


@register("readme_links")
def readme_links(run: RunInput, gold: dict) -> Verdict:
    trees = dict(run.after)
    broken: set[str] = set()
    for source, text in run.after.items():
        for target in _link_targets(text):
            resolved = _resolve_link(source, target)
            if resolved is not None and resolved not in trees:
                broken.add(f"{source} -> {target}")
    missing_owner: set[str] = set()
    owner_links = gold.get("owner_links", [])
    if isinstance(owner_links, dict):
        owner_links = [
            {"source": source, "target": target}
            for source, targets in owner_links.items()
            for target in (targets if isinstance(targets, list) else [targets])
        ]
    for link in owner_links:
        source, target = link["source"], link["target"]
        target_path = posixpath.normpath(target)
        resolved_targets = {
            resolved
            for authored in _link_targets(run.after.get(source, ""))
            if (resolved := _resolve_link(source, authored)) is not None
        }
        if target_path not in resolved_targets:
            missing_owner.add(f"{source} -> {target}")
    if broken:
        return Verdict("readme_links", "fail", "broken-link", f"unresolved relative links: {sorted(broken)}")
    if missing_owner:
        return Verdict("readme_links", "fail", "missing-owner-link", f"owner links missing: {sorted(missing_owner)}")
    return Verdict("readme_links", "pass", None, "relative and owner links resolve")
