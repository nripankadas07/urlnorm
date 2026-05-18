"""Tests for the top-level :func:`normalize` and :func:`equivalent` API."""

from __future__ import annotations

import pytest

from urlnorm import UrlNormError, equivalent, normalize


def test_normalize_lowercases_scheme_and_host() -> None:
    assert normalize("HTTP://Example.COM/") == "http://example.com/"


def test_normalize_preserves_path_case() -> None:
    assert normalize("https://example.com/AbC") == "https://example.com/AbC"


def test_normalize_strips_default_http_port() -> None:
    assert normalize("http://example.com:80/x") == "http://example.com/x"


def test_normalize_strips_default_https_port() -> None:
    assert normalize("https://example.com:443/x") == "https://example.com/x"


def test_normalize_keeps_non_default_port() -> None:
    assert normalize("http://example.com:8080/") == "http://example.com:8080/"


def test_normalize_keep_port_when_opt_off() -> None:
    assert (
        normalize("http://example.com:80/", strip_default_port=False)
        == "http://example.com:80/"
    )


def test_normalize_supplies_empty_path() -> None:
    assert normalize("https://example.com") == "https://example.com/"


def test_normalize_resolves_dot_segments() -> None:
    assert normalize("http://h/a/./b/../c") == "http://h/a/c"


def test_normalize_can_skip_dot_removal() -> None:
    assert (
        normalize("http://h/a/./b/../c", remove_dots=False)
        == "http://h/a/./b/../c"
    )


def test_normalize_canonicalizes_pct_in_path() -> None:
    assert (
        normalize("https://example.com/p%41/%2f")
        == "https://example.com/pA/%2F"
    )


def test_normalize_canonicalizes_pct_in_query() -> None:
    assert (
        normalize("https://example.com/?x=%2fa%2f")
        == "https://example.com/?x=%2Fa%2F"
    )


def test_normalize_strips_fragment_when_asked() -> None:
    assert (
        normalize("https://example.com/p#frag", strip_fragment=True)
        == "https://example.com/p"
    )


def test_normalize_canonicalizes_fragment() -> None:
    assert (
        normalize("https://example.com/p#%41%2F")
        == "https://example.com/p#A%2F"
    )


def test_normalize_sorts_query_when_asked() -> None:
    assert (
        normalize("https://h/p?z=3&a=1", sort_query=True)
        == "https://h/p?a=1&z=3"
    )


def test_normalize_canonicalizes_userinfo() -> None:
    assert (
        normalize("http://%41%42@example.com/")
        == "http://AB@example.com/"
    )


def test_normalize_lowercases_ipv6_host() -> None:
    assert (
        normalize("HTTP://[2001:DB8::1]:80/x")
        == "http://[2001:db8::1]/x"
    )


def test_normalize_default_scheme_attaches_when_missing() -> None:
    assert (
        normalize("//example.com/x", default_scheme="https")
        == "https://example.com/x"
    )


def test_normalize_default_scheme_does_not_override() -> None:
    assert (
        normalize("ftp://x/", default_scheme="https")
        == "ftp://x/"
    )


def test_normalize_default_scheme_invalid_raises() -> None:
    with pytest.raises(UrlNormError):
        normalize("//x/", default_scheme="9bad")


def test_normalize_rejects_non_string() -> None:
    with pytest.raises(UrlNormError):
        normalize(42)  # type: ignore[arg-type]


def test_equivalent_pct_encoding() -> None:
    assert equivalent(
        "https://example.com/p%2fq",
        "https://example.com/p%2Fq",
    )


def test_equivalent_with_default_port() -> None:
    assert equivalent("http://h:80/x", "http://H/x")


def test_equivalent_distinct_after_normalize() -> None:
    assert not equivalent("http://h/a", "http://h/b")


def test_normalize_keeps_relative_url_as_is() -> None:
    # Relative URLs without authority should still normalize cleanly.
    assert normalize("/a/./b/../c") == "/a/c"


def test_normalize_keeps_mailto_pass_through() -> None:
    # mailto: has no authority, no path-dot-segments, just a path payload.
    assert normalize("MAILTO:Alice@example.com") == "mailto:Alice@example.com"


def test_normalize_lowercases_scheme_only_for_ws() -> None:
    assert normalize("WS://example.com:80/echo") == "ws://example.com/echo"


def test_normalize_strips_default_ftp_port() -> None:
    assert normalize("ftp://example.com:21/path") == "ftp://example.com/path"


def test_normalize_empty_string_input_is_empty() -> None:
    assert normalize("") == ""


def test_normalize_sorts_stably_with_repeated_keys() -> None:
    assert normalize("https://h/p?k=b&k=a", sort_query=True) == "https://h/p?k=a&k=b"
