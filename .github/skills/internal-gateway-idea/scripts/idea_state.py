"""State and producer-consumer helpers for the idea gateway living spec."""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any

import yaml
from yaml.nodes import MappingNode

SCHEMA = "internal-gateway-idea/v1"
PACKET_SCHEMA = "internal-gateway-critical/full-analysis-v1"
HEADER_KEYS = frozenset(
    {
        "schema",
        "slug",
        "status",
        "revision",
        "target",
        "source_baseline",
        "lane",
        "assurance",
        "assurance_reason",
        "platform_semantics_controlling",
        "reviewed_revision",
        "approved_revision",
        "review_sources",
        "next_actor",
        "next_action",
    }
)
STATUSES = frozenset(
    {
        "discovering",
        "awaiting-decisions",
        "analyzing",
        "under-review",
        "awaiting-remedy-decision",
        "verifying",
        "awaiting-final-approval",
        "awaiting-independent-review",
        "approved",
        "superseded",
    }
)
LANES = frozenset({"shape-idea", "review-existing"})
ASSURANCES = frozenset({"standard", "high"})
ACTORS = frozenset({"agent", "user", "critic", "plan-writer", "none"})
DISPOSITIONS = frozenset({"open", "accepted-remedy", "accepted-risk", "closed"})
REQUIRED_SECTIONS = (
    "Context and Goal",
    "Decisions and Rationale",
    "Scope and Coverage",
    "Design",
    "Validation and Handoff",
    "Review Ledger",
    "Risks and Open Questions",
    "Continuation",
)
FINDING_ID_PATTERN = re.compile(r"^F-([0-9]{3})$")
PACKET_FINDING_ID_PATTERN = re.compile(r"^C-[0-9]{3}$")
PACKET_KEYS = frozenset(
    {
        "schema",
        "source",
        "target_path",
        "target_revision",
        "outcome",
        "findings",
        "residual_risks",
        "diagnostics",
    }
)
PACKET_SOURCES = frozenset({"standard", "independent"})
PACKET_OUTCOMES = frozenset(
    {
        "accepted",
        "revise-design",
        "reopen-analysis",
        "needs-clarification",
        "invalid-target",
        "request-separate-review",
    }
)


class DesignValidationError(ValueError):
    """Raised when a living design document cannot be resumed safely."""


class UniqueSafeLoader(yaml.SafeLoader):
    pass


def _construct_unique_mapping(
    loader: UniqueSafeLoader, node: MappingNode, deep: bool = False
) -> dict[object, object]:
    if not isinstance(node, MappingNode):
        raise yaml.constructor.ConstructorError(
            None, None, "expected a mapping", node.start_mark
        )
    mapping: dict[object, object] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in mapping:
            raise yaml.constructor.ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                f"duplicate key: {key}",
                key_node.start_mark,
            )
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


UniqueSafeLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _construct_unique_mapping
)


@dataclass(frozen=True)
class DesignHeader:
    schema: str
    slug: str
    status: str
    revision: int
    target: str
    source_baseline: str | None
    lane: str
    assurance: str
    assurance_reason: str
    platform_semantics_controlling: bool
    reviewed_revision: int | None
    approved_revision: int | None
    review_sources: tuple[str, ...]
    next_actor: str
    next_action: str


@dataclass(frozen=True)
class CoverageRow:
    requirement_id: str
    deliverable: str
    owner_design_element: str
    interface: str
    independent_decision: str
    consumer: str
    validation: str
    status: str


@dataclass(frozen=True)
class ReviewFinding:
    id: str
    source: str
    sources: tuple[str, ...]
    critique: str
    recommendation: str
    reason: str
    blocking: bool
    evidence: tuple[str, ...]
    disposition: str
    equivalence_key: str = ""
    conflict: bool = False


@dataclass(frozen=True)
class NormalizedFinding:
    critique: str
    recommendation: str
    reason: str
    blocking: bool
    source: str
    evidence: tuple[str, ...]
    equivalence_key: str


@dataclass(frozen=True)
class DesignDocument:
    header: DesignHeader
    sections: Mapping[str, str]
    coverage_rows: tuple[CoverageRow, ...]
    ledger: tuple[ReviewFinding, ...]
    raw_text: str

    @property
    def open_findings(self) -> tuple[ReviewFinding, ...]:
        return tuple(item for item in self.ledger if item.disposition == "open")


