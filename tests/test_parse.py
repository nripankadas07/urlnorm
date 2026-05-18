"""Tests for the low-level :func:`parse` / :func:`unparse` round-trip."""

from __future__ import annotations

import pytest

from urlnorm import UrlNormError, UrlParts, parse, unparse


def test_parse_full_url_extracts_every_component() -> None:
    parts = parse("https://user:pw@Example.com:8443/p/q?x=1&y=2#section")
    assert parts.scheme == "https"
    assert parts.userinfo == "user:pw"
    assert parts.host == "Example.com"
    assert parts.port == 8443
    assert parts.path == "/p/q"
    assert parts.query == "x=1&y=2"
    assert parts.fragment == "section"
    assert parts.has_authority is True


def test_parse_relative_path_only_has_no_authority() -> None:
    parts = parse("../a/b?z#f")
    assert parts.scheme == ""
    assert parts.has_authority is False
    assert parts.path == "../a/b"
    assert parts.query == "z"
    assert parts.fragment == "f"


def test_parse_scheme_must_start_with_letter() -> None:
    parts = parse("9foo:bar")
    # "9foo:bar" has no valid scheme; everything becomes the path.
    assert parts.scheme == ""
    assert parts.path == "9foo:bar"


def test_parse_scheme_allows_plus_dot_minus() -> None:
    parts = parse("git+ssh://example.org/repo")
    assert parts.scheme == "git+ssh"
    assert parts.host == "example.org"


def test_parse_letters_without_colon_are_not_a_scheme() -> None:
    # Leading letters but no terminating ':' — whole thing is a path.
    parts = parse("abc/def")
    assert parts.scheme == ""
    assert parts.path == "abc/def"


def test_parse_letter_then_slash_at_top_is_path() -> None:
    parts = parse("abc")
    assert parts.scheme == ""
    assert parts.path == "abc"


def test_parse_authority_present_but_empty() -> None:
    parts = parse("file:///etc/hosts")
    assert parts.has_authority is True
    assert parts.host == ""
    assert parts.path == "/etc/hosts"


def test_parse_ipv6_host_literal() -> None:
    parts = parse("http://[2001:db8::1]:8080/")
    assert parts.host == "[2001:db8::1]"
    assert parts.port == 8080


def test_parse_ipv6_without_port() -> None:
    parts = parse("http://[::1]/")
    assert parts.host == "[::1]"
    assert parts.port is None


def test_parse_ipv6_unterminated_raises() -> None:
    with pytest.raises(UrlNormError):
        parse("http://[::1/")


def test_parse_ipv6_garbage_after_bracket() -> None:
    with pytest.raises(UrlNormError):
        parse("http://[::1]garbage")


def test_parse_invalid_port_letters() -> None:
    with pytest.raises(UrlNormError):
        parse("http://example.com:abc/")


def test_parse_invalid_port_too_large() -> None:
    with pytest.raises(UrlNormError):
        parse("http://example.com:99999/")


def test_parse_empty_port_is_none() -> None:
    parts = parse("http://example.com:/")
    assert parts.port is None


def test_parse_query_only() -> None:
    parts = parse("?key=value")
    assert parts.query == "key=value"
    assert parts.path == ""
    assert parts.scheme == ""


def test_parse_fragment_only() -> None:
    parts = parse("#bare")
    assert parts.fragment == "bare"
    assert parts.path == ""


def test_parse_userinfo_with_multiple_at_signs() -> None:
    # rfind('@') used so the last @ separates userinfo from host.
    parts = parse("https://a@b@host.example/")
    assert parts.userinfo == "a@b"
    assert parts.host == "host.example"


def test_parse_rejects_non_string() -> None:
    with pytest.raises(UrlNormError):
        parse(123)  # type: ignore[arg-type]


def test_unparse_full_round_trip() -> None:
    src = "https://u@example.com:8000/p?x=1#f"
    assert unparse(parse(src)) == src


def test_unparse_no_authority_round_trip() -> None:
    src = "mailto:hello@example.com"
    assert unparse(parse(src)) == src


def test_unparse_rejects_non_parts() -> None:
    with pytest.raises(UrlNormError):
        unparse("https://example.com")  # type: ignore[arg-type]


def test_unparse_authority_with_no_userinfo_and_no_port() -> None:
    parts = UrlParts(scheme="http", host="example.com", has_authority=True, path="/")
    assert unparse(parts) == "http://example.com/"


def test_urlparts_authority_property_when_absent() -> None:
    parts = UrlParts()
    assert parts.authority == ""


def test_urlparts_replace_returns_new_instance() -> None:
    a = UrlParts(scheme="http", host="example.com", has_authority=True)
    b = a.replace(scheme="https")
    assert a.scheme == "http"
    assert b.scheme == "https"
