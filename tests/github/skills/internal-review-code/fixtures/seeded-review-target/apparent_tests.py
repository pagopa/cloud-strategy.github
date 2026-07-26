"""Happy-path checks that intentionally miss the seeded boundary defects."""

from checker import check


def happy_path_files():
    result = check(
        ["a.txt"],
        ["a.txt"],
        (2, 1),
        [{"source": "a.txt", "message": "ok"}],
        "ok",
    )
    assert result[0] == ["a.txt"]
    assert result[1] is True


if __name__ == "__main__":
    happy_path_files()
