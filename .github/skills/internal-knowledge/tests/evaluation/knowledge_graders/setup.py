"""Concrete output checks for the approved Area/Topic setup contract."""

from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from datetime import date
from pathlib import PurePosixPath

import yaml

from .core import RunInput, Verdict, changed_paths, register
from .filesystem import _matches, _result, managed_config_path, viewer_enabled

START = "<!-- knowledge:managed:start -->"
END = "<!-- knowledge:managed:end -->"
BLOCK = re.compile(re.escape(START) + r".*?" + re.escape(END), re.DOTALL)
AREA_README = re.compile(r"(?:docs/areas|work)/[^_/][^/]*/README\.md$")


def _outside(text: str) -> str:
    if text.count(START) != text.count(END) or text.count(START) > 1:
        raise ValueError("malformed or repeated managed markers")
    if START in text and not BLOCK.search(text):
        raise ValueError("reversed managed markers")
    return BLOCK.sub("", text)


@register("managed_blocks")
def managed_blocks(run: RunInput, gold: dict) -> Verdict:
    del gold
    for snapshot in (*run.steps, run.after):
        for path in changed_paths(run.before, snapshot):
            old, new = run.before.get(path, ""), snapshot.get(path, "")
            if not path.endswith(".md"):
                continue
            if not any(marker in old + new for marker in (START, END)):
                if path in run.before and old != new:
                    return _result(
                        "managed_blocks",
                        "managed-bytes",
                        f"{path}: unmarked content replaced",
                    )
                continue
            try:
                old_outside, new_outside = _outside(old), _outside(new)
                if path not in snapshot or (
                    path in run.before and old_outside != new_outside
                ):
                    raise ValueError("outside bytes changed")
            except ValueError as exc:
                return _result("managed_blocks", "managed-bytes", f"{path}: {exc}")
    return _result("managed_blocks")


@register("setup_repeat")
def setup_repeat(run: RunInput, gold: dict) -> Verdict:
    del gold
    if not run.trace_complete or run.second_after is None:
        return Verdict(
            "setup_repeat",
            "blocked",
            "missing-repeat",
            "complete trace and repeat snapshot required",
        )
    if (
        dict(run.before) != dict(run.after)
        or dict(run.second_after) != dict(run.after)
        or run.steps
        or any(event["kind"] in {"write", "shell"} for event in run.trace)
    ):
        return _result(
            "setup_repeat", "setup-rewrite", "repeat setup wrote or attempted a write"
        )
    return _result("setup_repeat")


@register("setup_layout")
def setup_layout(run: RunInput, gold: dict) -> Verdict:
    areas = gold["areas"]
    root = gold.get("operational_root", "work")
    required = {
        "AGENTS.local.md",
        *(
            f"docs/agents/{name}.md"
            for name in ("layout", "vocabulary", "promotion", "issue-tracker")
        ),
    }
    work_readmes = {f"{root}/{area}/README.md" for area in areas}
    required |= work_readmes | {f"docs/areas/{area}/README.md" for area in areas}
    topics = {
        f"docs/areas/{area}/{topic}/GLOSSARY.md"
        for area, names in areas.items()
        for topic in names
    }
    required |= topics
    if topics:
        required.add("GLOSSARY-MAP.md")
    errors = sorted(required - run.after.keys())
    for path in required & run.after.keys():
        text = run.after[path]
        try:
            _outside(text)
            if text.count(START) != 1:
                raise ValueError("missing managed block")
        except ValueError as exc:
            errors.append(f"{path}: {exc}")
        if path == "AGENTS.local.md":
            block = BLOCK.search(text)
            if block and len(block.group().splitlines()) > 15:
                errors.append("placement block exceeds 15 lines")
        if path in work_readmes | topics | {
            f"docs/areas/{area}/README.md" for area in areas
        }:
            if (
                "<!-- knowledge:placeholder -->" not in text
                or "Status: placeholder" not in text
            ):
                errors.append(f"{path}: unmarked scaffold")
        if path in work_readmes and not all(
            title in text
            for title in ("Knowledge owner:", "## Deliverable index", "## Evidence")
        ):
            errors.append(f"{path}: missing scaffold sections")
    for path in changed_paths(run.before, run.after):
        parts = PurePosixPath(path).parts
        if parts and parts[0] == root and path not in work_readmes:
            errors.append(f"{path}: operational authoring")
        if path.startswith("docs/") and (
            any(
                part
                in {
                    "sources",
                    "research",
                    "analyses",
                    "data",
                    "scripts",
                    "deliverables",
                    "tracker",
                }
                for part in parts
            )
            or path.endswith((".py", ".csv", ".xlsx", ".pdf", ".docx"))
        ):
            errors.append(f"{path}: operational content under docs")
    if topics and "GLOSSARY.md" in changed_paths(run.before, run.after):
        errors.append("new root glossary duplicates Topic ownership")
    glossary_map = run.after.get("GLOSSARY-MAP.md", "")
    for topic in topics:
        if topic not in glossary_map:
            errors.append(f"{topic}: missing map entry")
    return _result(
        "setup_layout", "setup-layout" if errors else None, "; ".join(errors)
    )


