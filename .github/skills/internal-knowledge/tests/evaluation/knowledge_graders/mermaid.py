"""Static Mermaid, relationship, warrant, and optional parse graders."""

from __future__ import annotations

import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from .core import RunInput, Verdict, changed_paths, register
from .report import parse_report

BLOCK = re.compile(r"```mermaid\s*\n(.*?)```", re.IGNORECASE | re.DOTALL)
EDGE = re.compile(
    r"(?<![\w])([^\s\[\](){}]+)(?:\s*(?:\[[^]\n]*\]|\([^\n)]*\)|\{[^}\n]*\}))?"
    r"\s*(?:-->|-.->|==>|--x|--o|->>|-->>)\s*([^\s\[\](){}]+)"
    r"(?:\s*(?:\[[^]\n]*\]|\([^\n)]*\)|\{[^}\n]*\}))?"
)
NODE = re.compile(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*(?:\[|\(|\{|-->|-.->|==>|--x|--o)")
ALLOWED_TYPES = ("flowchart", "sequenceDiagram", "stateDiagram-v2")


def _blocks(run: RunInput) -> dict[str, list[str]]:
    return {
        path: BLOCK.findall(text)
        for path, text in run.after.items()
        if BLOCK.search(text)
    }


def _verdict(name: str, code: str | None, evidence: str) -> Verdict:
    return Verdict(name, "fail" if code else "pass", code, evidence)


def _static_error(code: str) -> tuple[str | None, str]:
    return code, "Mermaid block violates the static contract"


def _check_block(block: str) -> str | None:
    lines = [line.strip() for line in block.splitlines() if line.strip()]
    first = next((line for line in lines if not line.startswith("%%")), "")
    if not first.split() or first.split()[0] not in ALLOWED_TYPES:
        return "mermaid-static"
    if not any(line.startswith("accTitle:") for line in lines) or not any(
        line.startswith("accDescr:") for line in lines
    ):
        return "mermaid-static"
    if re.search(r"%%\s*\{\s*init|\btheme\b|\blinkStyle\b|\bclick\b|<\s*/?\s*[A-Za-z][^>]*>", block, re.I):
        return "mermaid-static"
    if re.search(r"(?m)^\s*graph\s+TD\b", block):
        return "mermaid-static"
    for left, right in EDGE.findall(block):
        if any(not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", node) for node in (left, right)):
            return "mermaid-static"
    first_type = first.split()[0]
    if first_type == "sequenceDiagram":
        participants = set(re.findall(r"(?m)^\s*(?:participant|actor)\s+([A-Za-z_][A-Za-z0-9_]*)", block))
        participants.update(name for edge in EDGE.findall(block) for name in edge)
        messages = len(re.findall(r"(?:->>|-->>|-x|--)\s*", block))
        return "diagram-size" if len(participants) > 6 or messages > 15 else None
    if first_type in {"flowchart", "stateDiagram-v2"}:
        nodes = set(name for edge in EDGE.findall(block) for name in edge)
        nodes.update(NODE.findall(block))
        return "diagram-size" if len(nodes) > 15 else None
    return None


@register("mermaid_static")
def mermaid_static(run: RunInput, gold: dict) -> Verdict:
    del gold
    changed = changed_paths(run.before, run.after)
    blocks = {path: diagrams for path, diagrams in _blocks(run).items() if path in changed}
    for path, diagrams in blocks.items():
        for block in diagrams:
            error = _check_block(block)
            if error:
                return _verdict("mermaid_static", error, f"invalid diagram in {path}")
    for path, diagrams in blocks.items():
        if len(diagrams) <= 2:
            continue
        try:
            report = parse_report(run.report)
        except ValueError:
            report = {}
        entries = report.get("diagrams", "").split(";")
        if not any(
            entry.strip().startswith(f"{path}:")
            and re.search(r"derogated\(\s*[^\s)][^)]*\)", entry)
            for entry in entries
        ):
            return _verdict("mermaid_static", "diagram-cap", f"{path} has {len(diagrams)} blocks without derogation")
    return _verdict("mermaid_static", None, "Mermaid blocks pass static and size checks")


def _edge_pair(edge: object) -> tuple[str, str] | None:
    if isinstance(edge, str):
        match = re.fullmatch(r"\s*([^\s]+)\s*(?:->|-->)\s*([^\s]+)\s*", edge)
        return (match.group(1), match.group(2)) if match else None
    if isinstance(edge, (list, tuple)) and len(edge) == 2:
        return str(edge[0]), str(edge[1])
    if isinstance(edge, dict) and "from" in edge and "to" in edge:
        return str(edge["from"]), str(edge["to"])
    return None


@register("diagram_relations")
def diagram_relations(run: RunInput, gold: dict) -> Verdict:
    aliases = gold.get("aliases", {})
    expected: set[tuple[str, str]] = set()
    actual: set[tuple[str, str]] = set()
    for doc, edges in gold.get("diagram_edges", {}).items():
        for edge in edges:
            pair = _edge_pair(edge)
            if pair:
                expected.add((aliases.get(pair[0], pair[0]), aliases.get(pair[1], pair[1])))
        for block in BLOCK.findall(run.after.get(doc, "")):
            actual.update((aliases.get(a, a), aliases.get(b, b)) for a, b in EDGE.findall(block))
    false = actual - expected
    missing = expected - actual
    if false:
        return Verdict("diagram_relations", "fail", "false-relation", f"unexpected directed edges: {sorted(false)}")
    if missing:
        return Verdict("diagram_relations", "fail", "critical-omission", f"required edges missing: {sorted(missing)}")
    return Verdict("diagram_relations", "pass", None, "diagram relations match gold")


@register("diagram_warranted")
def diagram_warranted(run: RunInput, gold: dict) -> Verdict:
    blocks = _blocks(run)
    try:
        omitted = parse_report(run.report).get("omitted", "").split(";")
    except ValueError:
        omitted = []
    omitted_paths = {entry.split(":", 1)[0].strip() for entry in omitted if ":" in entry}
    for trigger in gold.get("diagram_triggers", []):
        doc, required = trigger["doc"], trigger["required"]
        has_diagram = bool(blocks.get(doc))
        if required and not has_diagram and doc not in omitted_paths:
            return Verdict("diagram_warranted", "fail", "critical-omission", f"{doc} needs a diagram or omission reason")
        if not required and has_diagram:
            return Verdict("diagram_warranted", "fail", "unwarranted-diagram", f"{doc} has no diagram trigger")
    return Verdict("diagram_warranted", "pass", None, "diagram presence follows documented triggers")


@register("mermaid_parse")
def mermaid_parse(run: RunInput, gold: dict) -> Verdict:
    del gold
    executable = shutil.which("mmdc")
    if executable is None:
        return Verdict("mermaid_parse", "not-run", "mmdc-unavailable", "mmdc is not installed")
    for path, diagrams in _blocks(run).items():
        for index, block in enumerate(diagrams):
            with tempfile.TemporaryDirectory() as directory:
                source = Path(directory) / f"diagram-{index}.mmd"
                output = Path(directory) / f"diagram-{index}.svg"
                source.write_text(block, encoding="utf-8")
                result = subprocess.run(
                    [executable, "-i", str(source), "-o", str(output)],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                if result.returncode:
                    return Verdict(
                        "mermaid_parse",
                        "fail",
                        "mermaid-parse",
                        f"{path} diagram {index}: {result.stderr.strip()}",
                    )
    return Verdict("mermaid_parse", "pass", None, "mmdc parsed every Mermaid block")
