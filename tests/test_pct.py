"""Tests for percent-encoding canonicalization."""

from __future__ import annotations

from urlnorm._pct import canonicalize


def test_uppercases_hex_digits() -> None:
    assert canonicalize("%2f%3a") == "%2F%3A"


def test_decodes_unreserved_alpha() -> None:
    assert canonicalize("%41%42%63") == "ABc"


def test_decodes_unreserved_digit_dash_underscore_tilde() -> None:
    assert canonicalize("%30%2D%5F%7E") == "0-_~"


def test_decodes_unreserved_dot() -> None:
    assert canonicalize("%2E") == "."


def test_preserves_reserved_encoding() -> None:
    # ``/`` is reserved (sub-delim / gen-delim) — must stay encoded.
    assert canonicalize("a%2Fb") == "a%2Fb"


def test_passes_through_unmodified_text() -> None:
    assert canonicalize("hello world") == "hello world"


def test_leaves_bare_percent_alone() -> None:
    assert canonicalize("100%done") == "100%done"


def test_short_trailing_percent() -> None:
    assert canonicalize("ab%2") == "ab%2"


def test_invalid_hex_digit_kept_as_is() -> None:
    assert canonicalize("%ZZ") == "%ZZ"


def test_empty_string() -> None:
    assert canonicalize("") == ""


def test_mixed_pcr_run() -> None:
    assert canonicalize("/p%41%2F/%30") == "/pA%2F/0"


def test_canonicalize_uppercases_lowercase_hex_for_sub_delim() -> None:
    # '*' (0x2A) is sub-delim, not unreserved — must stay encoded but with
    # the hex digits upper-cased.
    assert canonicalize("%2a") == "%2A"


def test_canonicalize_does_not_decode_space() -> None:
    # ' ' (0x20) is neither unreserved nor reserved — leave encoded but
    # upper-case the hex.
    assert canonicalize("a%20b") == "a%20b"
