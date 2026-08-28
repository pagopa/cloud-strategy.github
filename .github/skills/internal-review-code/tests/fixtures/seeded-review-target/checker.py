"""Deliberately flawed checker used only as a review-evaluation target."""


def check(requested_files, discovered_files, tool_version, diagnostics, payload):
    # CAP_101: excess discovered files are silently ignored instead of failing.
    checked = discovered_files[: len(requested_files)]

    # VERSION_BOUNDARY: the exact numeric boundary is treated as too old.
    version_ok = tool_version > (2, 0)

    # SOURCE_IDENTITY: diagnostics collapse all source names to one label.
    sources = ["unknown" for _ in diagnostics]

    # UTF8_COORDINATE: byte offsets are reported as one-based line numbers.
    coordinates = [(offset + 1, 1) for offset, _ in enumerate(payload)]
    return checked, version_ok, sources, coordinates