@dataclass(frozen=True)
class ResumeRoute:
    next_actor: str
    next_action: str
    source: str = "design.md"


@dataclass(frozen=True)
class ApprovalRoute:
    approved: bool
    next_actor: str
    next_action: str
    authorizes_execution: bool = False


@dataclass(frozen=True)
class RouteDecision:
    owner: str
    competing_owners: tuple[str, ...] = ()


def _non_empty(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _positive_integer(value: object) -> bool:
    return type(value) is int and value > 0


def _optional_integer(value: object) -> bool:
    return value is None or type(value) is int


def _normalise_header_name(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip()).casefold()


def _split_table_row(line: str) -> list[str]:
    content = line.strip()
    if content.startswith("|"):
        content = content[1:]
    if content.endswith("|"):
        content = content[:-1]
    return [cell.strip() for cell in content.split("|")]


def _is_separator_row(cells: Sequence[str]) -> bool:
    return bool(cells) and all(
        bool(re.fullmatch(r":?-+:?", cell.replace(" ", ""))) for cell in cells
    )


def _find_table(section: str, required_headers: set[str]) -> tuple[list[str], list[list[str]]] | None:
    lines = section.splitlines()
    for index, line in enumerate(lines):
        if "|" not in line:
            continue
        headers = _split_table_row(line)
        normalized = {_normalise_header_name(header) for header in headers}
        if not required_headers.issubset(normalized):
            continue
        rows: list[list[str]] = []
        for following in lines[index + 1 :]:
            if "|" not in following:
                if rows:
                    break
                continue
            cells = _split_table_row(following)
            if _is_separator_row(cells):
                continue
            rows.append(cells)
        return headers, rows
    return None


def _front_matter(text: str) -> tuple[str, str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise DesignValidationError("design.md must start with YAML front matter")
    try:
        end = next(index for index in range(1, len(lines)) if lines[index].strip() == "---")
    except StopIteration as error:
        raise DesignValidationError("YAML front matter is not closed") from error
    return "\n".join(lines[1:end]), "\n".join(lines[end + 1 :])


def _parse_sections(body: str) -> dict[str, str]:
    headings: list[tuple[int, str]] = []
    for index, line in enumerate(body.splitlines()):
        match = re.match(r"^##\s+(.+?)\s*$", line)
        if match:
            headings.append((index, match.group(1)))
    sections: dict[str, str] = {}
    lines = body.splitlines()
    for position, (start, name) in enumerate(headings):
        if name in sections:
            raise DesignValidationError(f"duplicate section: {name}")
        end = headings[position + 1][0] if position + 1 < len(headings) else len(lines)
        sections[name] = "\n".join(lines[start + 1 : end]).strip()
    missing = [name for name in REQUIRED_SECTIONS if name not in sections]
    if missing:
        raise DesignValidationError(f"missing required sections: {missing}")
    return sections


def _parse_coverage(section: str) -> tuple[CoverageRow, ...]:
    table = _find_table(
        section,
        {"id", "deliverable", "owner/design element", "validation", "status"},
    )
    if table is None:
        raise DesignValidationError("Scope and Coverage needs a coverage table")
    headers, rows = table
    positions = {_normalise_header_name(header): index for index, header in enumerate(headers)}
    required = {
        "id",
        "deliverable",
        "owner/design element",
        "validation",
        "status",
    }
    errors: list[str] = []
    missing = required - set(positions)
    if missing:
        errors.append(f"coverage table missing columns: {sorted(missing)}")
    if errors:
        raise DesignValidationError("; ".join(errors))

    def value(cells: list[str], name: str) -> str:
        index = positions.get(name)
        return cells[index].strip() if index is not None and index < len(cells) else ""

    parsed: list[CoverageRow] = []
    for row_index, cells in enumerate(rows, start=1):
        row = CoverageRow(
            requirement_id=value(cells, "id"),
            deliverable=value(cells, "deliverable"),
            owner_design_element=value(cells, "owner/design element"),
            interface=value(cells, "interface"),
            independent_decision=value(cells, "independent decision"),
            consumer=value(cells, "consumer"),
            validation=value(cells, "validation"),
            status=value(cells, "status"),
        )
        if not all(
            _non_empty(item)
            for item in (
                row.requirement_id,
                row.deliverable,
                row.owner_design_element,
                row.validation,
                row.status,
            )
        ):
            raise DesignValidationError(f"coverage row {row_index} has an empty required field")
        parsed.append(row)

    owner_count = len({row.owner_design_element for row in parsed})
    consumer_count = len({row.consumer for row in parsed if row.consumer})
    if owner_count >= 3 or consumer_count >= 3:
        required_multi_owner = {"interface", "independent decision", "consumer"}
        missing_multi_owner = required_multi_owner - set(positions)
        if missing_multi_owner:
            raise DesignValidationError(
                "multi-owner coverage needs columns: "
                + ", ".join(sorted(missing_multi_owner))
            )
        for row_index, row in enumerate(parsed, start=1):
            if not all(
                _non_empty(item)
                for item in (row.interface, row.independent_decision, row.consumer)
            ):
                raise DesignValidationError(
                    f"multi-owner coverage row {row_index} needs interface, independent decision, and consumer"
                )
    return tuple(parsed)


def _issue_key(critique: str, reason: str) -> str:
    return "|".join(
        re.sub(r"\s+", " ", value.strip().casefold()) for value in (critique, reason)
    )


def _parse_ledger(section: str) -> tuple[ReviewFinding, ...]:
    table = _find_table(
        section,
        {"id", "source", "critique", "recommendation", "reason", "blocking", "evidence", "disposition"},
    )
    if table is None:
        return ()
    headers, rows = table
    positions = {_normalise_header_name(header): index for index, header in enumerate(headers)}

    def value(cells: list[str], name: str) -> str:
        index = positions[name]
        return cells[index].strip() if index < len(cells) else ""

    findings: list[ReviewFinding] = []
    previous_number = 0
    seen: set[str] = set()
    for row_index, cells in enumerate(rows, start=1):
        finding_id = value(cells, "id")
        match = FINDING_ID_PATTERN.fullmatch(finding_id)
        if not match or finding_id in seen:
            raise DesignValidationError(f"invalid or duplicate finding ID at ledger row {row_index}")
        number = int(match.group(1))
        if number <= previous_number:
            raise DesignValidationError("ledger finding IDs must be monotonic and non-reused")
        previous_number = number
        seen.add(finding_id)

        blocking_text = value(cells, "blocking").casefold()
        if blocking_text not in {"true", "false"}:
            raise DesignValidationError(f"ledger row {row_index} has invalid blocking value")
        evidence = tuple(
            item.strip()
            for item in value(cells, "evidence").split(";")
            if item.strip()
        )
        disposition = value(cells, "disposition")
        if disposition not in DISPOSITIONS:
            raise DesignValidationError(f"ledger row {row_index} has invalid disposition")
        source = value(cells, "source")
        critique = value(cells, "critique")
        recommendation = value(cells, "recommendation")
        reason = value(cells, "reason")
        if not source or not critique or not recommendation or not reason or not evidence:
            raise DesignValidationError(f"ledger row {row_index} has an empty required field")
        findings.append(
            ReviewFinding(
                id=finding_id,
                source=source,
                sources=(source,),
                critique=critique,
                recommendation=recommendation,
                reason=reason,
                blocking=blocking_text == "true",
                evidence=evidence,
                disposition=disposition,
                equivalence_key=_issue_key(critique, reason),
            )
        )
    return tuple(findings)


def _validate_header(raw: object, expected_slug: str | None) -> DesignHeader:
    if not isinstance(raw, dict):
        raise DesignValidationError("front matter must be a mapping")
    keys = set(raw)
    missing = HEADER_KEYS - keys
    unknown = keys - HEADER_KEYS
    if missing or unknown:
        raise DesignValidationError(
            f"header keys mismatch; missing={sorted(missing)}, unknown={sorted(unknown)}"
        )
    errors: list[str] = []
    string_keys = (
        "schema",
        "slug",
        "status",
        "target",
        "assurance_reason",
        "next_action",
    )
    for key in string_keys:
        if not _non_empty(raw[key]):
            errors.append(f"{key} must be a non-empty string")
    if raw["schema"] != SCHEMA:
        errors.append(f"schema must be {SCHEMA}")
    if expected_slug is not None and raw["slug"] != expected_slug:
        errors.append("slug does not match the expected slug")
    if raw["status"] not in STATUSES:
        errors.append("status is not supported")
    if not _positive_integer(raw["revision"]):
        errors.append("revision must be a positive integer")
    if raw["lane"] not in LANES:
        errors.append("lane is not supported")
    if raw["assurance"] not in ASSURANCES:
        errors.append("assurance is not supported")
    if type(raw["platform_semantics_controlling"]) is not bool:
        errors.append("platform_semantics_controlling must be a boolean")
    if not _optional_integer(raw["reviewed_revision"]):
        errors.append("reviewed_revision must be an integer or null")
    if not _optional_integer(raw["approved_revision"]):
        errors.append("approved_revision must be an integer or null")
    review_sources = raw["review_sources"]
    if not isinstance(review_sources, list):
        errors.append("review_sources must be a list")
    else:
        invalid_sources = [
            source
            for source in review_sources
            if not isinstance(source, str) or source not in PACKET_SOURCES
        ]
        if invalid_sources:
            errors.append("review_sources contains an unknown value")
        elif len(set(review_sources)) != len(review_sources):
            errors.append("review_sources must contain unique values")
    if raw["source_baseline"] is not None and not _non_empty(raw["source_baseline"]):
        errors.append("source_baseline must be a non-empty string or null")
    if raw["lane"] == "review-existing" and not _non_empty(raw["source_baseline"]):
        errors.append("review-existing requires a non-empty source_baseline")
    if raw["next_actor"] not in ACTORS:
        errors.append("next_actor is not supported")
    if _positive_integer(raw["revision"]):
        revision = raw["revision"]
        for key in ("reviewed_revision", "approved_revision"):
            value = raw[key]
            if value is not None and value != revision:
                errors.append(f"{key} is stale for revision {revision}")

    if errors:
        raise DesignValidationError("; ".join(errors))
    return DesignHeader(
        schema=raw["schema"],
        slug=raw["slug"],
        status=raw["status"],
        revision=raw["revision"],
        target=raw["target"],
        source_baseline=raw["source_baseline"],
        lane=raw["lane"],
        assurance=raw["assurance"],
        assurance_reason=raw["assurance_reason"],
        platform_semantics_controlling=raw["platform_semantics_controlling"],
        reviewed_revision=raw["reviewed_revision"],
        approved_revision=raw["approved_revision"],
        review_sources=tuple(review_sources),
        next_actor=raw["next_actor"],
        next_action=raw["next_action"],
    )


def _review_sources_complete(
    header: DesignHeader,
    sources: Sequence[str] | None = None,
    *,
    required_independent: bool = False,
) -> bool:
    required = {"standard"}
    if header.assurance == "high" or required_independent:
        required.add("independent")
    available = set(header.review_sources if sources is None else sources)
    return required.issubset(available)


def _validate_state_consistency(header: DesignHeader, ledger: Sequence[ReviewFinding]) -> None:
    expected_actor = {
        "discovering": "agent",
        "awaiting-decisions": "user",
        "analyzing": "agent",
        "under-review": "critic",
        "awaiting-remedy-decision": "user",
        "verifying": "agent",
        "awaiting-final-approval": "user",
        "awaiting-independent-review": "user",
        "approved": "plan-writer",
        "superseded": "none",
    }[header.status]
    if header.next_actor != expected_actor:
        raise DesignValidationError(
            f"status {header.status} requires next_actor {expected_actor}"
        )
    if header.approved_revision is not None and header.status != "approved":
        raise DesignValidationError("approved_revision requires approved status")
    if header.status == "awaiting-final-approval":
        if header.reviewed_revision != header.revision or header.approved_revision is not None:
            raise DesignValidationError("awaiting-final-approval requires current reviewed state")
        if not _review_sources_complete(header):
            raise DesignValidationError("awaiting-final-approval requires complete review sources")
    if header.status == "approved":
        if (
            header.reviewed_revision != header.revision
            or header.approved_revision != header.revision
        ):
            raise DesignValidationError("approved state requires current review and approval")
        if not _review_sources_complete(header):
            raise DesignValidationError("approved state requires complete review sources")
        if _has_open_blocker_or_conflict(ledger):
            raise DesignValidationError("approved state cannot contain open blockers or conflicts")


def _validate_handoff_section(section: str) -> None:
    required_labels = (
        "Target",
        "Source baseline",
        "Anti-scope",
        "Nearest owner",
        "Validation path",
        "Stop conditions",
        "Observable acceptance",
        "Authority",
    )
    for label in required_labels:
        if not re.search(rf"(?im)^\s*[-*]?\s*{re.escape(label)}\s*:", section):
            raise DesignValidationError(f"Validation and Handoff is missing {label}")


def parse_design_document(text: str, *, expected_slug: str | None = None) -> DesignDocument:
    yaml_text, body = _front_matter(text)
    try:
        raw_header = yaml.load(yaml_text, Loader=UniqueSafeLoader)
    except yaml.YAMLError as error:
        raise DesignValidationError(f"invalid YAML front matter: {error}") from error
    header = _validate_header(raw_header, expected_slug)
    sections = _parse_sections(body)
    coverage_rows = _parse_coverage(sections["Scope and Coverage"])
    ledger = _parse_ledger(sections["Review Ledger"])
    _validate_handoff_section(sections["Validation and Handoff"])
    word_count = len(re.findall(r"\S+", text))
    if word_count > 1200 and not any(
        phrase in text.casefold() for phrase in ("independent systems", "bounded exception")
    ):
        raise DesignValidationError("design.md exceeds the 1,200-word hard budget")
    _validate_state_consistency(header, ledger)
    return DesignDocument(
        header=header,
        sections=sections,
        coverage_rows=coverage_rows,
        ledger=ledger,
        raw_text=text,
    )


def _has_open_blocker_or_conflict(findings: Sequence[ReviewFinding]) -> bool:
    return any(
        finding.disposition == "open" and (finding.blocking or finding.conflict)
        for finding in findings
    )


def can_complete_review(document: DesignDocument) -> bool:
    return (
        document.header.reviewed_revision == document.header.revision
        and _review_sources_complete(document.header)
        and not _has_open_blocker_or_conflict(document.ledger)
    )


def can_finalize_approval(document: DesignDocument) -> bool:
    return (
        document.header.status == "awaiting-final-approval"
        and document.header.approved_revision is None
        and can_complete_review(document)
    )


def can_handoff(document: DesignDocument) -> bool:
    return (
        document.header.status == "approved"
        and document.header.reviewed_revision == document.header.revision
        and document.header.approved_revision == document.header.revision
        and _review_sources_complete(document.header)
        and not _has_open_blocker_or_conflict(document.ledger)
    )


def apply_material_change(document: DesignDocument, *, central_change: bool) -> DesignDocument:
    header = replace(
        document.header,
        revision=document.header.revision + 1,
        reviewed_revision=None if central_change else document.header.reviewed_revision,
        approved_revision=None,
        review_sources=(),
        status="analyzing",
        next_actor="agent",
        next_action="Recompose the current design and run the required review.",
    )
    return replace(document, header=header)


def resume_route(document: DesignDocument) -> ResumeRoute:
    return ResumeRoute(
        next_actor=document.header.next_actor,
        next_action=document.header.next_action,
    )


def _packet_finding(
    item: object, source: str, index: int
) -> tuple[NormalizedFinding | None, str | None]:
    if not isinstance(item, Mapping):
        return None, f"findings[{index}] must be an object"
    required = {"id", "critique", "recommendation", "reason", "blocking", "evidence"}
    if set(item) != required:
        return None, f"findings[{index}] keys do not match the producer contract"
    if not isinstance(item["id"], str) or not PACKET_FINDING_ID_PATTERN.fullmatch(item["id"]):
        return None, f"findings[{index}].id is invalid"
    if not all(_non_empty(item[key]) for key in ("critique", "recommendation", "reason")):
        return None, f"findings[{index}] text fields must be non-empty"
    if type(item["blocking"]) is not bool:
        return None, f"findings[{index}].blocking is invalid"
    evidence = item["evidence"]
    if (
        not isinstance(evidence, list)
        or not evidence
        or any(not _non_empty(value) for value in evidence)
        or len(set(evidence)) != len(evidence)
    ):
        return None, f"findings[{index}].evidence is invalid"
    return (
        NormalizedFinding(
            critique=item["critique"].strip(),
            recommendation=item["recommendation"].strip(),
            reason=item["reason"].strip(),
            blocking=item["blocking"],
            source=source,
            evidence=tuple(evidence),
            equivalence_key=_issue_key(item["critique"], item["reason"]),
        ),
        None,
    )


def _validated_packet(
    packet: object, expected_target_path: str, expected_revision: int
) -> tuple[Mapping[str, Any] | None, tuple[NormalizedFinding, ...], str | None]:
    if not isinstance(packet, Mapping) or set(packet) != PACKET_KEYS:
        return None, (), "packet keys do not match full-analysis-v1"
    if packet["schema"] != PACKET_SCHEMA:
        return None, (), "packet schema is invalid"
    source = packet["source"]
    if source not in PACKET_SOURCES:
        return None, (), "packet source is invalid"
    if packet["target_path"] != expected_target_path:
        return None, (), "packet target_path is stale"
    if type(packet["target_revision"]) is not int or packet["target_revision"] != expected_revision:
        return None, (), "packet target_revision is stale"
    outcome = packet["outcome"]
    if outcome not in PACKET_OUTCOMES:
        return None, (), "packet outcome is invalid"
    if not all(isinstance(packet[key], list) for key in ("findings", "residual_risks", "diagnostics")):
        return None, (), "packet arrays are invalid"
    if any(not _non_empty(value) for value in packet["diagnostics"]):
        return None, (), "packet diagnostics are invalid"
    normalized: list[NormalizedFinding] = []
    finding_ids: set[str] = set()
    for index, item in enumerate(packet["findings"]):
        finding, error = _packet_finding(item, source, index)
        if error:
            return None, (), error
        assert finding is not None
        item_id = item["id"]
        if item_id in finding_ids:
            return None, (), "packet finding IDs must be unique"
        finding_ids.add(item_id)
        normalized.append(finding)
    blockers = tuple(item for item in normalized if item.blocking)
    diagnostics = tuple(packet["diagnostics"])
    if outcome == "accepted" and (blockers or diagnostics):
        return None, (), "accepted packet violates outcome invariants"
    if outcome == "revise-design" and not normalized:
        return None, (), "revise-design packet needs a finding"
    if outcome == "reopen-analysis" and not blockers:
        return None, (), "reopen-analysis packet needs a blocker"
    if outcome == "needs-clarification":
        text = " ".join(item.critique + " " + item.reason for item in blockers).casefold()
        if not blockers or not any(marker in text for marker in ("user decision", "unresolved", "clarif")):
            return None, (), "clarification packet needs an unresolved user decision"
    if outcome == "invalid-target" and not diagnostics:
        return None, (), "invalid-target packet needs diagnostics"
    if outcome == "request-separate-review" and (source != "independent" or not diagnostics):
        return None, (), "separate-review packet needs independent diagnostics"
    return packet, tuple(normalized), None


def _next_finding_number(findings: Sequence[ReviewFinding]) -> int:
    numbers = [
        int(match.group(1))
        for finding in findings
        if (match := FINDING_ID_PATTERN.fullmatch(finding.id))
    ]
    return max(numbers, default=0) + 1


def _union(left: Sequence[str], right: Sequence[str]) -> tuple[str, ...]:
    return tuple(dict.fromkeys((*left, *right)))


def consolidate_findings(
    existing: Sequence[ReviewFinding], incoming: Sequence[NormalizedFinding]
) -> tuple[ReviewFinding, ...]:
    findings = list(existing)
    next_number = _next_finding_number(findings)
    for item in incoming:
        exact_index = next(
            (
                index
                for index, finding in enumerate(findings)
                if finding.equivalence_key == item.equivalence_key
                and finding.recommendation == item.recommendation
            ),
            None,
        )
        conflict_indices = [
            index
            for index, finding in enumerate(findings)
            if finding.equivalence_key == item.equivalence_key
            and finding.recommendation != item.recommendation
        ]
        if exact_index is not None:
            current = findings[exact_index]
            findings[exact_index] = replace(
                current,
                source=", ".join(_union(current.source.split(", "), (item.source,))),
                sources=_union(current.sources or tuple(current.source.split(", ")), (item.source,)),
                blocking=current.blocking or item.blocking,
                evidence=_union(current.evidence, item.evidence),
                disposition=(
                    "open"
                    if current.blocking or item.blocking or current.conflict
                    else current.disposition
                ),
            )
            continue
        if conflict_indices:
            for index in conflict_indices:
                findings[index] = replace(findings[index], conflict=True, disposition="open")
        finding_id = f"F-{next_number:03d}"
        next_number += 1
        findings.append(
            ReviewFinding(
                id=finding_id,
                source=item.source,
                sources=(item.source,),
                critique=item.critique,
                recommendation=item.recommendation,
                reason=item.reason,
                blocking=item.blocking,
                evidence=item.evidence,
                disposition="open",
                equivalence_key=item.equivalence_key,
                conflict=bool(conflict_indices),
            )
        )
    return tuple(findings)


def _routed_document(
    document: DesignDocument,
    *,
    status: str,
    next_actor: str,
    next_action: str,
    reviewed_revision: int | None = None,
    approved_revision: int | None = None,
    ledger: Sequence[ReviewFinding] | None = None,
    review_sources: Sequence[str] | None = None,
) -> DesignDocument:
    header = replace(
        document.header,
        status=status,
        next_actor=next_actor,
        next_action=next_action,
        reviewed_revision=reviewed_revision,
        approved_revision=approved_revision,
        review_sources=tuple(
            document.header.review_sources if review_sources is None else review_sources
        ),
    )
    return replace(
        document,
        header=header,
        ledger=tuple(document.ledger if ledger is None else ledger),
    )


def apply_review_precedence(
    document: DesignDocument,
    packet_results: Sequence[Mapping[str, Any]],
    *,
    required_independent: bool,
) -> DesignDocument:
    valid_packets: list[Mapping[str, Any]] = []
    incoming: list[NormalizedFinding] = []
    seen_sources: set[str] = set()
    for packet in packet_results:
        if not isinstance(packet, Mapping):
            return _routed_document(
                document,
                status="analyzing",
                next_actor="agent",
                next_action="Discard the invalid packet and rerun analysis for the current revision.",
            )
        source = packet.get("source")
        if (
            not isinstance(source, str)
            or source not in PACKET_SOURCES
            or source in seen_sources
        ):
            return _routed_document(
                document,
                status="analyzing",
                next_actor="agent",
                next_action="Discard the invalid packet and rerun analysis for the current revision.",
            )
        seen_sources.add(source)
        validated, findings, error = _validated_packet(
            packet,
            expected_target_path=f"tmp/idea/{document.header.slug}/design.md",
            expected_revision=document.header.revision,
        )
        if error or validated is None:
            return _routed_document(
                document,
                status="analyzing",
                next_actor="agent",
                next_action="Discard the invalid packet and rerun analysis for the current revision.",
            )
        valid_packets.append(validated)
        incoming.extend(findings)

    ledger = consolidate_findings(document.ledger, incoming)
    sources = _union(
        document.header.review_sources,
        tuple(packet["source"] for packet in valid_packets),
    )
    if not valid_packets:
        return _routed_document(
            document,
            status="analyzing",
            next_actor="agent",
            next_action="Run the required review for the current revision.",
            ledger=ledger,
            review_sources=sources,
        )
    if not _review_sources_complete(
        document.header, sources, required_independent=required_independent
    ) and "standard" in sources:
        return _routed_document(
            document,
            status="awaiting-independent-review",
            next_actor="user",
            next_action="Obtain one isolated independent full-scope review for this revision.",
            ledger=ledger,
            review_sources=sources,
        )
    if "standard" not in sources:
        return _routed_document(
            document,
            status="analyzing",
            next_actor="agent",
            next_action="Obtain the required standard full-scope review for this revision.",
            ledger=ledger,
            review_sources=sources,
        )
    if any(
        packet["source"] == "independent" and packet["outcome"] == "request-separate-review"
        for packet in valid_packets
    ):
        return _routed_document(
            document,
            status="awaiting-independent-review",
            next_actor="user",
            next_action="Provide an isolated independent reviewer before continuing.",
            ledger=ledger,
            review_sources=sources,
        )
    if any(packet["outcome"] == "needs-clarification" for packet in valid_packets):
        return _routed_document(
            document,
            status="awaiting-decisions",
            next_actor="user",
            next_action="Answer the newly exposed user-owned decision in one bounded follow-up.",
            ledger=ledger,
            review_sources=sources,
        )
    if any(packet["outcome"] == "reopen-analysis" for packet in valid_packets):
        return _routed_document(
            document,
            status="analyzing",
            next_actor="agent",
            next_action="Reopen the assumption or scope analysis for this revision.",
            ledger=ledger,
            review_sources=sources,
        )
    if any(packet["outcome"] == "revise-design" for packet in valid_packets) or _has_open_blocker_or_conflict(ledger):
        return _routed_document(
            document,
            status="awaiting-remedy-decision",
            next_actor="user",
            next_action="Choose a remedy or explicitly accept the residual risk.",
            ledger=ledger,
            review_sources=sources,
        )
    return _routed_document(
        document,
        status="awaiting-final-approval",
        next_actor="user",
        next_action="Approve the current design or request a revision.",
        reviewed_revision=document.header.revision,
        ledger=ledger,
        review_sources=sources,
    )


def render_public_critique(findings: Sequence[ReviewFinding]) -> str:
    lines: list[str] = []
    for index, finding in enumerate(findings, start=1):
        lines.extend(
            (
                f"{index}. Critica: {finding.critique}",
                f"   Suggerimento: {finding.recommendation}",
                f"   Perché: {finding.reason}",
                f"   Bloccante: {'si' if finding.blocking else 'no'}",
            )
        )
    return "\n".join(lines)


def determine_assurance(signals: Mapping[str, object]) -> str:
    high_triggers = (
        "destructive",
        "security",
        "unknown_platform_claim",
        "feasibility_unknown",
        "explicit_user_request",
    )
    if any(bool(signals.get(trigger)) for trigger in high_triggers):
        return "high"
    if type(signals.get("independent_owners")) is int and signals["independent_owners"] >= 3:
        return "high"
    return "standard"


def route_final_approval(document: DesignDocument, command: str) -> ApprovalRoute:
    if not can_finalize_approval(document):
        return ApprovalRoute(
            approved=False,
            next_actor="user",
            next_action="The current revision is not eligible for final approval.",
        )
    normalized = command.strip().casefold()
    if any(word in normalized for word in ("esegui", "implementa", "execute")):
        return ApprovalRoute(
            approved=False,
            next_actor="user",
            next_action="Execution approval is a separate gateway decision.",
        )
    if "scrivi il piano" in normalized or "write the plan" in normalized:
        return ApprovalRoute(
            approved=True,
            next_actor="plan-writer",
            next_action="Route the approved design to /internal-gateway-writing-plans.",
        )
    if normalized in {"approvo", "approve", "approved"}:
        return ApprovalRoute(
            approved=True,
            next_actor="none",
            next_action="Design approved; stop before plan writing unless separately requested.",
        )
    return ApprovalRoute(
        approved=False,
        next_actor="user",
        next_action="Use an explicit current-revision approval phrase.",
    )


def resolve_route(prompt: str) -> RouteDecision:
    normalized = prompt.casefold()
    if any(term in normalized for term in ("critical analysis", "pressure-test", "challenge")):
        return RouteDecision("internal-gateway-critical-master")
    if "independent" in normalized and "review" in normalized:
        return RouteDecision("internal-review-high-level")
    if any(term in normalized for term in ("implement", "fix", "bounded task")):
        return RouteDecision("internal-gateway-simple-task")
    if any(term in normalized for term in ("idea", "brainstorm", "shape")):
        return RouteDecision("internal-gateway-idea")
    return RouteDecision("internal-gateway-idea")


__all__ = [
    "ApprovalRoute",
    "CoverageRow",
    "DesignDocument",
    "DesignHeader",
    "DesignValidationError",
    "NormalizedFinding",
    "ResumeRoute",
    "ReviewFinding",
    "RouteDecision",
    "apply_material_change",
    "apply_review_precedence",
    "can_complete_review",
    "can_finalize_approval",
    "can_handoff",
    "consolidate_findings",
    "determine_assurance",
    "parse_design_document",
    "render_public_critique",
    "resolve_route",
    "resume_route",
    "route_final_approval",
]
