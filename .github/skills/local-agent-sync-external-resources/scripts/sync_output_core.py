from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, order=True)
class OutputRecord:
    record: str
    key: str
    status: str
    value: str


def escape_tsv(value: str) -> str:
    return (
        value
        .replace("\\", "\\\\")
        .replace("\t", "\\t")
        .replace("\n", "\\n")
        .replace("\r", "\\r")
    )


def render_tsv(records: tuple[OutputRecord, ...] | list[OutputRecord]) -> str:
    sorted_records = sorted(records)
    lines = ["record\tkey\tstatus\tvalue"]
    for record in sorted_records:
        lines.append(
            "\t".join(
                escape_tsv(field)
                for field in (
                    record.record,
                    record.key,
                    record.status,
                    record.value,
                )
            )
        )
    return "\n".join(lines) + "\n"
