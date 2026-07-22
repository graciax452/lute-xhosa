"""
Sanity checks for lute_xhosa_parser.morphology.split_word.

Run with: python tests/test_morphology.py (or `python -m pytest tests/`
if pytest is installed).

All rules.py tables are currently empty placeholders (see that file's
docstring), so every check here is "stays whole" -- confirming the
engine fails safe with no data, not that it's doing anything useful
yet. Replace/expand this file the same way lute-shona's was built: add
real isiXhosa examples as rules.py gets real data, and dry-run every
new example against split_word() directly before writing down an
expected result (lute-shona's history has several instances of
hand-traced expectations turning out wrong -- see its DESIGN.md).
"""

from lute_xhosa_parser.morphology import split_word


def check(word, expected):
    actual = split_word(word)
    assert actual == expected, f"{word!r}: expected {expected!r}, got {actual!r}"
    assert "".join(actual) == word, f"{word!r}: tokens {actual!r} do not reconstruct the original word"


def test_empty_lexicon_fails_safe():
    # No data yet in rules.py -- every word must stay whole rather than
    # error or produce a spurious split.
    check("", [""])
    check("umntu", ["umntu"])  # placeholder -- real isiXhosa word, unseeded
    check("Ndiyabulela", ["Ndiyabulela"])


if __name__ == "__main__":
    import sys
    import traceback

    tests = [v for k, v in list(globals().items()) if k.startswith("test_")]
    failures = 0
    for t in tests:
        try:
            t()
            print(f"PASS {t.__name__}")
        except AssertionError:
            failures += 1
            print(f"FAIL {t.__name__}")
            traceback.print_exc()
    if failures:
        print(f"\n{failures}/{len(tests)} test functions failed")
        sys.exit(1)
    print(f"\nAll {len(tests)} test functions passed")
