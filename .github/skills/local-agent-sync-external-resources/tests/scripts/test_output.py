from sync_output_core import (
    OutputRecord,
    escape_tsv,
    render_tsv,
)


def test_escape_tsv_replaces_backslash_first() -> None:
    assert escape_tsv("a\\b") == "a\\\\b"


def test_escape_tsv_replaces_tab() -> None:
    assert escape_tsv("a\tb") == "a\\tb"


def test_escape_tsv_replaces_newline() -> None:
    assert escape_tsv("a\nb") == "a\\nb"


def test_escape_tsv_replaces_carriage_return() -> None:
    assert escape_tsv("a\rb") == "a\\rb"


def test_escape_tsv_order_backslash_before_others() -> None:
    assert escape_tsv("\\\t\n\r") == "\\\\\\t\\n\\r"


def test_render_tsv_header_is_fixed() -> None:
    records = [OutputRecord("summary", "mode", "ok", "audit")]
    output = render_tsv(records)
    first_line = output.split("\n", 1)[0]
    assert first_line == "record\tkey\tstatus\tvalue"


def test_render_tsv_sorts_lexically_by_record_key_status_value() -> None:
    records = [
        OutputRecord("z", "a", "ok", "v1"),
        OutputRecord("a", "z", "ok", "v2"),
        OutputRecord("a", "a", "ok", "v3"),
    ]
    output = render_tsv(records)
    lines = output.strip().split("\n")
    data_lines = lines[1:]
    assert data_lines == [
        "a\ta\tok\tv3",
        "a\tz\tok\tv2",
        "z\ta\tok\tv1",
    ]


def test_render_tsv_escapes_values() -> None:
    records = [OutputRecord("summary", "note", "ok", "has\ttab")]
    output = render_tsv(records)
    data_lines = output.strip().split("\n")[1:]
    assert len(data_lines) == 1
    assert "has\\ttab" in data_lines[0]
    assert "\t" not in data_lines[0].split("\t")[3]


def test_outcome_separates_delta_and_normalization_across_formats() -> None:
    from sync_external_resources import SyncOutcome, _format_text

    outcome = SyncOutcome(
        mode="plan", workspace="/tmp/workspace", managed_assets=1,
        changed_paths=("changed.txt",), normalized_paths=("normalized.txt",),
        override_results=(), validations=(), blockers=(), repository_changed=False,
    )
    payload = outcome.to_dict()
    assert payload["changed_paths"] == ["changed.txt"]
    assert payload["normalized_paths"] == ["normalized.txt"]
    records = outcome.to_records()
    assert OutputRecord("change", "changed.txt", "ok", "") in records
    assert OutputRecord("normalization", "normalized.txt", "ok", "") in records
    assert OutputRecord("summary", "normalized_paths", "ok", "1") in records
    text = _format_text(outcome)
    assert "Changed paths: 1" in text
    assert "Normalized paths: 1" in text