@register("legacy_move_plan")
def legacy_move_plan(run: RunInput, gold: dict) -> Verdict:
    for source, target in gold["move_plan"].items():
        if (
            source not in run.before
            or f"{source} -> {target}" not in run.report
            or run.after.get(source) != run.before[source]
            or target in changed_paths(run.before, run.after)
            or any(
                snapshot.get(source) != run.before[source] or target in snapshot
                for snapshot in run.steps
            )
        ):
            return _result(
                "legacy_move_plan",
                "legacy-plan",
                f"missing proposal or unapproved execution: {source}",
            )
    if not re.search(r"approval required", run.report, re.IGNORECASE):
        return _result("legacy_move_plan", "legacy-plan", "approval gate missing")
    return _result("legacy_move_plan")


@register("move_preserved")
def move_preserved(run: RunInput, gold: dict) -> Verdict:
    if not gold.get("transfers"):
        return Verdict(
            "move_preserved",
            "blocked",
            "missing-manifest",
            "sha256 transfer manifest required",
        )
    for item in gold["transfers"]:
        source, target, expected = item["source"], item["target"], item["sha256"]
        old, new = run.before.get(source), run.after.get(target)
        if (
            old is None
            or new is None
            or source in run.after
            or source == target
            or (target in run.before and run.before[target] != old)
            or hashlib.sha256(old.encode("utf-8")).hexdigest() != expected
            or hashlib.sha256(new.encode("utf-8")).hexdigest() != expected
        ):
            return _result(
                "move_preserved",
                "transfer-bytes",
                f"unverified move: {source} -> {target}",
            )
        for snapshot in run.steps:
            if any(
                path in snapshot and snapshot[path] != old for path in (source, target)
            ):
                return _result(
                    "move_preserved",
                    "transfer-bytes",
                    f"transfer bytes changed in step: {source}",
                )
    return _result("move_preserved")


def _unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate key: {key}")
        result[key] = value
    return result


class _FrontmatterLoader(yaml.BaseLoader):
    pass


def _mapping(loader, node):
    return _unique_pairs(loader.construct_pairs(node))


_FrontmatterLoader.add_constructor("tag:yaml.org,2002:map", _mapping)


def _properties(text):
    if not text.startswith(("---\n", "---\r\n")):
        return {}
    lines = text.splitlines()
    try:
        end = lines.index("---", 1)
    except ValueError as exc:
        raise ValueError("unterminated frontmatter") from exc
    properties = yaml.load("\n".join(lines[1:end]), Loader=_FrontmatterLoader)
    if not isinstance(properties, dict):
        raise ValueError("frontmatter must be a mapping")
    return properties


@register("obsidian_config")
def obsidian_config(run: RunInput, gold: dict) -> Verdict:
    try:
        for snapshot in (*run.steps, run.after):
            for path in changed_paths(run.before, snapshot):
                old, new = run.before.get(path, ""), snapshot.get(path, "")
                if path.startswith(".obsidian/") or path.endswith(".base"):
                    if (
                        not viewer_enabled(run)
                        or not managed_config_path(path)
                        or not _matches(path, run.allowlist)
                    ):
                        raise ValueError(f"unmanaged config: {path}")
                    if path not in snapshot:
                        raise ValueError(f"config deleted: {path}")
                    if path.endswith(".base"):
                        if not isinstance(yaml.safe_load(new), dict):
                            raise ValueError("Base must be a YAML mapping")
                        continue
                    previous = json.loads(old or "{}", object_pairs_hook=_unique_pairs)
                    current = json.loads(new, object_pairs_hook=_unique_pairs)
                    if not isinstance(previous, dict) or not isinstance(current, dict):
                        raise ValueError("config must be a JSON object")
                    allowed = (
                        {"colorGroups"}
                        if path.endswith("graph.json")
                        else {"useMarkdownLinks", "newLinkFormat", "userIgnoreFilters"}
                    )
                    if {k: v for k, v in previous.items() if k not in allowed} != {
                        k: v for k, v in current.items() if k not in allowed
                    }:
                        raise ValueError(f"unmanaged keys changed: {path}")
                    if path.endswith("app.json"):
                        ignores = current.get("userIgnoreFilters")
                        if (
                            current.get("useMarkdownLinks") is not True
                            or current.get("newLinkFormat") != "relative"
                            or not isinstance(ignores, list)
                            or any(not isinstance(value, str) for value in ignores)
                            or ignores.count("tmp/") != 1
                            or not set(previous.get("userIgnoreFilters", [])).issubset(
                                ignores
                            )
                        ):
                            raise ValueError("invalid links or lost exclusions")
                    elif not isinstance(current.get("colorGroups"), list):
                        raise ValueError("graph colorGroups must be a list")
                if path.endswith(".md"):
                    if Counter(re.findall(r"\[\[.*?\]\]", new, re.DOTALL)) - Counter(
                        re.findall(r"\[\[.*?\]\]", old, re.DOTALL)
                    ):
                        raise ValueError(f"new wikilink: {path}")
                    previous, current = _properties(old), _properties(new)
                    changed = {
                        key
                        for key in previous.keys() | current.keys()
                        if previous.get(key) != current.get(key)
                    }
                    allowed = set()
                    if viewer_enabled(run) and AREA_README.fullmatch(path):
                        allowed = {"status"}
                        if "status" in changed and current.get("status") not in {
                            "active",
                            "archived",
                        }:
                            raise ValueError("invalid Area status")
                        if "status" in changed:
                            area = PurePosixPath(path).parent.name
                            owner = f"docs/areas/{area}/README.md"
                            mirror = f"work/{area}/README.md"
                            if mirror in run.after and (
                                owner not in run.after
                                or _properties(run.after[owner]).get("status")
                                != _properties(run.after[mirror]).get("status")
                            ):
                                raise ValueError(
                                    "work status differs from docs authority"
                                )
                    elif "/research/" in path and "/sources/" not in path:
                        allowed = {"source", "retrieved"}
                        if "retrieved" in changed:
                            if not re.fullmatch(
                                r"\d{4}-\d{2}-\d{2}", current["retrieved"]
                            ):
                                raise ValueError("retrieved must use YYYY-MM-DD")
                            date.fromisoformat(current["retrieved"])
                    if path in gold.get("protected_paths", []) or path in gold.get(
                        "generated_paths", []
                    ):
                        allowed = set()
                    if changed - allowed:
                        raise ValueError(f"unmanaged properties: {path}")
    except (ValueError, TypeError, KeyError, yaml.YAMLError) as exc:
        return _result("obsidian_config", "obsidian-ownership", str(exc))
    return _result("obsidian_config")
